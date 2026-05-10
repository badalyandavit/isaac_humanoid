from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator

from humanoid_rl.utils import ensure_dir


PLOT_SPECS = [
    {
        "name": "reward",
        "title": "Isaac Learning Curve: Mean Reward",
        "ylabel": "Reward",
        "filename": "isaac_reward.png",
        "patterns": ("reward",),
        "reject": ("loss",),
    },
    {
        "name": "episode_length",
        "title": "Isaac Episode Length",
        "ylabel": "Episode length",
        "filename": "isaac_episode_length.png",
        "patterns": ("episode_length", "episode length"),
        "reject": (),
    },
    {
        "name": "loss",
        "title": "Isaac PPO Losses",
        "ylabel": "Loss",
        "filename": "isaac_losses.png",
        "patterns": ("loss",),
        "reject": (),
    },
    {
        "name": "throughput",
        "title": "Isaac Training Throughput",
        "ylabel": "Steps / second",
        "filename": "isaac_throughput.png",
        "patterns": ("fps", "steps/s", "throughput"),
        "reject": (),
    },
    {
        "name": "action_noise",
        "title": "Isaac Action Noise",
        "ylabel": "Std",
        "filename": "isaac_action_noise.png",
        "patterns": ("noise", "std"),
        "reject": (),
    },
]

MILESTONE_RUN_LABELS = {
    "_baseline": "Isaac V0",
    "_upright_controlled_v1": "Isaac V1",
    "_morphology_reward_v4": "Isaac V4",
    "_curriculum_gait_v9": "Isaac V9",
    "_cadence_gait_v14": "Isaac V14",
    "_stable_lower_arms_v16": "Isaac V16",
    "_final_stable_walk_v17": "Isaac V17",
    "_final_polished_walk_v18": "Isaac V18",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot Isaac Lab RSL-RL TensorBoard learning curves.")
    parser.add_argument("--log-root", type=Path, default=Path("/workspace/IsaacLab/logs/rsl_rl/humanoid_direct"))
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/isaac_learning_curves"))
    parser.add_argument("--smooth-window", type=int, default=3)
    parser.add_argument("--include-smoke", action="store_true")
    parser.add_argument("--include-all-runs", action="store_true")
    return parser.parse_args()


def run_label(run_dir: Path) -> str:
    name = run_dir.name
    for suffix, label in MILESTONE_RUN_LABELS.items():
        if name.endswith(suffix):
            return label
    return name


def is_milestone_run(run_dir: Path) -> bool:
    return any(run_dir.name.endswith(suffix) for suffix in MILESTONE_RUN_LABELS)


def discover_runs(log_root: Path, include_smoke: bool, include_all_runs: bool) -> list[Path]:
    if not log_root.exists():
        return []
    runs = [p for p in log_root.iterdir() if p.is_dir() and list(p.glob("events.out.tfevents.*"))]
    if not include_smoke:
        runs = [p for p in runs if "smoke" not in p.name.lower()]
    if not include_all_runs:
        runs = [p for p in runs if is_milestone_run(p)]
    return sorted(runs, key=lambda p: p.stat().st_mtime)


def read_run_scalars(run_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for event_file in sorted(run_dir.glob("events.out.tfevents.*")):
        accumulator = event_accumulator.EventAccumulator(
            str(event_file),
            size_guidance={event_accumulator.SCALARS: 0},
        )
        accumulator.Reload()
        for tag in accumulator.Tags().get("scalars", []):
            for event in accumulator.Scalars(tag):
                rows.append(
                    {
                        "run": run_dir.name,
                        "method": run_label(run_dir),
                        "tag": tag,
                        "step": event.step,
                        "wall_time": event.wall_time,
                        "value": event.value,
                    }
                )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return (
        df.sort_values(["run", "tag", "step", "wall_time"])
        .drop_duplicates(["run", "tag", "step"], keep="last")
        .reset_index(drop=True)
    )


def smooth(values: pd.Series, window: int) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce")
    if window <= 1:
        return values
    return values.rolling(window=window, min_periods=1).mean()


def matching_tags(df: pd.DataFrame, patterns: tuple[str, ...], reject: tuple[str, ...]) -> list[str]:
    tags: list[str] = []
    for tag in sorted(df["tag"].dropna().unique()):
        normalized = str(tag).lower().replace("/", "_")
        if not any(pattern in normalized for pattern in patterns):
            continue
        if any(pattern in normalized for pattern in reject):
            continue
        tags.append(str(tag))
    return tags


def plot_spec(df: pd.DataFrame, spec: dict[str, Any], out_path: Path, smooth_window: int) -> bool:
    tags = matching_tags(df, spec["patterns"], spec["reject"])
    if not tags:
        return False
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=160)
    plotted = False
    for method in sorted(df["method"].unique()):
        method_df = df[df["method"] == method]
        for tag in tags:
            tag_df = method_df[method_df["tag"] == tag].sort_values("step")
            if tag_df.empty:
                continue
            label = method if len(tags) == 1 else f"{method}: {tag}"
            ax.plot(
                tag_df["step"],
                smooth(tag_df["value"], smooth_window),
                linewidth=2.0,
                label=label,
            )
            plotted = True
    if not plotted:
        plt.close(fig)
        return False
    ax.set_title(spec["title"])
    ax.set_xlabel("TensorBoard step")
    ax.set_ylabel(spec["ylabel"])
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return True


def latest_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return (
        df.sort_values(["method", "tag", "step"])
        .groupby(["method", "tag"], as_index=False)
        .tail(1)
        .sort_values(["method", "tag"])
    )


def markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in df.to_dict(orient="records"):
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def write_report(out_dir: Path, df: pd.DataFrame, generated: list[Path], runs: list[Path]) -> None:
    lines = ["# Isaac Learning Curves", ""]
    if runs:
        lines.append("## Runs")
        for run in runs:
            lines.append(f"- `{run.name}` -> {run_label(run)}")
        lines.append("")
    if generated:
        lines.append("## Figures")
        for path in generated:
            rel = path.relative_to(out_dir)
            lines.append(f"- [{rel}]({rel})")
        lines.append("")
    lines.append("## Available Scalar Tags")
    if df.empty:
        lines.append("No TensorBoard scalar data found.")
    else:
        for method, method_df in df.groupby("method"):
            tags = ", ".join(sorted(method_df["tag"].unique()))
            lines.append(f"- **{method}**: {tags}")
    lines.append("")
    latest = latest_rows(df)
    if not latest.empty:
        lines.append("## Latest Scalar Values")
        lines.append(markdown_table(latest[["method", "tag", "step", "value"]]))
        lines.append("")
    lines.append("Raw scalar data is stored in `isaac_scalars.csv`.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = ensure_dir(args.out_dir)
    runs = discover_runs(args.log_root, args.include_smoke, args.include_all_runs)
    frames = [read_run_scalars(run) for run in runs]
    df = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True) if frames else pd.DataFrame()
    if not df.empty:
        df.to_csv(out_dir / "isaac_scalars.csv", index=False)

    generated: list[Path] = []
    for spec in PLOT_SPECS:
        out_path = out_dir / spec["filename"]
        if not df.empty and plot_spec(df, spec, out_path, args.smooth_window):
            generated.append(out_path)
    write_report(out_dir, df, generated, runs)
    print(f"Wrote Isaac learning curves to {out_dir}")


if __name__ == "__main__":
    main()
