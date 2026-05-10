from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import time
from pathlib import Path

from humanoid_rl.isaaclab import (
    existing_video_files,
    latest_video,
    load_isaac_ppo_config,
    resolve_isaac_checkpoint,
    reward_hydra_overrides,
    validate_isaaclab_dir,
)
from humanoid_rl.utils import ensure_dir, write_json


TRACKING_HELPER = '''

def _tensor_vec3_to_list(value):
    if value is None:
        return None
    try:
        if hasattr(value, "detach"):
            if getattr(value, "ndim", 0) > 1:
                value = value[0]
            value = value.detach().cpu().tolist()
        return [float(value[0]), float(value[1]), float(value[2])]
    except Exception:
        return None


def _tracking_root_position(env):
    base_env = env.unwrapped
    robot = getattr(base_env, "robot", None) or getattr(base_env, "_robot", None)
    if robot is None:
        scene = getattr(base_env, "scene", None)
        articulations = getattr(scene, "articulations", None)
        if isinstance(articulations, dict):
            robot = articulations.get("robot")
        if robot is None and scene is not None:
            try:
                robot = scene["robot"]
            except Exception:
                robot = None
    data = getattr(robot, "data", None)
    if data is None:
        return None
    for attr in ("root_pos_w", "root_link_pos_w"):
        pos = _tensor_vec3_to_list(getattr(data, attr, None))
        if pos is not None:
            return pos
    for attr in ("root_state_w", "root_link_state_w"):
        state = getattr(data, attr, None)
        if state is not None:
            try:
                return _tensor_vec3_to_list(state[..., :3])
            except Exception:
                continue
    return None


def _set_tracking_camera(env, args_cli):
    if not getattr(args_cli, "camera_tracking", False):
        return
    target = _tracking_root_position(env)
    if target is None:
        if not getattr(_set_tracking_camera, "_missing_target_warned", False):
            print("[WARN] Tracking camera could not find robot root position; using Isaac default camera.")
            _set_tracking_camera._missing_target_warned = True
        return
    eye = [
        target[0] - args_cli.camera_distance,
        target[1] + args_cli.camera_lateral,
        target[2] + args_cli.camera_height,
    ]
    lookat = [
        target[0] + args_cli.camera_lookahead,
        target[1],
        target[2] + args_cli.camera_look_height,
    ]
    try:
        env.unwrapped.sim.set_camera_view(eye, lookat)
    except Exception as exc:
        if not getattr(_set_tracking_camera, "_camera_warned", False):
            print(f"[WARN] Tracking camera update failed: {exc}")
            _set_tracking_camera._camera_warned = True
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record an Isaac Lab video with a camera that follows env_0.")
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("outputs/videos/isaac_policy_tracked.mp4"))
    parser.add_argument("--num-envs", type=int, default=1)
    parser.add_argument("--video-length", type=int, default=None)
    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--camera-distance", type=float, default=6.0)
    parser.add_argument("--camera-lateral", type=float, default=-2.5)
    parser.add_argument("--camera-height", type=float, default=2.4)
    parser.add_argument("--camera-lookahead", type=float, default=0.8)
    parser.add_argument("--camera-look-height", type=float, default=0.35)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def patch_play_script(isaaclab_dir: Path) -> Path:
    source_path = isaaclab_dir / "scripts" / "reinforcement_learning" / "rsl_rl" / "play.py"
    source = source_path.read_text(encoding="utf-8")
    source_dir = source_path.parent

    def sub_once(text: str, pattern: str, repl: str, description: str) -> str:
        updated, count = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE | re.DOTALL)
        if count != 1:
            raise RuntimeError(f"Could not patch Isaac Lab play.py; expected {description} not found.")
        return updated

    source = sub_once(
        source,
        r"import sys\s*from isaaclab\.app import AppLauncher",
        f'import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path({str(source_dir)!r})))\n'
        "from isaaclab.app import AppLauncher",
        "import sys followed by AppLauncher import",
    )
    source = sub_once(
        source,
        r'(?P<stmt>^[ \t]*parser\.add_argument\([^\n]*"--video_length"[^\n]*\)\s*\n?)',
        r'\g<stmt>'
        'parser.add_argument("--camera_tracking", action="store_true", default=False, help="Track env_0 robot with the viewer camera.")\n'
        'parser.add_argument("--camera_distance", type=float, default=6.0, help="Tracking camera distance behind the robot.")\n'
        'parser.add_argument("--camera_lateral", type=float, default=-2.5, help="Tracking camera lateral offset.")\n'
        'parser.add_argument("--camera_height", type=float, default=2.4, help="Tracking camera height above robot root.")\n'
        'parser.add_argument("--camera_lookahead", type=float, default=0.8, help="Tracking camera forward lookahead.")\n'
        'parser.add_argument("--camera_look_height", type=float, default=0.35, help="Tracking camera look-at height above robot root.")\n',
        "--video_length parser argument",
    )
    source = sub_once(source, r"import torch", "import torch" + TRACKING_HELPER, "import torch")
    source = sub_once(
        source,
        r"(?P<indent>[ \t]+)obs = env\.get_observations\(\)",
        "    obs = env.get_observations()\n    _set_tracking_camera(env, args_cli)",
        "initial observations line",
    )
    source = sub_once(
        source,
        r"(?P<indent>[ \t]+)obs, _, _, _ = env\.step\(actions\)",
        "            obs, _, _, _ = env.step(actions)\n            _set_tracking_camera(env, args_cli)",
        "environment step line",
    )

    out_path = isaaclab_dir / "logs" / "rsl_rl" / "_humanoid_tracking_play.py"
    ensure_dir(out_path.parent)
    out_path.write_text(source, encoding="utf-8")
    return out_path


def build_command(args: argparse.Namespace, tracking_script: Path, checkpoint: Path) -> list[str]:
    cfg = load_isaac_ppo_config(args.config)
    command = [
        str(Path(cfg.isaaclab_dir) / "isaaclab.sh"),
        "-p",
        str(tracking_script),
        "--task",
        cfg.task,
        "--num_envs",
        str(args.num_envs),
        "--checkpoint",
        str(checkpoint),
        "--device",
        cfg.device,
        "--video",
        "--video_length",
        str(args.video_length if args.video_length is not None else cfg.video_length),
        "--camera_tracking",
        "--camera_distance",
        str(args.camera_distance),
        "--camera_lateral",
        str(args.camera_lateral),
        "--camera_height",
        str(args.camera_height),
        "--camera_lookahead",
        str(args.camera_lookahead),
        "--camera_look_height",
        str(args.camera_look_height),
    ]
    if not args.no_headless:
        command.append("--headless")
    command.extend(reward_hydra_overrides(cfg))
    command.extend(cfg.hydra_overrides)
    return command


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    output_dir = ensure_dir(cfg.output_dir)
    checkpoint = resolve_isaac_checkpoint(cfg, args.checkpoint)
    tracking_script = Path(cfg.isaaclab_dir) / "logs" / "rsl_rl" / "_humanoid_tracking_play.py"
    if not args.dry_run:
        validate_isaaclab_dir(cfg.isaaclab_dir)
        tracking_script = patch_play_script(Path(cfg.isaaclab_dir))
        if not checkpoint.exists():
            raise FileNotFoundError(f"Isaac checkpoint not found: {checkpoint}")

    command = build_command(args, tracking_script, checkpoint)
    source_video: Path | None = None
    copied_video: Path | None = None
    started_at = time.time()
    if not args.dry_run:
        video_dir = checkpoint.parent / "videos" / "play"
        before = existing_video_files(video_dir)
        subprocess.run(command, cwd=cfg.isaaclab_dir, check=True)
        source_video = latest_video(video_dir, before)
        if source_video is None:
            raise FileNotFoundError(f"No Isaac video was written under: {video_dir}")
        copied_video = args.out
        ensure_dir(copied_video.parent)
        shutil.copy2(source_video, copied_video)

    manifest = {
        "baseline_name": cfg.baseline_name,
        "task": cfg.task,
        "reward_version": cfg.reward_version,
        "loss_version": cfg.loss_version,
        "checkpoint": str(checkpoint),
        "tracking_script": str(tracking_script),
        "source_video": str(source_video) if source_video else None,
        "copied_video": str(copied_video) if copied_video else str(args.out) if args.dry_run else None,
        "num_envs": args.num_envs,
        "video_length": args.video_length if args.video_length is not None else cfg.video_length,
        "camera": {
            "distance": args.camera_distance,
            "lateral": args.camera_lateral,
            "height": args.camera_height,
            "lookahead": args.camera_lookahead,
            "look_height": args.camera_look_height,
        },
        "elapsed_seconds": time.time() - started_at,
        "command": command,
    }
    write_json(output_dir / "tracking_video_manifest.json", manifest)
    print("Isaac tracking video manifest:")
    print(f"  baseline: {manifest['baseline_name']}")
    print(f"  checkpoint: {manifest['checkpoint']}")
    print(f"  video: {manifest['copied_video']}")


if __name__ == "__main__":
    main()
