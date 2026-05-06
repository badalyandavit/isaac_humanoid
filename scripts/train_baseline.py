from __future__ import annotations

import argparse

from humanoid_rl.config import load_ppo_config
from humanoid_rl.ppo import PPOTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/baseline_ppo.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_ppo_config(args.config)
    trainer = PPOTrainer(cfg, run_name="baseline")
    trainer.dump_config()
    try:
        trainer.train(cfg.total_timesteps)
        metrics = trainer.evaluate(cfg.eval_episodes)
        print(metrics)
        trainer.save(trainer.output_dir / "checkpoints" / "final.pt")
    finally:
        trainer.close()


if __name__ == "__main__":
    main()
