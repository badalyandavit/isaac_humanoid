from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class ReplayBatch:
    obs: torch.Tensor
    actions: torch.Tensor
    rewards: torch.Tensor
    next_obs: torch.Tensor
    dones: torch.Tensor


class ReplayBuffer:
    def __init__(
        self,
        capacity: int,
        obs_dim: int,
        action_dim: int,
        device: torch.device,
    ):
        self.capacity = int(capacity)
        self.device = device
        self.obs = np.zeros((self.capacity, obs_dim), dtype=np.float32)
        self.actions = np.zeros((self.capacity, action_dim), dtype=np.float32)
        self.rewards = np.zeros((self.capacity,), dtype=np.float32)
        self.next_obs = np.zeros((self.capacity, obs_dim), dtype=np.float32)
        self.dones = np.zeros((self.capacity,), dtype=np.float32)
        self.pos = 0
        self.full = False

    def add(
        self,
        obs: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_obs: np.ndarray,
        done: bool,
    ) -> None:
        self.obs[self.pos] = obs
        self.actions[self.pos] = action
        self.rewards[self.pos] = reward
        self.next_obs[self.pos] = next_obs
        self.dones[self.pos] = float(done)
        self.pos = (self.pos + 1) % self.capacity
        if self.pos == 0:
            self.full = True

    def __len__(self) -> int:
        return self.capacity if self.full else self.pos

    def sample(self, batch_size: int) -> ReplayBatch:
        size = len(self)
        if size <= 0:
            raise ValueError("Cannot sample from an empty replay buffer.")
        idx = np.random.randint(0, size, size=batch_size)
        return ReplayBatch(
            obs=torch.as_tensor(self.obs[idx], dtype=torch.float32, device=self.device),
            actions=torch.as_tensor(self.actions[idx], dtype=torch.float32, device=self.device),
            rewards=torch.as_tensor(self.rewards[idx], dtype=torch.float32, device=self.device),
            next_obs=torch.as_tensor(self.next_obs[idx], dtype=torch.float32, device=self.device),
            dones=torch.as_tensor(self.dones[idx], dtype=torch.float32, device=self.device),
        )
