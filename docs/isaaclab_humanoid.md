# Isaac Lab Humanoid PPO

This optional path ports the project idea to Isaac Lab without duplicating the
simulator task code. It uses Isaac Lab's registered `Isaac-Humanoid-Direct-v0`
environment and RSL-RL PPO runner.

## Why This Exists

Gymnasium/MuJoCo is simple and reproducible, but stepping many humanoid
environments is CPU/Python limited. Isaac Lab runs large vectorized simulations
on the GPU, so a single high-end GPU can step thousands of humanoids in
parallel.

## What We Inherit

From Isaac Lab:

- humanoid asset and environment registration
- vectorized GPU simulation
- direct humanoid reward/reset logic
- RSL-RL PPO implementation and checkpoint format

From this repo:

- fair aggregate budget orchestration
- independent-agent population training
- deterministic action averaging across checkpoints
- CSV/Markdown evaluation outputs

## Commands

Use an Isaac Sim/Isaac Lab compatible Python 3.11 environment.

```bash
bash runpod/setup_isaaclab_runpod.sh
make isaac-ppo-baseline
make isaac-ppo-pop
make isaac-fair-eval
```

Manual action averaging:

```bash
make isaac-ppo-eval \
  ISAAC_EVAL_CHECKPOINTS="ckpt_agent0.pt ckpt_agent1.pt ckpt_agent2.pt" \
  ISAAC_EVAL_AGGREGATOR=mean \
  ISAAC_EVAL_EPISODES=20 \
  ISAAC_EVAL_NUM_ENVS=64
```

Or call the evaluator directly with video:

```bash
/workspace/IsaacLab/isaaclab.sh -p /workspace/humanoid_population_ppo/scripts/evaluate_isaac_ppo_average.py \
  --task Isaac-Humanoid-Direct-v0 \
  --checkpoints ckpt_agent0.pt ckpt_agent1.pt ckpt_agent2.pt \
  --aggregator mean \
  --episodes 20 \
  --num_envs 64 \
  --output-dir outputs/isaac_fair_eval \
  --video \
  --headless
```

## Budget

The default configs use 15M aggregate Isaac env steps. With 4096 envs and 32
steps per PPO iteration:

```text
steps per iteration = 4096 * 32 = 131,072
baseline iterations = ceil(15,000,000 / 131,072) = 115
population per-agent iterations = ceil(5,000,000 / 131,072) = 39
```

This keeps the same fair-budget logic as the MuJoCo path, while using Isaac
Lab's faster simulator backend.
