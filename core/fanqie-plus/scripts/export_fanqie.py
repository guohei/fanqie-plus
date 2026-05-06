#!/usr/bin/env python3
"""Export final chapters to Fanqie-ready plain text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from gate_check import check as run_gate


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


def validate_chapters(chapters: list[Path], min_chars: int, max_chars: int, fail_on_warning: bool) -> list[dict]:
    failures: list[dict] = []
    for chapter in chapters:
        result = run_gate(chapter, min_chars, max_chars)
        if not result["passed"] or (fail_on_warning and result["warnings"]):
            failures.append(result)
    return failures


def print_gate_failures(failures: list[dict]) -> None:
    print("Export blocked: source chapters failed mechanical gates.", file=sys.stderr)
    for result in failures:
        print(f"- {result['path']}", file=sys.stderr)
        for finding in result["blocking_findings"]:
            print(f"  blocking: {finding['type']}", file=sys.stderr)
        for warning in result["warnings"]:
            print(f"  warning: {warning['type']}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Fanqie plain text from final chapters.")
    parser.add_argument("project_dir")
    parser.add_argument("--source", default="04_chapters/final")
    parser.add_argument("--out-dir", default="06_export/fanqie")
    parser.add_argument("--combined", action="store_true", help="Also write all chapters to full.txt.")
    parser.add_argument("--min-chars", type=int, default=2000)
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument("--fail-on-warning", action="store_true", help="Block export when mechanical gate warnings exist.")
    parser.add_argument("--no-gate", action="store_true", help="Skip mechanical gates and only transform text.")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    source = root / args.source
    out_dir = root / args.out_dir

    chapters = sorted(source.glob("*.md"), key=chapter_number)
    if not chapters:
        raise SystemExit(f"No .md chapters found in {source}")

    if not args.no_gate:
        failures = validate_chapters(chapters, args.min_chars, args.max_chars, args.fail_on_warning)
        if failures:
            print_gate_failures(failures)
            return 1

    out_dir.mkdir(parents=True, exist_ok=True)
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
