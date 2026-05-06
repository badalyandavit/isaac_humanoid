from __future__ import annotations

import argparse
import copy
import os
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/fair_ppo_baseline.yaml")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--out", type=str, default="outputs/videos/humanoid_policy.mp4")
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument(
        "--mujoco-gl",
        choices=["egl", "glfw", "osmesa"],
        default=None,
        help="MuJoCo OpenGL backend. Defaults to egl on headless Linux.",
    )
    return parser.parse_args()


def configure_rendering(mujoco_gl: str | None) -> None:
    if mujoco_gl is not None:
        os.environ["MUJOCO_GL"] = mujoco_gl
    elif sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        os.environ.setdefault("MUJOCO_GL", "egl")
    if os.environ.get("MUJOCO_GL") == "egl":
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")


def make_video_config(config_path: str, output_dir: Path):
    from humanoid_rl.config import (
        load_parameter_average_config,
        load_ppo_config,
        load_yaml,
    )

    data = load_yaml(config_path)
    if "average_every_rounds" in data:
        cfg = load_parameter_average_config(config_path)
        video_cfg = copy.deepcopy(cfg.worker)
        video_cfg.env_id = cfg.env_id
        video_cfg.seed = cfg.seed
        video_cfg.device = cfg.device
    else:
        video_cfg = load_ppo_config(config_path)
    video_cfg.num_envs = 1
    video_cfg.output_dir = str(output_dir / "video_loader")
    return video_cfg


def main() -> None:
    args = parse_args()
    configure_rendering(args.mujoco_gl)

    import gymnasium as gym
    import imageio.v2 as imageio
    import numpy as np
    import torch

    from humanoid_rl.ppo import PPOTrainer
    from humanoid_rl.utils import ensure_dir

    out_path = Path(args.out)
    cfg = make_video_config(args.config, out_path.parent)
    trainer = PPOTrainer(cfg, run_name="video_loader")
    trainer.load(args.checkpoint, load_optimizer=False)
    env = gym.make(cfg.env_id, render_mode="rgb_array")
    frames = []
    try:
        obs, _ = env.reset(seed=cfg.seed + 777)
        for _ in range(args.max_steps):
            frame = env.render()
            frames.append(frame)
            obs_batch = np.asarray(obs, dtype=np.float32).reshape(1, trainer.obs_dim)
            if cfg.obs_norm:
                obs_batch = trainer.obs_rms.normalize(obs_batch)
            with torch.no_grad():
                action = trainer.model.act_deterministic(
                    torch.as_tensor(obs_batch, dtype=torch.float32, device=trainer.device)
                )
            obs, _, terminated, truncated, _ = env.step(action.cpu().numpy()[0])
            if terminated or truncated:
                break
    finally:
        env.close()
        trainer.close()
    if not frames:
        raise RuntimeError("No video frames were rendered.")
    ensure_dir(out_path.parent)
    imageio.mimsave(out_path, frames, fps=30)
    print(f"Saved video to {out_path}")


if __name__ == "__main__":
    main()
