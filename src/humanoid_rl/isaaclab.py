from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from humanoid_rl.config import _merge_dict_into_dataclass, load_yaml
from humanoid_rl.utils import ensure_dir, write_json


ISAAC_HUMANOID_REWARD_DEFAULTS: dict[str, float] = {
    "heading_weight": 0.5,
    "up_weight": 0.1,
    "energy_cost_scale": 0.05,
    "actions_cost_scale": 0.01,
    "alive_reward_scale": 2.0,
    "dof_vel_scale": 0.1,
    "death_cost": -1.0,
    "termination_height": 0.8,
    "angular_velocity_scale": 0.25,
    "contact_force_scale": 0.01,
}

ISAAC_HUMANOID_V4_REWARD_DEFAULTS: dict[str, float] = {
    "height_target": 1.35,
    "height_bonus_scale": 4.0,
    "height_tracking_penalty_scale": 0.0,
    "low_height_threshold": 1.15,
    "low_height_penalty_scale": 6.0,
    "high_height_threshold": 1.60,
    "high_height_penalty_scale": 0.0,
    "torso_low_height": 1.10,
    "torso_low_penalty_scale": 4.0,
    "arm_low_height": 0.65,
    "arm_low_penalty_scale": 4.0,
    "leg_pose_penalty_scale": 0.6,
    "arm_pose_penalty_scale": 0.8,
    "action_rate_penalty_scale": 0.04,
    "vertical_velocity_penalty_scale": 0.0,
    "arm_action_penalty_scale": 0.0,
    "arm_velocity_penalty_scale": 0.0,
    "leg_action_symmetry_penalty_scale": 0.0,
    "leg_pose_symmetry_penalty_scale": 0.0,
    "non_foot_low_height": 0.55,
    "non_foot_low_penalty_scale": 0.0,
    "foot_air_height": 0.20,
    "foot_air_penalty_scale": 0.0,
    "foot_slip_height": 0.16,
    "foot_slip_penalty_scale": 0.0,
    "target_forward_velocity": 0.0,
    "forward_velocity_reward_scale": 0.0,
    "forward_velocity_sigma": 0.6,
    "lateral_velocity_penalty_scale": 0.0,
    "low_speed_threshold": 0.5,
    "low_speed_vertical_penalty_scale": 0.0,
    "arm_high_height": 1.55,
    "arm_high_penalty_scale": 0.0,
    "foot_contact_height": 0.14,
    "foot_contact_force_threshold": 1.0,
    "single_foot_contact_reward_scale": 0.0,
    "foot_contact_switch_reward_scale": 0.0,
    "no_foot_contact_penalty_scale": 0.0,
    "double_foot_contact_penalty_scale": 0.0,
    "foot_contact_balance_penalty_scale": 0.0,
    "foot_contact_ema_decay": 0.98,
}


@dataclass
class IsaacLabPPOConfig:
    baseline_name: str = "isaac_v0_official_humanoid_direct"
    simulator_backend: str = "Isaac Lab"
    reward_version: str = "isaac_v0_official"
    loss_version: str = "isaac_rsl_rl_ppo_default"
    reward_design_goal: str = "Official Isaac Lab direct humanoid reward."
    custom_isaac_task: bool = False
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
    heading_weight: float = ISAAC_HUMANOID_REWARD_DEFAULTS["heading_weight"]
    up_weight: float = ISAAC_HUMANOID_REWARD_DEFAULTS["up_weight"]
    energy_cost_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["energy_cost_scale"]
    actions_cost_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["actions_cost_scale"]
    alive_reward_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["alive_reward_scale"]
    dof_vel_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["dof_vel_scale"]
    death_cost: float = ISAAC_HUMANOID_REWARD_DEFAULTS["death_cost"]
    termination_height: float = ISAAC_HUMANOID_REWARD_DEFAULTS["termination_height"]
    angular_velocity_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["angular_velocity_scale"]
    contact_force_scale: float = ISAAC_HUMANOID_REWARD_DEFAULTS["contact_force_scale"]
    height_target: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["height_target"]
    height_bonus_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["height_bonus_scale"]
    height_tracking_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["height_tracking_penalty_scale"]
    low_height_threshold: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["low_height_threshold"]
    low_height_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["low_height_penalty_scale"]
    high_height_threshold: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["high_height_threshold"]
    high_height_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["high_height_penalty_scale"]
    torso_low_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["torso_low_height"]
    torso_low_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["torso_low_penalty_scale"]
    arm_low_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_low_height"]
    arm_low_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_low_penalty_scale"]
    leg_pose_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["leg_pose_penalty_scale"]
    arm_pose_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_pose_penalty_scale"]
    action_rate_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["action_rate_penalty_scale"]
    vertical_velocity_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["vertical_velocity_penalty_scale"]
    arm_action_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_action_penalty_scale"]
    arm_velocity_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_velocity_penalty_scale"]
    leg_action_symmetry_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["leg_action_symmetry_penalty_scale"]
    leg_pose_symmetry_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["leg_pose_symmetry_penalty_scale"]
    non_foot_low_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["non_foot_low_height"]
    non_foot_low_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["non_foot_low_penalty_scale"]
    foot_air_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_air_height"]
    foot_air_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_air_penalty_scale"]
    foot_slip_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_slip_height"]
    foot_slip_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_slip_penalty_scale"]
    target_forward_velocity: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["target_forward_velocity"]
    forward_velocity_reward_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["forward_velocity_reward_scale"]
    forward_velocity_sigma: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["forward_velocity_sigma"]
    lateral_velocity_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["lateral_velocity_penalty_scale"]
    low_speed_threshold: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["low_speed_threshold"]
    low_speed_vertical_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["low_speed_vertical_penalty_scale"]
    arm_high_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_high_height"]
    arm_high_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["arm_high_penalty_scale"]
    foot_contact_height: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_contact_height"]
    foot_contact_force_threshold: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_contact_force_threshold"]
    single_foot_contact_reward_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["single_foot_contact_reward_scale"]
    foot_contact_switch_reward_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_contact_switch_reward_scale"]
    no_foot_contact_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["no_foot_contact_penalty_scale"]
    double_foot_contact_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["double_foot_contact_penalty_scale"]
    foot_contact_balance_penalty_scale: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS[
        "foot_contact_balance_penalty_scale"
    ]
    foot_contact_ema_decay: float = ISAAC_HUMANOID_V4_REWARD_DEFAULTS["foot_contact_ema_decay"]
    reward_notes: list[str] = field(default_factory=list)
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


