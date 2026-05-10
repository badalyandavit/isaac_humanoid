"""Wrapper for Isaac Lab's skrl training launcher.

Trains PPO, SAC, or TD3 on `Isaac-Humanoid-Direct-Multi-v0` (must be installed
first via `scripts/install_isaac_skrl_offpolicy.py`). Reuses the Isaac config
machinery only for `isaaclab_dir` resolution; the algorithm choice and budget
are CLI flags.

Examples (run on the pod):

    # Add the Multi-v0 task with SAC/TD3 entry points (one-time):
    python scripts/install_isaac_skrl_offpolicy.py --config configs/isaac_ppo_baseline.yaml

    # PPO baseline at 4096 envs, 24k timesteps:
    python scripts/train_isaac_skrl.py --algorithm ppo --num-envs 4096 --timesteps 24000

    # SAC at 4096 envs, 24k timesteps (vectorized rollouts feeding a replay buffer):
    python scripts/train_isaac_skrl.py --algorithm sac --num-envs 4096 --timesteps 24000

    # TD3 at 4096 envs:
    python scripts/train_isaac_skrl.py --algorithm td3 --num-envs 4096 --timesteps 24000

Logs land under <isaaclab>/logs/skrl/<experiment>/<timestamp>/ as TensorBoard
events. Pull them with the same workflow as the rsl_rl PPO milestones.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from humanoid_rl.isaaclab import load_isaac_ppo_config, validate_isaaclab_dir
from humanoid_rl.utils import ensure_dir, write_json


VALID_ALGORITHMS = ("ppo", "sac", "td3")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml",
                        help="Reused only for isaaclab_dir / device. Reward overrides are ignored.")
    parser.add_argument("--algorithm", choices=VALID_ALGORITHMS, required=True)
    parser.add_argument("--task", type=str, default="Isaac-Humanoid-Direct-Multi-v0")
    parser.add_argument("--num-envs", type=int, default=4096)
    parser.add_argument("--timesteps", type=int, default=24000,
                        help="skrl trainer timesteps (env-step rollouts in the SequentialTrainer).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--experiment-name", type=str, default=None,
                        help="Defaults to humanoid_direct_skrl_<algorithm>.")
    parser.add_argument("--run-name", type=str, default="multi_v0")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="Manifest output dir; defaults to outputs/isaac_skrl_<algorithm>.")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--extra-hydra", nargs=argparse.REMAINDER,
                        help="Extra Hydra-style overrides forwarded to the launcher.")
    return parser.parse_args()


def build_command(args: argparse.Namespace, isaaclab_dir: Path, device: str) -> list[str]:
    isaaclab_sh = isaaclab_dir / "isaaclab.sh"
    command = [
        str(isaaclab_sh),
        "-p",
        "scripts/reinforcement_learning/skrl/train.py",
        "--task",
        args.task,
        "--algorithm",
        args.algorithm.upper(),
        "--num_envs",
        str(args.num_envs),
        "--seed",
        str(args.seed),
        "--max_iterations",
        str(max(1, args.timesteps)),
        "--device",
        device,
    ]
    if args.headless:
        command.append("--headless")
    if args.extra_hydra:
        command.extend(args.extra_hydra)
    return command


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    isaaclab_dir = Path(cfg.isaaclab_dir)
    validate_isaaclab_dir(isaaclab_dir)

    experiment = args.experiment_name or f"humanoid_direct_skrl_{args.algorithm}"
    out_dir = ensure_dir(args.out_dir or f"outputs/isaac_skrl_{args.algorithm}")
    command = build_command(args, isaaclab_dir, cfg.device)

    manifest = {
        "algorithm": f"skrl_{args.algorithm}",
        "task": args.task,
        "num_envs": args.num_envs,
        "timesteps": args.timesteps,
        "seed": args.seed,
        "experiment_name": experiment,
        "run_name": args.run_name,
        "device": cfg.device,
        "command": command,
        "logs_root_hint": str(isaaclab_dir / "logs" / "skrl" / experiment),
    }
    print("Isaac skrl training command:")
    print(" ".join(command))

    if args.dry_run:
        write_json(out_dir / "manifest_dry_run.json", manifest)
        print(f"Dry run; manifest written to {out_dir / 'manifest_dry_run.json'}")
        return

    start = time.perf_counter()
    completed = subprocess.run(command, cwd=str(isaaclab_dir), check=False)
    manifest["elapsed_seconds"] = time.perf_counter() - start
    manifest["return_code"] = completed.returncode
    write_json(out_dir / "manifest.json", manifest)
    if completed.returncode != 0:
        raise SystemExit(f"skrl {args.algorithm} training failed with code {completed.returncode}")
    print(f"Manifest written to {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
