#!/usr/bin/env python3
"""Commit and push a fanqie-plus project checkpoint."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def run_git(project_root: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def is_git_repo(project_root: Path) -> bool:
    proc = run_git(project_root, ["rev-parse", "--is-inside-work-tree"])
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def has_remote(project_root: Path) -> bool:
    proc = run_git(project_root, ["remote"])
    return proc.returncode == 0 and bool(proc.stdout.strip())


def has_upstream(project_root: Path) -> bool:
    proc = run_git(project_root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    return proc.returncode == 0 and bool(proc.stdout.strip())


def ensure_git_identity(project_root: Path) -> None:
    name = run_git(project_root, ["config", "user.name"]).stdout.strip()
    email = run_git(project_root, ["config", "user.email"]).stdout.strip()
    if not name:
        run_git(project_root, ["config", "user.name", "fanqie-plus agent"], check=True)
    if not email:
        run_git(project_root, ["config", "user.email", "fanqie-plus@example.local"], check=True)


def status_porcelain(project_root: Path) -> str:
    proc = run_git(project_root, ["status", "--porcelain"])
    return proc.stdout


def push_if_requested(project_root: Path, no_push: bool) -> int:
    if no_push:
        print("OK push skipped")
        return 0

    if not has_remote(project_root):
        print(
            "ERROR no git remote configured; local commit is not protected from temporary workspace cleanup",
            file=sys.stderr,
        )
        return 2

    if has_upstream(project_root):
        push = run_git(project_root, ["push"])
    else:
        branch = run_git(project_root, ["branch", "--show-current"]).stdout.strip() or "main"
        push = run_git(project_root, ["push", "-u", "origin", branch])
    if push.returncode != 0:
        print(push.stdout, end="")
        print(push.stderr, end="", file=sys.stderr)
        return push.returncode or 1
    print("OK pushed")
    if push.stdout.strip():
        print(push.stdout.strip())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Commit and push a fanqie-plus project checkpoint.")
    parser.add_argument("--project-root", default=".", help="Book project root.")
    parser.add_argument("--message", required=True, help="Commit message.")
    parser.add_argument("--no-push", action="store_true", help="Commit only; do not push.")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        print(f"ERROR project root does not exist: {project_root}", file=sys.stderr)
        return 2
    if not is_git_repo(project_root):
        print("ERROR project root is not a git repository", file=sys.stderr)
        return 2

    ensure_git_identity(project_root)
    run_git(project_root, ["add", "-A"], check=True)
    if not status_porcelain(project_root).strip():
        print("OK no changes to commit")
        return push_if_requested(project_root, args.no_push)

    commit = run_git(project_root, ["commit", "-m", args.message])
    if commit.returncode != 0:
        print(commit.stdout, end="")
        print(commit.stderr, end="", file=sys.stderr)
        return commit.returncode or 1
    print("OK committed")
    print(commit.stdout.strip())

    return push_if_requested(project_root, args.no_push)


if __name__ == "__main__":
    raise SystemExit(main())
