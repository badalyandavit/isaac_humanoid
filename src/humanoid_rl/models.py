from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import torch
from torch import nn
from torch.distributions import Normal


def layer_init(layer: nn.Linear, std: float = np.sqrt(2), bias_const: float = 0.0) -> nn.Linear:
    nn.init.orthogonal_(layer.weight, std)
    nn.init.constant_(layer.bias, bias_const)
    return layer


def activation_module(name: str) -> nn.Module:
    if name == "tanh":
        return nn.Tanh()
    if name == "relu":
        return nn.ReLU()
    if name == "silu":
        return nn.SiLU()
    raise ValueError(f"Unsupported activation '{name}'.")


def mlp(input_dim: int, hidden_sizes: Sequence[int], output_dim: int, activation: str, output_std: float) -> nn.Sequential:
    layers: list[nn.Module] = []
    last_dim = input_dim
    for hidden in hidden_sizes:
        layers.append(layer_init(nn.Linear(last_dim, hidden)))
        layers.append(activation_module(activation))
        last_dim = hidden
    layers.append(layer_init(nn.Linear(last_dim, output_dim), std=output_std))
    return nn.Sequential(*layers)


class ActorCritic(nn.Module):
    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        action_low: np.ndarray,
        action_high: np.ndarray,
        hidden_sizes: Sequence[int] = (256, 256),
        activation: str = "tanh",
    ):
        super().__init__()
        self.actor_mean = mlp(obs_dim, hidden_sizes, action_dim, activation, output_std=0.01)
        self.critic = mlp(obs_dim, hidden_sizes, 1, activation, output_std=1.0)
        self.actor_logstd = nn.Parameter(torch.zeros(1, action_dim))
        self.register_buffer("action_low", torch.as_tensor(action_low, dtype=torch.float32))
        self.register_buffer("action_high", torch.as_tensor(action_high, dtype=torch.float32))

    def get_value(self, obs: torch.Tensor) -> torch.Tensor:
        return self.critic(obs).squeeze(-1)

    def get_action_and_value(
        self,
        obs: torch.Tensor,
        action: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        mean = self.actor_mean(obs)
        logstd = self.actor_logstd.expand_as(mean)
        std = torch.exp(logstd)
        dist = Normal(mean, std)
        raw_action = dist.rsample() if action is None else action
        logprob = dist.log_prob(raw_action).sum(-1)
        entropy = dist.entropy().sum(-1)
        clipped_action = torch.max(torch.min(raw_action, self.action_high), self.action_low)
        value = self.get_value(obs)
        return clipped_action, logprob, entropy, value, raw_action

    @torch.no_grad()
    def act_deterministic(self, obs: torch.Tensor) -> torch.Tensor:
        mean = self.actor_mean(obs)
        return torch.max(torch.min(mean, self.action_high), self.action_low)
