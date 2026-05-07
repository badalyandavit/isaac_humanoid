#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_DIR=${ISAACLAB_DIR:-/workspace/IsaacLab}
ISAACLAB_REF=${ISAACLAB_REF:-main}

python3 - <<'PY'
import sys
if sys.version_info[:2] != (3, 11):
    raise SystemExit(
        "Isaac Sim 5.x requires Python 3.11. Use an Isaac Sim/Isaac Lab RunPod "
        "template or create a Python 3.11 environment before running this script."
    )
PY

apt-get update
apt-get install -y --no-install-recommends git build-essential cmake ninja-build ffmpeg tmux

if [[ ! -d "${ISAACLAB_DIR}/.git" ]]; then
  git clone --depth 1 --branch "${ISAACLAB_REF}" https://github.com/isaac-sim/IsaacLab.git "${ISAACLAB_DIR}"
fi

cd "${ISAACLAB_DIR}"
./isaaclab.sh --install
./isaaclab.sh -p - <<'PY'
import gymnasium as gym
import isaaclab_tasks  # noqa: F401
print("Isaac Lab task import OK")
print("Humanoid registered:", "Isaac-Humanoid-Direct-v0" in gym.registry)
PY
