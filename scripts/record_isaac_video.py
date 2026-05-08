from __future__ import annotations

import argparse
from pathlib import Path

from humanoid_rl.isaaclab import load_isaac_ppo_config, run_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record an Isaac Lab RSL-RL PPO policy video.")
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("outputs/videos/isaac_policy.mp4"))
    parser.add_argument("--num-envs", type=int, default=1)
    parser.add_argument("--video-length", type=int, default=None)
    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    manifest = run_video(
        cfg,
        checkpoint=args.checkpoint,
        out=args.out,
        num_envs=args.num_envs,
        video_length=args.video_length,
        headless=not args.no_headless,
        dry_run=args.dry_run,
    )
    print("Isaac video manifest:")
    print(f"  baseline: {manifest['baseline_name']}")
    print(f"  checkpoint: {manifest['checkpoint']}")
    print(f"  video: {manifest['copied_video']}")


if __name__ == "__main__":
    main()
