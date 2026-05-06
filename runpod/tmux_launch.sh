#!/usr/bin/env bash
set -euo pipefail
SESSION=${1:-ppo_baseline}
CMD=${2:-"bash runpod/train_ppo_baseline_runpod.sh"}
tmux new-session -d -s "$SESSION" "$CMD"
echo "Started tmux session: $SESSION"
echo "Attach with: tmux attach -t $SESSION"
