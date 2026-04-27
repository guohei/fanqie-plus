#!/usr/bin/env python3
"""Export final chapters to Fanqie-ready plain text."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CHAPTER_RE = re.compile(r"第\s*(\d+)\s*章")


def chapter_number(path: Path) -> int:
    match = CHAPTER_RE.search(path.stem)
    return int(match.group(1)) if match else 10**9


def clean_text(text: str) -> str:
    cleaned: list[str] = []
    skip_meta = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == "---":
            skip_meta = True
            continue
        if skip_meta and re.search(r"本章字数|情感锚点|结尾钩子|门禁|Quality Gate", line):
            continue
        if line.startswith("```"):
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?<!\*)", r"\1", line)
        line = re.sub(r"`([^`]*)`", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"^>\s*", "", line)
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = line.replace("：", " ", 1) if re.match(r"^第\s*\d+\s*章[:：]", line) else line
        cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Fanqie plain text from final chapters.")
    parser.add_argument("project_dir")
    parser.add_argument("--source", default="04_chapters/final")
    parser.add_argument("--out-dir", default="06_export/fanqie")
    parser.add_argument("--combined", action="store_true", help="Also write all chapters to full.txt.")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    source = root / args.source
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    chapters = sorted(source.glob("*.md"), key=chapter_number)
    if not chapters:
        raise SystemExit(f"No .md chapters found in {source}")

    combined_parts: list[str] = []
    for chapter in chapters:
        text = clean_text(chapter.read_text(encoding="utf-8"))
        out = out_dir / f"{chapter.stem}.txt"
        out.write_text(text, encoding="utf-8")
        combined_parts.append(text.strip())
        print(f"Exported {out}")

    if args.combined:
        full = out_dir / "full.txt"
        full.write_text("\n".join(combined_parts).strip() + "\n", encoding="utf-8")
        print(f"Exported {full}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
