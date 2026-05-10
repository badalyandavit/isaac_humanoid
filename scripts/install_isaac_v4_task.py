from __future__ import annotations

import argparse
from pathlib import Path

from humanoid_rl.isaaclab import load_isaac_ppo_config, validate_isaaclab_dir
from humanoid_rl.utils import ensure_dir


BEGIN_MARKER = "# BEGIN HUMANOID_RL_V4_TASK"
END_MARKER = "# END HUMANOID_RL_V4_TASK"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the custom Humanoid V4 Isaac Lab task.")
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_v4.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def registration_block() -> str:
    return f"""
{BEGIN_MARKER}
import gymnasium as gym
from . import agents
from .humanoid_v4_env import HumanoidV4Env, HumanoidV4EnvCfg

for _humanoid_rl_task_id in (
    "Isaac-Humanoid-V4-Direct-v0",
    "Isaac-Humanoid-V9-Direct-v0",
    "Isaac-Humanoid-V14-Direct-v0",
    "Isaac-Humanoid-V16-Direct-v0",
    "Isaac-Humanoid-V17-Direct-v0",
    "Isaac-Humanoid-V18-Direct-v0",
):
    gym.register(
        id=_humanoid_rl_task_id,
        entry_point=f"{{__name__}}.humanoid_v4_env:HumanoidV4Env",
        disable_env_checker=True,
        kwargs={{
            "env_cfg_entry_point": f"{{__name__}}.humanoid_v4_env:HumanoidV4EnvCfg",
            "rl_games_cfg_entry_point": f"{{agents.__name__}}:rl_games_ppo_cfg.yaml",
            "rsl_rl_cfg_entry_point": f"{{agents.__name__}}.rsl_rl_ppo_cfg:HumanoidPPORunnerCfg",
            "skrl_cfg_entry_point": f"{{agents.__name__}}:skrl_ppo_cfg.yaml",
        }},
    )
{END_MARKER}
"""


def replace_marked_block(text: str, block: str) -> str:
    if BEGIN_MARKER not in text:
        return text.rstrip() + "\n\n" + block.lstrip()
    start = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER, start) + len(END_MARKER)
    return text[:start].rstrip() + "\n\n" + block.strip() + "\n" + text[end:].lstrip()


def main() -> None:
    args = parse_args()
    cfg = load_isaac_ppo_config(args.config)
    isaaclab_dir = Path(cfg.isaaclab_dir)
    validate_isaaclab_dir(isaaclab_dir)

    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "src" / "humanoid_rl" / "isaac_tasks" / "v4_humanoid_env.py"
    target_pkg = isaaclab_dir / "source" / "isaaclab_tasks" / "isaaclab_tasks" / "direct" / "humanoid"
    target_env = target_pkg / "humanoid_v4_env.py"
    target_init = target_pkg / "__init__.py"

    if not template.exists():
        raise FileNotFoundError(f"V4 task template not found: {template}")
    if not target_init.exists():
        raise FileNotFoundError(f"Isaac Humanoid package __init__.py not found: {target_init}")

    source = template.read_text(encoding="utf-8")
    init_text = target_init.read_text(encoding="utf-8")
    patched_init = replace_marked_block(init_text, registration_block())

    print(f"V4 task module: {target_env}")
    print(f"V4 registration: {target_init}")
    if args.dry_run:
        print("Dry run only; no files written.")
        return

    ensure_dir(target_pkg)
    target_env.write_text(source, encoding="utf-8")
    target_init.write_text(patched_init, encoding="utf-8")
    print("Installed custom Isaac Humanoid V4/V9/V14/V16/V17/V18 task ids.")


if __name__ == "__main__":
    main()
