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

MULTI_REVIEW_MODES = {"auto", "live", "prompt-pack", "simulated", "off"}
MULTI_REVIEW_PRESETS = {
    "dual": ["gold-author", "chief-editor"],
    "roundtable": ["gold-author", "chief-editor", "veteran-reader"],
}
MULTI_REVIEW_ROLES = {
    "gold-author": {
        "title": "番茄金番作家",
        "mission": "从爆款作者视角审爽点、节奏、钩子、名场面和章节落点。",
        "focus": [
            "本章爽点或情绪兑现是否可见",
            "章首压力是否足够近",
            "章末钩子是否让读者想点下一章",
            "桥段是否像可连载的番茄商业章，而不是剧情说明书",
        ],
    },
    "chief-editor": {
        "title": "番茄主编",
        "mission": "从平台主编视角审商业承诺、题材适配、毒点和关键节点风险。",
        "focus": [
            "是否兑现标题、简介、黄金三章或当前阶段承诺",
            "是否有劝退毒点、平台风险或读者预期错位",
            "是否存在必须先修再继续的结构性问题",
            "修复建议是否足够小，不伤害连载推进",
        ],
    },
    "veteran-reader": {
        "title": "看书十年的老书虫",
        "mission": "从真实追更读者视角审无聊段、套路疲劳、角色降智和追读欲。",
        "focus": [
            "哪些段落最想滑走",
            "角色行为是否像活人，还是为了剧情硬转",
            "套路是否疲劳，是否缺少新鲜变量",
            "读完本章后最想知道什么，以及是否足够具体",
        ],
    },
    "platform-operator": {
        "title": "连载运营编辑",
        "mission": "从连载运营视角审更新稳定性、阶段节奏和商业节点准备。",
        "focus": [
            "当前章节是否服务 8w、10w、15w 或卷末节点",
            "是否存在连续慢章、连续高潮或缓冲不足",
            "下一章期待是否清晰可运营",
            "哪些问题可以进 backlog，不要阻塞日更",
        ],
    },
}


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


def _read_excerpt(path: Path, limit: int = 3000, tail: bool = False) -> str:
    if not path.is_file():
        return "（缺失）"
    text = path.read_text(encoding="utf-8")
    if len(text) <= limit:
        return text
    excerpt = text[-limit:] if tail else text[:limit]
    marker = "（前文截断，仅保留末尾）" if tail else "（后文截断）"
    return f"{excerpt}\n\n{marker}"


def _multi_review_roles(preset: str, roles_arg: str | None) -> list[str]:
    roles = [r.strip() for r in roles_arg.split(",")] if roles_arg else MULTI_REVIEW_PRESETS[preset]
    unknown = [r for r in roles if r not in MULTI_REVIEW_ROLES]
    if unknown:
        raise ValueError(f"unknown role(s): {', '.join(unknown)}")
    return roles


def _multi_review_context(fanqie_root: Path) -> str:
    parts = [
        ("Style Bible", fanqie_root / "00_config" / "style_bible.md", 2000, False),
        ("Chapter Queue", fanqie_root / "02_outline" / "chapter_queue.yaml", 3000, False),
        ("Recent Chapter Summaries", fanqie_root / "03_memory" / "chapter_summaries.md", 3000, True),
        ("Foreshadowing", fanqie_root / "01_bible" / "foreshadowing.yaml", 2000, False),
    ]
    rendered = []
    for title, path, limit, tail in parts:
        rendered.append(f"## {title}\n\n{_read_excerpt(path, limit=limit, tail=tail)}")
    return "\n\n".join(rendered)


def _render_role_prompt(
    *,
    chapter: int,
    chapter_content: str,
    context: str,
    role_key: str,
    requested_mode: str,
    resolved_mode: str,
) -> str:
    role = MULTI_REVIEW_ROLES[role_key]
    focus = "\n".join(f"- {item}" for item in role["focus"])
    return f"""# 多角色外部审稿 Prompt

## 角色

你是{role["title"]}。{role["mission"]}

## 审稿模式

- requested_mode: {requested_mode}
- resolved_mode: {resolved_mode}
- 你只负责独立审稿，不负责汇总，不直接改写正文。

## 最小上下文包

{context}

## 待审正文

{chapter_content}

## 审稿重点

{focus}

## 输出要求

只输出 P0/P1/P2 问题和最小修复建议。不要客套，不要说"写得不错"。

必须按下列结构输出：

```markdown
# 第{chapter:03d}章 · {role["title"]}审稿报告

## Verdict
- 建议：通过 / 修复后通过 / 强制重写
- P0:
- P1:
- P2:

## Issues
| # | 严重度 | 位置 | 类型 | 问题描述 | 最小修复建议 |
|---|:------:|------|------|---------|-------------|

## Keep
- [最多 3 条，不要泛夸，只保留不能误删的有效功能]
```

规则：
1. 只输出 P0/P1/P2；P0 才能阻塞继续写。
2. 每条问题必须有具体位置或引用原文。
3. 不要改写整章，只给最小修复建议。
4. 子代理或外部审稿人只给意见，不直接改 `04_chapters/final/`。
5. 如果没有 P0/P1/P2，明确写"无阻塞问题"。
"""


