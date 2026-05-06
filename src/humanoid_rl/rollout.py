from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class RolloutBatch:
    obs: torch.Tensor
    actions: torch.Tensor
    logprobs: torch.Tensor
    rewards: torch.Tensor
    dones: torch.Tensor
    values: torch.Tensor
    advantages: torch.Tensor
    returns: torch.Tensor


class RolloutStorage:
    def __init__(self, num_steps: int, num_envs: int, obs_dim: int, action_dim: int, device: torch.device):
        self.num_steps = num_steps
        self.num_envs = num_envs
        self.device = device
        self.obs = torch.zeros((num_steps, num_envs, obs_dim), device=device)
        self.actions = torch.zeros((num_steps, num_envs, action_dim), device=device)
        self.logprobs = torch.zeros((num_steps, num_envs), device=device)
        self.rewards = torch.zeros((num_steps, num_envs), device=device)
        self.dones = torch.zeros((num_steps, num_envs), device=device)
        self.values = torch.zeros((num_steps, num_envs), device=device)
        self.advantages = torch.zeros((num_steps, num_envs), device=device)
        self.returns = torch.zeros((num_steps, num_envs), device=device)

    def compute_gae(
        self,
        next_value: torch.Tensor,
        next_done: torch.Tensor,
        gamma: float,
        gae_lambda: float,
    ) -> None:
        lastgaelam = torch.zeros(self.num_envs, device=self.device)
        for t in reversed(range(self.num_steps)):
            if t == self.num_steps - 1:
                next_nonterminal = 1.0 - next_done
                next_values = next_value
            else:
                next_nonterminal = 1.0 - self.dones[t + 1]
                next_values = self.values[t + 1]
            delta = self.rewards[t] + gamma * next_values * next_nonterminal - self.values[t]
            lastgaelam = delta + gamma * gae_lambda * next_nonterminal * lastgaelam
            self.advantages[t] = lastgaelam
        self.returns = self.advantages + self.values

    def flatten(self) -> RolloutBatch:
        return RolloutBatch(
            obs=self.obs.reshape((-1, self.obs.shape[-1])),
            actions=self.actions.reshape((-1, self.actions.shape[-1])),
            logprobs=self.logprobs.reshape(-1),
            rewards=self.rewards.reshape(-1),
            dones=self.dones.reshape(-1),
            values=self.values.reshape(-1),
            advantages=self.advantages.reshape(-1),
            returns=self.returns.reshape(-1),
        )
