from __future__ import annotations

import copy
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from tqdm.auto import tqdm

from humanoid_rl.config import SACConfig
from humanoid_rl.envs import (
    RunningMeanStd,
    extract_episode_stats,
    info_array_mean,
    make_vector_env,
    scalar_info,
)
from humanoid_rl.models import QNetwork, SquashedGaussianActor
from humanoid_rl.replay import ReplayBuffer
from humanoid_rl.utils import CSVLogger, ensure_dir, resolve_device, set_seed, write_json


class SACTrainer:
    def __init__(self, cfg: SACConfig, run_name: str | None = None):
        self.cfg = cfg
        self.run_name = run_name or "sac"
        set_seed(cfg.seed)
        self.device = resolve_device(cfg.device)
        self.output_dir = ensure_dir(cfg.output_dir)
        self.ckpt_dir = ensure_dir(self.output_dir / "checkpoints")
        self.envs = make_vector_env(cfg.env_id, cfg.seed, cfg.num_envs, cfg.async_envs)
        if not isinstance(self.envs.single_action_space, gym.spaces.Box):
            raise TypeError("SACTrainer currently supports continuous Box action spaces only.")
        obs_shape = self.envs.single_observation_space.shape
        action_shape = self.envs.single_action_space.shape
        if obs_shape is None or action_shape is None:
            raise ValueError("Observation and action spaces must have static shapes.")
        self.obs_dim = int(np.prod(obs_shape))
        self.action_dim = int(np.prod(action_shape))
        self.action_low = np.asarray(self.envs.single_action_space.low, dtype=np.float32)
        self.action_high = np.asarray(self.envs.single_action_space.high, dtype=np.float32)
        self.actor = SquashedGaussianActor(
            self.obs_dim,
            self.action_dim,
            self.action_low,
            self.action_high,
            cfg.hidden_sizes,
            cfg.activation,
        ).to(self.device)
        self.q1 = QNetwork(self.obs_dim, self.action_dim, cfg.hidden_sizes, cfg.activation).to(self.device)
        self.q2 = QNetwork(self.obs_dim, self.action_dim, cfg.hidden_sizes, cfg.activation).to(self.device)
        self.q1_target = copy.deepcopy(self.q1).to(self.device)
        self.q2_target = copy.deepcopy(self.q2).to(self.device)
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=cfg.learning_rate)
        self.q_optimizer = torch.optim.Adam(
            list(self.q1.parameters()) + list(self.q2.parameters()),
            lr=cfg.q_learning_rate,
        )
        self.target_entropy = float(cfg.target_entropy if cfg.target_entropy is not None else -self.action_dim)
        self.log_alpha = torch.tensor(np.log(cfg.alpha), dtype=torch.float32, device=self.device, requires_grad=True)
        self.alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=cfg.learning_rate)
        self.replay = ReplayBuffer(cfg.buffer_size, self.obs_dim, self.action_dim, self.device)
        self.writer = SummaryWriter(str(self.output_dir / "tb" / self.run_name))
        self.csv_logger = CSVLogger(self.output_dir / f"{self.run_name}_train.csv")
        self.global_step = 0
        self.update_idx = 0
        self.start_time = time.perf_counter()
        obs, _ = self.envs.reset(seed=cfg.seed)
        self.next_obs = obs.reshape(cfg.num_envs, self.obs_dim).astype(np.float32)
        self.obs_rms = RunningMeanStd((self.obs_dim,))
        if cfg.obs_norm:
            self.obs_rms.update(self.next_obs)

    @property
    def alpha(self) -> torch.Tensor:
        if self.cfg.autotune_alpha:
            return self.log_alpha.exp()
        return torch.as_tensor(self.cfg.alpha, dtype=torch.float32, device=self.device)

    def _normalize_obs_np(self, obs: np.ndarray, update: bool) -> np.ndarray:
        obs = obs.reshape(obs.shape[0], self.obs_dim).astype(np.float32)
        if not self.cfg.obs_norm:
            return obs
        if update:
            self.obs_rms.update(obs)
        return self.obs_rms.normalize(obs)

    def _normalize_obs_tensor(self, obs: torch.Tensor) -> torch.Tensor:
        if not self.cfg.obs_norm:
            return obs
        mean = torch.as_tensor(self.obs_rms.mean, dtype=torch.float32, device=self.device)
        var = torch.as_tensor(self.obs_rms.var, dtype=torch.float32, device=self.device)
        return torch.clamp((obs - mean) / torch.sqrt(var + 1e-8), -10.0, 10.0)

    @torch.no_grad()
    def act(self, obs: np.ndarray, deterministic: bool = False) -> np.ndarray:
        obs_n = self._normalize_obs_np(obs, update=False)
        obs_t = torch.as_tensor(obs_n, dtype=torch.float32, device=self.device)
        if deterministic:
            action = self.actor.act_deterministic(obs_t)
        else:
            action, _, _ = self.actor.sample(obs_t)
        return action.cpu().numpy()

    def train(self, total_timesteps: int | None = None, show_progress: bool = True) -> None:
        total_timesteps = int(total_timesteps or self.cfg.total_timesteps)
        step_iter = range(0, total_timesteps, self.cfg.num_envs)
        progress = None
        if show_progress:
            progress = tqdm(step_iter, total=len(step_iter), desc=f"{self.run_name} env steps", unit="step")
            step_iter = progress
        episode_stats: list[dict[str, float]] = []
        action_l2_values: list[float] = []
        action_smoothness_values: list[float] = []
        forward_reward_values: list[float] = []
        ctrl_cost_values: list[float] = []
        prev_actions: np.ndarray | None = None
        last_log = time.perf_counter()
        for _ in step_iter:
            if self.global_step < self.cfg.learning_starts:
                actions = np.stack([self.envs.single_action_space.sample() for _ in range(self.cfg.num_envs)]).astype(
                    np.float32
                )
            else:
                actions = self.act(self.next_obs, deterministic=False)
            action_l2_values.append(float(np.mean(np.linalg.norm(actions, axis=-1))))
            if prev_actions is not None:
                action_smoothness_values.append(float(np.mean(np.square(actions - prev_actions))))
            prev_actions = actions.copy()
            next_obs, rewards, terminated, truncated, infos = self.envs.step(actions)
            done = np.logical_or(terminated, truncated)
            raw_next_obs = next_obs.reshape(self.cfg.num_envs, self.obs_dim).astype(np.float32)
            replay_next_obs = raw_next_obs.copy()
            final_obs = infos.get("final_observation")
            if final_obs is not None:
                for env_idx, item in enumerate(final_obs):
                    if item is not None:
                        replay_next_obs[env_idx] = np.asarray(item, dtype=np.float32).reshape(self.obs_dim)
            for env_idx in range(self.cfg.num_envs):
                self.replay.add(
                    self.next_obs[env_idx],
                    actions[env_idx],
                    float(rewards[env_idx]),
                    replay_next_obs[env_idx],
                    bool(done[env_idx]),
                )
            episode_stats.extend(extract_episode_stats(infos))
            forward_reward = info_array_mean(infos, "reward_forward", "reward_linvel", "x_velocity")
            ctrl_cost = info_array_mean(infos, "reward_ctrl", "reward_quadctrl", "control_cost", "reward_ctrl_cost")
            if forward_reward is not None:
                forward_reward_values.append(forward_reward)
            if ctrl_cost is not None:
                ctrl_cost_values.append(ctrl_cost)
            self.next_obs = raw_next_obs
            self._normalize_obs_np(self.next_obs, update=True)
            self.global_step += self.cfg.num_envs
            if (
                self.global_step >= self.cfg.learning_starts
                and len(self.replay) >= self.cfg.batch_size
                and self.global_step % self.cfg.train_freq == 0
            ):
                for _ in range(self.cfg.gradient_steps):
                    self.update_idx += 1
                    losses = self.update(self.update_idx)
                    self._write_scalars(losses)
            if self.global_step % self.cfg.log_interval_steps < self.cfg.num_envs:
                now = time.perf_counter()
                row = self._log_row(
                    episode_stats,
                    action_l2_values,
                    action_smoothness_values,
                    forward_reward_values,
                    ctrl_cost_values,
                    elapsed_since_last_log=now - last_log,
                )
                self.csv_logger.write(row)
                if progress is not None:
                    progress.set_postfix({"step": self.global_step, "return": row.get("episodic_return_mean", "")})
                last_log = now
        self.save(self.ckpt_dir / "final.pt")

    def update(self, update_idx: int) -> dict[str, float]:
        batch = self.replay.sample(self.cfg.batch_size)
        obs = self._normalize_obs_tensor(batch.obs)
        next_obs = self._normalize_obs_tensor(batch.next_obs)
        rewards = batch.rewards * self.cfg.reward_scale
        with torch.no_grad():
            next_action, next_log_prob, _ = self.actor.sample(next_obs)
            target_q = torch.min(
                self.q1_target(next_obs, next_action),
                self.q2_target(next_obs, next_action),
            ) - self.alpha.detach() * next_log_prob.squeeze(-1)
            target = rewards + (1.0 - batch.dones) * self.cfg.gamma * target_q
        q1_loss = F.mse_loss(self.q1(obs, batch.actions), target)
        q2_loss = F.mse_loss(self.q2(obs, batch.actions), target)
        q_loss = q1_loss + q2_loss
        self.q_optimizer.zero_grad(set_to_none=True)
        q_loss.backward()
        nn.utils.clip_grad_norm_(list(self.q1.parameters()) + list(self.q2.parameters()), self.cfg.max_grad_norm)
        self.q_optimizer.step()
        actor_loss_value = 0.0
        alpha_loss_value = 0.0
        if update_idx % self.cfg.policy_frequency == 0:
            action_pi, log_pi, _ = self.actor.sample(obs)
            min_q_pi = torch.min(self.q1(obs, action_pi), self.q2(obs, action_pi))
            actor_loss = (self.alpha.detach() * log_pi.squeeze(-1) - min_q_pi).mean()
            self.actor_optimizer.zero_grad(set_to_none=True)
            actor_loss.backward()
            nn.utils.clip_grad_norm_(self.actor.parameters(), self.cfg.max_grad_norm)
            self.actor_optimizer.step()
            actor_loss_value = float(actor_loss.item())
            if self.cfg.autotune_alpha:
                alpha_loss = -(self.log_alpha * (log_pi.detach() + self.target_entropy)).mean()
                self.alpha_optimizer.zero_grad(set_to_none=True)
                alpha_loss.backward()
                self.alpha_optimizer.step()
                alpha_loss_value = float(alpha_loss.item())
        if update_idx % self.cfg.target_network_frequency == 0:
            self.soft_update_targets()
        return {
            "q1_loss": float(q1_loss.item()),
            "q2_loss": float(q2_loss.item()),
            "q_loss": float(q_loss.item()),
            "actor_loss": actor_loss_value,
            "alpha": float(self.alpha.detach().item()),
            "alpha_loss": alpha_loss_value,
        }

    def soft_update_targets(self) -> None:
        for param, target_param in zip(self.q1.parameters(), self.q1_target.parameters(), strict=True):
            target_param.data.mul_(1.0 - self.cfg.tau).add_(param.data, alpha=self.cfg.tau)
        for param, target_param in zip(self.q2.parameters(), self.q2_target.parameters(), strict=True):
            target_param.data.mul_(1.0 - self.cfg.tau).add_(param.data, alpha=self.cfg.tau)

    def _write_scalars(self, row: dict[str, float]) -> None:
        for key, value in row.items():
            if np.isfinite(value):
                self.writer.add_scalar(f"train/{key}", value, self.global_step)

    def _log_row(
        self,
        episode_stats: list[dict[str, float]],
        action_l2_values: list[float],
        action_smoothness_values: list[float],
        forward_reward_values: list[float],
        ctrl_cost_values: list[float],
        elapsed_since_last_log: float,
    ) -> dict[str, Any]:
        returns = [x["return"] for x in episode_stats[-100:]]
        lengths = [x["length"] for x in episode_stats[-100:]]
        row: dict[str, Any] = {
            "global_step": self.global_step,
            "total_env_steps": self.global_step,
            "updates": self.update_idx,
            "wall_clock_s": time.perf_counter() - self.start_time,
            "env_steps_per_second": self.cfg.log_interval_steps / max(1e-9, elapsed_since_last_log),
            "replay_size": len(self.replay),
            "alpha": float(self.alpha.detach().item()),
            "action_l2_norm": float(np.mean(action_l2_values[-self.cfg.log_interval_steps :]))
            if action_l2_values
            else 0.0,
            "action_smoothness": float(np.mean(action_smoothness_values[-self.cfg.log_interval_steps :]))
            if action_smoothness_values
            else 0.0,
            "mean_forward_reward": float(np.mean(forward_reward_values[-self.cfg.log_interval_steps :]))
            if forward_reward_values
            else 0.0,
            "mean_ctrl_cost": float(np.mean(ctrl_cost_values[-self.cfg.log_interval_steps :]))
            if ctrl_cost_values
            else 0.0,
        }
        if returns:
            row["episodic_return_mean"] = float(np.mean(returns))
            row["episodic_length_mean"] = float(np.mean(lengths))
            row["fall_rate"] = float(np.mean(np.asarray(lengths) < 999.0))
        return row

    @torch.no_grad()
    def evaluate(
        self,
        episodes: int | None = None,
        deterministic: bool = True,
        show_progress: bool = False,
        desc: str | None = None,
        leave: bool = True,
    ) -> dict[str, Any]:
        episodes = int(episodes or self.cfg.eval_episodes)
        env = gym.make(self.cfg.env_id)
        returns: list[float] = []
        lengths: list[int] = []
        reward_ctrl_values: list[float] = []
        reward_forward_values: list[float] = []
        action_l2_values: list[float] = []
        action_smoothness_values: list[float] = []
        episode_iter = range(episodes)
        if show_progress:
            episode_iter = tqdm(episode_iter, desc=desc or f"{self.run_name} eval", unit="episode", leave=leave)
        for ep_idx in episode_iter:
            obs, _ = env.reset(seed=self.cfg.seed + 100_000 + ep_idx)
            done = False
            ep_return = 0.0
            ep_len = 0
            ep_ctrl = 0.0
            ep_forward = 0.0
            ep_action_l2: list[float] = []
            ep_action_smoothness: list[float] = []
            prev_action: np.ndarray | None = None
            while not done:
                obs_batch = np.asarray(obs, dtype=np.float32).reshape(1, self.obs_dim)
                action_np = self.act(obs_batch, deterministic=deterministic)[0]
                ep_action_l2.append(float(np.linalg.norm(action_np)))
                if prev_action is not None:
                    ep_action_smoothness.append(float(np.mean(np.square(action_np - prev_action))))
                prev_action = action_np.copy()
                obs, reward, terminated, truncated, info = env.step(action_np)
                done = bool(terminated or truncated)
                ep_return += float(reward)
                ep_len += 1
                ep_ctrl += scalar_info(info, "reward_ctrl", "reward_quadctrl", "control_cost", "reward_ctrl_cost") or 0.0
                ep_forward += scalar_info(info, "reward_forward", "reward_linvel", "x_velocity") or 0.0
            returns.append(ep_return)
            lengths.append(ep_len)
            reward_ctrl_values.append(ep_ctrl / max(1, ep_len))
            reward_forward_values.append(ep_forward / max(1, ep_len))
            action_l2_values.append(float(np.mean(ep_action_l2)) if ep_action_l2 else 0.0)
            action_smoothness_values.append(float(np.mean(ep_action_smoothness)) if ep_action_smoothness else 0.0)
        env.close()
        returns_np = np.asarray(returns, dtype=np.float64)
        lengths_np = np.asarray(lengths, dtype=np.float64)
        return {
            "returns": returns,
            "lengths": lengths,
            "mean_return": float(np.mean(returns_np)),
            "median_return": float(np.median(returns_np)),
            "q25_return": float(np.quantile(returns_np, 0.25)),
            "q75_return": float(np.quantile(returns_np, 0.75)),
            "std_return": float(np.std(returns_np)),
            "mean_length": float(np.mean(lengths_np)),
            "success_alive_duration": float(np.mean(lengths_np)),
            "fall_rate": float(np.mean(lengths_np < 999.0)),
            "mean_ctrl_reward": float(np.mean(reward_ctrl_values)),
            "mean_forward_reward": float(np.mean(reward_forward_values)),
            "action_l2_norm": float(np.mean(action_l2_values)),
            "action_smoothness": float(np.mean(action_smoothness_values)),
            "total_env_steps": self.global_step,
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "actor": self.actor.state_dict(),
                "q1": self.q1.state_dict(),
                "q2": self.q2.state_dict(),
                "q1_target": self.q1_target.state_dict(),
                "q2_target": self.q2_target.state_dict(),
                "actor_optimizer": self.actor_optimizer.state_dict(),
                "q_optimizer": self.q_optimizer.state_dict(),
                "log_alpha": self.log_alpha.detach().cpu(),
                "alpha_optimizer": self.alpha_optimizer.state_dict(),
                "obs_rms": self.obs_rms.state_dict(),
                "cfg": asdict(self.cfg),
                "global_step": self.global_step,
                "update_idx": self.update_idx,
            },
            path,
        )

    def load(self, path: str | Path, load_optimizers: bool = True) -> None:
        payload = torch.load(path, map_location=self.device, weights_only=False)
        self.actor.load_state_dict(payload["actor"])
        self.q1.load_state_dict(payload["q1"])
        self.q2.load_state_dict(payload["q2"])
        self.q1_target.load_state_dict(payload.get("q1_target", payload["q1"]))
        self.q2_target.load_state_dict(payload.get("q2_target", payload["q2"]))
        if load_optimizers:
            if "actor_optimizer" in payload:
                self.actor_optimizer.load_state_dict(payload["actor_optimizer"])
            if "q_optimizer" in payload:
                self.q_optimizer.load_state_dict(payload["q_optimizer"])
            if "alpha_optimizer" in payload:
                self.alpha_optimizer.load_state_dict(payload["alpha_optimizer"])
        if "log_alpha" in payload:
            self.log_alpha.data.copy_(payload["log_alpha"].to(self.device))
        if "obs_rms" in payload:
            self.obs_rms.load_state_dict(payload["obs_rms"])
        self.global_step = int(payload.get("global_step", 0))
        self.update_idx = int(payload.get("update_idx", 0))

    def close(self) -> None:
        self.envs.close()
        self.writer.close()

    def dump_config(self) -> None:
        write_json(self.output_dir / f"{self.run_name}_config.json", asdict(self.cfg))
