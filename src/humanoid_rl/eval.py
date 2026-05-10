from __future__ import annotations

from typing import Any, Callable

import gymnasium as gym
import numpy as np
from tqdm.auto import tqdm

from humanoid_rl.envs import scalar_info


ActFn = Callable[[np.ndarray, bool], np.ndarray]


def _resolve_fall_threshold(env: gym.Env, override: int | None) -> int:
    if override is not None:
        return int(override)
    spec = getattr(env, "spec", None)
    if spec is not None and getattr(spec, "max_episode_steps", None):
        return int(spec.max_episode_steps) - 1
    # Fall back to legacy hard-coded value if the env doesn't advertise a horizon.
    return 999


def evaluate_policy(
    env_id: str,
    act_fn: ActFn,
    episodes: int,
    seed: int,
    deterministic: bool = True,
    show_progress: bool = False,
    desc: str | None = None,
    leave: bool = True,
    fall_threshold: int | None = None,
) -> dict[str, Any]:
    """Run deterministic-by-default evaluation in a single Gym env.

    `act_fn(obs, deterministic) -> action` is the only policy-specific bit.
    Callers are responsible for any obs normalization inside `act_fn`.
    """
    env = gym.make(env_id)
    threshold = _resolve_fall_threshold(env, fall_threshold)
    returns: list[float] = []
    lengths: list[int] = []
    reward_ctrl_values: list[float] = []
    reward_forward_values: list[float] = []
    action_l2_values: list[float] = []
    action_smoothness_values: list[float] = []

    episode_iter: Any = range(episodes)
    if show_progress:
        episode_iter = tqdm(episode_iter, desc=desc or "eval", unit="episode", leave=leave)

    for ep_idx in episode_iter:
        obs, _ = env.reset(seed=seed + 100_000 + ep_idx)
        done = False
        ep_return = 0.0
        ep_len = 0
        ep_ctrl = 0.0
        ep_forward = 0.0
        ep_action_l2: list[float] = []
        ep_action_smoothness: list[float] = []
        prev_action: np.ndarray | None = None
        while not done:
            obs_batch = np.asarray(obs, dtype=np.float32).reshape(1, -1)
            action_np = np.asarray(act_fn(obs_batch, deterministic)).reshape(-1)
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
    n = max(1, returns_np.size)
    mean_return = float(np.mean(returns_np))
    std_return = float(np.std(returns_np, ddof=1)) if returns_np.size > 1 else 0.0
    # 95% CI via normal approximation (n is small; this is a rough bar, not a stats claim).
    ci95_return = 1.96 * std_return / np.sqrt(n) if returns_np.size > 1 else 0.0
    return {
        "returns": returns,
        "lengths": lengths,
        "mean_return": mean_return,
        "median_return": float(np.median(returns_np)),
        "q25_return": float(np.quantile(returns_np, 0.25)),
        "q75_return": float(np.quantile(returns_np, 0.75)),
        "std_return": float(np.std(returns_np)),
        "ci95_return": float(ci95_return),
        "mean_length": float(np.mean(lengths_np)),
        "success_alive_duration": float(np.mean(lengths_np)),
        "fall_rate": float(np.mean(lengths_np < threshold)),
        "fall_threshold": int(threshold),
        "mean_ctrl_reward": float(np.mean(reward_ctrl_values)),
        "mean_forward_reward": float(np.mean(reward_forward_values)),
        "action_l2_norm": float(np.mean(action_l2_values)),
        "action_smoothness": float(np.mean(action_smoothness_values)),
    }