def reward_parameters(cfg: IsaacLabPPOConfig) -> dict[str, float]:
    return {key: float(getattr(cfg, key)) for key in ISAAC_HUMANOID_REWARD_DEFAULTS}


def reward_parameter_changes(cfg: IsaacLabPPOConfig) -> dict[str, dict[str, float]]:
    changes: dict[str, dict[str, float]] = {}
    for key, official_value in ISAAC_HUMANOID_REWARD_DEFAULTS.items():
        configured_value = float(getattr(cfg, key))
        if configured_value != official_value:
            changes[key] = {
                "official_v0": official_value,
                "configured": configured_value,
            }
    return changes


def reward_hydra_overrides(cfg: IsaacLabPPOConfig) -> list[str]:
    overrides = [f"env.{key}={change['configured']}" for key, change in reward_parameter_changes(cfg).items()]
    if cfg.custom_isaac_task:
        overrides.extend(f"env.{key}={getattr(cfg, key)}" for key in ISAAC_HUMANOID_V4_REWARD_DEFAULTS)
    return overrides


def v4_reward_parameters(cfg: IsaacLabPPOConfig) -> dict[str, float]:
    return {key: float(getattr(cfg, key)) for key in ISAAC_HUMANOID_V4_REWARD_DEFAULTS}


