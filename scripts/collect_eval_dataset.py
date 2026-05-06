from __future__ import annotations

import argparse
import csv
import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tqdm.auto import tqdm

from humanoid_rl.config import (
    HeavyTailConfig,
    PPOConfig,
    load_average_config,
    load_heavytail_config,
    load_ppo_config,
    load_yaml,
)
from humanoid_rl.metrics import robust_worker_score
from humanoid_rl.ppo import PPOTrainer


@dataclass
class EvalSpec:
    config_path: Path
    method_key: str
    method_name: str
    output_dir: Path
    eval_cfg: PPOConfig
    eval_episodes: int
    num_workers: int
    score_cfg: HeavyTailConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate trained checkpoints and write episode-level and summary datasets."
    )
    parser.add_argument("--configs", nargs="+", required=True, help="Training config files to evaluate.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/eval_dataset.csv"),
        help="Episode-level CSV output path.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Summary CSV output path. Defaults to <out parent>/eval_summary.csv.",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=None,
        help="Override the evaluation episode count from each config.",
    )
    parser.add_argument(
        "--include-intermediate",
        action="store_true",
        help="Evaluate every checkpoint in each checkpoints directory, not only final checkpoints.",
    )
    parser.add_argument("--stochastic", action="store_true", help="Sample actions instead of using mean actions.")
    return parser.parse_args()


def infer_method(config_path: Path) -> str:
    data = load_yaml(config_path)
    if "average_every_rounds" in data:
        return "average"
    if "promote_margin" in data or "trim_fraction" in data:
        return "heavytail"
    return "baseline"


def make_spec(config_path: Path, episode_override: int | None, out_root: Path) -> EvalSpec:
    method_key = infer_method(config_path)
    score_cfg = HeavyTailConfig()
    if method_key == "average":
        cfg = load_average_config(config_path)
        eval_cfg = copy.deepcopy(cfg.worker)
        eval_cfg.env_id = cfg.env_id
        eval_cfg.seed = cfg.seed
        eval_cfg.device = cfg.device
        eval_cfg.num_envs = 1
        eval_cfg.output_dir = str(out_root / "eval_runs" / config_path.stem)
        return EvalSpec(
            config_path=config_path,
            method_key=method_key,
            method_name="Naive Average PPO",
            output_dir=Path(cfg.output_dir),
            eval_cfg=eval_cfg,
            eval_episodes=episode_override or cfg.eval_episodes,
            num_workers=cfg.num_workers,
            score_cfg=score_cfg,
        )
    if method_key == "heavytail":
        cfg = load_heavytail_config(config_path)
        eval_cfg = copy.deepcopy(cfg.worker)
        eval_cfg.env_id = cfg.env_id
        eval_cfg.seed = cfg.seed
        eval_cfg.device = cfg.device
        eval_cfg.num_envs = 1
        eval_cfg.output_dir = str(out_root / "eval_runs" / config_path.stem)
        return EvalSpec(
            config_path=config_path,
            method_key=method_key,
            method_name="Robust Heavy-Tail Cooperative PPO",
            output_dir=Path(cfg.output_dir),
            eval_cfg=eval_cfg,
            eval_episodes=episode_override or cfg.eval_episodes,
            num_workers=cfg.num_workers,
            score_cfg=cfg,
        )
    cfg = load_ppo_config(config_path)
    eval_cfg = copy.deepcopy(cfg)
    eval_cfg.num_envs = 1
    eval_cfg.output_dir = str(out_root / "eval_runs" / config_path.stem)
    return EvalSpec(
        config_path=config_path,
        method_key=method_key,
        method_name="Baseline PPO",
        output_dir=Path(cfg.output_dir),
        eval_cfg=eval_cfg,
        eval_episodes=episode_override or cfg.eval_episodes,
        num_workers=1,
        score_cfg=score_cfg,
    )


def checkpoint_label(path: Path) -> str:
    if path.name.startswith("best_round_"):
        match = re.search(r"best_round_(\d+)", path.name)
        return f"best_round_{match.group(1)}" if match else path.stem
    return path.stem


def checkpoint_sort_key(path: Path) -> tuple[int, int, str]:
    if path.name.startswith("best_round_"):
        match = re.search(r"best_round_(\d+)", path.name)
        return (0, int(match.group(1)) if match else -1, path.name)
    if path.name.startswith("step_"):
        match = re.search(r"step_(\d+)", path.name)
        return (1, int(match.group(1)) if match else -1, path.name)
    return (2, 0, path.name)


