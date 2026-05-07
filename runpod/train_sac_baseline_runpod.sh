#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
python scripts/train_sac_baseline.py --config configs/fair_sac_baseline.yaml
