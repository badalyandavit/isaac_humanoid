from __future__ import annotations

import argparse
import copy
from dataclasses import asdict

from tqdm.auto import tqdm

from humanoid_rl.config import PPOActionAverageConfig, load_ppo_action_average_config
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/fair_ppo_population.yaml")
    return parser.parse_args()


def make_agent_config(cfg: PPOActionAverageConfig, agent_idx: int):
    agent_cfg = copy.deepcopy(cfg.agent)
    agent_cfg.env_id = cfg.env_id
    agent_cfg.seed = cfg.seed + 10_000 * agent_idx
    agent_cfg.device = cfg.device
    agent_cfg.output_dir = str(ensure_dir(cfg.output_dir) / f"agent_{agent_idx}")
    return agent_cfg


def main() -> None:
    args = parse_args()
    cfg = load_ppo_action_average_config(args.config)
    output_dir = ensure_dir(cfg.output_dir)
    write_json(output_dir / "population_config.json", asdict(cfg))
    checkpoints: list[str] = []
    total_agent_steps = 0
    for agent_idx in tqdm(range(cfg.num_train_agents), desc="ppo train agents", unit="agent"):
        agent_cfg = make_agent_config(cfg, agent_idx)
        trainer = PPOTrainer(agent_cfg, run_name=f"ppo_agent_{agent_idx}")
        trainer.dump_config()
        try:
            trainer.train(agent_cfg.total_timesteps, desc=f"ppo agent {agent_idx} updates")
            path = trainer.output_dir / "checkpoints" / "final.pt"
            trainer.save(path)
            checkpoints.append(str(path))
            total_agent_steps += trainer.global_step
        finally:
            trainer.close()
    write_json(
        output_dir / "manifest.json",
        {
            "algorithm": "ppo",
            "num_train_agents": cfg.num_train_agents,
            "budget_mode": cfg.budget_mode,
            "configured_total_timesteps": cfg.total_timesteps,
            "per_agent_timesteps": cfg.agent.total_timesteps,
            "actual_aggregate_env_steps": total_agent_steps,
            "checkpoints": checkpoints,
            "config_path": args.config,
        },
    )


if __name__ == "__main__":
    main()
