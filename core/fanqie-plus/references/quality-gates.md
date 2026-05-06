# Quality Gates

Use these gates after every chapter. Mechanical checks can be scripted; semantic checks require agent judgment.

## Blocking Gates

If any blocking gate fails, repair before continuing.

| Gate | Failure examples |
| --- | --- |
| Meta contamination | TODO, author note, analysis, beat labels, gate comments inside正文 |
| Chapter length | Below or above the project/default chapter range, normally 2000-4000 Chinese characters |
| Platform compliance | URL, email, social/contact account, QR code, off-platform group, ad, transaction guidance, or unsafe policy content |
| Missing hook | Ending has no concrete next-click reason |
| Anchor violation | Resolves forbidden main conflict or outruns current outline anchor |
| Quota violation | A/B/C major events triggered together |
| Continuity break | Character state, timeline, ability, or setting contradicts tracked memory |
| Style break | POV switches accidentally, character voice collapses, prose becomes explanatory |
| Golden three miss | Chapter 1-3 fails its required Fanqie opening function |

## Advisory Gates

These usually require improvement but may not block a slow setup chapter:

- Weak conflict intensity.
- Low emotional feedback.
- Too much exposition.
- Similar dialogue voices.
- Repeated transition phrases.
- Paragraphs too long for mobile reading.
- Ending hook exists but feels generic.

## Mechanical Check Patterns

Use `scripts/gate_check.py` for:

- Character count range. Default 2000-4000 CJK characters is blocking unless project config explicitly overrides it.
- Forbidden meta markers.
- URL/contact/ad/off-platform diversion patterns.
- Markdown artifacts.
- Blank-line/format issues.
- Missing title.
- Weak hook keywords as a warning.

## Semantic Review Template

```markdown
# 第N章 Quality Gate

## Verdict
passed: true/false

## Blocking Findings
- [none or concrete finding]

## Advisory Findings
- [issue and fix]

## Pace Review
- Tier: slow/medium/fast
- A/B/C triggered: A/B/C/none
- Quota violation: yes/no
- Hidden acceleration: yes/no

## Continuity
- Character state changes:
- Timeline changes:
- Foreshadowing added:
- Foreshadowing resolved:

## Repair Plan
If failed, list the smallest repair path.
```

## AI-Pattern Cleanup

AI-generated Chinese prose has reliable fingerprints. The agent must scan for these and rewrite or delete them. `scripts/gate_check.py` runs the mechanical part of this list (the "AI_FINGERPRINTS" table); the agent still has to judge frequency, density, and naturalness.

Categories below use this convention:

- **Hard ban** — never appears in正文; if found, blocking finding.
- **Quota** — may appear at most N times per chapter; over quota is an advisory finding.
- **Frequency** — measured per 100 CJK characters across the whole chapter.

### 1. 万能开场/收尾/转场（Hard ban）

These are unambiguous AI tells. No good Fanqie writer uses them.

- "命运的齿轮 / 命运的车轮 / 故事还在继续 / 故事的开始"
- "在那遥远的 / 很久很久以前 / 一切的一切"
- "时间仿佛静止 / 时间仿佛凝固 / 空气仿佛凝固 / 气氛瞬间凝固"
- "山雨欲来"
- "幽深而神秘 / 古老而沧桑"

### 2. 时间/天气/景物开场（Quota: ≤1 per chapter）

Acceptable in moderation, but the章首应近距离压力开场，不靠景物烘托。

- "夜幕降临 / 夜幕缓缓降临"
- "晨光熹微 / 月光如水 / 华灯初上"
- "空气中弥漫着 / 气氛凝重 / 鸦雀无声 / 寂静无声 / 落针可闻 / 死寂一般"

### 3. 抽象总结/议论腔（Quota: ≤1 each, ≤2 total）

正文是场景，不是议论。把这些词全部替换成具体动作或细节。

- "总而言之 / 综上所述 / 归根结底 / 总的来说"
- "不得不说 / 值得一提的是 / 令人遗憾的是"
- "毫无疑问 / 不可否认 / 显而易见 / 众所周知"
- "不知不觉 / 不知为何 / 与此同时"
- "换句话说 / 也就是说 / 这意味着"

### 4. 直说情绪标签（Quota: ≤2 each — the most poisonous AI tell）

Show through action, dialogue, body, or environment. Replace label-style emotion with physiological evidence or behavior.

- "他/她很愤怒/伤心/震惊/无奈/疲惫……"
- "他/她感到一阵 / 心中涌起一阵 / 心中一紧"
- "陷入了沉思/沉默/回忆/纠结/挣扎"
- "心如刀绞 / 五味杂陈 / 百感交集 / 说不出话来"

### 5. 万能动作模板（Quota: ≤2 each, ≤4 total stock-action lines）

These are the most overused dialogue beats. Vary them with specific, scene-anchored action.

- "微微一笑 / 轻轻一笑 / 勾唇一笑"
- "缓缓道 / 缓缓说道 / 缓缓开口 / 淡淡道 / 淡淡说道"
- "轻轻点头 / 轻轻摇头 / 轻轻叹息 / 深深叹息 / 深深地看"
- "若有所思 / 若有若无 / 意味深长"
- "嘴角勾起 / 嘴角微微上扬 / 挑了挑眉"

### 6. AI 偏爱的形容词组合（Quota: ≤1-2 each）

- "复杂的眼神/情绪/目光"
- "深邃的目光/眼眸"
- "略带玩味/嘲讽/挑衅"
- "幽深而神秘 / 古老而沧桑"（hard ban — see §1）
- "难以言喻 / 难以名状 / 无可奈何"
- "莫名 / 莫名其妙"（≤3）

### 7. 翻译腔/解释腔（Quota: ≤1-2 each）

- "在...的情况下 / 对于...来说 / 作为一个/名/位/种"
- "让...成为可能"（hard ban）
- "也就是说"

### 8. 古风 AI 特征（玄幻/修仙易冒）

- "颔首 / 颔首道"
- "须知 / 殊不知 / 要知道"

### 9. 副词冗余（Frequency: ≤2.0 / 100 CJK chars total）

`(很|非常|十分|特别|格外|极其|无比)` 合计频次超过每百字 2 次 → 告警。AI prose tends to lean on degree adverbs as a substitute for specific images.

### 10. 句式重复（Agent judgment, not in script yet）

- 三连排比/四连排比 in non-climactic chapters.
- 相邻段落同字开头 ≥3 段。
- 章节内同一动作模板（如"XX道"）≥4 次。
- 单章三处以上"XX的XX"四字结构（如"复杂的情绪""深邃的目光""略带嘲衅"）。

### Repair Strategy

When the gate flags AI patterns:

1. Hard ban → 必删/必换。
2. Over-quota → 改写成具体动作、细节、对话、感官信号。情绪标签优先换成生理反应（心跳、呼吸、视野收窄、手指动作）。
3. 副词冗余 → 把"很 X"换成"X 得 [具体表现]"。
4. 重复模板 → 给每个角色写一组**专属动作词典**（在 `01_bible/characters.yaml` 的 voice 字段补充），让不同角色的笑、点头、说话方式各不相同。

Treat AI-pattern cleanup as a real gate, not a polish step. A chapter that triggers ≥6 advisory AI findings should go back to repair regardless of plot quality.

## Platform Compliance Review

Also read `platform-compliance.md` before publishing, signing, or checkpoint review. Mechanical scans can catch obvious URL/contact/ad patterns, but the agent must still judge policy risk, unsafe subject framing, illegal instruction content, privacy violations, and disguised diversion.
