# Experiment Protocol

Use the fair PPO/SAC suite as the main project experiment.

## Methods

1. Single PPO baseline
2. Single SAC baseline
3. PPO independent-agent population with deterministic action averaging at evaluation
4. SAC independent-agent population with deterministic action averaging at evaluation

The population methods do not average parameters or actions during training.
They train independent agents with different seeds. Evaluation loads the first
`K` trained agents and aggregates deterministic mean actions.

## Budget

Use `budget_mode: aggregate` for the main comparison:

```text
per-agent train steps = total_timesteps / num_train_agents
```

This keeps aggregate environment interaction comparable with the single-agent
baselines.

## Evaluation

Run:

```bash
python3 scripts/evaluate_fair.py \
  --num-average-agents 2,3 \
  --aggregators mean,median,trimmed_mean \
  --episodes 20 \
  --video-episodes 1
```

Report:

- mean return
- median return
- 25% return
- episode length / alive duration
- fall rate
- action L2 norm
- action smoothness
- total environment steps
- number of agents used
- aggregation method

## Main Table

| Method | Algorithm | K | Aggregate env steps | Mean return | Median return | 25% return | Fall rate |
|---|---|---:|---:|---:|---:|---:|---:|
| Single PPO | PPO | 1 | fixed | | | | |
| Single SAC | SAC | 1 | fixed | | | | |
| PPO action average | PPO | 2,3 | fixed | | | | |
| SAC action average | SAC | 2,3 | fixed | | | | |
