#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  git \
  build-essential \
  libgl1 \
  libglfw3 \
  libglfw3-dev \
  libglew-dev \
  libosmesa6-dev \
  patchelf \
  ffmpeg \
  tmux

python -m pip install --upgrade pip setuptools wheel

if [[ "${KEEP_RUNPOD_TORCH:-1}" == "1" ]]; then
  python -m pip install \
    "gymnasium[mujoco]>=1.0.0" \
    "numpy>=1.24" \
    "PyYAML>=6.0" \
    "pandas>=2.0" \
    "tensorboard>=2.14" \
    "tqdm>=4.66" \
    "imageio>=2.34" \
    "imageio-ffmpeg>=0.5"
  python -m pip install -e . --no-deps
else
  python -m pip install -e .
fi

python - <<'PY'
import torch, gymnasium as gym
print('torch:', torch.__version__)
print('cuda available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('gpu:', torch.cuda.get_device_name(0))
env = gym.make('Humanoid-v5')
obs, _ = env.reset(seed=0)
print('Humanoid-v5 obs shape:', obs.shape)
print('Humanoid-v5 action shape:', env.action_space.shape)
env.close()
PY
