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


# AI-pattern fingerprints. Each row: (pattern, max_count, category, severity).
# severity="block" -> blocking_findings (chapter must be repaired)
# severity="warn"  -> warnings (advisory, agent decides)
# Patterns may be plain strings or regex. count=0 means "any occurrence flags".
AI_FINGERPRINTS: list[tuple[str, int, str, str]] = [
    # ---- 万能开场/收尾/转场 (pure AI tells) ----
    ("命运的齿轮", 0, "stock_opening", "block"),
    ("命运的车轮", 0, "stock_opening", "block"),
    ("故事还在继续", 0, "stock_opening", "block"),
    ("故事的开始", 0, "stock_opening", "block"),
    ("在那遥远的", 0, "stock_opening", "block"),
    ("很久很久以前", 0, "stock_opening", "block"),
    ("一切的一切", 0, "stock_opening", "block"),
    ("夜幕降临", 1, "stock_opening", "warn"),
    ("夜幕缓缓降临", 0, "stock_opening", "warn"),
    ("晨光熹微", 1, "stock_opening", "warn"),
    ("月光如水", 1, "stock_opening", "warn"),
    ("华灯初上", 1, "stock_opening", "warn"),

    # ---- 万能氛围 (pure AI tells) ----
    ("时间仿佛静止", 0, "stock_atmosphere", "block"),
    ("时间仿佛凝固", 0, "stock_atmosphere", "block"),
    ("时间仿佛停止", 0, "stock_atmosphere", "block"),
    ("空气仿佛凝固", 0, "stock_atmosphere", "block"),
    ("空气瞬间凝固", 0, "stock_atmosphere", "block"),
    ("气氛瞬间凝固", 0, "stock_atmosphere", "block"),
    ("山雨欲来", 0, "stock_atmosphere", "block"),
    ("空气中弥漫着", 1, "stock_atmosphere", "warn"),
    ("气氛凝重", 1, "stock_atmosphere", "warn"),
    ("鸦雀无声", 1, "stock_atmosphere", "warn"),
    ("寂静无声", 1, "stock_atmosphere", "warn"),
    ("落针可闻", 1, "stock_atmosphere", "warn"),
    ("死寂一般", 1, "stock_atmosphere", "warn"),

    # ---- 抽象总结/议论腔 ----
    ("总而言之", 1, "abstract_summary", "warn"),
    ("综上所述", 0, "abstract_summary", "warn"),
    ("归根结底", 1, "abstract_summary", "warn"),
    ("不得不说", 1, "abstract_summary", "warn"),
    ("值得一提的是", 1, "abstract_summary", "warn"),
    ("令人遗憾的是", 1, "abstract_summary", "warn"),
    ("毫无疑问", 1, "abstract_summary", "warn"),
    ("不可否认", 1, "abstract_summary", "warn"),
    ("显而易见", 1, "abstract_summary", "warn"),
    ("众所周知", 1, "abstract_summary", "warn"),
    ("总的来说", 1, "abstract_summary", "warn"),
    ("不知不觉", 2, "abstract_summary", "warn"),
    ("不知为何", 1, "abstract_summary", "warn"),
    ("与此同时", 2, "abstract_summary", "warn"),
    ("换句话说", 1, "abstract_summary", "warn"),
    ("这意味着", 1, "abstract_summary", "warn"),

    # ---- 直说情绪标签 (the most poisonous AI tell) ----
    (r"(?:他|她|它)(?:很|非常|十分|无比|格外)(?:愤怒|伤心|难过|开心|高兴|震惊|惊讶|无奈|疲惫|紧张|忧虑|担忧|失望|愧疚|懊恼)", 2, "told_emotion", "warn"),
    (r"(?:他|她|它)(?:感到|觉得|心中)(?:一阵|无比|十分|格外)", 2, "told_emotion", "warn"),
    (r"陷入了(?:沉思|沉默|回忆|纠结|挣扎|绝望|沉睡)", 2, "told_emotion", "warn"),
    ("心中涌起", 2, "told_emotion", "warn"),
    ("心中一紧", 2, "told_emotion", "warn"),
    ("心如刀绞", 1, "told_emotion", "warn"),
    ("五味杂陈", 1, "told_emotion", "warn"),
    ("百感交集", 1, "told_emotion", "warn"),
    ("内心五味杂陈", 0, "told_emotion", "warn"),
    ("说不出话来", 2, "told_emotion", "warn"),

    # ---- 万能动作模板 ----
    ("微微一笑", 2, "stock_action", "warn"),
    ("缓缓道", 3, "stock_action", "warn"),
    ("缓缓说道", 2, "stock_action", "warn"),
    ("缓缓开口", 2, "stock_action", "warn"),
    ("淡淡道", 3, "stock_action", "warn"),
    ("淡淡说道", 2, "stock_action", "warn"),
    ("轻轻点头", 2, "stock_action", "warn"),
    ("轻轻摇头", 2, "stock_action", "warn"),
    ("轻轻叹息", 2, "stock_action", "warn"),
    ("轻轻一笑", 2, "stock_action", "warn"),
    ("深深叹息", 1, "stock_action", "warn"),
    ("深深地看", 1, "stock_action", "warn"),
    ("若有所思", 2, "stock_action", "warn"),
    ("若有若无", 1, "stock_action", "warn"),
    ("意味深长", 1, "stock_action", "warn"),
    ("嘴角勾起", 2, "stock_action", "warn"),
    ("嘴角微微上扬", 1, "stock_action", "warn"),
    ("挑了挑眉", 2, "stock_action", "warn"),
    ("勾唇一笑", 1, "stock_action", "warn"),

    # ---- AI 偏爱形容词组合 ----
    ("复杂的眼神", 2, "ai_adjective", "warn"),
    ("复杂的情绪", 2, "ai_adjective", "warn"),
    ("复杂的目光", 2, "ai_adjective", "warn"),
    ("深邃的目光", 1, "ai_adjective", "warn"),
    ("深邃的眼眸", 1, "ai_adjective", "warn"),
    ("略带玩味", 1, "ai_adjective", "warn"),
    ("略带嘲讽", 1, "ai_adjective", "warn"),
    ("略带挑衅", 1, "ai_adjective", "warn"),
    ("幽深而神秘", 0, "ai_adjective", "block"),
    ("古老而沧桑", 0, "ai_adjective", "block"),
    ("难以言喻", 1, "ai_adjective", "warn"),
    ("难以名状", 1, "ai_adjective", "warn"),
    ("无可奈何", 2, "ai_adjective", "warn"),
    (r"莫名(?:的|其妙)", 3, "ai_adjective", "warn"),

    # ---- 翻译腔/解释腔 ----
    (r"在.{1,15}的情况下", 1, "translation_tone", "warn"),
    (r"对于.{1,10}来说", 2, "translation_tone", "warn"),
    (r"作为一(?:个|名|位|种)", 2, "translation_tone", "warn"),
    (r"让.{1,8}成为可能", 0, "translation_tone", "block"),
    ("也就是说", 2, "translation_tone", "warn"),

    # ---- 古风 AI 特征 (玄幻/修仙易冒) ----
    ("颔首", 2, "stock_classical", "warn"),
    ("颔首道", 1, "stock_classical", "warn"),
    ("须知", 2, "stock_classical", "warn"),
    ("要知道", 3, "stock_classical", "warn"),
    ("殊不知", 2, "stock_classical", "warn"),
]


