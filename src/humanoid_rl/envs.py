from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import gymnasium as gym
import numpy as np


@dataclass
class RunningMeanStd:
    shape: tuple[int, ...]
    epsilon: float = 1e-4

    def __post_init__(self) -> None:
        self.mean = np.zeros(self.shape, dtype=np.float64)
        self.var = np.ones(self.shape, dtype=np.float64)
        self.count = self.epsilon

    def update(self, x: np.ndarray) -> None:
        x = np.asarray(x, dtype=np.float64)
        batch_mean = np.mean(x, axis=0)
        batch_var = np.var(x, axis=0)
        batch_count = x.shape[0]
        self.update_from_moments(batch_mean, batch_var, batch_count)

    def update_from_moments(self, batch_mean: np.ndarray, batch_var: np.ndarray, batch_count: int) -> None:
        delta = batch_mean - self.mean
        total_count = self.count + batch_count
        new_mean = self.mean + delta * batch_count / total_count
        m_a = self.var * self.count
        m_b = batch_var * batch_count
        m_2 = m_a + m_b + np.square(delta) * self.count * batch_count / total_count
        self.mean = new_mean
        self.var = m_2 / total_count
        self.count = total_count

    def normalize(self, x: np.ndarray, clip: float = 10.0) -> np.ndarray:
        x_norm = (x - self.mean) / np.sqrt(self.var + 1e-8)
        return np.clip(x_norm, -clip, clip).astype(np.float32)

    def state_dict(self) -> dict[str, np.ndarray | float]:
        return {"mean": self.mean, "var": self.var, "count": self.count}

    def load_state_dict(self, state: dict[str, np.ndarray | float]) -> None:
        self.mean = np.asarray(state["mean"], dtype=np.float64)
        self.var = np.asarray(state["var"], dtype=np.float64)
        self.count = float(state["count"])


def make_single_env(
    env_id: str,
    seed: int,
    idx: int = 0,
    capture_video: bool = False,
    video_dir: str | None = None,
    render_mode: str | None = None,
) -> Callable[[], gym.Env]:
    def thunk() -> gym.Env:
        kwargs = {}
        if render_mode is not None:
            kwargs["render_mode"] = render_mode
        env = gym.make(env_id, **kwargs)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        if capture_video:
            if video_dir is None:
                raise ValueError("video_dir must be provided when capture_video=True")
            env = gym.wrappers.RecordVideo(env, video_dir, episode_trigger=lambda ep: True)
        env.action_space.seed(seed + idx)
        env.observation_space.seed(seed + idx)
        return env

    return thunk


def make_vector_env(env_id: str, seed: int, num_envs: int, async_envs: bool = False) -> gym.vector.VectorEnv:
    thunks = [make_single_env(env_id, seed, idx=i) for i in range(num_envs)]
    if async_envs:
        return gym.vector.AsyncVectorEnv(thunks)
    return gym.vector.SyncVectorEnv(thunks)


def extract_episode_stats(infos: dict) -> list[dict[str, float]]:
    stats: list[dict[str, float]] = []
    final_info = infos.get("final_info")
    if final_info is None:
        return stats
    for item in final_info:
        if item is None or "episode" not in item:
            continue
        ep = item["episode"]
        stats.append({"return": float(ep["r"]), "length": float(ep["l"])})
    return stats


def info_array_mean(infos: dict, *keys: str) -> float | None:
    values: list[float] = []
    for key in keys:
        if key not in infos:
            continue
        item = infos[key]
        arr = np.asarray(item, dtype=np.float64).reshape(-1)
        values.extend(float(x) for x in arr if np.isfinite(x))
    if not values:
        return None
    return float(np.mean(values))


def scalar_info(info: dict, *keys: str) -> float | None:
    for key in keys:
        if key in info:
            value = info[key]
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None
