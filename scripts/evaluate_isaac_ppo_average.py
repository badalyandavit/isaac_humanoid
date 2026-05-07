"""Evaluate Isaac Lab RSL-RL PPO checkpoints with deterministic action averaging.

Run this script with the Isaac Lab launcher, for example:

    /workspace/IsaacLab/isaaclab.sh -p scripts/evaluate_isaac_ppo_average.py ...
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Evaluate Isaac Lab PPO checkpoints with action averaging.")
parser.add_argument("--task", type=str, default="Isaac-Humanoid-Direct-v0")
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoints", nargs="+", required=True)
parser.add_argument("--aggregator", choices=["mean", "median", "trimmed_mean"], default="mean")
parser.add_argument("--episodes", type=int, default=20)
parser.add_argument("--max-steps", type=int, default=20_000)
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--seed", type=int, default=501)
parser.add_argument("--output-dir", type=Path, default=Path("outputs/isaac_fair_eval"))
parser.add_argument("--video", action="store_true")
parser.add_argument("--video-length", type=int, default=500)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()
if args_cli.video:
    args_cli.enable_cameras = True
sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from isaaclab.envs import (  # noqa: E402
    DirectMARLEnv,
    DirectMARLEnvCfg,
    DirectRLEnvCfg,
    ManagerBasedRLEnvCfg,
    multi_agent_to_single_agent,
)
from isaaclab.utils.assets import retrieve_file_path  # noqa: E402
from isaaclab.utils.dict import print_dict  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlBaseRunnerCfg,
    RslRlVecEnvWrapper,
    handle_deprecated_rsl_rl_cfg,
)
import isaaclab_tasks  # noqa: E402,F401
from isaaclab_tasks.utils.hydra import hydra_task_config  # noqa: E402


def aggregate_actions(actions: list[torch.Tensor], method: str) -> torch.Tensor:
    stacked = torch.stack(actions, dim=0)
    if method == "mean":
        return stacked.mean(dim=0)
    if method == "median":
        return stacked.median(dim=0).values
    if method == "trimmed_mean":
        if stacked.shape[0] <= 2:
            return stacked.mean(dim=0)
        sorted_actions = stacked.sort(dim=0).values
        return sorted_actions[1:-1].mean(dim=0)
    raise ValueError(f"Unsupported aggregator: {method}")


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(out_dir: Path, rows: list[dict[str, float | int | str]]) -> None:
    if not rows:
        return
    returns = np.asarray([float(row["episode_return"]) for row in rows], dtype=np.float64)
    lengths = np.asarray([float(row["episode_length"]) for row in rows], dtype=np.float64)
    fall_rates = np.asarray([float(row["fall"]) for row in rows], dtype=np.float64)
    action_l2 = np.asarray([float(row["action_l2_norm"]) for row in rows], dtype=np.float64)
    smoothness = np.asarray([float(row["action_smoothness"]) for row in rows], dtype=np.float64)
    summary = {
        "method_key": rows[0]["method_key"],
        "task": rows[0]["task"],
        "algorithm": "isaac_rsl_rl_ppo_action_average",
        "num_agents": int(rows[0]["num_agents"]),
        "aggregator": rows[0]["aggregator"],
        "episodes": len(rows),
        "mean_return": float(returns.mean()),
        "median_return": float(np.median(returns)),
        "p25_return": float(np.percentile(returns, 25)),
        "mean_episode_length": float(lengths.mean()),
        "fall_rate": float(fall_rates.mean()),
        "mean_action_l2_norm": float(action_l2.mean()),
        "mean_action_smoothness": float(smoothness.mean()),
    }
    write_csv(out_dir / "summary.csv", [summary])
    with (out_dir / "summary.md").open("w", encoding="utf-8") as f:
        f.write("| Method | K | Aggregator | Episodes | Mean Return | Median Return | Fall Rate |\n")
        f.write("|---|---:|---|---:|---:|---:|---:|\n")
        f.write(
            f"| {summary['method_key']} | {summary['num_agents']} | {summary['aggregator']} | "
            f"{summary['episodes']} | {summary['mean_return']:.3f} | "
            f"{summary['median_return']:.3f} | {summary['fall_rate']:.3f} |\n"
        )


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg, agent_cfg: RslRlBaseRunnerCfg):
    import importlib.metadata as metadata

    installed_version = metadata.version("rsl-rl-lib")
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    agent_cfg.device = args_cli.device if args_cli.device is not None else agent_cfg.device
    out_dir = args_cli.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)
    if args_cli.video:
        video_kwargs = {
            "video_folder": str(out_dir / "videos" / f"k{len(args_cli.checkpoints)}_{args_cli.aggregator}"),
            "step_trigger": lambda step: step == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print("[INFO] Recording Isaac evaluation video.")
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    policies = []
    for checkpoint in args_cli.checkpoints:
        resume_path = retrieve_file_path(checkpoint)
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
        runner.load(resume_path)
        policies.append(runner.get_inference_policy(device=env.unwrapped.device))
        print(f"[INFO] Loaded checkpoint: {resume_path}")

    obs = env.get_observations()
    device = obs.device
    num_envs = obs.shape[0]
    episode_returns = torch.zeros(num_envs, dtype=torch.float32, device=device)
    episode_lengths = torch.zeros(num_envs, dtype=torch.long, device=device)
    action_l2_sum = torch.zeros(num_envs, dtype=torch.float32, device=device)
    action_smooth_sum = torch.zeros(num_envs, dtype=torch.float32, device=device)
    action_smooth_count = torch.zeros(num_envs, dtype=torch.float32, device=device)
    prev_actions: torch.Tensor | None = None
    has_prev_action = torch.zeros(num_envs, dtype=torch.bool, device=device)
    max_episode_length = int(getattr(env.unwrapped, "max_episode_length", 0) or 0)
    rows: list[dict[str, float | int | str]] = []
    method_key = f"isaac_ppo_avg_k{len(policies)}_{args_cli.aggregator}"

    step = 0
    while simulation_app.is_running() and len(rows) < args_cli.episodes and step < args_cli.max_steps:
        with torch.inference_mode():
            actions = aggregate_actions([policy(obs) for policy in policies], args_cli.aggregator)
            action_l2_sum += torch.linalg.norm(actions, dim=-1)
            if prev_actions is not None:
                smooth = torch.mean(torch.square(actions - prev_actions), dim=-1)
                action_smooth_sum[has_prev_action] += smooth[has_prev_action]
                action_smooth_count[has_prev_action] += 1.0
            prev_actions = actions.detach().clone()
            has_prev_action[:] = True
            obs, rewards, dones, _ = env.step(actions)
            episode_returns += rewards
            episode_lengths += 1
            for policy in policies:
                if hasattr(policy, "reset"):
                    policy.reset(dones)

        done_ids = torch.nonzero(dones, as_tuple=False).flatten().tolist()
        for env_idx in done_ids:
            if len(rows) >= args_cli.episodes:
                break
            ep_len = int(episode_lengths[env_idx].item())
            timeout = bool(max_episode_length and ep_len >= max_episode_length - 1)
            rows.append(
                {
                    "method_key": method_key,
                    "task": args_cli.task,
                    "algorithm": "isaac_rsl_rl_ppo",
                    "num_agents": len(policies),
                    "aggregator": args_cli.aggregator,
                    "episode": len(rows),
                    "episode_return": float(episode_returns[env_idx].item()),
                    "episode_length": ep_len,
                    "fall": 0 if timeout else 1,
                    "action_l2_norm": float(action_l2_sum[env_idx].item() / max(1, ep_len)),
                    "action_smoothness": float(
                        action_smooth_sum[env_idx].item() / max(1.0, action_smooth_count[env_idx].item())
                    ),
                }
            )
            episode_returns[env_idx] = 0.0
            episode_lengths[env_idx] = 0
            action_l2_sum[env_idx] = 0.0
            action_smooth_sum[env_idx] = 0.0
            action_smooth_count[env_idx] = 0.0
            has_prev_action[env_idx] = False
        step += 1

    write_csv(out_dir / "episodes.csv", rows)
    write_summary(out_dir, rows)
    print(f"[INFO] Wrote Isaac evaluation outputs to: {out_dir}")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
