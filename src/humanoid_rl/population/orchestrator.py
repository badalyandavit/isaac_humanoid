from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from humanoid_rl.config import HeavyTailConfig
from humanoid_rl.metrics import RobustScore, robust_worker_score
from humanoid_rl.population.graphs import gamma_neighborhoods, make_graph
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import CSVLogger, ensure_dir, write_json


@dataclass
class WorkerMessage:
    round_idx: int
    worker_id: int
    score: RobustScore
    state: dict[str, torch.Tensor]
    lr: float
    ent_coef: float


@dataclass
class CloneEvent:
    round_idx: int
    source_worker: int
    target_worker: int
    source_score: float
    target_score: float
    reason: str


class RobustHeavyTailOrchestrator:
    def __init__(self, cfg: HeavyTailConfig, workers: list[PPOTrainer]):
        self.cfg = cfg
        self.workers = workers
        self.output_dir = ensure_dir(cfg.output_dir)
        self.graph = make_graph(cfg.num_workers, cfg.graph)
        self.neighborhoods = gamma_neighborhoods(self.graph, cfg.graph_gamma)
        self.events: list[CloneEvent] = []
        self.round_logger = CSVLogger(self.output_dir / "heavytail_rounds.csv")
        self.event_logger = CSVLogger(self.output_dir / "heavytail_clone_events.csv")
        write_json(
            self.output_dir / "communication_graph.json",
            {"graph": {str(k): sorted(v) for k, v in self.graph.items()}, "gamma": cfg.graph_gamma},
        )

    def score_payload(self, eval_payload: dict[str, Any]) -> RobustScore:
        return robust_worker_score(
            eval_payload,
            trim_fraction=self.cfg.trim_fraction,
            q_low=self.cfg.q_low,
            median_weight=self.cfg.median_weight,
            fall_penalty=self.cfg.fall_penalty,
            energy_penalty=self.cfg.energy_penalty,
        )

    def build_messages(self, round_idx: int, scores: list[RobustScore]) -> list[WorkerMessage]:
        messages: list[WorkerMessage] = []
        for i, worker in enumerate(self.workers):
            messages.append(
                WorkerMessage(
                    round_idx=round_idx,
                    worker_id=i,
                    score=scores[i],
                    state=worker.policy_state_dict_cpu(),
                    lr=float(worker.optimizer.param_groups[0]["lr"]),
                    ent_coef=float(worker.cfg.ent_coef),
                )
            )
        return messages

    def orchestrate(self, round_idx: int, eval_payloads: list[dict[str, Any]]) -> dict[str, Any]:
        scores = [self.score_payload(payload) for payload in eval_payloads]
        messages = self.build_messages(round_idx, scores)
        score_values = np.asarray([s.robust_score for s in scores], dtype=np.float64)
        protected_count = max(1, int(math.ceil(self.cfg.protect_top_fraction * len(scores))))
        protected = set(np.argsort(score_values)[-protected_count:].tolist())
        clone_events_this_round: list[CloneEvent] = []
        if round_idx >= self.cfg.min_rounds_before_clone:
            candidates: list[tuple[float, WorkerMessage, int]] = []
            for target_id in range(len(self.workers)):
                if target_id in protected:
                    continue
                visible = [messages[j] for j in self.neighborhoods[target_id] if j != target_id]
                if not visible:
                    continue
                best = max(visible, key=lambda msg: msg.score.robust_score)
                margin = best.score.robust_score - scores[target_id].robust_score
                if margin >= self.cfg.promote_margin:
                    candidates.append((margin, best, target_id))
            candidates.sort(reverse=True, key=lambda x: x[0])
            for _, source, target_id in candidates[: self.cfg.max_clones_per_round]:
                self._clone_and_mutate(source, target_id)
                event = CloneEvent(
                    round_idx=round_idx,
                    source_worker=source.worker_id,
                    target_worker=target_id,
                    source_score=source.score.robust_score,
                    target_score=scores[target_id].robust_score,
                    reason="robust_neighborhood_promotion",
                )
                clone_events_this_round.append(event)
                self.events.append(event)
                self.event_logger.write(asdict(event))
        best_idx = int(np.argmax(score_values))
        row: dict[str, Any] = {
            "round": round_idx,
            "best_worker": best_idx,
            "best_robust_score": float(score_values[best_idx]),
            "median_robust_score": float(np.median(score_values)),
            "mean_robust_score": float(np.mean(score_values)),
            "num_clones": len(clone_events_this_round),
        }
        for i, score in enumerate(scores):
            for key, value in asdict(score).items():
                row[f"worker_{i}_{key}"] = value
        self.round_logger.write(row)
        return {
            "scores": scores,
            "row": row,
            "clone_events": clone_events_this_round,
            "best_worker": best_idx,
        }

    def _clone_and_mutate(self, source: WorkerMessage, target_id: int) -> None:
        target = self.workers[target_id]
        mutated_state = {k: v.clone() for k, v in source.state.items()}
        if self.cfg.policy_noise_std > 0:
            for key, tensor in mutated_state.items():
                if tensor.is_floating_point() and "critic" not in key:
                    tensor.add_(torch.randn_like(tensor) * self.cfg.policy_noise_std)
        target.load_policy_state_dict(mutated_state)
        target.obs_rms.load_state_dict(self.workers[source.worker_id].obs_rms.state_dict())
        lr_factor = float(np.exp(np.random.normal(0.0, self.cfg.mutate_lr_log_scale)))
        ent_factor = float(np.exp(np.random.normal(0.0, self.cfg.mutate_ent_coef_log_scale)))
        target.cfg.learning_rate = max(1e-6, min(3e-3, source.lr * lr_factor))
        target.cfg.ent_coef = max(0.0, min(0.05, source.ent_coef * ent_factor))
        target.reset_optimizer()

    def save_best(self, best_worker: int, round_idx: int) -> Path:
        path = self.output_dir / "checkpoints" / f"best_round_{round_idx}_worker_{best_worker}.pt"
        self.workers[best_worker].save(path)
        return path
