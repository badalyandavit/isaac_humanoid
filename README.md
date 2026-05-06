# Humanoid Population PPO

End-to-end PyTorch PPO training for `Humanoid-v5` with three experimental modes:

1. **Baseline PPO**: one PPO learner with vectorized MuJoCo environments.
2. **Naive Average PPO**: `N` PPO workers trained in parallel branches, periodically averaged by parameter averaging.
3. **Robust Heavy-Tail Cooperative PPO**: `N` PPO workers trained as a population. A message-passing orchestrator evaluates each worker with robust heavy-tail metrics, promotes strong workers, clones into weak workers, mutates hyperparameters, and logs scaling behavior as `N` increases.

The intended research question is:

> When Humanoid PPO outcomes are heavy-tailed across seeds/workers, does robust communication and promotion outperform naive averaging and independent PPO?

The repo also includes a fair-budget PPO/SAC baseline suite where population
methods train independent agents and average deterministic actions only during
evaluation. This is the recommended path for a course-project comparison.

## Repository layout

```text
configs/
  baseline_ppo.yaml
  baseline_smoke.yaml
  fair_ppo_baseline.yaml
  fair_ppo_population.yaml
  fair_sac_baseline.yaml
  fair_sac_population.yaml
  population_average.yaml
  population_heavytail.yaml
  population_heavytail_smoke.yaml
  scaling_sweep.yaml
runpod/
  setup_runpod.sh
  train_baseline_runpod.sh
  train_average_runpod.sh
  train_heavytail_runpod.sh
  tmux_launch.sh
scripts/
  train_baseline.py
  train_average.py
  train_heavytail.py
  sweep_scaling.py
  collect_eval_dataset.py
  analyze_results.py
  evaluate_fair.py
  evaluate.py
  record_video.py
  train_ppo_population.py
  train_sac_baseline.py
  train_sac_population.py
src/humanoid_rl/
  config.py
  envs.py
  metrics.py
  models.py
  ppo.py
  rollout.py
  utils.py
  population/
    averaging.py
    graphs.py
    orchestrator.py
```

## Install on RunPod

From the repo root:

```bash
bash runpod/setup_runpod.sh
```

The setup script preserves the Torch version already installed in the RunPod image by default. Set `KEEP_RUNPOD_TORCH=0` only if you intentionally want pip to resolve Torch again.

```bash
KEEP_RUNPOD_TORCH=0 bash runpod/setup_runpod.sh
```

## Smoke test

```bash
make smoke
```

This verifies that MuJoCo, Gymnasium, Torch, vectorized environments, PPO updates,
SAC updates, independent PPO population training, evaluation, and heavy-tail
orchestration all run. It is not meant to solve Humanoid.

## Fair PPO/SAC Experiment Suite

This is the course-project comparison path. It uses the same aggregate
environment-step budget for single-agent and population methods by default.
For the population configs, `budget_mode: aggregate` means:

```text
per-agent steps = total_timesteps / num_train_agents
```

Train the four methods:

```bash
make fair-ppo
make fair-sac
make fair-ppo-pop
make fair-sac-pop
```

Evaluate deterministic single policies and deterministic action averages:

```bash
make fair-eval
```

The evaluator supports K values and robust aggregators:

```bash
python scripts/evaluate_fair.py \
  --num-average-agents 1,2,4,8 \
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

The fair population methods do not average weights or actions during training.
They train independent PPO/SAC agents with different seeds and only average
deterministic mean actions during evaluation.

## Train baseline PPO

```bash
python scripts/train_baseline.py --config configs/baseline_ppo.yaml
```

Outputs:

```text
outputs/baseline_humanoid_v5/
  baseline_train.csv
  checkpoints/
  tb/
