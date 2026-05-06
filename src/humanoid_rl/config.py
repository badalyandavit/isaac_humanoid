from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PPOConfig:
    env_id: str = "Humanoid-v5"
    seed: int = 1
    total_timesteps: int = 1_000_000
    num_envs: int = 8
    num_steps: int = 1024
    learning_rate: float = 3.0e-4
    anneal_lr: bool = True
    gamma: float = 0.99
    gae_lambda: float = 0.95
    num_minibatches: int = 16
    update_epochs: int = 10
    norm_adv: bool = True
    clip_coef: float = 0.2
    clip_vloss: bool = True
    ent_coef: float = 0.0
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    target_kl: float | None = 0.03
    hidden_sizes: list[int] = field(default_factory=lambda: [256, 256])
    activation: str = "tanh"
    obs_norm: bool = True
    reward_scale: float = 1.0
    device: str = "cuda"
    torch_compile: bool = False
    amp: bool = False
    async_envs: bool = False
    log_interval_updates: int = 1
    eval_interval_updates: int = 10
    eval_episodes: int = 5
    save_interval_updates: int = 25
    output_dir: str = "outputs/baseline"


@dataclass
class PopulationConfig:
    env_id: str = "Humanoid-v5"
    seed: int = 7
    num_workers: int = 4
    total_rounds: int = 100
    round_timesteps: int = 65_536
    worker_num_envs: int = 4
    worker_num_steps: int = 512
    eval_episodes: int = 8
    graph: str = "complete"
    graph_gamma: int = 1
    output_dir: str = "outputs/population"
    device: str = "cuda"
    worker: PPOConfig = field(default_factory=PPOConfig)


@dataclass
class AverageConfig(PopulationConfig):
    average_every_rounds: int = 1
    reset_optimizer_after_average: bool = True


@dataclass
class HeavyTailConfig(PopulationConfig):
    trim_fraction: float = 0.2
    q_low: float = 0.25
    median_weight: float = 0.5
    fall_penalty: float = 500.0
    energy_penalty: float = 0.0
    promote_margin: float = 50.0
    protect_top_fraction: float = 0.25
    mutate_lr_log_scale: float = 0.20
    mutate_ent_coef_log_scale: float = 0.25
    policy_noise_std: float = 0.001
    min_rounds_before_clone: int = 2
    max_clones_per_round: int = 2
    distill_elites_after: bool = False
    elite_fraction: float = 0.25


def _merge_dict_into_dataclass(obj: Any, data: dict[str, Any]) -> Any:
    for key, value in data.items():
        if not hasattr(obj, key):
            raise KeyError(f"Unknown config key '{key}' for {type(obj).__name__}")
        current = getattr(obj, key)
        if hasattr(current, "__dataclass_fields__") and isinstance(value, dict):
            _merge_dict_into_dataclass(current, value)
        else:
            setattr(obj, key, value)
    return obj


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must contain a YAML mapping.")
    return data


def load_ppo_config(path: str | Path) -> PPOConfig:
    return _merge_dict_into_dataclass(PPOConfig(), load_yaml(path))


def load_average_config(path: str | Path) -> AverageConfig:
    cfg = AverageConfig()
    data = load_yaml(path)
    if "worker" not in data:
        data["worker"] = {}
    data["worker"].setdefault("env_id", data.get("env_id", cfg.env_id))
    data["worker"].setdefault("device", data.get("device", cfg.device))
    data["worker"].setdefault("num_envs", data.get("worker_num_envs", cfg.worker_num_envs))
    data["worker"].setdefault("num_steps", data.get("worker_num_steps", cfg.worker_num_steps))
    return _merge_dict_into_dataclass(cfg, data)


def load_heavytail_config(path: str | Path) -> HeavyTailConfig:
    cfg = HeavyTailConfig()
    data = load_yaml(path)
    if "worker" not in data:
        data["worker"] = {}
    data["worker"].setdefault("env_id", data.get("env_id", cfg.env_id))
    data["worker"].setdefault("device", data.get("device", cfg.device))
    data["worker"].setdefault("num_envs", data.get("worker_num_envs", cfg.worker_num_envs))
    data["worker"].setdefault("num_steps", data.get("worker_num_steps", cfg.worker_num_steps))
    return _merge_dict_into_dataclass(cfg, data)
