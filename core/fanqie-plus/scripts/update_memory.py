#!/usr/bin/env python3
"""Append accepted chapter memory to a Fanqie novel project."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Update memory after an accepted chapter.")
    parser.add_argument("project_dir")
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--emotion", default="")
    parser.add_argument("--hook", default="")
    parser.add_argument("--pace", default="")
    parser.add_argument("--quota", default="")
    parser.add_argument("--words", type=int, default=0)
    parser.add_argument("--gate-passed", default="true")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    memory_dir = root / "03_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    title = args.title or f"第{args.chapter}章"
    summaries = memory_dir / "chapter_summaries.md"
    with summaries.open("a", encoding="utf-8") as handle:
        handle.write(
            f"""
## 第{args.chapter}章 {title}
- Summary: {args.summary}
- Reader emotion: {args.emotion}
- Hook: {args.hook}
- New facts:
- Character changes:
- Foreshadowing:
- Continuity notes: {args.notes}
"""
        )

    state_path = memory_dir / "novel_state.json"
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_chapter"] = max(int(state.get("current_chapter", 0) or 0), args.chapter)
    state["current_words"] = int(state.get("current_words", 0) or 0) + max(args.words, 0)
    state["last_updated"] = date.today().isoformat()
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ledger = memory_dir / "pacing_ledger.csv"
    new_file = not ledger.exists()
    with ledger.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["chapter", "title", "pace", "quota", "hook_type", "words", "gate_passed", "notes"])
        writer.writerow([args.chapter, title, args.pace, args.quota, args.hook, args.words, args.gate_passed, args.notes])

    print(f"Updated memory for 第{args.chapter}章 in {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
