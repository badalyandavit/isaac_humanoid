PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))

.PHONY: install smoke baseline average heavytail scaling collect-data analyze video

install:
	$(PYTHON) -m pip install -e .

smoke:
	$(PYTHON) scripts/train_baseline.py --config configs/baseline_smoke.yaml
	$(PYTHON) scripts/train_heavytail.py --config configs/population_heavytail_smoke.yaml

baseline:
	$(PYTHON) scripts/train_baseline.py --config configs/baseline_ppo.yaml

average:
	$(PYTHON) scripts/train_average.py --config configs/population_average.yaml

heavytail:
	$(PYTHON) scripts/train_heavytail.py --config configs/population_heavytail.yaml

scaling:
	$(PYTHON) scripts/sweep_scaling.py --config configs/scaling_sweep.yaml --agents 1,2,4,8

collect-data:
	$(PYTHON) scripts/collect_eval_dataset.py --configs configs/baseline_ppo.yaml configs/population_average.yaml configs/population_heavytail.yaml

analyze:
	$(PYTHON) scripts/analyze_results.py --outputs outputs --out outputs/analysis

video:
	$(PYTHON) scripts/record_video.py --config configs/baseline_ppo.yaml --checkpoint outputs/baseline_humanoid_v5/checkpoints/final.pt
