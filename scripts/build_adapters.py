#!/usr/bin/env python3
"""Generate tool adapter skill copies from the shared core skill."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_SKILL = ROOT / "core/fanqie-plus"
TARGETS = [
    ROOT / "adapters/codex/skills/fanqie-plus",
    ROOT / "adapters/gemini/skills/fanqie-plus",
    ROOT / "adapters/windsurf/.windsurf/skills/fanqie-plus",
]


def copy_skill(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CORE_SKILL, target)
    print(f"Synced {CORE_SKILL.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


def main() -> int:
    if not CORE_SKILL.exists():
        raise SystemExit(f"Missing core skill: {CORE_SKILL}")
    for target in TARGETS:
        copy_skill(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
