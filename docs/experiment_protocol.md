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
bash runpod/setup_isaaclab_runpod.sh
make isaac-baseline-spec
make isaac-ppo-baseline
make isaac-v1-spec
make isaac-ppo-v1
make isaac-v2-spec
make isaac-ppo-v2
make isaac-v3-spec
make isaac-ppo-v3
make isaac-v4-spec
make isaac-ppo-v4
make isaac-v5-spec
make isaac-ppo-v5
make isaac-v6-spec
make isaac-ppo-v6
make isaac-v7-spec
make isaac-ppo-v7
make isaac-curves
make isaac-video-v0
make isaac-video-v1
make isaac-video-v2
make isaac-video-v3
make isaac-video-v4
make isaac-video-v5
make isaac-video-v6
make isaac-video-v7
make isaac-video-track-v0
make isaac-video-track-v1
make isaac-video-track-v2
make isaac-video-track-v3
make isaac-video-track-v4
make isaac-video-track-v5
make isaac-video-track-v6
make isaac-video-track-v7
```

Treat this as a simulator-backend extension. It uses
`Isaac-Humanoid-Direct-v0` and the Isaac Lab RSL-RL PPO runner, so its scores
should be reported separately from Gymnasium/MuJoCo `Humanoid-v5`.

The RunPod Isaac setup installs Isaac Sim `5.1.0` and Isaac Lab `v2.3.0` in a
Python 3.11 environment under `/workspace/isaaclab_env` so large packages do
not fill the small container overlay filesystem. On fresh Isaac-only pods, set
`ISAACLAB_USE_SYSTEM_PYTHON=1` to install into the current Python environment.
The setup preserves existing Torch package versions by default.

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

Report the Isaac V2 shaped-reward variant as:

```text
isaac_v2_mild_upright_controlled_humanoid_direct
```

V2 keeps the same Isaac simulator, PPO runner, and PPO loss. It is a softer
version of the V1 idea with a longer default budget of `200M` environment
steps:

- heading reward weight `0.5 -> 0.75`
- upright reward weight `0.1 -> 0.25`
- alive reward scale `2.0 -> 1.5`
- action cost scale `0.01 -> 0.015`
- energy cost scale `0.05 -> 0.06`
- death cost `-1.0 -> -2.0`
- termination torso height `0.8 -> 0.85`

Report V2 separately from V0/V1 because it changes both reward coefficients
and the intended training budget.

Report the Isaac V3 shaped-reward variant as:

```text
isaac_v3_tall_upright_humanoid_direct
```

V3 keeps the same Isaac simulator, PPO runner, and PPO loss. It is a stricter
upright-gait ablation motivated by V2's high-return but low crawling gait:

- heading reward weight `0.5 -> 1.0`
- upright reward weight `0.1 -> 0.75`
- alive reward scale `2.0 -> 1.2`
- action cost scale `0.01 -> 0.02`
- energy cost scale `0.05 -> 0.08`
- death cost `-1.0 -> -4.0`
- termination torso height `0.8 -> 1.0`

Report V3 separately because it intentionally trades raw reward for gait
quality.

Report the Isaac V4 custom-reward variant as:

```text
isaac_v4_morphology_reward_humanoid_direct
```

V4 registers and trains a new Isaac task id:

```text
Isaac-Humanoid-V4-Direct-v0
```

V4 keeps the Isaac simulator and RSL-RL PPO runner, but unlike V1-V3 it changes
the reward function itself. The custom task adds morphology and gait-quality
terms:

- root/torso height bonus and low-height penalty
- torso/pelvis/head low-body penalty
- arm/hand low-body penalty to discourage arm-supported crawling
- leg and arm joint pose penalties
- action-rate penalty

Report V4 as a custom-reward ablation. Its return can be lower than V2/V3
because it penalizes the high-return spider/crawling behavior.

Report the Isaac V5 custom-reward variant as:

```text
isaac_v5_anti_jump_morphology_humanoid_direct
```

V5 uses the same custom Isaac task module as V4 but removes the positive height
bonus that produced jumping. Height becomes a bounded constraint: low-height
penalty, high-height penalty, and vertical-velocity penalty. V5 keeps the
arm-low and arm-pose penalties to discourage spider/crawling locomotion.

Report V5 as the anti-jump follow-up to V4.

Report the Isaac V6 custom-reward variant as:

```text
isaac_v6_diagnostic_gait_reward_humanoid_direct
```

V6 uses the same custom Isaac task module as V4/V5. It adds reward-term
diagnostics under `custom/*`, arm action and velocity penalties, leg symmetry
penalties, non-foot low-body penalties, and foot-air/foot-slip proxy penalties.
The foot terms are proxies based on body height and foot velocity because this
direct humanoid task does not define explicit contact sensors.

Report V6 as the diagnostic gait-quality follow-up to V5.

Report the Isaac V7 custom-reward variant as:

```text
isaac_v7_contact_gait_reward_humanoid_direct
```

V7 uses the same custom Isaac task module as V4/V5/V6, but it moves from
generic anti-crawl penalties to gait-structure shaping. It adds target
forward-velocity reward, lateral drift penalty, a low-speed vertical-bounce
penalty, an arm-high penalty for the V6 overhead-arm exploit, and foot-contact
terms for single-foot support, foot switching, no-contact, double-contact, and
left/right foot-contact balance. It uses Isaac body contact forces when
available and falls back to foot-height contact proxies otherwise.

Report V7 as the contact/gait follow-up to V6.

The Isaac video targets use the checkpoint saved in each training manifest and
copy the recorded MP4s to:

```text
outputs/videos/isaac_v0_policy.mp4
outputs/videos/isaac_v1_policy.mp4
outputs/videos/isaac_v2_policy.mp4
outputs/videos/isaac_v3_policy.mp4
outputs/videos/isaac_v4_policy.mp4
outputs/videos/isaac_v5_policy.mp4
outputs/videos/isaac_v6_policy.mp4
outputs/videos/isaac_v7_policy.mp4
outputs/videos/isaac_v0_policy_tracked.mp4
outputs/videos/isaac_v1_policy_tracked.mp4
outputs/videos/isaac_v2_policy_tracked.mp4
outputs/videos/isaac_v3_policy_tracked.mp4
outputs/videos/isaac_v4_policy_tracked.mp4
outputs/videos/isaac_v5_policy_tracked.mp4
outputs/videos/isaac_v6_policy_tracked.mp4
outputs/videos/isaac_v7_policy_tracked.mp4
```

These targets use Isaac Lab's RSL-RL `play.py --video` flow, so `ffmpeg` must
be available in the Isaac environment. The untracked videos preserve Isaac
Lab's default fixed camera. The `isaac-video-track-*` targets patch a temporary
copy of Isaac Lab's play script at runtime and update the viewer camera from
the env-0 torso position; use them for presentation clips when the policy moves
out of the default frame.

Isaac learning curves are exported from TensorBoard event files in
`/workspace/IsaacLab/logs/rsl_rl/humanoid_direct/` to:

```text
outputs/isaac_learning_curves/
  isaac_scalars.csv
  report.md
  *.png
```