def _render_synthesis_prompt(chapter: int, roles: list[str], requested_mode: str, resolved_mode: str) -> str:
    role_titles = ", ".join(MULTI_REVIEW_ROLES[r]["title"] for r in roles)
    return f"""# 第{chapter:03d}章 多角色审稿汇总 Prompt

你是写作 Agent，也是最终总编。你要汇总这些独立审稿报告：{role_titles}。

## 模式

- requested_mode: {requested_mode}
- resolved_mode: {resolved_mode}

## 汇总规则

1. The writing agent remains the chief editor: 只由你裁决是否修改正文。
2. 子代理或外部审稿人只给意见，不直接改 `04_chapters/final/`。
3. 合并重复问题，优先处理 P0，其次处理会影响当前节点的 P1。
4. P2 进入 backlog；不要为了 P2 大修日更章。
5. 若意见冲突，以正文功能、读者承诺、已建记忆和最小修复原则裁决。

## 输出格式

```markdown
# 第{chapter:03d}章 多角色审稿汇总

## Verdict
- passed: true/false
- must repair before continuing:

## Consolidated P0
- [none or issue]

## Consolidated P1
- [none or issue]

## P2 Backlog
- [none or issue]

## Minimal Repair Plan
- [only edits needed before final/next chapter]
```
"""


def run_multi_review(args: argparse.Namespace, fanqie_root: Path) -> int:
    if args.mode not in MULTI_REVIEW_MODES:
        print(f"错误：未知 multi-review mode: {args.mode}", file=sys.stderr)
        return 2
    if args.mode == "off":
        print("[fanqie_audit] multi-review is off", file=sys.stderr)
        return 0
    if args.preset not in MULTI_REVIEW_PRESETS:
        print(f"错误：未知 multi-review preset: {args.preset}", file=sys.stderr)
        return 2

    try:
        chapter = int(args.chapter)
    except ValueError:
        print(f"错误：--chapter 必须是整数（收到 {args.chapter!r}）", file=sys.stderr)
        return 2

    try:
        roles = _multi_review_roles(args.preset, args.roles)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2

    chapter_file = _autoresolve_chapter_file(fanqie_root, chapter)
    if not chapter_file:
        print(f"错误：未在 04_chapters/final/ 找到第 {chapter} 章。", file=sys.stderr)
        return 2

    resolved_mode = "prompt-pack" if args.mode == "auto" else args.mode
    if args.mode == "auto":
        print("[fanqie_audit] auto mode resolved to prompt-pack; CLI cannot inspect runtime subagent tools", file=sys.stderr)

    out_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else fanqie_root / "05_reviews" / "cross" / "multi_review" / f"ch{chapter:03d}"
    )
    if not out_dir.is_absolute():
        out_dir = fanqie_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.prompt.md"):
        stale.unlink()

    chapter_content = chapter_file.read_text(encoding="utf-8")
    context = _multi_review_context(fanqie_root)

    written: list[str] = []
    if resolved_mode == "simulated":
        combined_roles = "\n\n".join(
            _render_role_prompt(
                chapter=chapter,
                chapter_content=chapter_content,
                context=context,
                role_key=role_key,
                requested_mode=args.mode,
                resolved_mode=resolved_mode,
            )
            for role_key in roles
        )
        prompt_path = out_dir / "simulated-roundtable.prompt.md"
        prompt_path.write_text(combined_roles, encoding="utf-8")
        written.append(prompt_path.name)
    else:
        for role_key in roles:
            prompt = _render_role_prompt(
                chapter=chapter,
                chapter_content=chapter_content,
                context=context,
                role_key=role_key,
                requested_mode=args.mode,
                resolved_mode=resolved_mode,
            )
            prompt_path = out_dir / f"{role_key}.prompt.md"
            prompt_path.write_text(prompt, encoding="utf-8")
            written.append(prompt_path.name)

    synthesis_path = out_dir / "00_synthesis.prompt.md"
    synthesis_path.write_text(
        _render_synthesis_prompt(chapter, roles, args.mode, resolved_mode),
        encoding="utf-8",
    )
    written.append(synthesis_path.name)

    manifest = {
        "chapter": chapter,
        "chapter_file": str(chapter_file),
        "requested_mode": args.mode,
        "resolved_mode": resolved_mode,
        "preset": args.preset,
        "roles": [{"key": key, "title": MULTI_REVIEW_ROLES[key]["title"]} for key in roles],
        "output_dir": str(out_dir),
        "prompts": written,
        "rules": [
            "Do not choose live mode unless the current runtime exposes a real delegation/subagent tool.",
            "auto resolves to prompt-pack when live delegation is not explicit.",
            "Simulated roundtable is only a low-trust diagnostic.",
            "The writing agent remains the chief editor.",
            "External reviewers do not directly edit 04_chapters/final/.",
        ],
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[fanqie_audit] multi-review prompts → {out_dir}", file=sys.stderr)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


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

    mr = sub.add_parser("multi-review", help="生成多角色审稿 prompt 包")
    mr.add_argument("--chapter", required=True, help="章节号")
    mr.add_argument("--preset", choices=sorted(MULTI_REVIEW_PRESETS), default="dual")
    mr.add_argument("--mode", choices=sorted(MULTI_REVIEW_MODES), default="auto")
    mr.add_argument("--roles", default=None, help="逗号分隔的角色 key，覆盖 preset")
    mr.add_argument("--output-dir", default=None, help="覆盖默认输出目录")

    args = ap.parse_args()
    fanqie_root = Path(args.project_root).expanduser().resolve()
    if not fanqie_root.is_dir():
        print(f"错误：项目目录不存在 - {fanqie_root}", file=sys.stderr)
        return 2

    if args.cmd == "cross-parse":
        return run_cross_parse(args, fanqie_root)
    if args.cmd == "multi-review":
        return run_multi_review(args, fanqie_root)

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