def baseline_spec(cfg: IsaacLabPPOConfig) -> dict[str, Any]:
    return {
        "baseline_name": cfg.baseline_name,
        "simulator_backend": cfg.simulator_backend,
        "task": cfg.task,
        "reward_version": cfg.reward_version,
        "loss_version": cfg.loss_version,
        "source": "Isaac Lab official direct humanoid task",
        "reference_url": "https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/modify_direct_rl_env.html",
        "comparison_note": (
            "This is a separate Isaac Lab baseline. Do not compare reward values directly "
            "against Gymnasium/MuJoCo Humanoid-v5."
        ),
        "simulator": {
            "dt": 1.0 / 120.0,
            "decimation": 2,
            "control_dt": 2.0 / 120.0,
            "episode_length_s": 15.0,
            "default_num_envs": cfg.num_envs,
            "terrain": "plane",
            "static_friction": 1.0,
            "dynamic_friction": 1.0,
            "restitution": 0.0,
            "action_scale": 1.0,
            "action_space": 21,
            "observation_space": 75,
            "termination_height": cfg.termination_height,
        },
        "reward": {
            "design_goal": cfg.reward_design_goal,
            "custom_isaac_task": cfg.custom_isaac_task,
            "progress_reward": "change in negative distance-to-target potential",
            "alive_reward_scale": cfg.alive_reward_scale,
            "heading_weight": cfg.heading_weight,
            "heading_full_reward_threshold": 0.8,
            "up_weight": cfg.up_weight,
            "up_reward_threshold": 0.93,
            "actions_cost_scale": cfg.actions_cost_scale,
            "energy_cost_scale": cfg.energy_cost_scale,
            "dof_vel_scale": cfg.dof_vel_scale,
            "dof_at_limit_cost": "subtract count of joints with scaled position > 0.98",
            "death_cost": cfg.death_cost,
            "angular_velocity_scale": cfg.angular_velocity_scale,
            "contact_force_scale": cfg.contact_force_scale,
            "official_v0_parameters": ISAAC_HUMANOID_REWARD_DEFAULTS,
            "configured_parameters": reward_parameters(cfg),
            "custom_v4_parameters": v4_reward_parameters(cfg) if cfg.custom_isaac_task else {},
            "parameter_changes_from_v0": reward_parameter_changes(cfg),
            "auto_hydra_overrides": reward_hydra_overrides(cfg),
            "custom_v4_reward_terms": (
                [
                    "height bonus for maintaining torso/root height near target",
                    "height tracking penalty to avoid jumping above the target posture",
                    "low torso/root height penalty",
                    "high torso/root height penalty to discourage hopping",
                    "low torso/pelvis/head body penalty",
                    "low arm/hand body penalty as a proxy for arm-supported crawling",
                    "high arm/hand body penalty to discourage raised-arm balance exploits",
                    "leg joint pose penalty to discourage deep crouch",
                    "arm joint pose penalty to discourage arm-driven locomotion",
                    "arm action magnitude penalty to discourage arm-driven locomotion",
                    "arm joint velocity penalty",
                    "leg action and pose symmetry penalties",
                    "target forward velocity reward",
                    "lateral velocity penalty",
                    "low-speed vertical bounce penalty",
                    "action-rate penalty for smoother motion",
                    "vertical velocity penalty to discourage bouncing",
                    "non-foot low-body proxy penalty",
                    "feet airborne and foot-slip proxy penalties",
                    "single-foot contact, foot-switch, no-contact, double-contact, and foot-balance terms",
                    "custom reward diagnostics under extras['log']",
                ]
                if cfg.custom_isaac_task
                else []
            ),
            "notes": cfg.reward_notes,
        },
        "training": {
            "algorithm": "RSL-RL PPO",
            "loss_version": cfg.loss_version,
            "loss_note": "Isaac shaped variants change reward coefficients only; PPO loss is unchanged.",
            "num_envs": cfg.num_envs,
            "num_steps_per_env": cfg.num_steps_per_env,
            "max_iterations": max_iterations(cfg),
            "configured_total_timesteps": cfg.total_timesteps,
            "expected_env_steps": expected_env_steps(cfg),
            "device": cfg.device,
        },
    }


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
    command.extend(reward_hydra_overrides(cfg))
    command.extend(cfg.hydra_overrides)
    return command


def play_command(
    cfg: IsaacLabPPOConfig,
    checkpoint: str | Path,
    num_envs: int = 1,
    video_length: int | None = None,
    headless: bool = True,
) -> list[str]:
    isaaclab_sh = Path(cfg.isaaclab_dir) / "isaaclab.sh"
    command = [
        str(isaaclab_sh),
        "-p",
        "scripts/reinforcement_learning/rsl_rl/play.py",
        "--task",
        cfg.task,
        "--num_envs",
        str(num_envs),
        "--checkpoint",
        str(checkpoint),
        "--device",
        cfg.device,
        "--video",
        "--video_length",
        str(video_length if video_length is not None else cfg.video_length),
    ]
    if headless:
        command.append("--headless")
    command.extend(reward_hydra_overrides(cfg))
    command.extend(cfg.hydra_overrides)
    return command


