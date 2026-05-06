#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
python scripts/train_ppo_baseline.py --config configs/fair_ppo_baseline.yaml
