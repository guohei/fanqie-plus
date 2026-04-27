#!/usr/bin/env python3
"""Create a Fanqie long-novel project skeleton."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Fanqie long-novel project.")
    parser.add_argument("project_dir", help="Project directory to create or update.")
    parser.add_argument("--title", default="", help="Novel title.")
    parser.add_argument("--genre", default="", help="Genre/subgenre.")
    parser.add_argument("--target-words", default="100-300万", help="Target total length.")
    parser.add_argument("--chapter-words", default="2000-4000", help="Target characters per chapter.")
    parser.add_argument("--audience", default="番茄移动端长篇网文读者", help="Target reader profile.")
    parser.add_argument("--style", default="第三人称限制视角，移动端爽文节奏，中高对话密度", help="Style summary.")
    parser.add_argument("--automation", default="半自动：每10章和重大转折确认", help="Automation level.")
    parser.add_argument("--forbidden", default="正文不得混入元信息、TODO、作者分析；避免无铺垫背叛和虐点堆砌", help="Forbidden zones.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing seed files.")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    title = args.title or root.name

    dirs = [
        "00_config",
        "01_bible",
        "02_outline",
        "03_memory",
        "04_chapters/drafts",
        "04_chapters/final",
        "05_reviews",
        "06_export/fanqie",
    ]
    for rel in dirs:
        (root / rel).mkdir(parents=True, exist_ok=True)

    write_text(
        root / "00_config/idea_seed.md",
        f"""# Idea Seed

- Title: {title}
- Genre: {args.genre or "未定"}
- Target reader: {args.audience}
- Writing style: {args.style}
- Forbidden zones: {args.forbidden}
- Automation level: {args.automation}
- Target scale: {args.target_words}
- Chapter size: {args.chapter_words}
- Created: {date.today().isoformat()}
""",
        args.force,
    )

    write_text(
        root / "00_config/target_profile.md",
        f"""# Target Profile

## Reader Promise

[写清楚读者为什么会点开、为什么会追更。]

## Shelf

- Platform: 番茄小说
- Genre: {args.genre or "未定"}
- Comparable reader taste: [补充]

## Differentiator

[一句话说明本书和同类题材的差异。]

## Reader Thunder Points

- {args.forbidden}
""",
        args.force,
    )

    write_text(
        root / "00_config/style_bible.md",
        f"""# Style Bible

- POV: 第三人称限制视角
- Tone: {args.style}
- Dialogue density: 中高
- Paragraph target: 移动端短段落
- Sentence rhythm: 长短交替，避免说明文腔
- AI-pattern bans: 总结式议论、泛化情绪标签、连续过渡词、正文元信息

## Character Voice Anchors

[为主角、重要配角、反派分别记录说话习惯和行动策略。]
""",
        args.force,
    )

    write_text(
        root / "00_config/platform_strategy.md",
        f"""# Platform Strategy

## Golden Three Chapters

- Chapter 1: immediate hook and protagonist pressure.
- Chapter 2: visible goal and concrete obstacle.
- Chapter 3: first payoff and strong next-click hook.

## Checkpoints

- 30 chapters: first arc habit formation.
- 8w words: recommendation evaluation preparation.
- 10w words: launch readiness.
- 15w words: automatic evaluation pressure.

## Update Cadence

[记录日更目标、存稿目标、发布时间。]
""",
        args.force,
    )

    write_text(root / "01_bible/characters.yaml", "characters: []\n", args.force)
    write_text(root / "01_bible/timeline.yaml", "events: []\n", args.force)
    write_text(root / "01_bible/foreshadowing.yaml", "threads: []\n", args.force)
    write_text(root / "01_bible/world.md", "# World Bible\n\n[记录世界规则、地点、能力体系、组织势力。]\n", args.force)

    write_text(root / "02_outline/novel_roadmap.md", "# Novel Roadmap\n\n[按阶段/卷记录百万字路线图。]\n", args.force)
    write_text(root / "02_outline/volume_plan.md", "# Volume Plan\n\n[记录每卷目标、字数、高潮、换地图节点。]\n", args.force)
    write_text(root / "02_outline/chapter_queue.yaml", "chapters: []\n", args.force)
    write_text(root / "02_outline/outline_anchors.yaml", "anchors: []\n", args.force)

    state_path = root / "03_memory/novel_state.json"
    if args.force or not state_path.exists():
        state = {
            "title": title,
            "current_chapter": 0,
            "current_words": 0,
            "current_arc": "",
            "last_updated": date.today().isoformat(),
            "open_threads": [],
            "active_characters": [],
            "next_required_review": "第10章",
        }
        write_text(state_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n", True)

    write_text(root / "03_memory/chapter_summaries.md", "# Chapter Summaries\n", args.force)
    ledger_path = root / "03_memory/pacing_ledger.csv"
    if args.force or not ledger_path.exists():
        with ledger_path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(["chapter", "title", "pace", "quota", "hook_type", "words", "gate_passed", "notes"])

    print(f"Initialized Fanqie novel project: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
