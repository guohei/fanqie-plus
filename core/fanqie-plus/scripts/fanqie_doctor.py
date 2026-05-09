#!/usr/bin/env python3
"""Check fanqie-plus project workflow and checkpoint readiness."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


REQUIRED_DIRS = [
    ".fanqie-plus",
    "00_config",
    "01_bible",
    "02_outline",
    "03_memory",
    "04_chapters/drafts",
    "04_chapters/final",
    "05_reviews",
    "06_export/fanqie",
]

REQUIRED_EMBEDDED_FILES = [
    ".fanqie-plus/SKILL.md",
    ".fanqie-plus/manifest.json",
    ".fanqie-plus/scripts/gate_check.py",
    ".fanqie-plus/scripts/fanqie_doctor.py",
    ".fanqie-plus/scripts/git_checkpoint.py",
]


@dataclass
class Finding:
    severity: str
    message: str


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _chapter_re(chapter: int) -> re.Pattern[str]:
    return re.compile(rf"第\s*0*{chapter}\s*章")


def _find_chapter_file(root: Path, rel_dir: str, chapter: int) -> Path | None:
    directory = root / rel_dir
    if not directory.is_dir():
        return None
    pattern = _chapter_re(chapter)
    for path in sorted(directory.glob("*.md")):
        if pattern.search(path.name):
            return path
    return None


def _find_numbered_artifact(root: Path, rel_dir: str, chapter: int, suffix: str, extension: str) -> Path | None:
    directory = root / rel_dir
    if not directory.is_dir():
        return None
    pattern = re.compile(
        rf"第\s*0*{chapter}\s*章{re.escape(suffix)}{re.escape(extension)}$"
    )
    for path in sorted(directory.glob(f"*{extension}")):
        if pattern.search(path.name):
            return path
    return None


def _chapter_numbers(root: Path) -> list[int]:
    final_dir = root / "04_chapters" / "final"
    if not final_dir.is_dir():
        return []
    numbers: list[int] = []
    for path in final_dir.glob("*.md"):
        match = re.search(r"第\s*0*(\d+)\s*章", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return sorted(set(numbers))


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, f"invalid json: {e}"
    if not isinstance(data, dict):
        return None, "json root is not an object"
    return data, None


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None


def _checkpoint_severity(require_git_remote: bool) -> str:
    return "BLOCKED" if require_git_remote else "WARN"


def _check_git_remote(root: Path, findings: list[Finding], require_git_remote: bool) -> None:
    severity = _checkpoint_severity(require_git_remote)
    repo = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if repo is None or repo.returncode != 0 or repo.stdout.strip() != "true":
        findings.append(Finding(severity, "project root is not a git repository; checkpoint push unavailable"))
        return

    remote = _run_git(root, ["remote"])
    if remote is None or remote.returncode != 0 or not remote.stdout.strip():
        findings.append(Finding(severity, "git remote is not configured; checkpoint push cannot protect temporary workspaces"))


def _parse_review_chapter(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"(\d+)", str(value))
    return int(match.group(1)) if match else None


def _has_summary(root: Path, chapter: int) -> bool:
    path = root / "03_memory" / "chapter_summaries.md"
    if not path.is_file():
        return False
    return bool(_chapter_re(chapter).search(path.read_text(encoding="utf-8")))


def _has_pacing_row(root: Path, chapter: int) -> bool:
    path = root / "03_memory" / "pacing_ledger.csv"
    if not path.is_file():
        return False
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                raw = (row.get("chapter") or "").strip()
                if raw.isdigit() and int(raw) == chapter:
                    return True
    except csv.Error:
        return False
    return False


def _consistency_report_exists(root: Path, chapter: int) -> bool:
    directory = root / "05_reviews" / "consistency"
    if not directory.is_dir():
        return False
    names = {
        f"chapter-{chapter}.md",
        f"chapter-{chapter:03d}.md",
        f"第{chapter}章.md",
    }
    return any((directory / name).is_file() for name in names)


def _check_gate(root: Path, chapter: int, findings: list[Finding]) -> None:
    default_gate = root / "05_reviews" / f"第{chapter}章-gate.json"
    gate = _find_numbered_artifact(root, "05_reviews", chapter, "-gate", ".json")
    if not gate:
        findings.append(Finding("BLOCKED", f"missing {_rel(root, default_gate)}"))
        return
    data, err = _read_json(gate)
    if err:
        findings.append(Finding("BLOCKED", f"invalid {_rel(root, gate)}: {err}"))
        return
    if data and data.get("passed") is not True:
        findings.append(Finding("BLOCKED", f"{_rel(root, gate)} did not pass"))
    blocking = data.get("blocking_findings") if data else None
    if isinstance(blocking, list) and blocking:
        findings.append(Finding("BLOCKED", f"{_rel(root, gate)} has {len(blocking)} blocking finding(s)"))


def check_chapter(root: Path, chapter: int) -> list[Finding]:
    findings: list[Finding] = []

    required_artifacts = [
        ("05_reviews", "-beat", ".md", root / "05_reviews" / f"第{chapter}章-beat.md"),
        ("04_chapters/drafts", "", ".md", root / "04_chapters" / "drafts" / f"第{chapter}章.md"),
    ]
    for rel_dir, suffix, extension, default_path in required_artifacts:
        if not _find_numbered_artifact(root, rel_dir, chapter, suffix, extension):
            findings.append(Finding("BLOCKED", f"missing {_rel(root, default_path)}"))

    if not _find_chapter_file(root, "04_chapters/final", chapter):
        findings.append(Finding("BLOCKED", f"missing 04_chapters/final/第{chapter}章*.md"))

    _check_gate(root, chapter, findings)

    state_path = root / "03_memory" / "novel_state.json"
    state, err = _read_json(state_path)
    if err:
        findings.append(Finding("BLOCKED", f"invalid {_rel(root, state_path)}: {err}"))
    else:
        current = state.get("current_chapter") if state else None
        if current != chapter:
            findings.append(Finding("BLOCKED", f"novel_state.current_chapter is {current}, expected {chapter}"))

    if not _has_summary(root, chapter):
        findings.append(Finding("BLOCKED", f"missing chapter_summaries.md entry for 第{chapter}章"))
    if not _has_pacing_row(root, chapter):
        findings.append(Finding("BLOCKED", f"missing pacing_ledger.csv row for 第{chapter}章"))

    return findings


def check_project(root: Path, require_git_remote: bool = False) -> list[Finding]:
    findings: list[Finding] = []

    agents = root / "AGENTS.md"
    if not agents.is_file():
        findings.append(Finding("BLOCKED", "missing AGENTS.md"))
    else:
        agents_text = agents.read_text(encoding="utf-8")
        if "fanqie-plus" not in agents_text:
            findings.append(Finding("BLOCKED", "AGENTS.md does not mention fanqie-plus"))
        if ".fanqie-plus" not in agents_text:
            findings.append(Finding("BLOCKED", "AGENTS.md does not mention .fanqie-plus"))

    _check_git_remote(root, findings, require_git_remote)

    for rel_dir in REQUIRED_DIRS:
        if not (root / rel_dir).is_dir():
            findings.append(Finding("BLOCKED", f"missing directory {rel_dir}"))

    for rel_file in REQUIRED_EMBEDDED_FILES:
        if not (root / rel_file).is_file():
            findings.append(Finding("BLOCKED", f"missing {rel_file}"))

    chapters = _chapter_numbers(root)
    if not chapters:
        findings.append(Finding("WARN", "no final chapters found"))
        return findings

    latest = chapters[-1]
    findings.extend(check_chapter(root, latest))

    state_path = root / "03_memory" / "novel_state.json"
    state, err = _read_json(state_path)
    if not err and state:
        current = state.get("current_chapter")
        if current != latest:
            findings.append(Finding("BLOCKED", f"novel_state.current_chapter is {current}, latest final chapter is {latest}"))
        review_due = _parse_review_chapter(state.get("next_required_review"))
        if review_due is not None and latest >= review_due:
            if not _consistency_report_exists(root, review_due):
                findings.append(Finding("BLOCKED", f"next_required_review {state.get('next_required_review')} is due"))

    for due in range(10, latest + 1, 10):
        if not _consistency_report_exists(root, due):
            findings.append(Finding("BLOCKED", f"missing 05_reviews/consistency/chapter-{due:03d}.md"))

    return findings


def _print_findings(command: str, findings: list[Finding]) -> None:
    blocked = [f for f in findings if f.severity == "BLOCKED"]
    warnings = [f for f in findings if f.severity == "WARN"]
    if not blocked:
        print(f"OK {command}")
    for finding in findings:
        print(f"{finding.severity} {finding.message}")
    if warnings and not blocked:
        print(f"WARNINGS {len(warnings)}")


def _return_code(findings: list[Finding]) -> int:
    return 1 if any(f.severity == "BLOCKED" for f in findings) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check fanqie-plus project workflow and checkpoint readiness.")
    parser.add_argument("--project-root", required=True, help="fanqie-plus book project root")
    sub = parser.add_subparsers(dest="cmd", required=True)

    project = sub.add_parser("project-check", help="Check project skeleton, latest chapter transaction, review due state, and optional Git remote readiness.")
    project.add_argument(
        "--require-git-remote",
        action="store_true",
        help="Block when the project is not a git repo or has no remote. Use for temporary/cloud workspaces and handoff.",
    )
    chapter = sub.add_parser("chapter-check", help="Check one chapter transaction is complete.")
    chapter.add_argument("--chapter", type=int, required=True, help="Chapter number to check.")

    args = parser.parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR project root does not exist: {root}", file=sys.stderr)
        return 2

    if args.cmd == "project-check":
        findings = check_project(root, require_git_remote=args.require_git_remote)
    elif args.cmd == "chapter-check":
        findings = check_chapter(root, args.chapter)
    else:
        return 2

    _print_findings(args.cmd, findings)
    return _return_code(findings)


if __name__ == "__main__":
    raise SystemExit(main())
