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
scripts/
  train_ppo_baseline.py
  train_sac_baseline.py
  evaluate_single.py
  record_video.py
src/humanoid_rl/
  config.py
  envs.py
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
