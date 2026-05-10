# Humanoid PPO/SAC Baselines

PyTorch implementations for single-policy PPO and SAC on Gymnasium/MuJoCo
`Humanoid-v5`, plus milestone Isaac Lab PPO variants for the humanoid walking
reward work.

The current project path is intentionally single-agent:

1. **Single PPO baseline**
2. **Single SAC baseline**
3. **Single-agent Isaac Lab PPO milestones**

There is no population training, parameter averaging, or action averaging in
the current repo.

## Repository Layout

```text
configs/
  fair_ppo_baseline.yaml
  fair_ppo_smoke.yaml
  fair_sac_baseline.yaml
  fair_sac_smoke.yaml
  isaac_ppo_baseline.yaml
  isaac_ppo_v1.yaml
  isaac_ppo_v4.yaml
  isaac_ppo_v9.yaml
  isaac_ppo_v14.yaml
  isaac_ppo_v16.yaml
  isaac_ppo_v17.yaml
  isaac_ppo_v18.yaml
scripts/
  train_ppo_baseline.py
  train_sac_baseline.py
  train_isaac_ppo_baseline.py
  install_isaac_v4_task.py
  write_isaac_baseline_spec.py
  record_isaac_video.py
  record_isaac_tracking_video.py
  plot_isaac_learning_curves.py
  evaluate_single.py
  plot_learning_curves.py
  record_video.py
src/humanoid_rl/
  config.py
  envs.py
  isaaclab.py
  isaac_tasks/
  models.py
  ppo.py
  replay.py
  rollout.py
  sac.py
  utils.py
```

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

This runs small PPO and SAC jobs. It is only a sanity check; it is not meant to
solve Humanoid.

## Train MuJoCo Baselines

Train PPO:

```bash
make ppo-baseline
```

Train SAC:

```bash
make sac-baseline
```

Outputs are written under:

```text
outputs/fair_ppo_baseline/
outputs/fair_sac_baseline/
```

## Isaac PPO Milestones

These are single-agent Isaac Lab PPO variants. They are not population methods
and are not directly comparable to Gymnasium/MuJoCo `Humanoid-v5`, because they
use Isaac Lab's humanoid direct task and the RSL-RL PPO runner.

The kept milestone variants are:

- **V0**: `isaac_v0_official_humanoid_direct`
- **V1**: `isaac_v1_upright_controlled_humanoid_direct`
- **V4**: `isaac_v4_morphology_reward_humanoid_direct`
- **V9**: `isaac_v9_curriculum_gait_reward_humanoid_direct`
- **V14**: `isaac_v14_cadence_gait_reward_humanoid_direct`
- **V16**: `isaac_v16_stable_lower_arms_gait_reward_humanoid_direct`
- **V17**: `isaac_v17_final_stable_walk_humanoid_direct`
- **V18**: `isaac_v18_final_polished_walk_humanoid_direct`

Intermediate tuning branches V2, V3, V5-V8, V10-V13, and V15 were pruned from
the tracked repo to keep the history focused on reportable milestones.

### V0 Official Isaac Baseline

V0 uses the official Isaac Lab direct humanoid simulator and reward:

- simulator timestep `dt = 1 / 120`
- control decimation `2`
- plane terrain with static/dynamic friction `1.0`
- 21-dimensional continuous action space
- 75-dimensional policy observation space
- episode length `15s`
- termination when torso height is below `0.8`
- reward terms for progress, alive bonus, heading alignment, uprightness,
  action cost, energy cost, joint-limit cost, and death cost

Reference: <https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/modify_direct_rl_env.html>

### V1 Upright Reward

V1 keeps the same Isaac simulator, robot, physics timestep, action space,
RSL-RL PPO runner, and PPO loss as V0. It changes reward coefficients only:

- heading reward weight `0.5 -> 1.0`
- upright reward weight `0.1 -> 0.5`
- alive reward scale `2.0 -> 1.0`
- action cost scale `0.01 -> 0.02`
- energy cost scale `0.05 -> 0.08`
- death cost `-1.0 -> -5.0`
- termination torso height `0.8 -> 0.95`

The intent is to reduce the hunched/collapsed walking pattern seen in V0 by
rewarding upright forward alignment more strongly and penalizing thrashy or
collapsed locomotion earlier.

### V4 Morphology Reward

V4 registers the custom Isaac task id:

```text
Isaac-Humanoid-V4-Direct-v0
```

Unlike V1, V4 is not only a coefficient sweep. It installs a small custom
Isaac Lab task module into the Isaac Lab checkout and adds explicit
gait-quality terms:

