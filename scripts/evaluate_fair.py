from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sys
from typing import Any

import gymnasium as gym
import numpy as np
import torch
from tqdm.auto import tqdm

from humanoid_rl.config import (
    PPOConfig,
    SACConfig,
    load_ppo_action_average_config,
    load_ppo_config,
    load_sac_action_average_config,
    load_sac_config,
)
from humanoid_rl.envs import scalar_info
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.sac import SACTrainer
from humanoid_rl.utils import ensure_dir


class LoadedPolicy:
    def __init__(self, algorithm: str, trainer: PPOTrainer | SACTrainer):
        self.algorithm = algorithm
        self.trainer = trainer
        self.total_env_steps = int(getattr(trainer, "global_step", 0))

    @torch.no_grad()
    def act_deterministic(self, obs: np.ndarray) -> np.ndarray:
        obs_batch = np.asarray(obs, dtype=np.float32).reshape(1, self.trainer.obs_dim)
        if self.algorithm == "ppo":
            if self.trainer.cfg.obs_norm:
                obs_batch = self.trainer.obs_rms.normalize(obs_batch)
            obs_t = torch.as_tensor(obs_batch, dtype=torch.float32, device=self.trainer.device)
            return self.trainer.model.act_deterministic(obs_t).cpu().numpy()[0]
        return self.trainer.act(obs_batch, deterministic=True)[0]

    def close(self) -> None:
        self.trainer.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate single and action-averaged PPO/SAC policies.")
    parser.add_argument("--ppo-config", type=str, default="configs/fair_ppo_baseline.yaml")
    parser.add_argument("--ppo-checkpoint", type=str, default="outputs/fair_ppo_baseline/checkpoints/final.pt")
    parser.add_argument("--sac-config", type=str, default="configs/fair_sac_baseline.yaml")
    parser.add_argument("--sac-checkpoint", type=str, default="outputs/fair_sac_baseline/checkpoints/final.pt")
    parser.add_argument("--ppo-pop-config", type=str, default="configs/fair_ppo_population.yaml")
    parser.add_argument("--ppo-pop-dir", type=str, default="outputs/fair_ppo_population")
    parser.add_argument("--sac-pop-config", type=str, default="configs/fair_sac_population.yaml")
    parser.add_argument("--sac-pop-dir", type=str, default="outputs/fair_sac_population")
    parser.add_argument("--num-average-agents", type=str, default="1,2,4,8")
    parser.add_argument("--aggregators", type=str, default="mean", help="Comma list: mean,median,trimmed_mean")
    parser.add_argument("--trim-fraction", type=float, default=0.2)
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/fair_eval"))
    parser.add_argument("--video-episodes", type=int, default=0)
    parser.add_argument("--max-video-steps", type=int, default=1000)
    parser.add_argument(
        "--mujoco-gl",
        choices=["egl", "glfw", "osmesa"],
        default=None,
        help="MuJoCo OpenGL backend for video rendering. Defaults to egl on headless Linux.",
    )
    return parser.parse_args()


def configure_rendering(mujoco_gl: str | None) -> None:
    if mujoco_gl is not None:
        os.environ["MUJOCO_GL"] = mujoco_gl
    elif sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        os.environ.setdefault("MUJOCO_GL", "egl")
    if os.environ.get("MUJOCO_GL") == "egl":
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload if isinstance(payload, dict) else {}


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_ppo_policy(config: PPOConfig, checkpoint: Path, run_name: str) -> LoadedPolicy:
    cfg = copy_ppo_eval_config(config, run_name)
    trainer = PPOTrainer(cfg, run_name=run_name)
    trainer.load(checkpoint, load_optimizer=False)
    return LoadedPolicy("ppo", trainer)


def copy_ppo_eval_config(config: PPOConfig, run_name: str) -> PPOConfig:
    import copy

    cfg = copy.deepcopy(config)
    cfg.num_envs = 1
    cfg.output_dir = str(Path("outputs/eval_loaders") / run_name)
    return cfg


def load_sac_policy(config: SACConfig, checkpoint: Path, run_name: str) -> LoadedPolicy:
    import copy

    cfg = copy.deepcopy(config)
    cfg.num_envs = 1
    cfg.output_dir = str(Path("outputs/eval_loaders") / run_name)
    trainer = SACTrainer(cfg, run_name=run_name)
    trainer.load(checkpoint, load_optimizers=False)
    return LoadedPolicy("sac", trainer)


def aggregate_actions(actions: np.ndarray, aggregator: str, trim_fraction: float) -> np.ndarray:
    if aggregator == "mean":
        return np.mean(actions, axis=0)
    if aggregator == "median":
        return np.median(actions, axis=0)
    if aggregator == "trimmed_mean":
        sorted_actions = np.sort(actions, axis=0)
        k = int(np.floor(trim_fraction * sorted_actions.shape[0]))
        if 2 * k >= sorted_actions.shape[0]:
            return np.median(sorted_actions, axis=0)
        return np.mean(sorted_actions[k : sorted_actions.shape[0] - k], axis=0)
    raise ValueError(f"Unsupported aggregator '{aggregator}'.")


