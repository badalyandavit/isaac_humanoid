from __future__ import annotations

import argparse
from pathlib import Path

import gymnasium as gym
import imageio.v2 as imageio
import numpy as np
import torch

from humanoid_rl.config import load_ppo_config
from humanoid_rl.ppo import PPOTrainer
from humanoid_rl.utils import ensure_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/baseline_ppo.yaml")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--out", type=str, default="outputs/videos/humanoid_policy.mp4")
    parser.add_argument("--max-steps", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_ppo_config(args.config)
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
    out_path = Path(args.out)
    ensure_dir(out_path.parent)
    imageio.mimsave(out_path, frames, fps=30)
    print(f"Saved video to {out_path}")


if __name__ == "__main__":
    main()
