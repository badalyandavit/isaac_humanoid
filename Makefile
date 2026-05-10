PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))
VIDEO_CONFIG ?= configs/fair_ppo_baseline.yaml
VIDEO_CHECKPOINT ?= outputs/fair_ppo_baseline/checkpoints/final.pt
VIDEO_OUT ?= outputs/videos/humanoid_policy.mp4
VIDEO_MAX_STEPS ?= 1000
ISAAC_VIDEO_CONFIG ?= configs/isaac_ppo_baseline.yaml
ISAAC_VIDEO_CHECKPOINT ?=
ISAAC_VIDEO_CHECKPOINT_ARG := $(if $(ISAAC_VIDEO_CHECKPOINT),--checkpoint $(ISAAC_VIDEO_CHECKPOINT),)
ISAAC_VIDEO_OUT ?= outputs/videos/isaac_policy.mp4
ISAAC_VIDEO_MAX_STEPS ?= 500
ISAAC_VIDEO_NUM_ENVS ?= 1

.PHONY: install smoke ppo-baseline sac-baseline isaac-ppo-baseline isaac-ppo-v1 isaac-ppo-v4 isaac-ppo-v9 isaac-ppo-v14 isaac-ppo-v16 isaac-ppo-v17 isaac-baseline-spec isaac-v1-spec isaac-v4-spec isaac-v9-spec isaac-v14-spec isaac-v16-spec isaac-v17-spec isaac-v4-install eval single-eval curves isaac-curves video isaac-video isaac-video-v0 isaac-video-v1 isaac-video-v4 isaac-video-v9 isaac-video-v14 isaac-video-v16 isaac-video-v17 isaac-video-track isaac-video-track-v0 isaac-video-track-v1 isaac-video-track-v4 isaac-video-track-v9 isaac-video-track-v14 isaac-video-track-v16 isaac-video-track-v17

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

isaac-v4-install:
	$(PYTHON) scripts/install_isaac_v4_task.py --config configs/isaac_ppo_v4.yaml

isaac-ppo-v4: isaac-v4-install
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v4.yaml

isaac-ppo-v9: isaac-v4-install
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v9.yaml

isaac-ppo-v14: isaac-v4-install
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v14.yaml

isaac-ppo-v16: isaac-v4-install
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v16.yaml

isaac-ppo-v17: isaac-v4-install
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_v17.yaml

isaac-baseline-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_baseline.yaml --out-dir outputs/isaac_ppo_baseline

isaac-v1-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v1.yaml --out-dir outputs/isaac_ppo_v1

isaac-v4-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v4.yaml --out-dir outputs/isaac_ppo_v4

isaac-v9-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v9.yaml --out-dir outputs/isaac_ppo_v9

isaac-v14-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v14.yaml --out-dir outputs/isaac_ppo_v14

isaac-v16-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v16.yaml --out-dir outputs/isaac_ppo_v16

isaac-v17-spec:
	$(PYTHON) scripts/write_isaac_baseline_spec.py --config configs/isaac_ppo_v17.yaml --out-dir outputs/isaac_ppo_v17

eval: single-eval

single-eval:
	$(PYTHON) scripts/evaluate_single.py --out-dir outputs/single_eval

curves:
	$(PYTHON) scripts/plot_learning_curves.py --out-dir outputs/learning_curves

isaac-curves:
	$(PYTHON) scripts/plot_isaac_learning_curves.py --out-dir outputs/isaac_learning_curves

video:
	$(PYTHON) scripts/record_video.py --config $(VIDEO_CONFIG) --checkpoint $(VIDEO_CHECKPOINT) --out $(VIDEO_OUT) --max-steps $(VIDEO_MAX_STEPS)

isaac-video:
	$(PYTHON) scripts/record_isaac_video.py --config $(ISAAC_VIDEO_CONFIG) $(ISAAC_VIDEO_CHECKPOINT_ARG) --out $(ISAAC_VIDEO_OUT) --num-envs $(ISAAC_VIDEO_NUM_ENVS) --video-length $(ISAAC_VIDEO_MAX_STEPS)

isaac-video-v0:
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_baseline.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v0_policy.mp4

isaac-video-v1:
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v1.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v1_policy.mp4

isaac-video-v4: isaac-v4-install
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v4.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v4_policy.mp4

isaac-video-v9: isaac-v4-install
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v9.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v9_policy.mp4

isaac-video-v14: isaac-v4-install
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v14.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v14_policy.mp4

isaac-video-v16: isaac-v4-install
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v16.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v16_policy.mp4

isaac-video-v17: isaac-v4-install
	$(MAKE) isaac-video ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v17.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v17_policy.mp4

isaac-video-track:
	$(PYTHON) scripts/record_isaac_tracking_video.py --config $(ISAAC_VIDEO_CONFIG) $(ISAAC_VIDEO_CHECKPOINT_ARG) --out $(ISAAC_VIDEO_OUT) --num-envs $(ISAAC_VIDEO_NUM_ENVS) --video-length $(ISAAC_VIDEO_MAX_STEPS)

isaac-video-track-v0:
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_baseline.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v0_policy_tracked.mp4

isaac-video-track-v1:
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v1.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v1_policy_tracked.mp4

isaac-video-track-v4: isaac-v4-install
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v4.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v4_policy_tracked.mp4

isaac-video-track-v9: isaac-v4-install
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v9.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v9_policy_tracked.mp4

isaac-video-track-v14: isaac-v4-install
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v14.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v14_policy_tracked.mp4

isaac-video-track-v16: isaac-v4-install
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v16.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v16_policy_tracked.mp4

isaac-video-track-v17: isaac-v4-install
	$(MAKE) isaac-video-track ISAAC_VIDEO_CONFIG=configs/isaac_ppo_v17.yaml ISAAC_VIDEO_OUT=outputs/videos/isaac_v17_policy_tracked.mp4
