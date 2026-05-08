# Story Memory

Use this reference to keep a long novel coherent across hundreds of chapters.

## Memory Files

### `03_memory/novel_state.json`

Track current position:

```json
{
  "title": "",
  "current_chapter": 0,
  "current_words": 0,
  "current_arc": "",
  "last_updated": "",
  "open_threads": [],
  "active_characters": [],
  "next_required_review": "第10章"
}
```

### `03_memory/chapter_summaries.md`

Append after each accepted final chapter:

```markdown
## 第N章 标题
- Summary:
- Reader emotion:
- Hook:
- New facts:
- Character changes:
- Foreshadowing:
- Continuity notes / guardrails:
- Outline sync:
```

### `03_memory/pacing_ledger.csv`

Columns:

```csv
chapter,title,pace,quota,hook_type,words,gate_passed,notes
```

### `01_bible/characters.yaml`

Track:

- stable identity and voice
- goals
- secrets
- relationships
- current physical/emotional state
- last appearance chapter

### `01_bible/timeline.yaml`

Track:

- story date/time
- location
- elapsed time
- impossible overlaps

### `01_bible/foreshadowing.yaml`

Track:

- seed chapter
- expected payoff range
- status: open/resolved/reframed
- related characters

For information-gap hooks, also track:

- known_by: reader, protagonist, antagonist, specific supporting characters
- hidden_from: reader, protagonist, antagonist, specific supporting characters
- reveal_range: small gap within 3-5 chapters, medium gap within 15-20 chapters, large gap within 50+ chapters
- payoff_type: face-slap, reversal, rescue, betrayal, identity reveal, ability reveal, clue reveal

Use information gaps deliberately:

- Reader knows, character does not: creates tension and anticipation.
- Protagonist knows, opponent does not: powers face-slap and reversal scenes.
- Character knows, reader does not: creates mystery, but must be fairly seeded.

## Update Rules

Update memory only after a chapter passes gates or after the user accepts a repaired version.

Record facts, not interpretations. Prefer:

- "陆沉在第12章知道林晚有系统异常。"

Avoid:

- "陆沉应该会越来越喜欢林晚。"

Use `Outline sync:` only for real plan drift:

- `none` when正文 matches the chapter queue and current anchor.
- `queue update needed` when正文 is coherent but future `chapter_queue.yaml` should change.
- `anchor/memory repair needed` when the drift affects runway, pacing quota, timeline, or foreshadowing.

Do not create extra drift ledgers unless the user explicitly asks. Reuse `chapter_summaries.md`, `pacing_ledger.csv`, and the 10-chapter consistency audit.

Use `Continuity notes / guardrails:` for concrete continuity risks that could affect the next chapters. Keep them factual and local. They are not permanent bans: later chapters may override them when there is a clear story reason, and stale guardrails should be revised during memory updates or consistency audits.

Advance `next_required_review` only after the due review passes. Example: after the 第10章 consistency audit passes or is repaired, set `next_required_review` to `第20章`. If the audit fails, leave it unchanged until repair is complete.

## Retrieval Rules

Before a chapter, retrieve only relevant memory:

- previous chapter summary
- active characters
- open foreshadowing due within 5-10 chapters
- timeline and location
- current arc anchor

For every 10 chapters, compress summaries into an arc recap and keep detailed chapter summaries available for search.