- root/torso height bonus and low-height penalty
- torso/pelvis/head low-body penalty
- arm/hand low-body penalty as a proxy for arm-supported crawling
- leg joint pose penalty to discourage deep crouch
- arm joint pose penalty to discourage arm-driven locomotion
- action-rate penalty for smoother motion

The intent is to address policies that get high survival reward while moving
in a low spider-like crouch.

### V9 Curriculum Gait Reward

V9 registers:

```text
Isaac-Humanoid-V9-Direct-v0
```

It keeps the V4 custom task path and adds a curriculum over gait-shaping terms:

- permissive survival envelope
- forward-speed cap and slip control
- contact/gait shaping ramped from partial to full strength early in training
- soft single-support and mild foot-height-difference rewards
- reduced hard contact-balance pressure versus failed intermediate variants

The intent is to move from "stay upright" toward an actual alternating gait
without collapsing into short reset loops.

### V14 Cadence Gait Reward

V14 registers:

```text
Isaac-Humanoid-V14-Direct-v0
```

It focuses on the grounded-shuffle failure mode:

- soft foot-dominance switch reward for left/right support changes
- overlong same-foot stance penalty
- underused-foot contact reward
- relaxed air-time and foot-height limits so a real swing step remains possible
- moderate arm pose/action/height penalties to reduce raised-arm balancing

The intent is to turn contact balance into an active gait objective rather than
just a survival constraint.

### V16 Stable Lower-Arms Reward

V16 registers:

```text
Isaac-Humanoid-V16-Direct-v0
```

V16 uses V14 as the stable base and avoids the V15 collapse:

- moderate arm-down pressure, stronger than V14 but weaker than V15
- mild cadence-balance increase without excessive stance-duration pressure
- V14-like foot-air-time control to avoid long-airtime one-sided support
- full-episode stability prioritized before further arm/gait polishing

### V17 Final Stable-Walk Reward

V17 registers:

```text
Isaac-Humanoid-V17-Direct-v0
```

V17 is the final conservative tune from the V16 evaluation. V16 still leaned
low, kept one arm near the head, and showed too much no-foot airtime. V17:

- restores V14's taller root-height target and stronger low-height pressure
- keeps lower-arm pressure moderate so it does not repeat the V15 collapse
- strengthens no-foot-contact, foot-airtime, and high-swing penalties
- keeps one-foot rewards small to discourage airborne gliding
- slightly strengthens cadence and underused-foot terms for left/right balance
- extends training to `300M` environment steps

### V18 Final Polished-Walk Reward

V18 registers:

```text
Isaac-Humanoid-V18-Direct-v0
```

V18 is the final polish pass on V17. It keeps the same custom task and PPO loss,
but makes small reward-weight changes aimed at the remaining V17 issues:

- stronger arm-high, arm-neutral-height, arm-action, and arm-velocity pressure
- stronger foot-slip and stance-foot-slip penalties for the dragging/shuffling
  gait
- small swing-clearance, touchdown, and contact-switch incentives so feet lift
  and replace instead of sliding continuously
- mild extra root/torso height pressure to avoid returning to the lower V16
  posture
- still uses `300M` environment steps

## Isaac Setup And Training

Use an Isaac Sim / Isaac Lab compatible Python 3.11 environment:

```bash
bash runpod/setup_isaaclab_runpod.sh
make isaac-ppo-baseline
make isaac-ppo-v1
make isaac-ppo-v4
make isaac-ppo-v9
make isaac-ppo-v14
make isaac-ppo-v16
make isaac-ppo-v17
make isaac-ppo-v18
```

The Isaac setup script installs Isaac Sim `5.1.0` from NVIDIA's pip index and
pins Isaac Lab to `v2.3.0`, which matches the Python 3.11 requirement. If you
already have an Isaac Lab checkout from a failed attempt, remove it before
rerunning the setup:

```bash
rm -rf /workspace/IsaacLab
bash runpod/setup_isaaclab_runpod.sh
```

The script creates `/workspace/isaaclab_env` and uses `/workspace/tmp` so the
large Isaac packages do not fill the small container overlay filesystem. On a
fresh Isaac-only pod with enough root storage, set
`ISAACLAB_USE_SYSTEM_PYTHON=1` to install into the current Python environment
instead. By default, the setup preserves already-installed `torch`,
`torchvision`, and `torchaudio` versions using pip constraints; set
`PRESERVE_TORCH=0` only if you want Isaac Sim to choose different Torch
packages.

The wrappers write manifests to:

```text
outputs/isaac_ppo_baseline/manifest.json
outputs/isaac_ppo_v1/manifest.json
outputs/isaac_ppo_v4/manifest.json
outputs/isaac_ppo_v9/manifest.json
outputs/isaac_ppo_v14/manifest.json
outputs/isaac_ppo_v16/manifest.json
outputs/isaac_ppo_v17/manifest.json
outputs/isaac_ppo_v18/manifest.json
```

