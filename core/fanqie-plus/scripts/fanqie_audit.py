#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fanqie_audit.py — fanqie-plus 项目调用 novelist-skill 审稿工具的适配层。

novelist-skill 的 reader_simulator.py 与 cross_agent_reviewer.py 假定项目布局：
  <root>/02-写作计划.json
  <root>/01-大纲.md
  <root>/03_manuscript/第NNN章_xxx.md
  <root>/04_editing/...

fanqie-plus 项目布局：
  <root>/02_outline/chapter_queue.yaml
  <root>/02_outline/novel_roadmap.md
  <root>/03_memory/novel_state.json
  <root>/04_chapters/final/第NNN章_xxx.md
  <root>/05_reviews/...

本脚本在 fanqie-plus 项目下创建一个 .audit_workdir/ 目录，把 fanqie-plus 文件
"投影"成 novelist-skill 期望的形状（用符号链接 + 自动生成的 stub JSON），然后
调用底层脚本，最后把结果复制回 05_reviews/。

依赖：仅 Python 标准库。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from cross_agent_reviewer import parse_review_report

SCRIPT_DIR = Path(__file__).resolve().parent
WORKDIR_NAME = ".audit_workdir"


def build_workdir(fanqie_root: Path) -> Path:
    workdir = fanqie_root / WORKDIR_NAME
    # Reset stale state from previous audit runs so we never copy onto stale
    # files. Only the workdir we own is touched; fanqie source dirs are
    # untouched.
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(exist_ok=True)
    (workdir / "03_manuscript").mkdir(exist_ok=True)
    (workdir / "04_editing").mkdir(exist_ok=True)
    (workdir / "04_editing" / "gate_artifacts").mkdir(exist_ok=True)

    # 03_manuscript: symlink chapter final files
    final_dir = fanqie_root / "04_chapters" / "final"
    if final_dir.is_dir():
        target_dir = workdir / "03_manuscript"
        # clear stale links
        for p in target_dir.iterdir():
            if p.is_symlink() or p.is_file():
                p.unlink()
        for chapter_file in sorted(final_dir.glob("第*.md")):
            link = target_dir / chapter_file.name
            try:
                link.symlink_to(chapter_file.resolve())
            except OSError:
                # filesystems without symlink support → fall back to copy
                shutil.copy2(chapter_file, link)

    # 01-大纲.md: derive from novel_roadmap.md if present
    roadmap = fanqie_root / "02_outline" / "novel_roadmap.md"
    outline_target = workdir / "01-大纲.md"
    if roadmap.is_file():
        if outline_target.exists() or outline_target.is_symlink():
            outline_target.unlink()
        try:
            outline_target.symlink_to(roadmap.resolve())
        except OSError:
            shutil.copy2(roadmap, outline_target)
    else:
        outline_target.write_text("# 大纲（占位）\n\nfanqie-plus 项目尚未生成 02_outline/novel_roadmap.md。\n", encoding="utf-8")

    # 02-写作计划.json: synthesize a minimal valid structure
    plan_path = workdir / "02-写作计划.json"
    plan = synthesize_plan(fanqie_root, workdir)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return workdir


def synthesize_plan(fanqie_root: Path, workdir: Path) -> dict:
    """Build a minimal 02-写作计划.json from fanqie-plus state files.

    Field names follow the schema expected by reader_simulator.py / cross_agent_reviewer.py
    (`chapterNumber`, `filePath`). Chapter files are bridged into `<workdir>/03_manuscript/`
    (where the novelist scripts look) by copying from `<fanqie_root>/04_chapters/final/`.
    """
    final_dir = fanqie_root / "04_chapters" / "final"
    manuscript_dir = workdir / "03_manuscript"
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    chapters = []
    if final_dir.is_dir():
        for f in sorted(final_dir.glob("第*.md")):
            # Expect filename like 第042章_xxx.md
            stem = f.stem
            num_str = "".join(ch for ch in stem.split("章")[0] if ch.isdigit())
            if not num_str:
                continue
            # Bridge chapter file into workdir/03_manuscript so the script's
            # default path resolver finds it. Copy is cheap, robust, and avoids
            # symlink permission issues on some platforms.
            bridged = manuscript_dir / f.name
            if bridged.resolve() == f.resolve():
                # workdir is somehow inside the source dir; skip the copy.
                pass
            else:
                if bridged.exists():
                    bridged.unlink()
                shutil.copy2(f, bridged)
            chapters.append({
                "chapterNumber": int(num_str),
                "title": stem,
                "filePath": f.name,
                "status": "final",
            })

    # Pull thresholds and reader profile from project config if present
    config_path = fanqie_root / "00_config" / "audit_config.json"
    config = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    return {
        "chapters": chapters,
        "gateThresholds": config.get("gateThresholds", {"reader": 70}),
        "readerProfile": config.get("readerProfile", "webnovel_veteran"),
        "_synthesized_by": "fanqie_audit.py",
        "_synthesized_at": datetime.now().isoformat(timespec="seconds"),
    }


