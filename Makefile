PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))
VIDEO_CONFIG ?= configs/baseline_ppo.yaml
VIDEO_CHECKPOINT ?= outputs/baseline_humanoid_v5/checkpoints/final.pt
VIDEO_OUT ?= outputs/videos/humanoid_policy.mp4
VIDEO_MAX_STEPS ?= 1000

.PHONY: install smoke baseline average heavytail scaling fair-ppo fair-sac fair-ppo-pop fair-sac-pop fair-eval collect-data analyze video

install:
	$(PYTHON) -m pip install -e .

smoke:
	$(PYTHON) scripts/train_baseline.py --config configs/baseline_smoke.yaml
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_smoke.yaml
	$(PYTHON) scripts/train_ppo_population.py --config configs/fair_ppo_population_smoke.yaml
	$(PYTHON) scripts/train_heavytail.py --config configs/population_heavytail_smoke.yaml

baseline:
	$(PYTHON) scripts/train_baseline.py --config configs/baseline_ppo.yaml

average:
	$(PYTHON) scripts/train_average.py --config configs/population_average.yaml

heavytail:
	$(PYTHON) scripts/train_heavytail.py --config configs/population_heavytail.yaml

scaling:
	$(PYTHON) scripts/sweep_scaling.py --config configs/scaling_sweep.yaml --agents 1,2,4,8

fair-ppo:
	$(PYTHON) scripts/train_baseline.py --config configs/fair_ppo_baseline.yaml

fair-sac:
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_baseline.yaml

fair-ppo-pop:
	$(PYTHON) scripts/train_ppo_population.py --config configs/fair_ppo_population.yaml

fair-sac-pop:
	$(PYTHON) scripts/train_sac_population.py --config configs/fair_sac_population.yaml

fair-eval:
	$(PYTHON) scripts/evaluate_fair.py --out-dir outputs/fair_eval

collect-data:
	$(PYTHON) scripts/collect_eval_dataset.py --configs configs/baseline_ppo.yaml configs/population_average.yaml configs/population_heavytail.yaml

analyze:
	$(PYTHON) scripts/analyze_results.py --outputs outputs --out outputs/analysis

video:
	$(PYTHON) scripts/record_video.py --config $(VIDEO_CONFIG) --checkpoint $(VIDEO_CHECKPOINT) --out $(VIDEO_OUT) --max-steps $(VIDEO_MAX_STEPS)
