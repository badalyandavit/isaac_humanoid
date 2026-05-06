#!/usr/bin/env bash
set -euo pipefail
SESSION=${1:-humanoid_ht}
CMD=${2:-"bash runpod/train_heavytail_runpod.sh"}
tmux new-session -d -s "$SESSION" "$CMD"
echo "Started tmux session: $SESSION"
echo "Attach with: tmux attach -t $SESSION"