def export_artifacts(workdir: Path, fanqie_root: Path, kind: str) -> list[Path]:
    """Copy any audit artifacts from workdir/04_editing/ to fanqie 05_reviews/<kind>/."""
    src = workdir / "04_editing"
    dst = fanqie_root / "05_reviews" / kind
    dst.mkdir(parents=True, exist_ok=True)
    exported = []
    if src.is_dir():
        for p in src.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".json"}:
                rel = p.relative_to(src)
                target = dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                exported.append(target)
    return exported


def run_reader(args: argparse.Namespace, fanqie_root: Path, workdir: Path) -> int:
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "reader_simulator.py"),
        "--project-root", str(workdir),
        "--chapter", str(args.chapter),
    ]
    if args.threshold is not None:
        cmd += ["--threshold", str(args.threshold)]
    if args.reader_profile:
        cmd += ["--reader-profile", args.reader_profile]
    if args.prompt_only:
        cmd += ["--prompt-only"]
    if args.dry_run:
        cmd += ["--dry-run"]
    rc = subprocess.call(cmd)
    exported = export_artifacts(workdir, fanqie_root, "reader")
    for path in exported:
        print(f"[fanqie_audit] exported → {path}", file=sys.stderr)
    return rc


def _autoresolve_chapter_file(fanqie_root: Path, chapter_number: int) -> Path | None:
    """Find 第N章 file in 04_chapters/final/ by chapter number."""
    final_dir = fanqie_root / "04_chapters" / "final"
    if not final_dir.is_dir():
        return None
    # Match "第001章", "第 1 章", "第42章" etc. — any number of leading zeros.
    pattern = re.compile(rf"第\s*0*{chapter_number}\s*章")
    for p in sorted(final_dir.glob("*.md")):
        if pattern.search(p.name):
            return p
    return None


def run_cross_review(args: argparse.Namespace, fanqie_root: Path, workdir: Path) -> int:
    if args.chapter_file:
        chapter_file = (
            Path(args.chapter_file)
            if Path(args.chapter_file).is_absolute()
            else fanqie_root / "04_chapters" / "final" / args.chapter_file
        )
    else:
        try:
            n = int(args.chapter)
        except ValueError:
            print(f"错误：--chapter 必须是整数（收到 {args.chapter!r}）", file=sys.stderr)
            return 2
        resolved = _autoresolve_chapter_file(fanqie_root, n)
        if not resolved:
            print(f"错误：未在 04_chapters/final/ 找到第 {n} 章。请用 --chapter-file 指定。", file=sys.stderr)
            return 2
        chapter_file = resolved
        print(f"[fanqie_audit] auto-resolved chapter file → {chapter_file}", file=sys.stderr)
    # Default --output to an export-friendly path inside workdir/04_editing so
    # export_artifacts() automatically picks it up. User can override with --output.
    output_path = args.output or str(
        workdir / "04_editing" / "cross_review" / f"ch{int(args.chapter):03d}_review_prompt.md"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "cross_agent_reviewer.py"),
        "review",
        "--chapter-file", str(chapter_file),
        "--chapter", str(args.chapter),
        "--project-root", str(workdir),
        "--output", output_path,
    ]
    if args.reviewer:
        cmd += ["--reviewer", args.reviewer]
    if args.round is not None:
        cmd += ["--round", str(args.round)]
    rc = subprocess.call(cmd)
    exported = export_artifacts(workdir, fanqie_root, "cross")
    for path in exported:
        print(f"[fanqie_audit] exported → {path}", file=sys.stderr)
    return rc


