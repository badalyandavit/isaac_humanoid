"""Build a markdown milestone summary from the exported Isaac learning-curve CSV.

Reads `outputs/isaac_learning_curves/isaac_scalars.csv` (produced by
`make isaac-curves`) and emits a per-milestone table with final and best
training reward plus final episode length. Pulls from training scalars, not
eval rollouts, so this is "what the policy saw at the end of training" rather
than a held-out eval — but it's the closest summary available without
re-running the Isaac stack.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from collections import defaultdict


REWARD_TAG = "Train/mean_reward"
LENGTH_TAG = "Train/mean_episode_length"


def load_scalars(path: Path) -> dict[tuple[str, str], list[tuple[int, float]]]:
    series: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = row["tag"]
            if tag not in (REWARD_TAG, LENGTH_TAG):
                continue
            method = row["method"]
            try:
                step = int(row["step"])
                value = float(row["value"])
            except (TypeError, ValueError):
                continue
            series[(method, tag)].append((step, value))
    return series


def summarize(series: dict[tuple[str, str], list[tuple[int, float]]]) -> list[dict[str, object]]:
    methods = sorted({m for (m, _) in series})
    rows: list[dict[str, object]] = []
    for method in methods:
        rewards = sorted(series.get((method, REWARD_TAG), []))
        lengths = sorted(series.get((method, LENGTH_TAG), []))
        if not rewards:
            continue
        final_step, final_reward = rewards[-1]
        best_step, best_reward = max(rewards, key=lambda x: x[1])
        final_length = lengths[-1][1] if lengths else float("nan")
        rows.append(
            {
                "method": method,
                "iters": final_step + 1,
                "final_reward": final_reward,
                "best_reward": best_reward,
                "best_iter": best_step,
                "final_length": final_length,
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    header = (
        "| Milestone | Iters | Final reward | Best reward (iter) | Final episode length |\n"
        "| --- | ---: | ---: | ---: | ---: |\n"
    )
    body_lines = []
    for r in rows:
        body_lines.append(
            f"| {r['method']} | {r['iters']} | {r['final_reward']:.2f} | "
            f"{r['best_reward']:.2f} ({r['best_iter']}) | {r['final_length']:.1f} |"
        )
    return header + "\n".join(body_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scalars-csv",
        type=Path,
        default=Path("outputs/isaac_learning_curves/isaac_scalars.csv"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/isaac_learning_curves/milestone_summary.md"),
    )
    args = parser.parse_args()

    if not args.scalars_csv.exists():
        raise SystemExit(f"scalars CSV not found at {args.scalars_csv}; run `make isaac-curves` first")

    series = load_scalars(args.scalars_csv)
    rows = summarize(series)
    if not rows:
        raise SystemExit(f"no {REWARD_TAG} rows found in {args.scalars_csv}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("# Isaac milestone summary\n\n" + render_markdown(rows), encoding="utf-8")
    print(f"wrote {args.out}")
    print(render_markdown(rows))


if __name__ == "__main__":
    main()
