from __future__ import annotations

import argparse
import copy
from dataclasses import asdict

from tqdm.auto import tqdm

from humanoid_rl.isaaclab import (
    expected_env_steps,
    load_isaac_ppo_population_config,
    run_training,
)
from humanoid_rl.utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_population.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_population_config(args.config)
    output_dir = ensure_dir(cfg.output_dir)
    write_json(output_dir / "population_config.json", asdict(cfg))
    manifests = []
    checkpoints = []
    total_expected_env_steps = 0
    for agent_idx in tqdm(range(cfg.num_train_agents), desc="isaac ppo train agents", unit="agent"):
        agent_cfg = copy.deepcopy(cfg.agent)
        agent_cfg.seed = cfg.seed + 10_000 * agent_idx
        agent_cfg.run_name = f"{cfg.run_name_prefix}_{agent_idx}"
        agent_cfg.output_dir = str(output_dir / f"agent_{agent_idx}")
        manifest = run_training(agent_cfg, dry_run=args.dry_run)
        manifests.append(manifest)
        if manifest["checkpoint"]:
            checkpoints.append(manifest["checkpoint"])
        total_expected_env_steps += expected_env_steps(agent_cfg)
    write_json(
        output_dir / "manifest.json",
        {
            "task": cfg.task,
            "algorithm": "isaac_rsl_rl_ppo_action_average",
            "num_train_agents": cfg.num_train_agents,
            "num_average_agents": cfg.num_average_agents,
            "budget_mode": cfg.budget_mode,
            "configured_total_timesteps": cfg.total_timesteps,
            "per_agent_timesteps": cfg.agent.total_timesteps,
            "expected_aggregate_env_steps": total_expected_env_steps,
            "checkpoints": checkpoints,
            "agent_manifests": manifests,
            "config_path": args.config,
        },
    )


if __name__ == "__main__":
    main()

