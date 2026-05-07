PYTHON ?= python3
export PYTHONPATH := src$(if $(PYTHONPATH),:$(PYTHONPATH))
VIDEO_CONFIG ?= configs/fair_ppo_baseline.yaml
VIDEO_CHECKPOINT ?= outputs/fair_ppo_baseline/checkpoints/final.pt
VIDEO_OUT ?= outputs/videos/humanoid_policy.mp4
VIDEO_MAX_STEPS ?= 1000
ISAACLAB_DIR ?= /workspace/IsaacLab
ISAAC_EVAL_CHECKPOINTS ?=
ISAAC_EVAL_EPISODES ?= 20
ISAAC_EVAL_NUM_ENVS ?= 64
ISAAC_EVAL_AGGREGATOR ?= mean
ISAAC_EVAL_OUT ?= outputs/isaac_fair_eval

.PHONY: install smoke ppo-baseline sac-baseline ppo-pop sac-pop fair-eval average-parameters video isaac-ppo-baseline isaac-ppo-pop isaac-fair-eval isaac-ppo-eval

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

isaac-ppo-baseline:
	$(PYTHON) scripts/train_isaac_ppo_baseline.py --config configs/isaac_ppo_baseline.yaml

isaac-ppo-pop:
	$(PYTHON) scripts/train_isaac_ppo_population.py --config configs/isaac_ppo_population.yaml

isaac-fair-eval:
	$(PYTHON) scripts/evaluate_isaac_fair.py \
		--isaaclab-dir $(ISAACLAB_DIR) \
		--aggregators $(ISAAC_EVAL_AGGREGATOR) \
		--episodes $(ISAAC_EVAL_EPISODES) \
		--num-envs $(ISAAC_EVAL_NUM_ENVS) \
		--output-dir $(ISAAC_EVAL_OUT)

isaac-ppo-eval:
	@test -n "$(ISAAC_EVAL_CHECKPOINTS)" || (echo "Set ISAAC_EVAL_CHECKPOINTS='ckpt1.pt ckpt2.pt ...'"; exit 1)
	$(ISAACLAB_DIR)/isaaclab.sh -p $(CURDIR)/scripts/evaluate_isaac_ppo_average.py \
		--task Isaac-Humanoid-Direct-v0 \
		--checkpoints $(ISAAC_EVAL_CHECKPOINTS) \
		--aggregator $(ISAAC_EVAL_AGGREGATOR) \
		--episodes $(ISAAC_EVAL_EPISODES) \
		--num_envs $(ISAAC_EVAL_NUM_ENVS) \
		--output-dir $(ISAAC_EVAL_OUT) \
		--headless
