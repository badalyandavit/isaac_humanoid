from __future__ import annotations

import torch


def average_state_dicts(states: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    if not states:
        raise ValueError("states must be non-empty")
    keys = states[0].keys()
    out: dict[str, torch.Tensor] = {}
    for key in keys:
        stacked = torch.stack([state[key].float() for state in states], dim=0)
        out[key] = stacked.mean(dim=0).to(states[0][key].dtype)
    return out


def weighted_average_state_dicts(
    states: list[dict[str, torch.Tensor]], weights: list[float]
) -> dict[str, torch.Tensor]:
    if len(states) != len(weights):
        raise ValueError("states and weights must have the same length")
    total = float(sum(weights))
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    norm = [w / total for w in weights]
    out: dict[str, torch.Tensor] = {}
    for key in states[0].keys():
        acc = torch.zeros_like(states[0][key], dtype=torch.float32)
        for state, weight in zip(states, norm):
            acc += state[key].float() * weight
        out[key] = acc.to(states[0][key].dtype)
    return out
