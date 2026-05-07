from __future__ import annotations

import argparse

from humanoid_rl.isaaclab import load_isaac_ppo_config, run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    manifest = run_training(cfg, dry_run=args.dry_run)
    print("Isaac PPO baseline manifest:")
    print(f"  task: {manifest['task']}")
    print(f"  expected_env_steps: {manifest['expected_env_steps']}")
    print(f"  checkpoint: {manifest['checkpoint']}")


if __name__ == "__main__":
    main()