def discover_checkpoints(spec: EvalSpec, include_intermediate: bool) -> list[Path]:
    checkpoint_dir = spec.output_dir / "checkpoints"
    if not checkpoint_dir.exists():
        return []
    if include_intermediate:
        return sorted(checkpoint_dir.glob("*.pt"), key=checkpoint_sort_key)
    preferred_names = {
        "baseline": ["final.pt"],
        "average": ["final_average.pt", "final.pt"],
        "heavytail": ["final_best.pt", "final.pt"],
    }[spec.method_key]
    checkpoints = [checkpoint_dir / name for name in preferred_names if (checkpoint_dir / name).exists()]
    if checkpoints:
        return checkpoints
    best_rounds = sorted(checkpoint_dir.glob("best_round_*.pt"), key=checkpoint_sort_key)
    if best_rounds:
        return [best_rounds[-1]]
    step_checkpoints = sorted(checkpoint_dir.glob("step_*.pt"), key=checkpoint_sort_key)
    return [step_checkpoints[-1]] if step_checkpoints else []


def score_summary(metrics: dict[str, Any], score_cfg: HeavyTailConfig) -> dict[str, Any]:
    score = robust_worker_score(
        metrics,
        trim_fraction=score_cfg.trim_fraction,
        q_low=score_cfg.q_low,
        median_weight=score_cfg.median_weight,
        fall_penalty=score_cfg.fall_penalty,
        energy_penalty=score_cfg.energy_penalty,
    )
    return {f"robust_{key}": value for key, value in score.__dict__.items()}


def evaluate_checkpoint(
    spec: EvalSpec,
    checkpoint: Path,
    deterministic: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trainer = PPOTrainer(spec.eval_cfg, run_name=f"collect_eval_{spec.method_key}_{checkpoint.stem}")
    try:
        trainer.load(checkpoint, load_optimizer=False)
        metrics = trainer.evaluate(
            spec.eval_episodes,
            deterministic=deterministic,
            show_progress=True,
            desc=f"{spec.method_key} {checkpoint_label(checkpoint)} eval",
        )
    finally:
        trainer.close()

    base = {
        "method_key": spec.method_key,
        "method": spec.method_name,
        "num_workers": spec.num_workers,
        "config_path": str(spec.config_path),
        "output_dir": str(spec.output_dir),
        "checkpoint": str(checkpoint),
        "checkpoint_label": checkpoint_label(checkpoint),
        "eval_episodes": spec.eval_episodes,
        "deterministic": deterministic,
    }
    episode_rows = []
    for episode_idx, (episode_return, episode_length) in enumerate(
        zip(metrics["returns"], metrics["lengths"], strict=True)
    ):
        episode_rows.append(
            {
                **base,
                "episode": episode_idx,
                "episode_return": episode_return,
                "episode_length": episode_length,
            }
        )
    summary = {
        **base,
        **{key: value for key, value in metrics.items() if key not in {"returns", "lengths"}},
        **score_summary(metrics, spec.score_cfg),
    }
    return episode_rows, summary


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    summary_out = args.summary_out or (args.out.parent / "eval_summary.csv")
    episode_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for config in tqdm(args.configs, desc="configs", unit="config"):
        spec = make_spec(Path(config), args.episodes, args.out.parent)
        checkpoints = discover_checkpoints(spec, args.include_intermediate)
        if not checkpoints:
            missing.append(f"{spec.config_path}: no checkpoints under {spec.output_dir / 'checkpoints'}")
            continue
        for checkpoint in tqdm(checkpoints, desc=f"{spec.method_key} checkpoints", unit="ckpt"):
            rows, summary = evaluate_checkpoint(
                spec,
                checkpoint,
                deterministic=not args.stochastic,
            )
            episode_rows.extend(rows)
            summary_rows.append(summary)
            tqdm.write(f"Evaluated {checkpoint} over {spec.eval_episodes} episodes.")

    if not summary_rows:
        for item in missing:
            print(item)
        raise SystemExit("No checkpoints were evaluated.")

    write_rows(args.out, episode_rows)
    write_rows(summary_out, summary_rows)
    print(f"Wrote episode dataset to {args.out}")
    print(f"Wrote summary dataset to {summary_out}")
    for item in missing:
        print(f"Skipped: {item}")


if __name__ == "__main__":
    main()
