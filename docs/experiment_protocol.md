# Experiment Protocol

Use the single-policy PPO/SAC suite as the main course-project experiment, and
report Isaac Lab PPO as a separate simulator-backend extension.

## Main Methods

1. Single PPO baseline
2. Single SAC baseline

Both agents are trained and evaluated independently on Gymnasium/MuJoCo
`Humanoid-v5`.

## MuJoCo Training

Run:

```bash
make ppo-baseline
make sac-baseline
```

The main PPO config currently uses 15M environment steps. The SAC config is
kept smaller by default because this implementation updates almost every
environment step and is much slower on Humanoid.

## MuJoCo Evaluation

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

## MuJoCo Learning Curves

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

## Isaac PPO Extension

The repo keeps only the reportable Isaac milestones:

```bash
bash runpod/setup_isaaclab_runpod.sh
make isaac-baseline-spec
make isaac-ppo-baseline
make isaac-v1-spec
make isaac-ppo-v1
make isaac-v4-spec
make isaac-ppo-v4
make isaac-v9-spec
make isaac-ppo-v9
make isaac-v14-spec
make isaac-ppo-v14
make isaac-v16-spec
make isaac-ppo-v16
make isaac-curves
```

Treat Isaac results as a simulator-backend extension. Isaac uses the Isaac Lab
humanoid direct task and RSL-RL PPO runner, so its scores should be reported
separately from Gymnasium/MuJoCo `Humanoid-v5`.

The RunPod Isaac setup installs Isaac Sim `5.1.0` and Isaac Lab `v2.3.0` in a
Python 3.11 environment under `/workspace/isaaclab_env` so large packages do
not fill the small container overlay filesystem. On fresh Isaac-only pods, set
`ISAACLAB_USE_SYSTEM_PYTHON=1` to install into the current Python environment.
The setup preserves existing Torch package versions by default.

## Isaac Milestones

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

Report the Isaac V4 custom-reward milestone as:

```text
isaac_v4_morphology_reward_humanoid_direct
```

V4 registers and trains:

```text
Isaac-Humanoid-V4-Direct-v0
```

V4 keeps the Isaac simulator and RSL-RL PPO runner, but changes the reward
function itself. The custom task adds morphology and gait-quality terms:

- root/torso height bonus and low-height penalty
- torso/pelvis/head low-body penalty
- arm/hand low-body penalty to discourage arm-supported crawling
- leg and arm joint pose penalties
- action-rate penalty

Report the Isaac V9 curriculum-gait milestone as:

```text
isaac_v9_curriculum_gait_reward_humanoid_direct
```

V9 registers:

```text
Isaac-Humanoid-V9-Direct-v0
```

V9 is the first kept milestone after the early custom-reward failures. It
keeps the V4 task module and adds gait curriculum shaping, forward-speed
tracking, slip control, and softer contact-balance terms to avoid short reset
loops.

Report the Isaac V14 cadence-gait milestone as:

```text
isaac_v14_cadence_gait_reward_humanoid_direct
```

V14 registers:

```text
Isaac-Humanoid-V14-Direct-v0
```

V14 targets grounded shuffle and one-foot dominance with soft foot-dominance
switch rewards, overlong same-foot stance penalties, underused-foot contact
reward, relaxed swing constraints, and moderate arm penalties.

Report the Isaac V16 stable-lower-arms milestone as:

```text
isaac_v16_stable_lower_arms_gait_reward_humanoid_direct
```

V16 registers:

```text
Isaac-Humanoid-V16-Direct-v0
```

V16 keeps V14 as the stable base and adds only moderate arm-down and
cadence-balance pressure. It prioritizes full-episode stability before further
arm/gait polishing.

## Isaac Videos

Record tracked-camera milestone videos with:

```bash
make isaac-video-track-v0
make isaac-video-track-v1
make isaac-video-track-v4
make isaac-video-track-v9
make isaac-video-track-v14
make isaac-video-track-v16
```

The video targets use the checkpoint saved in each training manifest and copy
the recorded MP4s to:

```text
outputs/videos/isaac_v0_policy_tracked.mp4
outputs/videos/isaac_v1_policy_tracked.mp4
outputs/videos/isaac_v4_policy_tracked.mp4
outputs/videos/isaac_v9_policy_tracked.mp4
outputs/videos/isaac_v14_policy_tracked.mp4
outputs/videos/isaac_v16_policy_tracked.mp4
```

The `isaac-video-track-*` targets patch a temporary copy of Isaac Lab's play
script at runtime and update the viewer camera from the env-0 torso position.
Use them for presentation clips when the policy moves out of the default frame.

## Isaac Learning Curves

Isaac learning curves are exported from TensorBoard event files in
`/workspace/IsaacLab/logs/rsl_rl/humanoid_direct/` to:

```text
outputs/isaac_learning_curves/
  isaac_scalars.csv
  report.md
  *.png
```

By default, `make isaac-curves` includes only the kept milestones. Use
`--include-all-runs` only for private debugging when you need the pruned
intermediate runs that may still exist on a RunPod disk.
