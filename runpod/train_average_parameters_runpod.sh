#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
python scripts/train_average_parameters.py --config configs/population_average_parameters.yaml
