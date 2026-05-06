# Experiment protocol

## Hypothesis

Humanoid PPO training has heavy-tailed outcomes across random seeds and population branches. Therefore, naive averaging can underperform robust orchestration because it destroys incompatible gait modes and lets outlier returns dominate selection.

## Methods

### Baseline PPO

A single PPO learner with vectorized Humanoid environments.

### Naive Average PPO

`N` PPO learners train independently for one round. After evaluation, their parameters are averaged and broadcast back to all workers. This is a deliberately simple population baseline.

### Robust Cooperative Heavy-Tail PPO

Each worker is treated as an agent on a communication graph. The graph can be complete, ring, line, or star. During each orchestration round, each worker sends a compact message:

```text
worker_id, robust_score, evaluation_distribution, policy_state, learning_rate, entropy_coef
```

Visible messages are restricted to the `graph_gamma`-hop neighborhood. The orchestrator protects the top fraction of workers and replaces weak workers only if a visible neighbor beats them by a robust margin.

## Robust score

```text
score = q25_return + median_weight * median_return
        - fall_penalty * fall_rate
        - energy_penalty * abs(mean_ctrl_reward)
```

This intentionally punishes fragile policies that sometimes get high return but often fall early.

## Scaling-law study

Run:

```bash
python scripts/sweep_scaling.py --config configs/scaling_sweep.yaml --agents 1,2,4,8
```

Suggested dependent variables:

- best robust score after fixed total environment steps
- median robust score across workers
- environment steps to pass a threshold
- clone events per round
- wall-clock time
- robustness gap: mean return minus q25 return

## Fairness notes

For strict budget fairness, compare methods using the same total environment interactions. If `N` workers each use `S` steps per round, either divide per-worker steps by `N` or report both per-worker and total population steps.
