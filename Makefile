PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))
VIDEO_CONFIG ?= configs/fair_ppo_baseline.yaml
VIDEO_CHECKPOINT ?= outputs/fair_ppo_baseline/checkpoints/final.pt
VIDEO_OUT ?= outputs/videos/humanoid_policy.mp4
VIDEO_MAX_STEPS ?= 1000

.PHONY: install smoke ppo-baseline sac-baseline isaac-ppo-baseline isaac-ppo-v1 isaac-baseline-spec isaac-v1-spec eval single-eval curves video

install:
	$(PYTHON) -m pip install -e .

smoke:
	$(PYTHON) scripts/train_ppo_baseline.py --config configs/fair_ppo_smoke.yaml
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_smoke.yaml

ppo-baseline:
	$(PYTHON) scripts/train_ppo_baseline.py --config configs/fair_ppo_baseline.yaml

sac-baseline:
	$(PYTHON) scripts/train_sac_baseline.py --config configs/fair_sac_baseline.yaml

isaac-ppo-baseline:
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_baseline.yaml

isaac-ppo-v1:
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v1.yaml

isaac-baseline-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_baseline.yaml --out-dir outputs/isaac_ppo_baseline

isaac-v1-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v1.yaml --out-dir outputs/isaac_ppo_v1

eval: single-eval

single-eval:
	$(PYTHON) scripts/evaluate_single.py --out-dir outputs/single_eval

curves:
	$(PYTHON) scripts/plot_learning_curves.py --out-dir outputs/learning_curves

video:
	$(PYTHON) scripts/record_video.py --config $(VIDEO_CONFIG) --checkpoint $(VIDEO_CHECKPOINT) --out $(VIDEO_OUT) --max-steps $(VIDEO_MAX_STEPS)
