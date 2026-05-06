from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize training, evaluation, and scaling outputs.")
    parser.add_argument("--outputs", type=Path, default=Path("outputs"), help="Root outputs directory.")
    parser.add_argument("--out", type=Path, default=Path("outputs/analysis"), help="Analysis output dir.")
    return parser.parse_args()


def read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload if isinstance(payload, dict) else {}


def infer_worker_count(columns: list[str]) -> int | None:
    worker_ids = []
    for column in columns:
        match = re.match(r"worker_(\d+)_", column)
        if match:
            worker_ids.append(int(match.group(1)))
    return max(worker_ids) + 1 if worker_ids else None


def last_value(row: pd.Series, *names: str) -> Any:
    for name in names:
        if name in row and pd.notna(row[name]):
            return row[name]
    return None


def summarize_baseline(path: Path) -> dict[str, Any] | None:
    df = read_csv(path)
    if df is None or df.empty:
        return None
    final = df.iloc[-1]
    return {
        "method_key": "baseline",
        "method": "Baseline PPO",
        "source": str(path),
        "num_workers": 1,
        "final_update": last_value(final, "update"),
        "env_steps": last_value(final, "global_step"),
        "final_train_return": last_value(final, "episodic_return_mean"),
        "best_train_return": df["episodic_return_mean"].max()
        if "episodic_return_mean" in df
        else None,
        "final_median_return": None,
        "final_q25_return": None,
        "final_fall_rate": None,
        "best_robust_score": None,
        "median_robust_score": None,
        "num_clones": None,
    }


def summarize_average(path: Path) -> dict[str, Any] | None:
    df = read_csv(path)
    if df is None or df.empty:
        return None
    final = df.iloc[-1]
    cfg = load_json(path.parent / "average_config.json")
    num_workers = int(cfg.get("num_workers") or infer_worker_count(list(df.columns)) or 0)
    round_timesteps = cfg.get("round_timesteps")
    env_steps = None
    if round_timesteps is not None and "round" in final:
        env_steps = int(final["round"]) * int(round_timesteps) * max(1, num_workers)
    return {
        "method_key": "average",
        "method": "Naive Average PPO",
        "source": str(path),
        "num_workers": num_workers or None,
        "final_update": last_value(final, "round"),
        "env_steps": env_steps,
        "final_train_return": last_value(final, "mean_worker_return"),
        "best_train_return": df["best_mean_return"].max() if "best_mean_return" in df else None,
        "final_median_return": last_value(final, "median_worker_return"),
        "final_q25_return": None,
        "final_fall_rate": average_worker_column(final, "fall_rate"),
        "best_robust_score": None,
        "median_robust_score": None,
        "num_clones": None,
    }


def summarize_heavytail(path: Path) -> dict[str, Any] | None:
    df = read_csv(path)
    if df is None or df.empty:
        return None
    final = df.iloc[-1]
    cfg = load_json(path.parent / "heavytail_config.json")
    num_workers = int(cfg.get("num_workers") or infer_worker_count(list(df.columns)) or 0)
    round_timesteps = cfg.get("round_timesteps")
    env_steps = None
    if round_timesteps is not None and "round" in final:
        env_steps = int(final["round"]) * int(round_timesteps) * max(1, num_workers)
    return {
        "method_key": "heavytail",
        "method": "Robust Heavy-Tail Cooperative PPO",
        "source": str(path),
        "num_workers": num_workers or None,
        "final_update": last_value(final, "round"),
        "env_steps": env_steps,
        "final_train_return": average_worker_column(final, "mean"),
        "best_train_return": df["best_robust_score"].max() if "best_robust_score" in df else None,
        "final_median_return": average_worker_column(final, "median"),
        "final_q25_return": average_worker_column(final, "q_low"),
        "final_fall_rate": average_worker_column(final, "fall_rate"),
        "best_robust_score": last_value(final, "best_robust_score"),
        "median_robust_score": last_value(final, "median_robust_score"),
        "num_clones": last_value(final, "num_clones"),
    }


def average_worker_column(row: pd.Series, suffix: str) -> float | None:
    values = []
    pattern = re.compile(rf"worker_\d+_{re.escape(suffix)}$")
    for key, value in row.items():
        if pattern.match(str(key)) and pd.notna(value):
            values.append(float(value))
    if not values:
        return None
    return float(sum(values) / len(values))


