# Humanoid PPO/SAC Action Averaging

PyTorch implementations for a fair `Humanoid-v5` RL course-project comparison:

1. **Single PPO baseline**
2. **Single SAC baseline**
3. **Independent PPO agents with deterministic action averaging at evaluation**
4. **Independent SAC agents with deterministic action averaging at evaluation**

The main project path uses fair aggregate environment-step budgets. Population
configs default to:

```text
per-agent steps = total_timesteps / num_train_agents
```

No actions or parameters are averaged during PPO/SAC training in the main fair
experiments. Agents are trained independently with different seeds, then their
deterministic mean actions are aggregated during evaluation.

## Repository Layout

```text
configs/
  fair_ppo_baseline.yaml
  fair_ppo_smoke.yaml
  fair_ppo_population.yaml
  fair_ppo_population_smoke.yaml
  fair_sac_baseline.yaml
  fair_sac_smoke.yaml
  fair_sac_population.yaml
  population_average_parameters.yaml
scripts/
  train_ppo_baseline.py
  train_sac_baseline.py
  train_ppo_population.py
  train_sac_population.py
  train_average_parameters.py
  evaluate_fair.py
  record_video.py
src/humanoid_rl/
  averaging.py
  config.py
  envs.py
  models.py
  ppo.py
  replay.py
  rollout.py
  sac.py
  utils.py
```

`train_average_parameters.py` is a legacy ablation for parameter averaging. It is
not part of the main fair PPO/SAC comparison.

## Install On RunPod

```bash
bash runpod/setup_runpod.sh
```

The setup script preserves the Torch version already installed in the RunPod
image by default.

## Smoke Test

```bash
make smoke
```

This runs small PPO, SAC, and independent PPO-population jobs. It is only a
sanity check; it is not meant to solve Humanoid.

## Train Fair Experiments

```bash
make ppo-baseline
```

```bash
make sac-baseline
```

```bash
make ppo-pop
```

```bash
make sac-pop
```

Outputs are written under:

```text
outputs/fair_ppo_baseline/
outputs/fair_sac_baseline/
outputs/fair_ppo_population/
outputs/fair_sac_population/
```

Population training writes a `manifest.json` listing the trained checkpoints.

## Evaluate

Use `evaluate_fair.py` as the canonical evaluator. It replaces the old
single-checkpoint evaluator and the old dataset collector.

```bash
make fair-eval
```

More complete evaluation:

```bash
python3 scripts/evaluate_fair.py \
  --num-average-agents 2,3 \
  --aggregators mean,median,trimmed_mean \
  --episodes 20 \
  --video-episodes 1
```

Outputs:

```text
outputs/fair_eval/
  episodes.csv
  summary.csv
  summary.md
  videos/
```

Evaluation is deterministic where possible:

- PPO uses the Gaussian mean action.
- SAC uses the actor mean action after tanh squashing.
- Population methods average deterministic actions, not sampled stochastic actions.
- `K=1` is reported by the single-agent PPO/SAC baselines, so population
  action averaging starts at `K=2`. The default configs train 3 agents and
  evaluate `K=2,3`.

## Video

Render the PPO baseline:

```bash
make video
```

Render a specific PPO checkpoint:

```bash
make video \
  VIDEO_CONFIG=configs/fair_ppo_baseline.yaml \
  VIDEO_CHECKPOINT=outputs/fair_ppo_baseline/checkpoints/final.pt \
  VIDEO_OUT=outputs/videos/ppo_baseline.mp4
```

For SAC or action-averaged population videos, prefer:

```bash
python3 scripts/evaluate_fair.py --video-episodes 1
```

The video path defaults to EGL rendering on headless Linux.

## Metrics

Training and evaluation log:

- episodic return
- episode length / alive duration
- fall rate
- forward reward when exposed by the environment info dict
- control reward/cost when exposed by the environment info dict
- action L2 norm
- action smoothness
- wall-clock time
- environment steps per second
- total environment steps
- number of trained agents used
- aggregation method

## Notes

- PPO is implemented directly in PyTorch with GAE, clipped policy objective,
  value loss, entropy bonus, advantage normalization, minibatch SGD, rollout
  storage, observation normalization, action clipping, and gradient clipping.
- SAC is implemented directly in PyTorch with replay buffer, tanh-squashed
  Gaussian actor, twin Q critics, target networks, entropy temperature alpha,
  automatic alpha tuning, observation normalization, action squashing, reward
  scaling, and gradient clipping.
- Normalization statistics are saved in checkpoints.
- The failed exploratory orchestration and worker-count sweep code were removed
  because they are not part of the final course-project method.
