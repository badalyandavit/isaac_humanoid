from __future__ import annotations

from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from tqdm.auto import tqdm

from humanoid_rl.config import PPOConfig
from humanoid_rl.envs import RunningMeanStd, extract_episode_stats, make_single_env, make_vector_env
from humanoid_rl.models import ActorCritic
from humanoid_rl.rollout import RolloutStorage
from humanoid_rl.utils import CSVLogger, ensure_dir, resolve_device, set_seed, write_json


class PPOTrainer:
    def __init__(self, cfg: PPOConfig, run_name: str | None = None):
        self.cfg = cfg
        self.run_name = run_name or "ppo"
        set_seed(cfg.seed)
        self.device = resolve_device(cfg.device)
        self.output_dir = ensure_dir(cfg.output_dir)
        self.ckpt_dir = ensure_dir(self.output_dir / "checkpoints")
        self.envs = make_vector_env(cfg.env_id, cfg.seed, cfg.num_envs, cfg.async_envs)
        if not isinstance(self.envs.single_action_space, gym.spaces.Box):
            raise TypeError("PPOTrainer currently supports continuous Box action spaces only.")
        obs_shape = self.envs.single_observation_space.shape
        action_shape = self.envs.single_action_space.shape
        if obs_shape is None or action_shape is None:
            raise ValueError("Observation and action spaces must have static shapes.")
        self.obs_dim = int(np.prod(obs_shape))
        self.action_dim = int(np.prod(action_shape))
        self.action_low = np.asarray(self.envs.single_action_space.low, dtype=np.float32)
        self.action_high = np.asarray(self.envs.single_action_space.high, dtype=np.float32)
        self.model = ActorCritic(
            self.obs_dim,
            self.action_dim,
            self.action_low,
            self.action_high,
            cfg.hidden_sizes,
            cfg.activation,
        ).to(self.device)
        if cfg.torch_compile and hasattr(torch, "compile"):
            self.model = torch.compile(self.model)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=cfg.learning_rate, eps=1e-5)
        self.scaler = torch.amp.GradScaler("cuda", enabled=cfg.amp and self.device.type == "cuda")
        self.writer = SummaryWriter(str(self.output_dir / "tb" / self.run_name))
        self.csv_logger = CSVLogger(self.output_dir / f"{self.run_name}_train.csv")
        self.global_step = 0
        self.update_idx = 0
        self.start_time = None
        obs, _ = self.envs.reset(seed=cfg.seed)
        obs = obs.reshape(cfg.num_envs, self.obs_dim).astype(np.float32)
        self.obs_rms = RunningMeanStd((self.obs_dim,))
        if cfg.obs_norm:
            self.obs_rms.update(obs)
            obs = self.obs_rms.normalize(obs)
        self.next_obs = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
        self.next_done = torch.zeros(cfg.num_envs, dtype=torch.float32, device=self.device)

    def reset_optimizer(self) -> None:
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.cfg.learning_rate, eps=1e-5)
        self.scaler = torch.amp.GradScaler("cuda", enabled=self.cfg.amp and self.device.type == "cuda")

    def _normalize_obs_np(self, obs: np.ndarray, update: bool) -> np.ndarray:
        obs = obs.reshape(obs.shape[0], self.obs_dim).astype(np.float32)
        if not self.cfg.obs_norm:
            return obs
        if update:
            self.obs_rms.update(obs)
        return self.obs_rms.normalize(obs)

    def collect_rollout(self) -> tuple[RolloutStorage, list[dict[str, float]]]:
        cfg = self.cfg
        storage = RolloutStorage(cfg.num_steps, cfg.num_envs, self.obs_dim, self.action_dim, self.device)
        episode_stats: list[dict[str, float]] = []
        for step in range(cfg.num_steps):
            storage.obs[step] = self.next_obs
            storage.dones[step] = self.next_done
            with torch.no_grad():
                env_action, logprob, _, value, raw_action = self.model.get_action_and_value(self.next_obs)
            storage.actions[step] = raw_action
            storage.logprobs[step] = logprob
            storage.values[step] = value
            actions_np = env_action.detach().cpu().numpy()
            next_obs, reward, terminated, truncated, infos = self.envs.step(actions_np)
            done = np.logical_or(terminated, truncated)
            episode_stats.extend(extract_episode_stats(infos))
            storage.rewards[step] = torch.as_tensor(reward, dtype=torch.float32, device=self.device) * cfg.reward_scale
            self.global_step += cfg.num_envs
            next_obs = self._normalize_obs_np(next_obs, update=True)
            self.next_obs = torch.as_tensor(next_obs, dtype=torch.float32, device=self.device)
            self.next_done = torch.as_tensor(done.astype(np.float32), dtype=torch.float32, device=self.device)
        with torch.no_grad():
            next_value = self.model.get_value(self.next_obs)
        storage.compute_gae(next_value, self.next_done, cfg.gamma, cfg.gae_lambda)
        return storage, episode_stats

    def update(self, storage: RolloutStorage) -> dict[str, float]:
        cfg = self.cfg
        batch = storage.flatten()
        batch_size = cfg.num_envs * cfg.num_steps
        minibatch_size = batch_size // cfg.num_minibatches
        if minibatch_size <= 0:
            raise ValueError("num_envs * num_steps must be >= num_minibatches")
        b_inds = np.arange(batch_size)
        clipfracs: list[float] = []
        approx_kl_value = 0.0
        pg_loss_value = 0.0
        v_loss_value = 0.0
        entropy_loss_value = 0.0
        for _ in range(cfg.update_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_inds = b_inds[start:end]
                with torch.amp.autocast(self.device.type, enabled=cfg.amp and self.device.type == "cuda"):
                    _, newlogprob, entropy, newvalue, _ = self.model.get_action_and_value(
                        batch.obs[mb_inds], batch.actions[mb_inds]
                    )
                    logratio = newlogprob - batch.logprobs[mb_inds]
                    ratio = logratio.exp()
                    mb_advantages = batch.advantages[mb_inds]
                    if cfg.norm_adv:
                        mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)
                    pg_loss1 = -mb_advantages * ratio
                    pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - cfg.clip_coef, 1 + cfg.clip_coef)
                    pg_loss = torch.max(pg_loss1, pg_loss2).mean()
                    newvalue = newvalue.view(-1)
                    if cfg.clip_vloss:
                        v_loss_unclipped = (newvalue - batch.returns[mb_inds]) ** 2
                        v_clipped = batch.values[mb_inds] + torch.clamp(
                            newvalue - batch.values[mb_inds], -cfg.clip_coef, cfg.clip_coef
                        )
                        v_loss_clipped = (v_clipped - batch.returns[mb_inds]) ** 2
                        v_loss = 0.5 * torch.max(v_loss_unclipped, v_loss_clipped).mean()
                    else:
                        v_loss = 0.5 * ((newvalue - batch.returns[mb_inds]) ** 2).mean()
                    entropy_loss = entropy.mean()
                    loss = pg_loss - cfg.ent_coef * entropy_loss + cfg.vf_coef * v_loss
                with torch.no_grad():
                    old_approx_kl = (-logratio).mean()
                    approx_kl = ((ratio - 1) - logratio).mean()
                    clipfracs.append(((ratio - 1.0).abs() > cfg.clip_coef).float().mean().item())
                self.optimizer.zero_grad(set_to_none=True)
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                nn.utils.clip_grad_norm_(self.model.parameters(), cfg.max_grad_norm)
                self.scaler.step(self.optimizer)
                self.scaler.update()
                approx_kl_value = approx_kl.item()
                pg_loss_value = pg_loss.item()
                v_loss_value = v_loss.item()
                entropy_loss_value = entropy_loss.item()
            if cfg.target_kl is not None and approx_kl_value > cfg.target_kl:
                break
        explained_var = self._explained_variance(batch.values.detach(), batch.returns.detach())
        return {
            "policy_loss": pg_loss_value,
            "value_loss": v_loss_value,
            "entropy": entropy_loss_value,
            "old_approx_kl": float(old_approx_kl.item()),
            "approx_kl": approx_kl_value,
            "clipfrac": float(np.mean(clipfracs)) if clipfracs else 0.0,
            "explained_variance": explained_var,
        }

    @staticmethod
    def _explained_variance(values: torch.Tensor, returns: torch.Tensor) -> float:
        y_pred = values.cpu().numpy()
        y_true = returns.cpu().numpy()
        var_y = np.var(y_true)
        if var_y == 0:
            return float("nan")
        return float(1 - np.var(y_true - y_pred) / var_y)

    def train(
        self,
        total_timesteps: int | None = None,
        show_progress: bool = True,
        desc: str | None = None,
    ) -> None:
        total_timesteps = int(total_timesteps or self.cfg.total_timesteps)
        batch_size = self.cfg.num_envs * self.cfg.num_steps
        num_updates = max(1, total_timesteps // batch_size)
        update_iter = range(num_updates)
        progress = None
        if show_progress:
            progress = tqdm(update_iter, desc=desc or f"{self.run_name} updates", unit="update")
            update_iter = progress
        for _ in update_iter:
            row = self.train_one_update(total_updates=num_updates)
            if progress is not None:
                postfix = {"step": self.global_step}
                if "episodic_return_mean" in row:
                    postfix["return"] = f"{row['episodic_return_mean']:.1f}"
                progress.set_postfix(postfix)

    def train_one_update(self, total_updates: int | None = None) -> dict[str, float]:
        self.update_idx += 1
        if self.cfg.anneal_lr and total_updates is not None:
            frac = 1.0 - (self.update_idx - 1.0) / total_updates
            lr_now = frac * self.cfg.learning_rate
            for param_group in self.optimizer.param_groups:
                param_group["lr"] = lr_now
        storage, episode_stats = self.collect_rollout()
        metrics = self.update(storage)
        returns = [x["return"] for x in episode_stats]
        lengths = [x["length"] for x in episode_stats]
        row = {
            "update": self.update_idx,
            "global_step": self.global_step,
            "lr": self.optimizer.param_groups[0]["lr"],
            **metrics,
        }
        if returns:
            row["episodic_return_mean"] = float(np.mean(returns))
            row["episodic_length_mean"] = float(np.mean(lengths))
            self.writer.add_scalar("charts/episodic_return", row["episodic_return_mean"], self.global_step)
            self.writer.add_scalar("charts/episodic_length", row["episodic_length_mean"], self.global_step)
        for key, value in row.items():
            if isinstance(value, (int, float)) and np.isfinite(value):
                self.writer.add_scalar(f"train/{key}", value, self.global_step)
        if self.update_idx % self.cfg.log_interval_updates == 0:
            self.csv_logger.write(row)
        if self.update_idx % self.cfg.save_interval_updates == 0:
            self.save(self.ckpt_dir / f"step_{self.global_step}.pt")
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
        episode_iter = range(episodes)
        if show_progress:
            episode_iter = tqdm(
                episode_iter,
                desc=desc or f"{self.run_name} eval",
                unit="episode",
                leave=leave,
            )
        for ep_idx in episode_iter:
            obs, _ = env.reset(seed=self.cfg.seed + 100_000 + ep_idx)
            done = False
            ep_return = 0.0
            ep_len = 0
            ep_ctrl = 0.0
            while not done:
                obs_batch = np.asarray(obs, dtype=np.float32).reshape(1, self.obs_dim)
                if self.cfg.obs_norm:
                    obs_batch = self.obs_rms.normalize(obs_batch)
                obs_t = torch.as_tensor(obs_batch, dtype=torch.float32, device=self.device)
                if deterministic:
                    action_t = self.model.act_deterministic(obs_t)
                else:
                    action_t, _, _, _, _ = self.model.get_action_and_value(obs_t)
                obs, reward, terminated, truncated, info = env.step(action_t.cpu().numpy()[0])
                done = bool(terminated or truncated)
                ep_return += float(reward)
                ep_len += 1
                ctrl = info.get("reward_ctrl", info.get("reward_quadctrl", 0.0))
                ep_ctrl += float(ctrl)
            returns.append(ep_return)
            lengths.append(ep_len)
            reward_ctrl_values.append(ep_ctrl / max(1, ep_len))
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
            "fall_rate": float(np.mean(lengths_np < 999.0)),
            "mean_ctrl_reward": float(np.mean(reward_ctrl_values)),
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model": self.policy_state_dict_cpu(),
                "optimizer": self.optimizer.state_dict(),
                "obs_rms": self.obs_rms.state_dict(),
                "cfg": self.cfg.__dict__,
                "global_step": self.global_step,
                "update_idx": self.update_idx,
            },
            path,
        )

    def load(self, path: str | Path, load_optimizer: bool = True) -> None:
        payload = torch.load(path, map_location=self.device)
        self.model.load_state_dict(payload["model"])
        if load_optimizer and "optimizer" in payload:
            self.optimizer.load_state_dict(payload["optimizer"])
        if "obs_rms" in payload:
            self.obs_rms.load_state_dict(payload["obs_rms"])
        self.global_step = int(payload.get("global_step", 0))
        self.update_idx = int(payload.get("update_idx", 0))

    def policy_state_dict_cpu(self) -> dict[str, torch.Tensor]:
        model = self.model._orig_mod if hasattr(self.model, "_orig_mod") else self.model
        return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    def load_policy_state_dict(self, state: dict[str, torch.Tensor]) -> None:
        model = self.model._orig_mod if hasattr(self.model, "_orig_mod") else self.model
        model.load_state_dict({k: v.to(self.device) for k, v in state.items()})

    def close(self) -> None:
        self.envs.close()
        self.writer.close()

    def dump_config(self) -> None:
        write_json(self.output_dir / f"{self.run_name}_config.json", self.cfg.__dict__)
