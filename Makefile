PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))
VIDEO_CONFIG ?= configs/fair_ppo_baseline.yaml
VIDEO_CHECKPOINT ?= outputs/fair_ppo_baseline/checkpoints/final.pt
VIDEO_OUT ?= outputs/videos/humanoid_policy.mp4
VIDEO_MAX_STEPS ?= 1000

.PHONY: install smoke ppo-baseline sac-baseline ppo-pop sac-pop fair-eval average-parameters video

install:
	$(PYTHON) -m pip install -e .

smoke:
	$(PYTHON) scripts/train_ppo_baseline.py --config configs/fair_ppo_smoke.yaml
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_smoke.yaml
	$(PYTHON) scripts/train_ppo_population.py --config configs/fair_ppo_population_smoke.yaml

ppo-baseline:
	$(PYTHON) scripts/train_ppo_baseline.py --config configs/fair_ppo_baseline.yaml

sac-baseline:
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_baseline.yaml

ppo-pop:
	$(PYTHON) scripts/train_ppo_population.py --config configs/fair_ppo_population.yaml

sac-pop:
	$(PYTHON) scripts/train_sac_population.py --config configs/fair_sac_population.yaml

fair-eval:
	$(PYTHON) scripts/evaluate_fair.py --out-dir outputs/fair_eval

average-parameters:
	$(PYTHON) scripts/train_average_parameters.py --config configs/population_average_parameters.yaml

video:
	$(PYTHON) scripts/record_video.py --config $(VIDEO_CONFIG) --checkpoint $(VIDEO_CHECKPOINT) --out $(VIDEO_OUT) --max-steps $(VIDEO_MAX_STEPS)
