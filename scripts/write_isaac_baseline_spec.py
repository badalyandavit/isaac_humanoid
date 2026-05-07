from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from humanoid_rl.isaaclab import baseline_spec, load_isaac_ppo_config
from humanoid_rl.utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the Isaac baseline simulator/reward spec.")
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/isaac_ppo_baseline"))
    return parser.parse_args()


def flatten(prefix: str, value: Any) -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        rows: list[tuple[str, Any]] = []
        for key, nested in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else key
            rows.extend(flatten(next_prefix, nested))
        return rows
    return [(prefix, value)]


def markdown(spec: dict[str, Any]) -> str:
    rows = flatten("", spec)
    lines = [
        "# Isaac Baseline Spec",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for key, value in rows:
        lines.append(f"| `{key}` | {value} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    spec = baseline_spec(cfg)
    out_dir = ensure_dir(args.out_dir)
    write_json(out_dir / "baseline_spec.json", spec)
    (out_dir / "baseline_spec.md").write_text(markdown(spec), encoding="utf-8")
    print(f"Wrote Isaac baseline spec to {out_dir}")


if __name__ == "__main__":
    main()