def evaluate_policy_set(
    *,
    method_key: str,
    method: str,
    algorithm: str,
    env_id: str,
    seed: int,
    policies: list[LoadedPolicy],
    episodes: int,
    aggregator: str,
    trim_fraction: float,
    out_dir: Path,
    video_episodes: int,
    max_video_steps: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    env = gym.make(env_id, render_mode="rgb_array" if video_episodes else None)
    action_low = np.asarray(env.action_space.low, dtype=np.float32)
    action_high = np.asarray(env.action_space.high, dtype=np.float32)
    episode_rows: list[dict[str, Any]] = []
    try:
        for episode_idx in tqdm(range(episodes), desc=f"{method_key} eval", unit="episode"):
            obs, _ = env.reset(seed=seed + 100_000 + episode_idx)
            done = False
            frames = []
            ep_return = 0.0
            ep_len = 0
            ep_ctrl = 0.0
            ep_forward = 0.0
            action_l2: list[float] = []
            action_smoothness: list[float] = []
            prev_action: np.ndarray | None = None
            while not done:
                if video_episodes and episode_idx < video_episodes and ep_len < max_video_steps:
                    frame = env.render()
                    if frame is not None:
                        frames.append(frame)
                actions = np.stack([policy.act_deterministic(obs) for policy in policies], axis=0)
                action = aggregate_actions(actions, aggregator, trim_fraction)
                action = np.clip(action, action_low, action_high)
                action_l2.append(float(np.linalg.norm(action)))
                if prev_action is not None:
                    action_smoothness.append(float(np.mean(np.square(action - prev_action))))
                prev_action = action.copy()
                obs, reward, terminated, truncated, info = env.step(action)
                done = bool(terminated or truncated)
                ep_return += float(reward)
                ep_len += 1
                ep_ctrl += scalar_info(info, "reward_ctrl", "reward_quadctrl", "control_cost", "reward_ctrl_cost") or 0.0
                ep_forward += scalar_info(info, "reward_forward", "reward_linvel", "x_velocity") or 0.0
            if frames:
                import imageio.v2 as imageio

                video_path = out_dir / "videos" / f"{method_key}_episode_{episode_idx}.mp4"
                ensure_dir(video_path.parent)
                imageio.mimsave(video_path, frames, fps=30)
            episode_rows.append(
                {
                    "method_key": method_key,
                    "method": method,
                    "algorithm": algorithm,
                    "episode": episode_idx,
                    "episode_return": ep_return,
                    "episode_length": ep_len,
                    "success_alive_duration": ep_len,
                    "fall": float(ep_len < 999),
                    "mean_forward_reward": ep_forward / max(1, ep_len),
                    "mean_ctrl_reward": ep_ctrl / max(1, ep_len),
                    "action_l2_norm": float(np.mean(action_l2)) if action_l2 else 0.0,
                    "action_smoothness": float(np.mean(action_smoothness)) if action_smoothness else 0.0,
                    "num_trained_agents_used": len(policies),
                    "aggregation_method": aggregator,
                    "total_env_steps": sum(policy.total_env_steps for policy in policies),
                }
            )
    finally:
        env.close()
    returns = np.asarray([row["episode_return"] for row in episode_rows], dtype=np.float64)
    lengths = np.asarray([row["episode_length"] for row in episode_rows], dtype=np.float64)
    summary = {
        "method_key": method_key,
        "method": method,
        "algorithm": algorithm,
        "episodes": episodes,
        "mean_return": float(np.mean(returns)),
        "median_return": float(np.median(returns)),
        "q25_return": float(np.quantile(returns, 0.25)),
        "q75_return": float(np.quantile(returns, 0.75)),
        "std_return": float(np.std(returns)),
        "mean_length": float(np.mean(lengths)),
        "success_alive_duration": float(np.mean(lengths)),
        "fall_rate": float(np.mean(lengths < 999)),
        "mean_forward_reward": float(np.mean([row["mean_forward_reward"] for row in episode_rows])),
        "mean_ctrl_reward": float(np.mean([row["mean_ctrl_reward"] for row in episode_rows])),
        "action_l2_norm": float(np.mean([row["action_l2_norm"] for row in episode_rows])),
        "action_smoothness": float(np.mean([row["action_smoothness"] for row in episode_rows])),
        "total_env_steps": sum(policy.total_env_steps for policy in policies),
        "num_trained_agents_used": len(policies),
        "aggregation_method": aggregator,
    }
    return episode_rows, summary


def load_manifest_checkpoints(pop_dir: Path) -> list[Path]:
    manifest = load_json(pop_dir / "manifest.json")
    checkpoints = manifest.get("checkpoints", [])
    return [Path(path) for path in checkpoints if Path(path).exists()]


def markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No evaluation rows were produced."
    columns = [
        "method",
        "num_trained_agents_used",
        "aggregation_method",
        "total_env_steps",
        "mean_return",
        "median_return",
        "q25_return",
        "fall_rate",
        "action_l2_norm",
        "action_smoothness",
    ]
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        vals = []
        for col in columns:
            value = row.get(col, "")
            vals.append(f"{value:.4g}" if isinstance(value, float) else str(value))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep, *body])


