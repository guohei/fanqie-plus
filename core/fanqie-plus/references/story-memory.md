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
- Continuity notes:
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

## Update Rules

Update memory only after a chapter passes gates or after the user accepts a repaired version.

Record facts, not interpretations. Prefer:

- "陆沉在第12章知道林晚有系统异常。"

Avoid:

- "陆沉应该会越来越喜欢林晚。"

## Retrieval Rules

Before a chapter, retrieve only relevant memory:

- previous chapter summary
- active characters
- open foreshadowing due within 5-10 chapters
- timeline and location
- current arc anchor

For every 10 chapters, compress summaries into an arc recap and keep detailed chapter summaries available for search.