def collect_run_summaries(outputs: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted(outputs.glob("**/baseline_train.csv")):
        row = summarize_baseline(path)
        if row:
            rows.append(row)
    for path in sorted(outputs.glob("**/average_rounds.csv")):
        row = summarize_average(path)
        if row:
            rows.append(row)
    for path in sorted(outputs.glob("**/heavytail_rounds.csv")):
        row = summarize_heavytail(path)
        if row:
            rows.append(row)
    return pd.DataFrame(rows)


def build_experiment_table(run_summary: pd.DataFrame, eval_summary: pd.DataFrame | None) -> pd.DataFrame:
    if eval_summary is not None and not eval_summary.empty:
        table = eval_summary.copy()
        table = table.sort_values(["method_key", "checkpoint_label"])
        return pd.DataFrame(
            {
                "Method": table["method"],
                "N": table["num_workers"],
                "Eval episodes": table["eval_episodes"],
                "Mean return": table["mean_return"],
                "Median return": table["median_return"],
                "25% return": table["q25_return"],
                "Fall rate": table["fall_rate"],
                "Robust score": table.get("robust_robust_score"),
                "Checkpoint": table["checkpoint_label"],
            }
        )
    if run_summary.empty:
        return pd.DataFrame()
    return pd.DataFrame(
        {
            "Method": run_summary["method"],
            "N": run_summary["num_workers"],
            "Env steps": run_summary["env_steps"],
            "Best mean/score": run_summary["best_train_return"],
            "Median return": run_summary["final_median_return"],
            "25% return": run_summary["final_q25_return"],
            "Fall rate": run_summary["final_fall_rate"],
            "Source": run_summary["source"],
        }
    )


def write_report(
    out_dir: Path,
    outputs: Path,
    run_summary: pd.DataFrame,
    eval_summary: pd.DataFrame | None,
    experiment_table: pd.DataFrame,
    scaling: pd.DataFrame | None,
) -> None:
    lines = [
        "# Humanoid PPO Analysis",
        "",
        f"Outputs root: `{outputs}`",
        "",
        "## Generated files",
        "",
        "- `run_summary.csv`: final training-log summaries.",
        "- `main_experiment_table.csv`: comparison table, using `eval_summary.csv` when available.",
    ]
    if eval_summary is not None and not eval_summary.empty:
        lines.append("- `eval_summary.csv`: copy of the collected checkpoint evaluation summary.")
    if scaling is not None and not scaling.empty:
        lines.append("- `scaling_summary.csv`: copy of the scaling sweep summary.")
    lines.extend(["", "## Main experiment table", ""])
    if experiment_table.empty:
        lines.append("No analyzable training or evaluation CSVs were found.")
    else:
        lines.append(markdown_table(experiment_table))
    lines.extend(["", "## Source counts", ""])
    lines.append(f"- Training summaries: {len(run_summary)}")
    lines.append(f"- Evaluation summaries: {0 if eval_summary is None else len(eval_summary)}")
    lines.append(f"- Scaling rows: {0 if scaling is None else len(scaling)}")
    (out_dir / "analysis_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    columns = [str(column) for column in df.columns]
    rows = [[format_markdown_cell(value) for value in row] for row in df.itertuples(index=False, name=None)]
    widths = [len(column) for column in columns]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))
    header = "| " + " | ".join(column.ljust(widths[idx]) for idx, column in enumerate(columns)) + " |"
    separator = "| " + " | ".join("-" * widths[idx] for idx in range(len(columns))) + " |"
    body = [
        "| " + " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row)) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def format_markdown_cell(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    run_summary = collect_run_summaries(args.outputs)
    run_summary.to_csv(args.out / "run_summary.csv", index=False)

    eval_summary = read_csv(args.outputs / "eval_summary.csv")
    if eval_summary is not None and not eval_summary.empty:
        eval_summary.to_csv(args.out / "eval_summary.csv", index=False)

    scaling = read_csv(args.outputs / "scaling_humanoid_v5" / "scaling_summary.csv")
    if scaling is None:
        scaling_candidates = sorted(args.outputs.glob("**/scaling_summary.csv"))
        scaling = read_csv(scaling_candidates[0]) if scaling_candidates else None
    if scaling is not None and not scaling.empty:
        scaling.to_csv(args.out / "scaling_summary.csv", index=False)

    experiment_table = build_experiment_table(run_summary, eval_summary)
    experiment_table.to_csv(args.out / "main_experiment_table.csv", index=False)

    write_report(args.out, args.outputs, run_summary, eval_summary, experiment_table, scaling)
    if run_summary.empty and (eval_summary is None or eval_summary.empty) and (
        scaling is None or scaling.empty
    ):
        raise SystemExit(f"No result CSVs found under {args.outputs}.")
    print(f"Wrote analysis to {args.out}")


if __name__ == "__main__":
    main()