def run_training(cfg: IsaacLabPPOConfig, dry_run: bool = False) -> dict[str, Any]:
    output_dir = ensure_dir(cfg.output_dir)
    log_roots = isaac_log_roots(cfg)
    before = {root: existing_run_dirs(root) for root in log_roots}
    command = train_command(cfg)
    started_at = time.time()
    if not dry_run:
        validate_isaaclab_dir(cfg.isaaclab_dir)
        subprocess.run(command, cwd=cfg.isaaclab_dir, check=True)
    elapsed = time.time() - started_at
    run_dir = find_isaac_run_dir(cfg, before) if not dry_run else None
    checkpoint = latest_checkpoint(run_dir) if run_dir is not None else None
    manifest = {
        "baseline_name": cfg.baseline_name,
        "task": cfg.task,
        "reward_version": cfg.reward_version,
        "loss_version": cfg.loss_version,
        "algorithm": "isaac_rsl_rl_ppo",
        "baseline_spec": baseline_spec(cfg),
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


def run_video(
    cfg: IsaacLabPPOConfig,
    checkpoint: str | Path | None = None,
    out: str | Path | None = None,
    num_envs: int = 1,
    video_length: int | None = None,
    headless: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    output_dir = ensure_dir(cfg.output_dir)
    checkpoint_path = resolve_isaac_checkpoint(cfg, checkpoint)
    command = play_command(
        cfg,
        checkpoint_path,
        num_envs=num_envs,
        video_length=video_length,
        headless=headless,
    )
    source_video: Path | None = None
    copied_video: Path | None = None
    started_at = time.time()
    if not dry_run:
        validate_isaaclab_dir(cfg.isaaclab_dir)
        checkpoint_for_fs = Path(checkpoint_path)
        if not checkpoint_for_fs.exists():
            raise FileNotFoundError(f"Isaac checkpoint not found: {checkpoint_for_fs}")
        video_dir = checkpoint_for_fs.parent / "videos" / "play"
        before = existing_video_files(video_dir)
        subprocess.run(command, cwd=cfg.isaaclab_dir, check=True)
        source_video = latest_video(video_dir, before)
        if source_video is None:
            raise FileNotFoundError(f"No Isaac video was written under: {video_dir}")
        if out is not None:
            copied_video = Path(out)
            ensure_dir(copied_video.parent)
            shutil.copy2(source_video, copied_video)
    elapsed = time.time() - started_at
    manifest = {
        "baseline_name": cfg.baseline_name,
        "task": cfg.task,
        "reward_version": cfg.reward_version,
        "loss_version": cfg.loss_version,
        "checkpoint": str(checkpoint_path),
        "source_video": str(source_video) if source_video else None,
        "copied_video": str(copied_video) if copied_video else str(out) if dry_run and out else None,
        "num_envs": num_envs,
        "video_length": video_length if video_length is not None else cfg.video_length,
        "elapsed_seconds": elapsed,
        "command": command,
    }
    write_json(output_dir / "video_manifest.json", manifest)
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


def isaac_log_roots(cfg: IsaacLabPPOConfig) -> list[Path]:
    logs_root = Path(cfg.isaaclab_dir) / "logs" / "rsl_rl"
    roots = [
        logs_root / cfg.experiment_name,
        logs_root / "humanoid_direct",
    ]
    if logs_root.exists():
        roots.extend(p for p in logs_root.iterdir() if p.is_dir())
    deduped: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if root not in seen:
            deduped.append(root)
            seen.add(root)
    return deduped


def find_isaac_run_dir(
    cfg: IsaacLabPPOConfig,
    before_by_root: dict[Path, set[Path]] | None = None,
) -> Path | None:
    candidates: list[Path] = []
    matching: list[Path] = []
    for root in isaac_log_roots(cfg):
        before = before_by_root.get(root, set()) if before_by_root else set()
        if before_by_root is not None:
            root_candidates = [p for p in existing_run_dirs(root) if p not in before]
        else:
            root_candidates = list(existing_run_dirs(root))
        candidates.extend(root_candidates)
        matching.extend(p for p in root_candidates if p.name.endswith(f"_{cfg.run_name}"))
    candidates = matching or candidates
    if before_by_root is not None and not candidates:
        return find_isaac_run_dir(cfg, None)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


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


def resolve_isaac_checkpoint(cfg: IsaacLabPPOConfig, checkpoint: str | Path | None = None) -> Path:
    if checkpoint is not None:
        return Path(checkpoint)
    manifest_path = Path(cfg.output_dir) / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No Isaac manifest found at {manifest_path}. Run the training target first or pass --checkpoint."
        )
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_checkpoint = manifest.get("checkpoint")
    if manifest_checkpoint:
        return Path(manifest_checkpoint)
    run_dir = find_isaac_run_dir(cfg)
    discovered_checkpoint = latest_checkpoint(run_dir)
    if discovered_checkpoint is not None:
        return discovered_checkpoint
    raise FileNotFoundError(
        f"No checkpoint is recorded in {manifest_path}, and no checkpoint was found under "
        f"{Path(cfg.isaaclab_dir) / 'logs' / 'rsl_rl'} for run name '{cfg.run_name}'. "
        "Run training first or pass --checkpoint."
    )


def existing_video_files(video_dir: Path) -> set[Path]:
    if not video_dir.exists():
        return set()
    return set(video_dir.rglob("*.mp4"))


def latest_video(video_dir: Path, before: set[Path] | None = None) -> Path | None:
    before = before or set()
    if not video_dir.exists():
        return None
    candidates = [p for p in video_dir.rglob("*.mp4") if p not in before]
    if not candidates:
        candidates = list(video_dir.rglob("*.mp4"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def checkpoint_sort_key(path: Path) -> tuple[int, float]:
    match = re.search(r"model_(\d+)\.pt$", path.name)
    if match:
        return int(match.group(1)), path.stat().st_mtime
    return -1, path.stat().st_mtime
