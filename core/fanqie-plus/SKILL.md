---
name: fanqie-plus
description: Use when opening, planning, writing, continuing, reviewing, repairing, or exporting a Chinese long-form Fanqie/Tomato web novel project; especially for 番茄小说, 黄金三章, 日更, 百万字长篇, 章节续写, 去AI味, 推荐评估, 8万字/15万字节点, 伏笔/角色/时间线长期一致性, and platform-ready plain-text export.
---

# Fanqie Plus

Build and maintain a long-form Chinese web novel optimized for Fanqie-style mobile reading. Keep the core workflow platform-neutral so Codex, Gemini CLI, Windsurf, and similar coding agents can follow it with their own file tools.

## Operating Rules

- Treat every novel as a file-backed project, not a one-off chat draft.
- Keep正文 and meta separate. Never place analysis, TODOs, gate notes, bracketed instructions, or author comments inside chapter正文.
- Prefer the smallest useful context: project state, outline anchor, current chapter brief, relevant characters, last chapter, and selected memory snippets.
- Do not advance to the next chapter while the current chapter gate fails. Repair first.
- Treat Fanqie-ready chapters as publishable units: default target is 2000-4000 Chinese characters, one concrete ending hook, and no non正文 residue.
- Do not change the main roadmap casually. If the user wants a major turn, run a rewrite-planning pass and update downstream outline anchors, memory, and chapter queue.
- For long books, preserve runway. Do not resolve core conflicts early; keep chapter progress inside the current anchor quota.

## Workflow

### 1. Open a new book

Use when the user has an idea, trope, genre, title, or only says they want to write a Fanqie novel.

1. Read `references/open-book.md`.
2. Confirm or infer the five seed fields: target reader, style, forbidden zones, automation level, and target scale.
3. Create the directory structure under `Project Layout` with your file tools.
4. Produce `00_config/idea_seed.md`, `target_profile.md`, `style_bible.md`, and `platform_strategy.md` based on the user's actual idea, not generic templates.
5. Draft 3-5 title/introduction options if the project is intended for Fanqie release.

### 2. Plan the long book

Use when creating or rebuilding the roadmap, volume plan, chapter queue, or million-word runway.

1. Read `references/outline-anchor.md` and `references/fanqie-platform.md`.
2. Produce a roadmap with stage/volume anchors, expected word counts, cool-down chapters, and major reveal limits.
3. Fill `02_outline/chapter_queue.yaml` for the next 10-30 chapters only; keep far-future plans coarse.
4. Mark Fanqie checkpoints: golden three chapters, 8w review, 10w launch readiness, 15w automatic review.

### 3. Continue the next chapter

Use for "继续写", "写下一章", "今天N章", or any single/batch chapter drafting request.

1. Read `references/chapter-pipeline.md`, `references/story-memory.md`, and `references/quality-gates.md`.
2. Determine the next chapter number from `03_memory/novel_state.json` or by listing `04_chapters/final/`. Read the minimal context set listed in `chapter-pipeline.md`.
3. Create a beat sheet before正文 and keep it outside chapter正文. Confirm the chapter pace tier and the one allowed major quota item.
4. Draft 2000-4000 Chinese characters per chapter unless the user or project config says otherwise.
5. Run quality gate checks. Use `scripts/gate_check.py` for mechanical checks, then perform semantic checks yourself.
6. If passed, update `03_memory/chapter_summaries.md`, `novel_state.json`, and `pacing_ledger.csv` with the chapter outcome.

### 4. Repair a chapter

Use when a gate fails, the user dislikes a chapter, or a review identifies concrete defects.

1. Preserve the intended chapter function before rewriting.
2. Repair the smallest layer that fixes the issue: beat sheet, scene order, dialogue, hook, or full chapter.
3. Re-run the same gates that failed.
4. Update memory only after the repaired final chapter is accepted.

### 5. Review a stage

Use every 10 chapters and at Fanqie checkpoints.

1. Read `references/fanqie-platform.md` and `references/quality-gates.md`.
2. Check: golden three chapters, title/introduction promise, character consistency, pacing ledger, unresolved hooks, AI-pattern residue, and toxicity/risk points.
3. Produce a prioritized fix list. Separate "must repair before continuing" from "can improve later".

### 6. Export to Fanqie

Use before posting or when the user asks for 番茄格式.

1. Read `references/export-fanqie.md`.
2. Run `scripts/export_fanqie.py` or manually apply the same rules. The script runs mechanical gates by default; use `--no-gate` only for diagnostics, never for publish-ready export.
3. Verify there are no Markdown markers, blank-line gaps, indentation, metadata blocks, or non正文 notes in the exported text.

## Project Layout

Use this layout unless an existing project already has a clear structure.

```text
book/
├── 00_config/
│   ├── idea_seed.md
│   ├── target_profile.md
│   ├── style_bible.md
│   └── platform_strategy.md
├── 01_bible/
│   ├── characters.yaml
│   ├── world.md
│   ├── timeline.yaml
│   └── foreshadowing.yaml
├── 02_outline/
│   ├── novel_roadmap.md
│   ├── volume_plan.md
│   ├── chapter_queue.yaml
│   └── outline_anchors.yaml
├── 03_memory/
│   ├── novel_state.json
│   ├── chapter_summaries.md
│   └── pacing_ledger.csv
├── 04_chapters/
│   ├── drafts/
│   └── final/
├── 05_reviews/
└── 06_export/fanqie/
```

## Resource Map

- `references/open-book.md`: seed questions, title/introduction, target reader, style bible.
- `references/fanqie-platform.md`: Fanqie-specific commercial checkpoints and mobile reading standards.
- `references/platform-compliance.md`: platform audit risks, URL/contact bans, advertising, unsafe content.
- `references/outline-anchor.md`: long-book roadmap, anchor quotas, pacing cool-downs.
- `references/chapter-pipeline.md`: beat-sheet-to-chapter production loop.
- `references/quality-gates.md`: blocking and advisory gates.
- `references/story-memory.md`: memory files and update rules.
- `references/export-fanqie.md`: platform plain-text formatting.

## Scripts

- `scripts/gate_check.py`: run mechanical chapter checks (URL/contact/meta contamination, blocking character count, hook signal) and optionally write JSON.
- `scripts/export_fanqie.py`: gate final chapters, then convert Markdown/text into Fanqie-ready `.txt`.

Scripts are reserved for deterministic pattern matching and text transformation. Project setup, chapter discovery, and memory updates are handled directly by the agent with its file tools — see the workflow steps above.

Semantic checks such as emotional pull, hidden pacing acceleration, trope fit, and character voice must be performed by the agent.
