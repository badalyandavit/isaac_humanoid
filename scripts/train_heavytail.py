from __future__ import annotations

import argparse
import copy
from dataclasses import asdict

from humanoid_rl.config import HeavyTailConfig, load_heavytail_config
from humanoid_rl.population.orchestrator import RobustHeavyTailOrchestrator
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/population_heavytail.yaml")
    return parser.parse_args()


def make_workers(cfg: HeavyTailConfig) -> list[PPOTrainer]:
    workers: list[PPOTrainer] = []
    for i in range(cfg.num_workers):
        worker_cfg = copy.deepcopy(cfg.worker)
        worker_cfg.env_id = cfg.env_id
        worker_cfg.seed = cfg.seed + 10_000 * i
        worker_cfg.num_envs = cfg.worker_num_envs
        worker_cfg.num_steps = cfg.worker_num_steps
        worker_cfg.device = cfg.device
        worker_cfg.output_dir = str(ensure_dir(cfg.output_dir) / f"worker_{i}")
        workers.append(PPOTrainer(worker_cfg, run_name=f"ht_worker_{i}"))
    return workers


def train_worker_round(worker: PPOTrainer, round_timesteps: int, total_updates: int) -> None:
    batch_size = worker.cfg.num_envs * worker.cfg.num_steps
    updates = max(1, round_timesteps // batch_size)
    for _ in range(updates):
        worker.train_one_update(total_updates=total_updates)


def main() -> None:
    args = parse_args()
    cfg = load_heavytail_config(args.config)
    output_dir = ensure_dir(cfg.output_dir)
    write_json(output_dir / "heavytail_config.json", asdict(cfg))
    workers = make_workers(cfg)
    orchestrator = RobustHeavyTailOrchestrator(cfg, workers)
    batch_size = cfg.worker_num_envs * cfg.worker_num_steps
    updates_per_round = max(1, cfg.round_timesteps // batch_size)
    total_updates = cfg.total_rounds * updates_per_round
    try:
        best_global_score = float("-inf")
        for round_idx in range(1, cfg.total_rounds + 1):
            for worker in workers:
                train_worker_round(worker, cfg.round_timesteps, total_updates)
            evals = [worker.evaluate(cfg.eval_episodes) for worker in workers]
            result = orchestrator.orchestrate(round_idx, evals)
            row = result["row"]
            print(row)
            if row["best_robust_score"] > best_global_score:
                best_global_score = row["best_robust_score"]
                orchestrator.save_best(result["best_worker"], round_idx)
        best_worker = max(range(len(workers)), key=lambda i: workers[i].evaluate(cfg.eval_episodes)["median_return"])
        workers[best_worker].save(output_dir / "checkpoints" / "final_best.pt")
    finally:
        for worker in workers:
            worker.close()


if __name__ == "__main__":
    main()
