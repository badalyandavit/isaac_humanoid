from __future__ import annotations

import argparse

from humanoid_rl.config import load_sac_config
from humanoid_rl.sac import SACTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/fair_sac_baseline.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_sac_config(args.config)
    trainer = SACTrainer(cfg, run_name="sac_baseline")
    trainer.dump_config()
    try:
        trainer.train(cfg.total_timesteps)
        metrics = trainer.evaluate(cfg.eval_episodes, show_progress=True, desc="sac baseline eval")
        print(metrics)
        trainer.save(trainer.output_dir / "checkpoints" / "final.pt")
    finally:
        trainer.close()


if __name__ == "__main__":
    main()
