#!/usr/bin/env python3
"""Embed fanqie-plus into a book project."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


GITIGNORE_LINES = [
    ".audit_workdir/",
    "__pycache__/",
    "*.pyc",
    ".DS_Store",
]


def _copy_ignore(_dir: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".DS_Store"}
    ignored.update(name for name in names if name.endswith(".pyc"))
    return ignored


def _git_commit(source: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "--short", "HEAD"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def write_gitignore(project_root: Path) -> None:
    path = project_root / ".gitignore"
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    merged = list(existing)
    for line in GITIGNORE_LINES:
        if line not in merged:
            merged.append(line)
    path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")


def embed_skill(project_root: Path, source: Path) -> Path:
    target = project_root / ".fanqie-plus"
    if source != target.resolve():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, ignore=_copy_ignore)
    manifest = {
        "name": "fanqie-plus",
        "embedded_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(source),
        "source_commit": _git_commit(source),
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def write_agents(project_root: Path, embedded_root: Path) -> str:
    template = embedded_root / "assets" / "project_AGENTS.md"
    if not template.is_file():
        raise FileNotFoundError(f"missing project AGENTS template: {template}")
    path = project_root / "AGENTS.md"
    template_text = template.read_text(encoding="utf-8").rstrip() + "\n"
    if not path.exists():
        path.write_text(template_text, encoding="utf-8")
        return "wrote"

    existing = path.read_text(encoding="utf-8")
    if ".fanqie-plus/SKILL.md" in existing:
        return "kept"

    merged = f"{template_text}\n## Existing Project Instructions\n\n{existing.lstrip()}"
    path.write_text(merged.rstrip() + "\n", encoding="utf-8")
    return "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed fanqie-plus into a book project.")
    parser.add_argument("--project-root", required=True, help="Book project root.")
    parser.add_argument(
        "--source",
        default=str(Path(__file__).resolve().parents[1]),
        help="fanqie-plus skill source directory. Defaults to this script's skill root.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    source = Path(args.source).expanduser().resolve()
    if not source.joinpath("SKILL.md").is_file():
        print(f"ERROR source is not a fanqie-plus skill root: {source}", file=sys.stderr)
        return 2
    project_root.mkdir(parents=True, exist_ok=True)

    embedded = embed_skill(project_root, source)
    agents_status = write_agents(project_root, embedded)
    write_gitignore(project_root)
    print(f"OK embedded fanqie-plus -> {embedded}")
    print(f"OK {agents_status} AGENTS.md")
    print("OK updated .gitignore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
