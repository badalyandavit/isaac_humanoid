from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isaaclab-dir", type=Path, default=Path("/workspace/IsaacLab"))
    parser.add_argument("--task", type=str, default="Isaac-Humanoid-Direct-v0")
    parser.add_argument("--population-manifest", type=Path, default=Path("outputs/isaac_ppo_population/manifest.json"))
    parser.add_argument("--baseline-manifest", type=Path, default=Path("outputs/isaac_ppo_baseline/manifest.json"))
    parser.add_argument("--num-average-agents", type=str, default="2,3")
    parser.add_argument("--aggregators", type=str, default="mean")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--num-envs", type=int, default=64)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/isaac_fair_eval"))
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def valid_checkpoints(paths: list[str | None]) -> list[str]:
    return [str(path) for path in paths if path]


def eval_command(
    isaaclab_dir: Path,
    task: str,
    checkpoints: list[str],
    aggregator: str,
    episodes: int,
    num_envs: int,
    output_dir: Path,
    video: bool,
) -> list[str]:
    command = [
        str(isaaclab_dir / "isaaclab.sh"),
        "-p",
        str(Path.cwd() / "scripts" / "evaluate_isaac_ppo_average.py"),
        "--task",
        task,
        "--checkpoints",
        *checkpoints,
        "--aggregator",
        aggregator,
        "--episodes",
        str(episodes),
        "--num_envs",
        str(num_envs),
        "--output-dir",
        str(output_dir),
        "--headless",
    ]
    if video:
        command.append("--video")
    return command


def main() -> None:
    args = parse_args()
    commands: list[list[str]] = []
    if args.baseline_manifest.exists():
        baseline = load_manifest(args.baseline_manifest)
        checkpoint = baseline.get("checkpoint")
        if checkpoint:
            commands.append(
                eval_command(
                    args.isaaclab_dir,
                    args.task,
                    [checkpoint],
                    "mean",
                    args.episodes,
                    args.num_envs,
                    args.output_dir / "single_ppo",
                    args.video,
                )
            )
    population = load_manifest(args.population_manifest)
    checkpoints = valid_checkpoints(population.get("checkpoints", []))
    k_values = sorted({int(x.strip()) for x in args.num_average_agents.split(",") if x.strip()})
    aggregators = [x.strip() for x in args.aggregators.split(",") if x.strip()]
    for k in k_values:
        if k < 2 or len(checkpoints) < k:
            continue
        for aggregator in aggregators:
            commands.append(
                eval_command(
                    args.isaaclab_dir,
                    args.task,
                    checkpoints[:k],
                    aggregator,
                    args.episodes,
                    args.num_envs,
                    args.output_dir / f"k{k}_{aggregator}",
                    args.video,
                )
            )
    if not commands:
        raise SystemExit("No Isaac checkpoints found to evaluate.")
    for command in commands:
        print(" ".join(command))
        if not args.dry_run:
            subprocess.run(command, check=True)


if __name__ == "__main__":
    main()

