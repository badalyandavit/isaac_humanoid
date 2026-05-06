from __future__ import annotations

import argparse
import copy
from dataclasses import asdict

import pandas as pd

from humanoid_rl.config import HeavyTailConfig, load_heavytail_config
from humanoid_rl.population.orchestrator import RobustHeavyTailOrchestrator
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/scaling_sweep.yaml")
    parser.add_argument("--agents", type=str, default="1,2,4,8")
    parser.add_argument("--rounds", type=int, default=None)
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
        workers.append(PPOTrainer(worker_cfg, run_name=f"scale_worker_{i}"))
    return workers


def train_worker_round(worker: PPOTrainer, round_timesteps: int, total_updates: int) -> None:
    batch_size = worker.cfg.num_envs * worker.cfg.num_steps
    updates = max(1, round_timesteps // batch_size)
    for _ in range(updates):
        worker.train_one_update(total_updates=total_updates)


def run_one(base_cfg: HeavyTailConfig, n_agents: int, rounds: int | None) -> dict:
    cfg = copy.deepcopy(base_cfg)
    cfg.num_workers = n_agents
    if rounds is not None:
        cfg.total_rounds = rounds
    cfg.output_dir = str(ensure_dir(base_cfg.output_dir) / f"N_{n_agents}")
    workers = make_workers(cfg)
    orchestrator = RobustHeavyTailOrchestrator(cfg, workers)
    batch_size = cfg.worker_num_envs * cfg.worker_num_steps
    updates_per_round = max(1, cfg.round_timesteps // batch_size)
    total_updates = cfg.total_rounds * updates_per_round
    final_row = None
    try:
        for round_idx in range(1, cfg.total_rounds + 1):
            for worker in workers:
                train_worker_round(worker, cfg.round_timesteps, total_updates)
            evals = [worker.evaluate(cfg.eval_episodes) for worker in workers]
            result = orchestrator.orchestrate(round_idx, evals)
            final_row = result["row"]
    finally:
        for worker in workers:
            worker.close()
    if final_row is None:
        raise RuntimeError("No scaling result produced.")
    return {
        "num_workers": n_agents,
        "total_rounds": cfg.total_rounds,
        "round_timesteps": cfg.round_timesteps,
        "best_robust_score": final_row["best_robust_score"],
        "median_robust_score": final_row["median_robust_score"],
        "mean_robust_score": final_row["mean_robust_score"],
        "num_clones_last_round": final_row["num_clones"],
    }


def main() -> None:
    args = parse_args()
    base_cfg = load_heavytail_config(args.config)
    output_dir = ensure_dir(base_cfg.output_dir)
    write_json(output_dir / "scaling_config.json", asdict(base_cfg))
    agent_counts = [int(x.strip()) for x in args.agents.split(",") if x.strip()]
    rows = [run_one(base_cfg, n, args.rounds) for n in agent_counts]
    df = pd.DataFrame(rows)
    out = output_dir / "scaling_summary.csv"
    df.to_csv(out, index=False)
    print(df)
    print(f"Saved scaling summary to {out}")


if __name__ == "__main__":
    main()