def run_cross_batch(args: argparse.Namespace, fanqie_root: Path, workdir: Path) -> int:
    try:
        start = int(args.chapter_start)
        end = int(args.chapter_end)
    except ValueError:
        print(
            f"错误：--chapter-start/--chapter-end 必须是整数（收到 {args.chapter_start!r}, {args.chapter_end!r}）",
            file=sys.stderr,
        )
        return 2

    output_path = args.output or str(
        workdir
        / "04_editing"
        / "cross_review"
        / f"batch_ch{start:03d}-{end:03d}_review_prompt.md"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "cross_agent_reviewer.py"),
        "batch-review",
        "--project-root", str(workdir),
        "--chapter-start", str(args.chapter_start),
        "--chapter-end", str(args.chapter_end),
        "--output", output_path,
    ]
    rc = subprocess.call(cmd)
    exported = export_artifacts(workdir, fanqie_root, "cross")
    for path in exported:
        print(f"[fanqie_audit] exported → {path}", file=sys.stderr)
    return rc


def _resolve_report_file(fanqie_root: Path, report_file: str) -> Path:
    raw = Path(report_file).expanduser()
    candidates = [raw] if raw.is_absolute() else [
        fanqie_root / raw,
        fanqie_root / "05_reviews" / "cross" / raw,
        raw,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    searched = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"未找到外部审稿报告：{report_file}（搜索：{searched}）")


def _default_issues_path(fanqie_root: Path, report_file: Path) -> Path:
    stem = report_file.stem
    for suffix in ("_review_report", "_report"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return fanqie_root / "05_reviews" / "cross" / f"{stem}_issues.json"


def run_cross_parse(args: argparse.Namespace, fanqie_root: Path) -> int:
    try:
        report_file = _resolve_report_file(fanqie_root, args.report_file)
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2

    result = parse_review_report(report_file.read_text(encoding="utf-8"))
    output = Path(args.output).expanduser() if args.output else _default_issues_path(fanqie_root, report_file)
    if not output.is_absolute():
        output = fanqie_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"[fanqie_audit] parsed external review → {output} "
        f"(P0={result['p0_count']}, P1={result['p1_count']}, P2={result['p2_count']})",
        file=sys.stderr,
    )
    return 1 if result["p0_count"] > 0 else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="fanqie_audit.py", description="fanqie-plus → novelist 审稿适配层")
    ap.add_argument("--project-root", required=True, help="fanqie-plus 书籍项目根目录（含 02_outline/、04_chapters/）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reader", help="跑 reader_simulator")
    r.add_argument("--chapter", required=True, help="章节号（如 042）")
    r.add_argument("--threshold", type=int, default=None)
    r.add_argument("--reader-profile", default=None)
    r.add_argument("--prompt-only", action="store_true")
    r.add_argument("--dry-run", action="store_true")

    cr = sub.add_parser("cross-review", help="跑 cross_agent_reviewer review")
    cr.add_argument("--chapter", required=True, help="章节号")
    cr.add_argument("--chapter-file", default=None, help="章节文件路径（相对 04_chapters/final/ 或绝对路径）。若省略则按章节号自动定位。")
    cr.add_argument("--reviewer", default=None)
    cr.add_argument("--round", type=int, default=None)
    cr.add_argument("--output", default=None)

    cb = sub.add_parser("cross-batch", help="跑 cross_agent_reviewer batch-review")
    cb.add_argument("--chapter-start", required=True)
    cb.add_argument("--chapter-end", required=True)
    cb.add_argument("--output", default=None)

    cp = sub.add_parser("cross-parse", help="解析外部审稿报告到 05_reviews/cross/*_issues.json")
    cp.add_argument("--report-file", required=True, help="外部审稿报告路径；可传绝对路径、项目相对路径，或 05_reviews/cross/ 下的文件名。")
    cp.add_argument("--output", default=None, help="覆盖默认 issues JSON 输出路径。")

    args = ap.parse_args()
    fanqie_root = Path(args.project_root).expanduser().resolve()
    if not fanqie_root.is_dir():
        print(f"错误：项目目录不存在 - {fanqie_root}", file=sys.stderr)
        return 2

    if args.cmd == "cross-parse":
        return run_cross_parse(args, fanqie_root)

    workdir = build_workdir(fanqie_root)
    print(f"[fanqie_audit] workdir → {workdir}", file=sys.stderr)

    if args.cmd == "reader":
        return run_reader(args, fanqie_root, workdir)
    if args.cmd == "cross-review":
        return run_cross_review(args, fanqie_root, workdir)
    if args.cmd == "cross-batch":
        return run_cross_batch(args, fanqie_root, workdir)
    return 2


if __name__ == "__main__":
    sys.exit(main())
