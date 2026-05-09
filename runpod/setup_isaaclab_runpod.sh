#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_DIR=${ISAACLAB_DIR:-/workspace/IsaacLab}
ISAACLAB_REF=${ISAACLAB_REF:-v2.3.0}
ISAACSIM_VERSION=${ISAACSIM_VERSION:-5.1.0}
ISAACLAB_VENV=${ISAACLAB_VENV:-/workspace/isaaclab_env}
ISAACLAB_USE_SYSTEM_PYTHON=${ISAACLAB_USE_SYSTEM_PYTHON:-0}
PRESERVE_TORCH=${PRESERVE_TORCH:-1}
WORKSPACE_TMP=${WORKSPACE_TMP:-/workspace/tmp}
PIP_CACHE_DIR=${PIP_CACHE_DIR:-/workspace/pip-cache}

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
apt-get clean
rm -rf /var/lib/apt/lists/*

mkdir -p "${WORKSPACE_TMP}" "${PIP_CACHE_DIR}"
export TMPDIR="${WORKSPACE_TMP}"
export PIP_CACHE_DIR

if [[ "${ISAACLAB_USE_SYSTEM_PYTHON}" != "1" && -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ ! -x "${ISAACLAB_VENV}/bin/python" ]]; then
    python3 -m venv "${ISAACLAB_VENV}"
  fi
  # shellcheck disable=SC1091
  source "${ISAACLAB_VENV}/bin/activate"
fi

python -m pip install --upgrade pip

PIP_CONSTRAINT_ARGS=()
if [[ "${PRESERVE_TORCH}" == "1" ]]; then
  TORCH_CONSTRAINTS="${WORKSPACE_TMP}/torch_constraints.txt"
  python - "${TORCH_CONSTRAINTS}" <<'PY'
from __future__ import annotations

import importlib.util
import sys
from importlib import metadata
from pathlib import Path

constraints_path = Path(sys.argv[1])
packages = ("torch", "torchvision", "torchaudio")
constraints: list[str] = []
for package in packages:
    if importlib.util.find_spec(package) is None:
        continue
    try:
        version = metadata.version(package)
    except metadata.PackageNotFoundError:
        continue
    constraints.append(f"{package}=={version}")

constraints_path.write_text("\n".join(constraints) + ("\n" if constraints else ""), encoding="utf-8")
if constraints:
    print("[INFO] Preserving existing Torch package versions:")
    for constraint in constraints:
        print(f"  {constraint}")
PY
  if [[ -s "${TORCH_CONSTRAINTS}" ]]; then
    PIP_CONSTRAINT_ARGS=(-c "${TORCH_CONSTRAINTS}")
  fi
fi

python -m pip install --upgrade-strategy only-if-needed --no-cache-dir "${PIP_CONSTRAINT_ARGS[@]}" "isaacsim[all,extscache]==${ISAACSIM_VERSION}" --extra-index-url https://pypi.nvidia.com

if [[ -e "${ISAACLAB_DIR}" && ! -d "${ISAACLAB_DIR}/.git" ]]; then
  echo "[ERROR] ${ISAACLAB_DIR} exists but is not a git checkout. Move or remove it before setup."
  exit 1
fi

if [[ ! -d "${ISAACLAB_DIR}/.git" ]]; then
  git clone --depth 1 --branch "${ISAACLAB_REF}" https://github.com/isaac-sim/IsaacLab.git "${ISAACLAB_DIR}"
else
  git -C "${ISAACLAB_DIR}" fetch --depth 1 origin "${ISAACLAB_REF}"
  git -C "${ISAACLAB_DIR}" checkout --detach FETCH_HEAD
fi

cd "${ISAACLAB_DIR}"
./isaaclab.sh --install
./isaaclab.sh -p - <<'PY'
import gymnasium as gym
import isaaclab_tasks  # noqa: F401
print("Isaac Lab task import OK")
print("Humanoid registered:", "Isaac-Humanoid-Direct-v0" in gym.registry)
PY
