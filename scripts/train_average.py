from __future__ import annotations

import argparse
import copy
from dataclasses import asdict

import numpy as np

from humanoid_rl.config import AverageConfig, load_average_config
from humanoid_rl.population.averaging import average_state_dicts
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import CSVLogger, ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/population_average.yaml")
    return parser.parse_args()


def make_workers(cfg: AverageConfig) -> list[PPOTrainer]:
    workers: list[PPOTrainer] = []
    for i in range(cfg.num_workers):
        worker_cfg = copy.deepcopy(cfg.worker)
        worker_cfg.env_id = cfg.env_id
        worker_cfg.seed = cfg.seed + 10_000 * i
        worker_cfg.num_envs = cfg.worker_num_envs
        worker_cfg.num_steps = cfg.worker_num_steps
        worker_cfg.device = cfg.device
        worker_cfg.output_dir = str(ensure_dir(cfg.output_dir) / f"worker_{i}")
        workers.append(PPOTrainer(worker_cfg, run_name=f"avg_worker_{i}"))
    return workers


def train_worker_round(worker: PPOTrainer, round_timesteps: int, total_updates: int) -> None:
    batch_size = worker.cfg.num_envs * worker.cfg.num_steps
    updates = max(1, round_timesteps // batch_size)
    for _ in range(updates):
        worker.train_one_update(total_updates=total_updates)


def main() -> None:
    args = parse_args()
    cfg = load_average_config(args.config)
    output_dir = ensure_dir(cfg.output_dir)
    write_json(output_dir / "average_config.json", asdict(cfg))
    workers = make_workers(cfg)
    logger = CSVLogger(output_dir / "average_rounds.csv")
    batch_size = cfg.worker_num_envs * cfg.worker_num_steps
    updates_per_round = max(1, cfg.round_timesteps // batch_size)
    total_updates = cfg.total_rounds * updates_per_round
    try:
        for round_idx in range(1, cfg.total_rounds + 1):
            for worker in workers:
                train_worker_round(worker, cfg.round_timesteps, total_updates)
            evals = [worker.evaluate(cfg.eval_episodes) for worker in workers]
            if round_idx % cfg.average_every_rounds == 0:
                avg_state = average_state_dicts([worker.policy_state_dict_cpu() for worker in workers])
                for worker in workers:
                    worker.load_policy_state_dict(avg_state)
                    if cfg.reset_optimizer_after_average:
                        worker.reset_optimizer()
            returns = [payload["mean_return"] for payload in evals]
            medians = [payload["median_return"] for payload in evals]
            row = {
                "round": round_idx,
                "mean_worker_return": float(np.mean(returns)),
                "median_worker_return": float(np.median(medians)),
                "best_worker": int(np.argmax(returns)),
                "best_mean_return": float(np.max(returns)),
            }
            for i, payload in enumerate(evals):
                row[f"worker_{i}_mean_return"] = payload["mean_return"]
                row[f"worker_{i}_median_return"] = payload["median_return"]
                row[f"worker_{i}_fall_rate"] = payload["fall_rate"]
            logger.write(row)
            print(row)
            if round_idx % max(1, cfg.total_rounds // 10) == 0:
                best_idx = int(np.argmax(returns))
                workers[best_idx].save(output_dir / "checkpoints" / f"best_round_{round_idx}.pt")
        final_state = average_state_dicts([worker.policy_state_dict_cpu() for worker in workers])
        workers[0].load_policy_state_dict(final_state)
        workers[0].save(output_dir / "checkpoints" / "final_average.pt")
    finally:
        for worker in workers:
            worker.close()


if __name__ == "__main__":
    main()
