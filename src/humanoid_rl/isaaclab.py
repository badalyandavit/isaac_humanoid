from __future__ import annotations

import math
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from humanoid_rl.config import _merge_dict_into_dataclass, load_yaml
from humanoid_rl.utils import ensure_dir, write_json


@dataclass
class IsaacLabPPOConfig:
    isaaclab_dir: str = "/workspace/IsaacLab"
    task: str = "Isaac-Humanoid-Direct-v0"
    seed: int = 301
    num_envs: int = 4096
    total_timesteps: int = 15_000_000
    num_steps_per_env: int = 32
    max_iterations: int | None = None
    save_interval: int = 10
    experiment_name: str = "humanoid_direct_single_ppo"
    run_name: str = "baseline"
    output_dir: str = "outputs/isaac_ppo_baseline"
    device: str = "cuda:0"
    headless: bool = True
    video: bool = False
    video_length: int = 200
    video_interval: int = 2000
    hydra_overrides: list[str] = field(default_factory=list)


def load_isaac_ppo_config(path: str | Path) -> IsaacLabPPOConfig:
    cfg = IsaacLabPPOConfig()
    return _merge_dict_into_dataclass(cfg, load_yaml(path))


def max_iterations(cfg: IsaacLabPPOConfig) -> int:
    if cfg.max_iterations is not None:
        return int(cfg.max_iterations)
    steps_per_iteration = cfg.num_envs * cfg.num_steps_per_env
    return max(1, math.ceil(cfg.total_timesteps / steps_per_iteration))


def expected_env_steps(cfg: IsaacLabPPOConfig) -> int:
    return max_iterations(cfg) * cfg.num_envs * cfg.num_steps_per_env


def train_command(cfg: IsaacLabPPOConfig) -> list[str]:
    isaaclab_sh = Path(cfg.isaaclab_dir) / "isaaclab.sh"
    command = [
        str(isaaclab_sh),
        "-p",
        "scripts/reinforcement_learning/rsl_rl/train.py",
        "--task",
        cfg.task,
        "--num_envs",
        str(cfg.num_envs),
        "--seed",
        str(cfg.seed),
        "--max_iterations",
        str(max_iterations(cfg)),
        "--experiment_name",
        cfg.experiment_name,
        "--run_name",
        cfg.run_name,
        "--device",
        cfg.device,
        f"agent.num_steps_per_env={cfg.num_steps_per_env}",
        f"agent.save_interval={cfg.save_interval}",
    ]
    if cfg.headless:
        command.append("--headless")
    if cfg.video:
        command.extend(
            [
                "--video",
                "--video_length",
                str(cfg.video_length),
                "--video_interval",
                str(cfg.video_interval),
            ]
        )
    command.extend(cfg.hydra_overrides)
    return command


def run_training(cfg: IsaacLabPPOConfig, dry_run: bool = False) -> dict[str, Any]:
    output_dir = ensure_dir(cfg.output_dir)
    log_root = Path(cfg.isaaclab_dir) / "logs" / "rsl_rl" / cfg.experiment_name
    before = existing_run_dirs(log_root)
    command = train_command(cfg)
    started_at = time.time()
    if not dry_run:
        validate_isaaclab_dir(cfg.isaaclab_dir)
        subprocess.run(command, cwd=cfg.isaaclab_dir, check=True)
    elapsed = time.time() - started_at
    run_dir = find_new_run_dir(log_root, before, cfg.run_name) if not dry_run else None
    checkpoint = latest_checkpoint(run_dir) if run_dir is not None else None
    manifest = {
        "task": cfg.task,
        "algorithm": "isaac_rsl_rl_ppo",
        "seed": cfg.seed,
        "num_envs": cfg.num_envs,
        "num_steps_per_env": cfg.num_steps_per_env,
        "max_iterations": max_iterations(cfg),
        "configured_total_timesteps": cfg.total_timesteps,
        "expected_env_steps": expected_env_steps(cfg),
        "experiment_name": cfg.experiment_name,
        "run_name": cfg.run_name,
        "run_dir": str(run_dir) if run_dir else None,
        "checkpoint": str(checkpoint) if checkpoint else None,
        "elapsed_seconds": elapsed,
        "command": command,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def validate_isaaclab_dir(path: str | Path) -> None:
    root = Path(path)
    script = root / "isaaclab.sh"
    train_script = root / "scripts" / "reinforcement_learning" / "rsl_rl" / "train.py"
    if not script.exists():
        raise FileNotFoundError(f"Isaac Lab launcher not found: {script}")
    if not train_script.exists():
        raise FileNotFoundError(f"Isaac Lab RSL-RL train script not found: {train_script}")


def existing_run_dirs(log_root: Path) -> set[Path]:
    if not log_root.exists():
        return set()
    return {p for p in log_root.iterdir() if p.is_dir()}


def find_new_run_dir(log_root: Path, before: set[Path], run_name: str) -> Path | None:
    if not log_root.exists():
        return None
    candidates = [p for p in log_root.iterdir() if p.is_dir() and p not in before]
    named = [p for p in candidates if p.name.endswith(f"_{run_name}")]
    candidates = named or candidates
    if not candidates:
        all_named = [p for p in log_root.iterdir() if p.is_dir() and p.name.endswith(f"_{run_name}")]
        candidates = all_named or [p for p in log_root.iterdir() if p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def latest_checkpoint(run_dir: Path | None) -> Path | None:
    if run_dir is None:
        return None
    checkpoints = sorted(run_dir.glob("model_*.pt"), key=checkpoint_sort_key)
    if not checkpoints:
        checkpoints = sorted(run_dir.glob("*.pt"), key=lambda p: p.stat().st_mtime)
    if not checkpoints:
        return None
    return checkpoints[-1]


def checkpoint_sort_key(path: Path) -> tuple[int, float]:
    match = re.search(r"model_(\d+)\.pt$", path.name)
    if match:
        return int(match.group(1)), path.stat().st_mtime
    return -1, path.stat().st_mtime
