#!/usr/bin/env python3
"""Inspect a Fanqie novel project and report the next chapter context checklist."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CHAPTER_RE = re.compile(r"第\s*(\d+)\s*章")


def chapter_number(path: Path) -> int | None:
    match = CHAPTER_RE.search(path.stem)
    return int(match.group(1)) if match else None


def find_latest_chapter(root: Path) -> int:
    nums: list[int] = []
    for folder in [root / "04_chapters/final", root / "04_chapters/drafts"]:
        if folder.exists():
            nums.extend(n for p in folder.glob("*.md") if (n := chapter_number(p)) is not None)
    return max(nums, default=0)


def load_state(root: Path) -> dict:
    state_path = root / "03_memory/novel_state.json"
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Find next chapter and print context checklist.")
    parser.add_argument("project_dir")
    parser.add_argument("--chapter", type=int, default=0, help="Override chapter number.")
    parser.add_argument("--write-brief", action="store_true", help="Write a preflight brief to 05_reviews/.")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    state = load_state(root)
    latest = max(int(state.get("current_chapter", 0) or 0), find_latest_chapter(root))
    chapter = args.chapter or latest + 1

    previous = root / f"04_chapters/final/第{chapter - 1}章.md"
    checklist = {
        "project": str(root),
        "chapter": chapter,
        "target_draft": str(root / f"04_chapters/drafts/第{chapter}章.md"),
        "target_final": str(root / f"04_chapters/final/第{chapter}章.md"),
        "read_first": [
            "00_config/style_bible.md",
            "02_outline/chapter_queue.yaml",
            "02_outline/outline_anchors.yaml",
            "03_memory/novel_state.json",
            "03_memory/chapter_summaries.md",
            f"04_chapters/final/第{chapter - 1}章.md" if chapter > 1 else "",
        ],
        "missing_recommended_files": [],
    }
    for rel in checklist["read_first"]:
        if rel and not (root / rel).exists():
            checklist["missing_recommended_files"].append(rel)

    print(json.dumps(checklist, ensure_ascii=False, indent=2))

    if args.write_brief:
        brief = root / f"05_reviews/第{chapter}章-preflight.md"
        brief.parent.mkdir(parents=True, exist_ok=True)
        previous_note = str(previous) if previous.exists() else "无"
        brief.write_text(
            f"""# 第{chapter}章 Preflight

## Read Set

- `00_config/style_bible.md`
- `02_outline/chapter_queue.yaml`
- `02_outline/outline_anchors.yaml`
- `03_memory/novel_state.json`
- `03_memory/chapter_summaries.md`
- Previous chapter: `{previous_note}`

## Fill Before Drafting

- Pace tier:
- A/B/C quota:
- Reader emotion:
- Ending hook:
- Must not resolve:
- Expected memory updates:
""",
            encoding="utf-8",
        )
        print(f"Wrote brief: {brief}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
