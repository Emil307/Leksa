#!/usr/bin/env python3
"""Validate the repository's Claude-to-Codex compatibility layer."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    sync_script = REPO_ROOT / ".codex" / "scripts" / "sync_claude_agents.py"
    subprocess.run([sys.executable, str(sync_script), "--check"], check=True)

    with (REPO_ROOT / ".codex" / "config.toml").open("rb") as config_file:
        tomllib.load(config_file)
    with (REPO_ROOT / ".codex" / "hooks.json").open(encoding="utf-8") as hooks_file:
        json.load(hooks_file)

    agent_files = sorted((REPO_ROOT / ".codex" / "agents").glob("*.toml"))
    source_agents = sorted((REPO_ROOT / ".claude" / "agents").glob("*.md"))
    if len(agent_files) != len(source_agents):
        raise RuntimeError(
            f"agent count mismatch: {len(source_agents)} Claude, {len(agent_files)} Codex"
        )
    for agent_file in agent_files:
        with agent_file.open("rb") as toml_file:
            agent = tomllib.load(toml_file)
        missing = {"name", "description", "developer_instructions"} - agent.keys()
        if missing:
            raise RuntimeError(f"{agent_file}: missing {sorted(missing)}")

    skill_link = REPO_ROOT / ".agents" / "skills"
    expected_skills = (REPO_ROOT / ".claude" / "skills").resolve()
    if not skill_link.is_symlink() or skill_link.resolve() != expected_skills:
        raise RuntimeError(".agents/skills must link to .claude/skills")
    skill_files = sorted(skill_link.glob("*/SKILL.md"))
    source_skills = sorted(expected_skills.glob("*/SKILL.md"))
    if len(skill_files) != len(source_skills):
        raise RuntimeError(
            f"skill count mismatch: {len(source_skills)} Claude, {len(skill_files)} Codex"
        )

    subprocess.run(
        ["bash", str(REPO_ROOT / ".claude" / "hooks" / "agent-timing-smoke.sh")],
        cwd=REPO_ROOT,
        check=True,
    )
    print(
        f"Codex compatibility OK: {len(agent_files)} agents, "
        f"{len(skill_files)} skills, config and hooks valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
