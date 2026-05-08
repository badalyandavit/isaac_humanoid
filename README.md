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
scripts/
  train_ppo_baseline.py
  train_sac_baseline.py
  train_isaac_ppo_baseline.py
  write_isaac_baseline_spec.py
  record_isaac_video.py
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

Use an Isaac Sim / Isaac Lab compatible Python 3.11 environment:

```bash
bash runpod/setup_isaaclab_runpod.sh
make isaac-ppo-baseline
make isaac-ppo-v1
```

The wrappers write manifests to:

```text
outputs/isaac_ppo_baseline/manifest.json
outputs/isaac_ppo_v1/manifest.json
```

Record Isaac videos after training:

```bash
make isaac-video-v0
make isaac-video-v1
```

This uses Isaac Lab's RSL-RL `play.py --video` flow and requires `ffmpeg` in
the Isaac environment.

Outputs:

```text
outputs/videos/isaac_v0_policy.mp4
outputs/videos/isaac_v1_policy.mp4
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
```

Outputs:

```text
outputs/isaac_ppo_baseline/
  baseline_spec.json
  baseline_spec.md
outputs/isaac_ppo_v1/
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
