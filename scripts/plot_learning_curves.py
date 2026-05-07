from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from humanoid_rl.utils import ensure_dir


SERIES = {
    "return": {
        "columns": ["episodic_return_mean"],
        "title": "Learning Curve: Episodic Return",
        "ylabel": "Mean episodic return",
        "filename": "learning_curve_return.png",
    },
    "length": {
        "columns": ["episodic_length_mean"],
        "title": "Episode Length / Alive Duration",
        "ylabel": "Mean episode length",
        "filename": "learning_curve_length.png",
    },
    "fall": {
        "columns": ["fall_rate"],
        "title": "Fall Rate",
        "ylabel": "Fall rate",
        "filename": "learning_curve_fall_rate.png",
    },
    "actions": {
        "columns": ["action_l2_norm", "action_smoothness"],
        "title": "Action Magnitude And Smoothness",
        "ylabel": "Metric value",
        "filename": "learning_curve_actions.png",
    },
    "throughput": {
        "columns": ["env_steps_per_second"],
        "title": "Environment Throughput",
        "ylabel": "Env steps / second",
        "filename": "learning_curve_throughput.png",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot PPO/SAC learning curves from training CSV logs.")
    parser.add_argument("--ppo-log", type=Path, default=Path("outputs/fair_ppo_baseline/ppo_baseline_train.csv"))
    parser.add_argument("--sac-log", type=Path, default=Path("outputs/fair_sac_baseline/sac_baseline_train.csv"))
    parser.add_argument("--eval-summary", type=Path, default=Path("outputs/single_eval/summary.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/learning_curves"))
    parser.add_argument("--smooth-window", type=int, default=5)
    return parser.parse_args()


def load_log(path: Path, method: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame()
    df["method"] = method
    if "total_env_steps" not in df.columns and "global_step" in df.columns:
        df["total_env_steps"] = df["global_step"]
    if "total_env_steps" not in df.columns:
        return pd.DataFrame()
    for col in df.columns:
        if col == "method":
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().any():
            df[col] = converted
    return df.sort_values("total_env_steps")


def smooth(values: pd.Series, window: int) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if window <= 1:
        return numeric
    return numeric.rolling(window=window, min_periods=1).mean()


def plot_metric(
    frames: list[pd.DataFrame],
    columns: list[str],
    title: str,
    ylabel: str,
    out_path: Path,
    smooth_window: int,
) -> bool:
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=160)
    plotted = False
    for df in frames:
        if df.empty:
            continue
        method = str(df["method"].iloc[0])
        for col in columns:
            if col not in df.columns:
                continue
            y = pd.to_numeric(df[col], errors="coerce")
            valid = y.notna()
            if not valid.any():
                continue
            x = pd.to_numeric(df.loc[valid, "total_env_steps"], errors="coerce")
            y_smooth = smooth(y.loc[valid], smooth_window)
            label = method if len(columns) == 1 else f"{method}: {col}"
            ax.plot(x, y_smooth, linewidth=2.0, label=label)
            plotted = True
    if not plotted:
        plt.close(fig)
        return False
    ax.set_title(title)
    ax.set_xlabel("Environment steps")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return True


def plot_optimizer_metrics(frames: list[pd.DataFrame], out_path: Path, smooth_window: int) -> bool:
    specs = [
        ("PPO policy/value", ["policy_loss", "value_loss"]),
        ("PPO stability", ["approx_kl", "clipfrac"]),
        ("SAC Q/actor losses", ["q_loss", "actor_loss"]),
        ("SAC entropy temperature", ["alpha"]),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=160)
    plotted_any = False
    for ax, (title, columns) in zip(axes.flatten(), specs, strict=True):
        plotted = False
        for df in frames:
            if df.empty:
                continue
            method = str(df["method"].iloc[0])
            for col in columns:
                if col not in df.columns:
                    continue
                y = pd.to_numeric(df[col], errors="coerce")
                valid = y.notna()
                if not valid.any():
                    continue
                x = pd.to_numeric(df.loc[valid, "total_env_steps"], errors="coerce")
                ax.plot(x, smooth(y.loc[valid], smooth_window), linewidth=1.8, label=f"{method}: {col}")
                plotted = True
                plotted_any = True
        ax.set_title(title)
        ax.set_xlabel("Environment steps")
        ax.grid(True, alpha=0.25)
        if plotted:
            ax.legend(fontsize=8)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    if not plotted_any:
        plt.close(fig)
        return False
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return True


def load_eval_summary(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df if not df.empty else pd.DataFrame()


def final_training_rows(frames: list[pd.DataFrame]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keep = [
        "method",
        "total_env_steps",
        "episodic_return_mean",
        "episodic_length_mean",
        "fall_rate",
        "action_l2_norm",
        "action_smoothness",
        "env_steps_per_second",
    ]
    for df in frames:
        if df.empty:
            continue
        row = df.iloc[-1].to_dict()
        rows.append({key: row.get(key, "") for key in keep})
    return rows


def markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No rows available.\n"
    columns = list(rows[0].keys())
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float) and np.isfinite(value):
                values.append(f"{value:.4g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def write_report(out_dir: Path, generated: list[Path], frames: list[pd.DataFrame], eval_summary: pd.DataFrame) -> None:
    lines = ["# Learning Curves\n"]
    if generated:
        lines.append("## Figures\n")
        for path in generated:
            rel = path.relative_to(out_dir)
            lines.append(f"- [{rel}]({rel})")
        lines.append("")
    else:
        lines.append("No figures were generated because no usable training logs were found.\n")
    lines.append("## Latest Training Rows\n")
    lines.append(markdown_table(final_training_rows(frames)))
    if not eval_summary.empty:
        lines.append("## Final Evaluation Summary\n")
        lines.append(markdown_table(eval_summary.to_dict(orient="records")))
    lines.append(
        "Training curves use the CSV logs written during training. "
        "Run `make curves` again after more training to refresh the figures.\n"
    )
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = ensure_dir(args.out_dir)
    frames = [
        load_log(args.ppo_log, "PPO"),
        load_log(args.sac_log, "SAC"),
    ]
    generated: list[Path] = []
    for spec in SERIES.values():
        out_path = out_dir / spec["filename"]
        if plot_metric(
            frames,
            spec["columns"],
            spec["title"],
            spec["ylabel"],
            out_path,
            args.smooth_window,
        ):
            generated.append(out_path)
    optimizer_path = out_dir / "learning_curve_optimizer.png"
    if plot_optimizer_metrics(frames, optimizer_path, args.smooth_window):
        generated.append(optimizer_path)
    eval_summary = load_eval_summary(args.eval_summary)
    write_report(out_dir, generated, frames, eval_summary)
    if generated:
        print(f"Wrote {len(generated)} learning-curve figures to {out_dir}")
    else:
        print(f"No usable training logs found. Wrote report to {out_dir / 'report.md'}")


if __name__ == "__main__":
    main()