Isaac Lab writes training TensorBoard event files under:

```text
/workspace/IsaacLab/logs/rsl_rl/humanoid_direct/
```

## Isaac Learning Curves

Export milestone Isaac scalar logs and learning-curve figures into this repo:

```bash
make isaac-curves
```

By default this includes only V0, V1, V4, V9, V14, V16, V17, and V18. To include every
old local RunPod run that still exists on disk:

```bash
python3 scripts/plot_isaac_learning_curves.py \
  --out-dir outputs/isaac_learning_curves \
  --include-all-runs
```

Outputs:

```text
outputs/isaac_learning_curves/
  isaac_scalars.csv
  isaac_reward.png
  isaac_episode_length.png
  isaac_losses.png
  isaac_throughput.png
  isaac_action_noise.png
  report.md
```

The Isaac scalar CSV is allowed in git because the curve exporter now defaults
to milestone runs only.

## Isaac Videos

Record default Isaac videos after training:

```bash
make isaac-video-v0
make isaac-video-v1
make isaac-video-v4
make isaac-video-v9
make isaac-video-v14
make isaac-video-v16
make isaac-video-v17
make isaac-video-v18
```

Record tracked-camera videos when you want the camera to follow the humanoid:

```bash
make isaac-video-track-v0
make isaac-video-track-v1
make isaac-video-track-v4
make isaac-video-track-v9
make isaac-video-track-v14
make isaac-video-track-v16
make isaac-video-track-v17
make isaac-video-track-v18
```

The tracked-camera recorder creates a temporary patched copy of Isaac Lab's
RSL-RL `play.py` under `/workspace/IsaacLab/logs/rsl_rl/` and updates the
viewer camera from the env-0 torso position every step. It does not change the
policy, checkpoint, simulator, reward, or training code.

The video script uses the checkpoint recorded in each Isaac training manifest
by default. To point at a specific checkpoint:

```bash
make isaac-video-v1 ISAAC_VIDEO_CHECKPOINT=/workspace/IsaacLab/logs/rsl_rl/.../model_115.pt
```

Write the Isaac simulator/reward spec without launching Isaac:

```bash
make isaac-baseline-spec
make isaac-v1-spec
make isaac-v4-spec
make isaac-v9-spec
make isaac-v14-spec
make isaac-v16-spec
make isaac-v17-spec
make isaac-v18-spec
```

## Evaluate MuJoCo Baselines

Evaluate both single-policy checkpoints:

```bash
make eval
```

Equivalent command:

```bash
python3 scripts/evaluate_single.py --out-dir outputs/single_eval
```

More complete evaluation with videos:

```bash
MUJOCO_GL=egl python3 scripts/evaluate_single.py \
  --episodes 20 \
  --video-episodes 1 \
  --out-dir outputs/single_eval
```

Outputs:

```text
outputs/single_eval/
  episodes.csv
  summary.csv
  summary.md
  videos/
```

Evaluation is deterministic:

- PPO uses the Gaussian mean action.
- SAC uses the actor mean action after tanh squashing.

## MuJoCo Learning Curves

Generate report figures from the PPO/SAC training CSV logs:

```bash
make curves
```

Equivalent command:

```bash
python3 scripts/plot_learning_curves.py --out-dir outputs/learning_curves
```

The script can be rerun while training is partially complete. It skips missing
logs and refreshes the figures from the latest CSV rows.

## MuJoCo Video

Render the PPO baseline:

```bash
MUJOCO_GL=egl make video
```

Render a specific PPO checkpoint:

```bash
MUJOCO_GL=egl make video \
  VIDEO_CONFIG=configs/fair_ppo_baseline.yaml \
  VIDEO_CHECKPOINT=outputs/fair_ppo_baseline/checkpoints/final.pt \
  VIDEO_OUT=outputs/videos/ppo_baseline.mp4
```

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

## Implementation Notes

- PPO is implemented directly in PyTorch with GAE, clipped policy objective,
  value loss, entropy bonus support, advantage normalization, minibatch SGD,
  rollout storage, observation normalization, action clipping, target-KL early
  stopping, and gradient clipping.
- SAC is implemented directly in PyTorch with replay buffer, tanh-squashed
  Gaussian actor, twin Q critics, target networks, entropy temperature alpha,
  automatic alpha tuning, observation normalization, action squashing, reward
  scaling, and gradient clipping.
- Normalization statistics are saved in checkpoints and restored for
  deterministic evaluation.
