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
        # `dones` marks episode boundaries (terminated OR truncated) and resets the GAE carry.
        # `terminations` is the strict termination flag and zeroes the value bootstrap; on
        # truncation we still bootstrap with V(real_next_obs).
        self.dones = torch.zeros((num_steps, num_envs), device=device)
        self.terminations = torch.zeros((num_steps, num_envs), device=device)
        self.values = torch.zeros((num_steps, num_envs), device=device)
        # V evaluated on the actual next state of the transition (final_observation on
        # boundary steps, else the regular next obs). Avoids using the post-reset obs as
        # the bootstrap target on truncation.
        self.next_values = torch.zeros((num_steps, num_envs), device=device)
        self.advantages = torch.zeros((num_steps, num_envs), device=device)
        self.returns = torch.zeros((num_steps, num_envs), device=device)

    def compute_gae(self, gamma: float, gae_lambda: float) -> None:
        lastgaelam = torch.zeros(self.num_envs, device=self.device)
        for t in reversed(range(self.num_steps)):
            done_carry = self.dones[t + 1] if t < self.num_steps - 1 else self.dones[t].new_zeros(self.num_envs)
            bootstrap_mask = 1.0 - self.terminations[t]
            delta = self.rewards[t] + gamma * self.next_values[t] * bootstrap_mask - self.values[t]
            lastgaelam = delta + gamma * gae_lambda * (1.0 - done_carry) * lastgaelam
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
