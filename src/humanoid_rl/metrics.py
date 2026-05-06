from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class RobustScore:
    trimmed_mean: float
    median: float
    q_low: float
    q_high: float
    mean: float
    std: float
    robust_score: float
    fall_rate: float
    mean_length: float
    mean_ctrl_reward: float
    hill_tail_index: float | None


def trimmed_mean(values: list[float] | np.ndarray, trim_fraction: float) -> float:
    x = np.sort(np.asarray(values, dtype=np.float64))
    if x.size == 0:
        return float("nan")
    k = int(math.floor(trim_fraction * x.size))
    if 2 * k >= x.size:
        return float(np.median(x))
    return float(np.mean(x[k : x.size - k]))


def hill_tail_index(values: list[float] | np.ndarray, top_fraction: float = 0.2) -> float | None:
    x = np.asarray(values, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size < 8:
        return None
    shifted = x - np.min(x) + 1e-6
    shifted = np.sort(shifted)
    k = max(2, int(top_fraction * shifted.size))
    if k >= shifted.size:
        return None
    tail = shifted[-k:]
    threshold = shifted[-k - 1]
    if threshold <= 0:
        return None
    estimate = np.mean(np.log(tail) - np.log(threshold))
    if estimate <= 0:
        return None
    return float(1.0 / estimate)


def robust_worker_score(
    eval_payload: dict[str, Any],
    trim_fraction: float,
    q_low: float,
    median_weight: float,
    fall_penalty: float,
    energy_penalty: float,
) -> RobustScore:
    returns = np.asarray(eval_payload["returns"], dtype=np.float64)
    lengths = np.asarray(eval_payload["lengths"], dtype=np.float64)
    q_low_value = float(np.quantile(returns, q_low))
    q_high_value = float(np.quantile(returns, 1.0 - q_low))
    med = float(np.median(returns))
    tmean = trimmed_mean(returns, trim_fraction)
    fall_rate = float(eval_payload.get("fall_rate", np.mean(lengths < 999.0)))
    mean_ctrl = float(eval_payload.get("mean_ctrl_reward", 0.0))
    score = q_low_value + median_weight * med - fall_penalty * fall_rate - energy_penalty * abs(mean_ctrl)
    return RobustScore(
        trimmed_mean=tmean,
        median=med,
        q_low=q_low_value,
        q_high=q_high_value,
        mean=float(np.mean(returns)),
        std=float(np.std(returns)),
        robust_score=float(score),
        fall_rate=fall_rate,
        mean_length=float(np.mean(lengths)),
        mean_ctrl_reward=mean_ctrl,
        hill_tail_index=hill_tail_index(returns),
    )


def flatten_score(prefix: str, score: RobustScore) -> dict[str, float | None]:
    return {f"{prefix}_{k}": v for k, v in score.__dict__.items()}
