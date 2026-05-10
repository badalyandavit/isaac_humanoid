"""Install skrl SAC and TD3 agent configs for the Isaac humanoid direct task.

Registers a new task id `Isaac-Humanoid-Direct-Multi-v0` that uses the same env
config as the official `Isaac-Humanoid-Direct-v0` but exposes three agent
entry points (PPO, SAC, TD3) so the skrl training launcher can pick the
algorithm via `--algorithm`.

Run on the pod after `setup_isaaclab_runpod.sh`:

    python scripts/install_isaac_skrl_offpolicy.py --config configs/isaac_ppo_baseline.yaml

The installer:
  1. Reads SAC/TD3 hyperparameters from configs/isaac_skrl_sac.yaml and
     configs/isaac_skrl_td3.yaml and copies them into
     <isaaclab>/source/isaaclab_tasks/isaaclab_tasks/direct/humanoid/agents/
     under the names `skrl_sac_humanoid.yaml` and `skrl_td3_humanoid.yaml`
     (the names the gym registration entry points reference).
  2. Adds a marker block to that package's __init__.py that registers the
     Multi-v0 task id with rsl_rl PPO, skrl PPO, skrl SAC, and skrl TD3
     entry points.

Idempotent: re-running replaces the marker block and overwrites the YAMLs.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from humanoid_rl.isaaclab import load_isaac_ppo_config, validate_isaaclab_dir
from humanoid_rl.utils import ensure_dir


BEGIN_MARKER = "# BEGIN HUMANOID_RL_SKRL_OFFPOLICY"
END_MARKER = "# END HUMANOID_RL_SKRL_OFFPOLICY"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=str, default="configs/isaac_ppo_baseline.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def registration_block() -> str:
    return f"""
{BEGIN_MARKER}
import gymnasium as gym
from . import agents
from .humanoid_env import HumanoidEnv, HumanoidEnvCfg

gym.register(
    id="Isaac-Humanoid-Direct-Multi-v0",
    entry_point=f"{{__name__}}.humanoid_env:HumanoidEnv",
    disable_env_checker=True,
    kwargs={{
        "env_cfg_entry_point": f"{{__name__}}.humanoid_env:HumanoidEnvCfg",
        "rsl_rl_cfg_entry_point": f"{{agents.__name__}}.rsl_rl_ppo_cfg:HumanoidPPORunnerCfg",
        "skrl_cfg_entry_point": f"{{agents.__name__}}:skrl_ppo_cfg.yaml",
        "skrl_ppo_cfg_entry_point": f"{{agents.__name__}}:skrl_ppo_cfg.yaml",
        "skrl_sac_cfg_entry_point": f"{{agents.__name__}}:skrl_sac_humanoid.yaml",
        "skrl_td3_cfg_entry_point": f"{{agents.__name__}}:skrl_td3_humanoid.yaml",
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
    sac_src = repo_root / "configs" / "isaac_skrl_sac.yaml"
    td3_src = repo_root / "configs" / "isaac_skrl_td3.yaml"

    target_pkg = isaaclab_dir / "source" / "isaaclab_tasks" / "isaaclab_tasks" / "direct" / "humanoid"
    target_agents_pkg = target_pkg / "agents"
    target_init = target_pkg / "__init__.py"
    target_sac = target_agents_pkg / "skrl_sac_humanoid.yaml"
    target_td3 = target_agents_pkg / "skrl_td3_humanoid.yaml"

    for src in (sac_src, td3_src):
        if not src.exists():
            raise FileNotFoundError(f"YAML template not found: {src}")
    if not target_agents_pkg.exists():
        raise FileNotFoundError(f"Isaac humanoid agents package not found: {target_agents_pkg}")
    if not target_init.exists():
        raise FileNotFoundError(f"Isaac humanoid package __init__.py not found: {target_init}")

    init_text = target_init.read_text(encoding="utf-8")
    patched_init = replace_marked_block(init_text, registration_block())

    print(f"SAC yaml:    {target_sac}")
    print(f"TD3 yaml:    {target_td3}")
    print(f"Patch init:  {target_init}")
    if args.dry_run:
        print("Dry run only; no files written.")
        return

    ensure_dir(target_agents_pkg)
    target_sac.write_text(sac_src.read_text(encoding="utf-8"), encoding="utf-8")
    target_td3.write_text(td3_src.read_text(encoding="utf-8"), encoding="utf-8")
    target_init.write_text(patched_init, encoding="utf-8")
    print("Installed Isaac-Humanoid-Direct-Multi-v0 task with PPO + SAC + TD3 entry points.")


if __name__ == "__main__":
    main()
