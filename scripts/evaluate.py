from __future__ import annotations

import argparse

from humanoid_rl.config import load_ppo_config
from humanoid_rl.ppo import PPOTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/baseline_ppo.yaml")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--stochastic", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_ppo_config(args.config)
    trainer = PPOTrainer(cfg, run_name="eval")
    try:
        trainer.load(args.checkpoint, load_optimizer=False)
        metrics = trainer.evaluate(args.episodes, deterministic=not args.stochastic)
        print(metrics)
    finally:
        trainer.close()


if __name__ == "__main__":
    main()
