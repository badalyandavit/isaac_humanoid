# Experiment Protocol

Use the single-policy PPO/SAC suite as the project experiment.

## Methods

1. Single PPO baseline
2. Single SAC baseline

Both agents are trained and evaluated independently on Gymnasium/MuJoCo
`Humanoid-v5`.

## Training

Run:

```bash
make ppo-baseline
make sac-baseline
```

The main PPO config currently uses 15M environment steps. The SAC config is
kept smaller by default because this implementation updates almost every
environment step and is much slower on Humanoid.

## Evaluation

Run:

```bash
python3 scripts/evaluate_single.py \
  --episodes 20 \
  --video-episodes 1 \
  --out-dir outputs/single_eval
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

## Learning Curves

Generate learning-curve figures after or during training:

```bash
make curves
```

Include at least:

- episodic return versus environment steps
- episode length / alive duration versus environment steps
- fall rate versus environment steps when available
- action L2 norm and action smoothness
- environment steps per second
- PPO/SAC optimization metrics

## Main Table

| Method | Algorithm | Env steps | Mean return | Median return | 25% return | Fall rate |
|---|---|---:|---:|---:|---:|---:|
| Single PPO | PPO | fixed | | | | |
| Single SAC | SAC | fixed | | | | |

## Optional Isaac PPO

The repo includes separate single-agent Isaac Lab PPO variants:

```bash
make isaac-baseline-spec
make isaac-ppo-baseline
make isaac-v1-spec
make isaac-ppo-v1
```

Treat this as a simulator-backend extension. It uses
`Isaac-Humanoid-Direct-v0` and the Isaac Lab RSL-RL PPO runner, so its scores
should be reported separately from Gymnasium/MuJoCo `Humanoid-v5`.

Report the Isaac V0 baseline as:

```text
isaac_v0_official_humanoid_direct
```

This baseline keeps the official Isaac Lab direct humanoid simulator/reward:

- `dt = 1 / 120`
- control decimation `2`
- 15 second episodes
- plane terrain with static/dynamic friction `1.0`
- death when torso height is below `0.8`
- reward = progress + alive + heading + uprightness - action cost - energy cost
  - joint-limit cost, with death cost on termination

Reference: <https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/modify_direct_rl_env.html>

Report the Isaac V1 shaped-reward variant as:

```text
isaac_v1_upright_controlled_humanoid_direct
```

V1 keeps the same Isaac simulator, PPO runner, and PPO loss, but changes reward
coefficients to target the collapsed or hunched walking pattern observed in
V0:

- heading reward weight `0.5 -> 1.0`
- upright reward weight `0.1 -> 0.5`
- alive reward scale `2.0 -> 1.0`
- action cost scale `0.01 -> 0.02`
- energy cost scale `0.05 -> 0.08`
- death cost `-1.0 -> -5.0`
- termination torso height `0.8 -> 0.95`

When reporting, keep V0 and V1 as separate rows because V1 is a shaped-reward
ablation, not the official Isaac reward.