def count_cjk(text: str) -> int:
    return len(re.findall(r"[一-鿿]", text))


def check_ai_fingerprints(text: str) -> tuple[list[dict], list[dict]]:
    """Return (blocking, advisory) AI-pattern findings."""
    blocking: list[dict] = []
    advisory: list[dict] = []
    for pattern, max_count, category, severity in AI_FINGERPRINTS:
        matches = re.findall(pattern, text)
        count = len(matches)
        if count > max_count:
            record = {
                "type": "ai_pattern",
                "category": category,
                "pattern": pattern,
                "count": count,
                "max_allowed": max_count,
            }
            (blocking if severity == "block" else advisory).append(record)
    return blocking, advisory


def check_adverb_overuse(text: str, cjk: int) -> dict | None:
    """Flag chapters where degree adverbs swamp the prose (a common AI tell)."""
    if cjk == 0:
        return None
    count = len(re.findall(r"(?:很|非常|十分|特别|格外|极其|无比)", text))
    rate = count / cjk * 100
    if rate > 2.0:
        return {
            "type": "ai_adverb_overuse",
            "count": count,
            "per_100_chars": round(rate, 2),
            "threshold_per_100_chars": 2.0,
        }
    return None


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

    ai_block, ai_warn = check_ai_fingerprints(text)
    findings.extend(ai_block)
    warnings.extend(ai_warn)

    adverb_finding = check_adverb_overuse(text, cjk)
    if adverb_finding:
        warnings.append(adverb_finding)

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
