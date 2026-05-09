# Humanoid PPO/SAC Baselines

PyTorch implementations for single-policy PPO and SAC on Gymnasium/MuJoCo
`Humanoid-v5`.

The repository is intentionally scoped to two methods:

1. **Single PPO baseline**
2. **Single SAC baseline**

There is no population training, parameter averaging, or action averaging in
the current project path.

## Repository Layout

```text
configs/
  fair_ppo_baseline.yaml
  fair_ppo_smoke.yaml
  fair_sac_baseline.yaml
  fair_sac_smoke.yaml
  isaac_ppo_baseline.yaml
  isaac_ppo_v1.yaml
  isaac_ppo_v2.yaml
  isaac_ppo_v3.yaml
  isaac_ppo_v4.yaml
  isaac_ppo_v5.yaml
  isaac_ppo_v6.yaml
  isaac_ppo_v7.yaml
  isaac_ppo_v8.yaml
  isaac_ppo_v9.yaml
  isaac_ppo_v10.yaml
  isaac_ppo_v11.yaml
  isaac_ppo_v12.yaml
  isaac_ppo_v13.yaml
  isaac_ppo_v14.yaml
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

## Train

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

## Optional Isaac PPO

There are also single-agent Isaac Lab PPO variants. These are not population
methods and are not directly comparable to Gymnasium/MuJoCo `Humanoid-v5`,
because they use Isaac Lab's `Isaac-Humanoid-Direct-v0` task and RSL-RL PPO
runner.

The Isaac V0 baseline is named:

```text
isaac_v0_official_humanoid_direct
```

It uses the official Isaac Lab direct humanoid simulator and reward:

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

The Isaac V1 shaped-reward variant is named:

```text
isaac_v1_upright_controlled_humanoid_direct
```

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

The Isaac V2 shaped-reward variant is named:

```text
isaac_v2_mild_upright_controlled_humanoid_direct
```

V2 keeps the same simulator and PPO runner, but uses milder shaping than V1 and
a longer default training budget of `200M` environment steps:

- heading reward weight `0.5 -> 0.75`
- upright reward weight `0.1 -> 0.25`
- alive reward scale `2.0 -> 1.5`
- action cost scale `0.01 -> 0.015`
- energy cost scale `0.05 -> 0.06`
- death cost `-1.0 -> -2.0`
- termination torso height `0.8 -> 0.85`

The intent is to keep V1's cleaner-upright goal but avoid punishing early
falls so harshly that the policy never learns a stable gait.

The Isaac V3 shaped-reward variant is named:

```text
isaac_v3_tall_upright_humanoid_direct
```

V3 keeps the same simulator and PPO runner, but targets the low crawling gait
seen in V2:

- heading reward weight `0.5 -> 1.0`
- upright reward weight `0.1 -> 0.75`
- alive reward scale `2.0 -> 1.2`
- action cost scale `0.01 -> 0.02`
- energy cost scale `0.05 -> 0.08`
- death cost `-1.0 -> -4.0`
- termination torso height `0.8 -> 1.0`

The intent is to trade off some raw return for a taller, more human-like gait.

The Isaac V4 custom-reward variant is named:

```text
isaac_v4_morphology_reward_humanoid_direct
```

V4 registers a new Isaac task id:

```text
Isaac-Humanoid-V4-Direct-v0
```

Unlike V1-V3, V4 is not only a coefficient sweep. It installs a small custom
Isaac Lab task module into the Isaac Lab checkout and adds explicit gait-quality
terms:

- root/torso height bonus and low-height penalty
- torso/pelvis/head low-body penalty
- arm/hand low-body penalty as a proxy for arm-supported crawling
- leg joint pose penalty to discourage deep crouch
- arm joint pose penalty to discourage arm-driven locomotion
- action-rate penalty for smoother motion

The intent is to address the V2/V3 failure mode where the policy gets high
survival reward while moving in a low spider-like crouch.

The Isaac V5 anti-jump custom-reward variant is named:

```text
isaac_v5_anti_jump_morphology_humanoid_direct
```

V5 uses the same custom task module as V4 but removes V4's positive height
bonus. It instead treats height as a bounded constraint:

- no positive height bonus
- low-height penalty to prevent crawling
- high-height penalty to prevent hopping
- vertical-velocity penalty to discourage jumping
- arm-low and arm-pose penalties retained to discourage spider/crawling gait

The intent is to fix the V4 jump/hop exploit without returning to the V2/V3
crawling exploit.

The Isaac V6 diagnostic gait-reward variant is named:

```text
isaac_v6_diagnostic_gait_reward_humanoid_direct
```

V6 uses the same custom task module as V4/V5 and adds the next set of terms
for the remaining V5 failure mode:

- TensorBoard diagnostics for custom reward terms under `custom/*`
- arm action magnitude penalty
- arm joint velocity penalty
- leg action and pose symmetry penalties
- non-foot low-body penalty
- feet-airborne and foot-slip proxy penalties

The direct humanoid task does not define explicit contact sensors, so V6 uses
body-height and foot-velocity proxies for contact-like behavior.

The Isaac V7 contact-gait custom-reward variant is named:

```text
isaac_v7_contact_gait_reward_humanoid_direct
```

V7 keeps the V6 diagnostics and adds gait structure aimed at the V6 raised-arm
hopping exploit:

- target forward-velocity reward
- lateral drift penalty
- extra vertical-bounce penalty when forward speed is low
- arm-high penalty for overhead balance exploits
- single-foot support reward
- foot-switch reward
- no-contact, double-contact, and left/right foot-balance penalties

V7 uses Isaac body contact forces when available and falls back to foot-height
contact proxies otherwise.

The Isaac V8 step-transition custom-reward variant is named:

```text
isaac_v8_step_transition_reward_humanoid_direct
```

V8 keeps the V7 contact/gait terms and adds the next step-quality terms after
V7 moved forward but still had weak foot switching and high stance-foot slip:

- forward-speed tracking and high-speed penalties
- soft foot-contact transition reward
- swing-foot clearance reward
- fore-aft step-length reward
- foot lateral-spread penalty
- stronger stance-foot slip and left/right contact-balance penalties

The Isaac V9 curriculum-gait custom-reward variant is named:

```text
isaac_v9_curriculum_gait_reward_humanoid_direct
```

V9 addresses the V8 regression where step-transition shaping reduced slip but
collapsed episode length into a short one-leg hopping/reset loop:

- restores a more permissive survival envelope from V7
- keeps V8's forward-speed cap and slip control
- ramps contact/gait shaping from 25% to full strength early in training
- adds soft single-support and mild foot-height-difference rewards
- weakens step-length, swing-clearance, and hard contact-balance terms

The Isaac V10 balanced-gait custom-reward variant is named:

```text
isaac_v10_balanced_gait_reward_humanoid_direct
```

V10 targets the remaining V9 failure mode: stable upright forward motion with
one-sided foot contact and lateral drift:

- stronger lateral velocity penalty
- stronger but curriculum-ramped left/right contact-balance penalty
- weaker soft single-support reward so one-foot shuffling is less attractive
- slightly lower target/max forward speed to reduce sideways rushing
- longer contact/gait curriculum before full gait pressure is applied

The Isaac V11 grounded-gait custom-reward variant is named:

```text
isaac_v11_grounded_gait_reward_humanoid_direct
```

V11 targets the V10 high-knee floating-foot exploit:

- explicit penalty for excessive swing-foot height
- explicit penalty for excessive left/right foot-height difference
- much weaker one-foot and soft single-support rewards
- stronger arm-high and arm-pose penalties for raised-arm balance exploits
- keeps V10's lateral-drift control while removing the high-foot incentive

The Isaac V12 touchdown-slip custom-reward variant is named:

```text
isaac_v12_touchdown_slip_reward_humanoid_direct
```

V12 targets the remaining V11 shuffle/slide failure mode:

- contact-aware stance-foot slip penalty, so planted feet cannot slide cheaply
- touchdown reward only after a short foot air-time window while the other foot was stance
- lower arm-neutral height penalty for arms-up balance exploits below the high-arm threshold
- slightly slower target forward speed and stronger double-contact pressure
- keeps V11's high-foot and foot-height-difference safeguards

The Isaac V13 air-time-balance custom-reward variant is named:

```text
isaac_v13_airtime_balance_reward_humanoid_direct
```

V13 targets the V12 one-foot airborne glide:

- explicit maximum foot-air-time penalty
- stronger sustained left/right contact-balance penalty
- tighter left/right foot-height-difference limit
- reduced stance-foot slip pressure so one airborne foot is less attractive
- keeps touchdown reward as a secondary cue rather than the main gait driver

The Isaac V14 cadence-gait custom-reward variant is named:

```text
isaac_v14_cadence_gait_reward_humanoid_direct
```

V14 targets the V13 grounded-shuffle failure mode:

- soft foot-dominance switch reward for left/right support changes even when contacts are not perfectly binary
- overlong same-foot stance penalty so one foot cannot dominate contact for most of the rollout
- underused-foot contact reward to turn long-horizon balance into an active gait objective
- relaxed V13 air-time and foot-height limits so a real swing step is possible
- slightly stronger arm-pose, arm-action, and arm-height penalties to reduce raised-arm balancing

Use an Isaac Sim / Isaac Lab compatible Python 3.11 environment:

```bash
bash runpod/setup_isaaclab_runpod.sh
make isaac-ppo-baseline
make isaac-ppo-v1
make isaac-ppo-v2
make isaac-ppo-v3
make isaac-ppo-v4
make isaac-ppo-v5
make isaac-ppo-v6
make isaac-ppo-v7
make isaac-ppo-v8
make isaac-ppo-v9
make isaac-ppo-v10
make isaac-ppo-v11
make isaac-ppo-v12
make isaac-ppo-v13
make isaac-ppo-v14
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
large Isaac packages do not fill the small container overlay filesystem.
On a fresh Isaac-only pod with enough root storage, set
`ISAACLAB_USE_SYSTEM_PYTHON=1` to install into the current Python environment
instead. By default, the setup preserves already-installed `torch`,
`torchvision`, and `torchaudio` versions using pip constraints; set
`PRESERVE_TORCH=0` only if you want Isaac Sim to choose different Torch
packages.

The wrappers write manifests to:

```text
outputs/isaac_ppo_baseline/manifest.json
outputs/isaac_ppo_v1/manifest.json
outputs/isaac_ppo_v2/manifest.json
outputs/isaac_ppo_v3/manifest.json
outputs/isaac_ppo_v4/manifest.json
outputs/isaac_ppo_v5/manifest.json
outputs/isaac_ppo_v6/manifest.json
outputs/isaac_ppo_v7/manifest.json
outputs/isaac_ppo_v8/manifest.json
outputs/isaac_ppo_v9/manifest.json
outputs/isaac_ppo_v10/manifest.json
outputs/isaac_ppo_v11/manifest.json
outputs/isaac_ppo_v12/manifest.json
outputs/isaac_ppo_v13/manifest.json
outputs/isaac_ppo_v14/manifest.json
```

Isaac Lab writes training TensorBoard event files under:

```text
/workspace/IsaacLab/logs/rsl_rl/humanoid_direct/
```

Export Isaac V0/V1/V2/V3/V4/V5/V6/V7/V8/V9/V10/V11/V12/V13/V14 scalar logs and learning-curve figures into this repo:

```bash
make isaac-curves
```

Outputs:

```text
outputs/isaac_learning_curves/
  isaac_scalars.csv
  isaac_reward.png
  isaac_episode_length.png
  isaac_losses.png
  report.md
```

Record Isaac videos after training:

```bash
make isaac-video-v0
make isaac-video-v1
make isaac-video-v2
make isaac-video-v3
make isaac-video-v4
make isaac-video-v5
make isaac-video-v6
make isaac-video-v7
make isaac-video-v8
make isaac-video-v9
make isaac-video-v10
make isaac-video-v11
make isaac-video-v12
make isaac-video-v13
make isaac-video-v14
```

This uses Isaac Lab's RSL-RL `play.py --video` flow and requires `ffmpeg` in
the Isaac environment. These videos use Isaac Lab's default viewer camera, so
fast policies may walk out of frame.

Record tracked-camera videos when you want the camera to follow the humanoid:

```bash
make isaac-video-track-v0
make isaac-video-track-v1
make isaac-video-track-v2
make isaac-video-track-v3
make isaac-video-track-v4
make isaac-video-track-v5
make isaac-video-track-v6
make isaac-video-track-v7
make isaac-video-track-v8
make isaac-video-track-v9
make isaac-video-track-v10
make isaac-video-track-v11
make isaac-video-track-v12
make isaac-video-track-v13
make isaac-video-track-v14
```

The tracked-camera recorder creates a temporary patched copy of Isaac Lab's
RSL-RL `play.py` under `/workspace/IsaacLab/logs/rsl_rl/` and updates the
viewer camera from the env-0 torso position every step. It does not change the
policy, checkpoint, simulator, reward, or training code.

Outputs:

```text
outputs/videos/isaac_v0_policy.mp4
outputs/videos/isaac_v1_policy.mp4
outputs/videos/isaac_v2_policy.mp4
outputs/videos/isaac_v3_policy.mp4
outputs/videos/isaac_v4_policy.mp4
outputs/videos/isaac_v5_policy.mp4
outputs/videos/isaac_v6_policy.mp4
outputs/videos/isaac_v7_policy.mp4
outputs/videos/isaac_v8_policy.mp4
outputs/videos/isaac_v9_policy.mp4
outputs/videos/isaac_v10_policy.mp4
outputs/videos/isaac_v11_policy.mp4
outputs/videos/isaac_v12_policy.mp4
outputs/videos/isaac_v13_policy.mp4
outputs/videos/isaac_v14_policy.mp4
outputs/videos/isaac_v0_policy_tracked.mp4
outputs/videos/isaac_v1_policy_tracked.mp4
outputs/videos/isaac_v2_policy_tracked.mp4
outputs/videos/isaac_v3_policy_tracked.mp4
outputs/videos/isaac_v4_policy_tracked.mp4
outputs/videos/isaac_v5_policy_tracked.mp4
outputs/videos/isaac_v6_policy_tracked.mp4
outputs/videos/isaac_v7_policy_tracked.mp4
outputs/videos/isaac_v8_policy_tracked.mp4
outputs/videos/isaac_v9_policy_tracked.mp4
outputs/videos/isaac_v10_policy_tracked.mp4
outputs/videos/isaac_v11_policy_tracked.mp4
outputs/videos/isaac_v12_policy_tracked.mp4
outputs/videos/isaac_v13_policy_tracked.mp4
outputs/videos/isaac_v14_policy_tracked.mp4
```

The video script uses the checkpoint recorded in each Isaac training manifest
by default. To point at a specific checkpoint:

```bash
make isaac-video-v1 ISAAC_VIDEO_CHECKPOINT=/workspace/IsaacLab/logs/rsl_rl/.../model_115.pt
```

Write the Isaac simulator/reward spec without launching Isaac:

```bash
make isaac-baseline-spec
make isaac-v1-spec
make isaac-v2-spec
make isaac-v3-spec
make isaac-v4-spec
make isaac-v5-spec
make isaac-v6-spec
make isaac-v7-spec
make isaac-v8-spec
make isaac-v9-spec
make isaac-v10-spec
make isaac-v11-spec
make isaac-v12-spec
make isaac-v13-spec
make isaac-v14-spec
```

Outputs:

```text
outputs/isaac_ppo_baseline/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v1/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v2/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v3/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v4/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v5/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v6/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v7/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v8/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v9/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v10/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v11/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v12/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v13/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v14/
  baseline_spec.json
  baseline_spec.md
```

## Evaluate

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

## Learning Curves

Generate report figures from the PPO/SAC training CSV logs:

```bash
make curves
```

Equivalent command:

```bash
python3 scripts/plot_learning_curves.py --out-dir outputs/learning_curves
```

Outputs:

```text
outputs/learning_curves/
  learning_curve_return.png
  learning_curve_length.png
  learning_curve_fall_rate.png
  learning_curve_actions.png
  learning_curve_throughput.png
  learning_curve_optimizer.png
  report.md
```

The script can be rerun while training is partially complete. It skips missing
logs and refreshes the figures from the latest CSV rows.

## Video

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