def main() -> None:
    args = parse_args()
    configure_rendering(args.mujoco_gl)
    out_dir = ensure_dir(args.out_dir)
    k_values = [int(x.strip()) for x in args.num_average_agents.split(",") if x.strip()]
    aggregators = [x.strip() for x in args.aggregators.split(",") if x.strip()]
    all_episode_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    ppo_checkpoint = Path(args.ppo_checkpoint)
    if ppo_checkpoint.exists():
        cfg = load_ppo_config(args.ppo_config)
        policies = [load_ppo_policy(cfg, ppo_checkpoint, "eval_ppo_single")]
        try:
            episodes = args.episodes or cfg.eval_episodes
            rows, summary = evaluate_policy_set(
                method_key="ppo_single",
                method="Single PPO",
                algorithm="ppo",
                env_id=cfg.env_id,
                seed=cfg.seed,
                policies=policies,
                episodes=episodes,
                aggregator="mean",
                trim_fraction=args.trim_fraction,
                out_dir=out_dir,
                video_episodes=args.video_episodes,
                max_video_steps=args.max_video_steps,
            )
            all_episode_rows.extend(rows)
            summaries.append(summary)
        finally:
            for policy in policies:
                policy.close()

    sac_checkpoint = Path(args.sac_checkpoint)
    if sac_checkpoint.exists():
        cfg = load_sac_config(args.sac_config)
        policies = [load_sac_policy(cfg, sac_checkpoint, "eval_sac_single")]
        try:
            episodes = args.episodes or cfg.eval_episodes
            rows, summary = evaluate_policy_set(
                method_key="sac_single",
                method="Single SAC",
                algorithm="sac",
                env_id=cfg.env_id,
                seed=cfg.seed,
                policies=policies,
                episodes=episodes,
                aggregator="mean",
                trim_fraction=args.trim_fraction,
                out_dir=out_dir,
                video_episodes=args.video_episodes,
                max_video_steps=args.max_video_steps,
            )
            all_episode_rows.extend(rows)
            summaries.append(summary)
        finally:
            for policy in policies:
                policy.close()

    ppo_pop_checkpoints = load_manifest_checkpoints(Path(args.ppo_pop_dir))
    if ppo_pop_checkpoints:
        cfg = load_ppo_action_average_config(args.ppo_pop_config)
        episodes = args.episodes or cfg.eval_episodes
        for k in k_values:
            if len(ppo_pop_checkpoints) < k:
                continue
            for aggregator in aggregators:
                policies = [
                    load_ppo_policy(cfg.agent, checkpoint, f"eval_ppo_avg_{k}_{idx}")
                    for idx, checkpoint in enumerate(ppo_pop_checkpoints[:k])
                ]
                try:
                    rows, summary = evaluate_policy_set(
                        method_key=f"ppo_average_k{k}_{aggregator}",
                        method=f"PPO Action Average K={k}",
                        algorithm="ppo",
                        env_id=cfg.env_id,
                        seed=cfg.seed,
                        policies=policies,
                        episodes=episodes,
                        aggregator=aggregator,
                        trim_fraction=args.trim_fraction,
                        out_dir=out_dir,
                        video_episodes=args.video_episodes,
                        max_video_steps=args.max_video_steps,
                    )
                    all_episode_rows.extend(rows)
                    summaries.append(summary)
                finally:
                    for policy in policies:
                        policy.close()

    sac_pop_checkpoints = load_manifest_checkpoints(Path(args.sac_pop_dir))
    if sac_pop_checkpoints:
        cfg = load_sac_action_average_config(args.sac_pop_config)
        episodes = args.episodes or cfg.eval_episodes
        for k in k_values:
            if len(sac_pop_checkpoints) < k:
                continue
            for aggregator in aggregators:
                policies = [
                    load_sac_policy(cfg.agent, checkpoint, f"eval_sac_avg_{k}_{idx}")
                    for idx, checkpoint in enumerate(sac_pop_checkpoints[:k])
                ]
                try:
                    rows, summary = evaluate_policy_set(
                        method_key=f"sac_average_k{k}_{aggregator}",
                        method=f"SAC Action Average K={k}",
                        algorithm="sac",
                        env_id=cfg.env_id,
                        seed=cfg.seed,
                        policies=policies,
                        episodes=episodes,
                        aggregator=aggregator,
                        trim_fraction=args.trim_fraction,
                        out_dir=out_dir,
                        video_episodes=args.video_episodes,
                        max_video_steps=args.max_video_steps,
                    )
                    all_episode_rows.extend(rows)
                    summaries.append(summary)
                finally:
                    for policy in policies:
                        policy.close()

    if not summaries:
        raise SystemExit("No checkpoints found to evaluate.")
    write_rows(out_dir / "episodes.csv", all_episode_rows)
    write_rows(out_dir / "summary.csv", summaries)
    (out_dir / "summary.md").write_text("# Fair PPO/SAC Evaluation\n\n" + markdown_table(summaries) + "\n", encoding="utf-8")
    print(f"Wrote fair evaluation outputs to {out_dir}")


if __name__ == "__main__":
    main()
