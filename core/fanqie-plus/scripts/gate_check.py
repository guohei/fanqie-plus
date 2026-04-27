#!/usr/bin/env python3
"""Run mechanical checks on a chapter file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


META_PATTERNS = [
    r"TODO",
    r"\[说明\]",
    r"（注[:：]",
    r"Beat Sheet",
    r"Quality Gate",
    r"门禁",
    r"本章字数",
    r"情感锚点",
    r"结尾钩子",
    r"作者的话",
]

PLATFORM_BLOCK_PATTERNS = [
    (r"https?://\S+", "url"),
    (r"\bwww\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "url"),
    (r"\b[A-Za-z0-9.-]+\.(?:com|cn|net|org|top|xyz|vip|cc|io|me)\b", "domain"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "email"),
    (r"(?<!\d)1[3-9]\d{9}(?!\d)", "phone_number"),
    (r"(?:微信|微.?信|VX|vx|V信|v信|QQ|企鹅号|群号|公众号|二维码|扫码|加群|进群|私信|私聊|关注我)", "contact_or_diversion"),
    (r"(?:完整版|未删减|番外).{0,12}(?:群|网盘|链接|私信|主页|公众号|外站)", "off_platform_access"),
    (r"(?:淘宝|拼多多|京东|支付宝|微信支付|下单|优惠券|返利|赞助|广告合作|商务合作|打赏|众筹)", "advertising_or_transaction"),
]

HOOK_HINTS = ["？", "！", "竟", "却", "忽然", "门外", "电话", "系统", "危险", "真相", "名字", "声音", "短信"]


def count_cjk(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def check(path: Path, min_chars: int, max_chars: int) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    nonempty = [line for line in lines if line.strip()]
    findings: list[dict] = []
    warnings: list[dict] = []

    title_ok = bool(nonempty and re.match(r"^#?\s*第\s*\d+\s*章", nonempty[0]))
    if not title_ok:
        findings.append({"type": "missing_title", "message": "Chapter should start with 第N章 title."})

    cjk = count_cjk(text)
    if cjk < min_chars:
        warnings.append({"type": "short_chapter", "message": f"CJK character count {cjk} is below {min_chars}."})
    if cjk > max_chars:
        warnings.append({"type": "long_chapter", "message": f"CJK character count {cjk} is above {max_chars}."})

    for pattern in META_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append({"type": "meta_contamination", "pattern": pattern})

    for pattern, kind in PLATFORM_BLOCK_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append({"type": "platform_compliance", "kind": kind, "pattern": pattern})

    markdown_lines = [line for line in lines if re.match(r"^\s*(```|---|>|[-*]\s+\[|#{2,}\s)", line)]
    if markdown_lines:
        warnings.append({"type": "markdown_artifacts", "count": len(markdown_lines)})

    blank_runs = re.findall(r"\n\s*\n\s*\n+", text)
    if blank_runs:
        warnings.append({"type": "excess_blank_lines", "count": len(blank_runs)})

    tail = text[-500:]
    if not any(hint in tail for hint in HOOK_HINTS):
        warnings.append({"type": "weak_hook_signal", "message": "Ending lacks common hook signals; perform semantic hook review."})

    return {
        "path": str(path),
        "passed": not findings,
        "cjk_chars": cjk,
        "blocking_findings": findings,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanical Fanqie chapter gate.")
    parser.add_argument("chapter_file")
    parser.add_argument("--min-chars", type=int, default=1800)
    parser.add_argument("--max-chars", type=int, default=4500)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()

    result = check(Path(args.chapter_file), args.min_chars, args.max_chars)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