```

TensorBoard:

```bash
tensorboard --logdir outputs/baseline_humanoid_v5/tb --host 0.0.0.0 --port 6006
```

## Train naive averaged population PPO

```bash
python scripts/train_average.py --config configs/population_average.yaml
```

This trains `N` PPO workers, evaluates each worker, averages their policy parameters every configured number of rounds, and logs whether naive averaging helps or destroys useful gait branches.

## Train robust heavy-tail cooperative population PPO

```bash
python scripts/train_heavytail.py --config configs/population_heavytail.yaml
```

The orchestrator uses robust scores instead of mean return:

```text
score = q_low_return + median_weight * median_return
        - fall_penalty * fall_rate
        - energy_penalty * abs(mean_ctrl_reward)
```

Each round:

1. Every worker performs PPO updates on its own vectorized Humanoid environments.
2. Every worker is evaluated for multiple episodes.
3. Workers send messages over a communication graph with `graph_gamma`-hop visibility.
4. Weak unprotected workers can be replaced by stronger neighbors if the robust margin is large enough.
5. Cloned policies are mutated through learning-rate, entropy-coefficient, and small policy-noise perturbations.

Logs:

```text
outputs/heavytail_population_humanoid_v5/
  heavytail_rounds.csv
  heavytail_clone_events.csv
  communication_graph.json
  worker_0/
  worker_1/
  ...
  checkpoints/
```

## Scaling sweep over number of workers

```bash
python scripts/sweep_scaling.py \
  --config configs/scaling_sweep.yaml \
  --agents 1,2,4,8
```

The output file is:

```text
outputs/scaling_humanoid_v5/scaling_summary.csv
```

## Collect evaluation data

After training the baseline, naive average, and heavy-tail runs, collect normalized
checkpoint evaluation data with:

```bash
make collect-data
```

This evaluates the final checkpoint for each configured method and writes:

```text
outputs/eval_dataset.csv
outputs/eval_summary.csv
```

Use `--include-intermediate` with `scripts/collect_eval_dataset.py` to evaluate all
checkpoints in each run's `checkpoints/` directory.

## Analyze outputs

Summarize training logs, collected evaluations, and scaling results with:

```bash
make analyze
```

This writes analysis tables and a short Markdown report under:

```text
outputs/analysis/
```

Useful scaling plots to make later:

```text
N workers vs best robust score
N workers vs median robust score
N workers vs clone rate
N workers vs wall-clock time
N workers vs environment steps to threshold
```

## Run inside tmux on RunPod

```bash
bash runpod/tmux_launch.sh humanoid_ht "bash runpod/train_heavytail_runpod.sh"
tmux attach -t humanoid_ht
```

## Evaluate a checkpoint

```bash
python scripts/evaluate.py \
  --config configs/baseline_ppo.yaml \
  --checkpoint outputs/baseline_humanoid_v5/checkpoints/final.pt \
  --episodes 20
```

## Record video

```bash
python scripts/record_video.py \
  --config configs/baseline_ppo.yaml \
  --checkpoint outputs/baseline_humanoid_v5/checkpoints/final.pt \
  --out outputs/videos/humanoid_policy.mp4
```

## Main experiment table

Recommended first table:

| Method | N | Env steps | Best mean return | Median return | 25% return | Fall rate | Wall-clock | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Baseline PPO | 1 | fixed | | | | | | |
| Independent best-of-N | N | fixed | | | | | | no sharing |
| Naive average PPO | N | fixed | | | | | | weight averaging |
| Robust cooperative PPO | N | fixed | | | | | | message passing + robust promotion |

## Notes on GPU usage

Gymnasium MuJoCo physics is CPU simulation. The GPU is used for the actor-critic forward/backward passes and PPO updates. For true GPU physics, porting the environment layer to Isaac Lab would be the next step, but this repo intentionally keeps the first version runnable on standard RunPod PyTorch images with MuJoCo.

## Design choices

- PPO is implemented directly in PyTorch, not hidden behind Stable-Baselines3.
- The averaged-population baseline uses real parameter averaging, which is intentionally naive and often brittle.
- The heavy-tail method does not average policies. It performs robust evaluation, communication, cloning, mutation, and protection of top workers.
- The orchestrator supports `complete`, `ring`, `line`, and `star` communication graphs.
- Evaluation tracks mean, median, lower quantile, fall rate, episode length, control reward, and a simple Hill tail-index diagnostic.
