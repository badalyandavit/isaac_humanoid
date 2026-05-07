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
    minibatch_size: int | None = None
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
class SACConfig:
    env_id: str = "Humanoid-v5"
    seed: int = 3
    total_timesteps: int = 1_000_000
    num_envs: int = 1
    learning_rate: float = 3.0e-4
    q_learning_rate: float = 3.0e-4
    gamma: float = 0.99
    tau: float = 0.005
    buffer_size: int = 1_000_000
    batch_size: int = 256
    learning_starts: int = 10_000
    train_freq: int = 1
    gradient_steps: int = 1
    policy_frequency: int = 2
    target_network_frequency: int = 1
    alpha: float = 0.2
    autotune_alpha: bool = True
    target_entropy: float | None = None
    hidden_sizes: list[int] = field(default_factory=lambda: [256, 256])
    activation: str = "relu"
    obs_norm: bool = True
    reward_scale: float = 1.0
    max_grad_norm: float = 10.0
    device: str = "cuda"
    async_envs: bool = False
    log_interval_steps: int = 5_000
    eval_episodes: int = 5
    output_dir: str = "outputs/sac_baseline"


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


def load_sac_config(path: str | Path) -> SACConfig:
    return _merge_dict_into_dataclass(SACConfig(), load_yaml(path))
