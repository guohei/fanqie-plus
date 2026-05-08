---
name: fanqie-plus
description: Use when opening, planning, writing, continuing, reviewing, repairing, or exporting a Chinese long-form Fanqie/Tomato web novel project; especially for 番茄小说, 黄金三章, 日更, 百万字长篇, 章节续写, 去AI味, 推荐评估, 8万字/15万字节点, 伏笔/角色/时间线长期一致性, and platform-ready plain-text export.
---

# Fanqie Plus

Build and maintain a long-form Chinese web novel optimized for Fanqie-style mobile reading. Keep the core workflow platform-neutral so Codex, Gemini CLI, Windsurf, and similar coding agents can follow it with their own file tools.

## Operating Contract

- Treat every novel as a file-backed project, not a one-off chat draft.
- Keep正文 and meta separate. Never place analysis, TODOs, gate notes, bracketed instructions, or author comments inside chapter正文.
- Load the smallest useful context: project state, current anchor, chapter brief, relevant characters, last chapter, and selected memory snippets.
- Do not advance to the next chapter while the current chapter gate fails. Repair first.
- Keep routine drift control inside existing outline, memory, pacing, and 10-chapter audit files. Do not add new tracking artifacts unless the user explicitly asks.
- Put craft details in project config or references, not in project-root `AGENTS.md`.
- Use scripts for deterministic checks and exports; use agent judgment for semantic quality.

## Workflow

### 1. Open a new book

Use when the user has an idea, trope, genre, title, or only says they want to write a Fanqie novel.

1. Read `references/open-book.md`.
2. Confirm or infer the five seed fields: target reader, style, forbidden zones, automation level, and target scale.
3. Identify the dominant genre. If the genre is clear, read `references/genres/INDEX.md`, then `references/genres/INDEX-genre-frameworks.md`, then load only the matching genre subfile. Do not read the whole `genres/` tree.
4. Create the directory structure under `Project Layout` with your file tools.
5. Create project-root `AGENTS.md` from `assets/project_AGENTS.md` so future agents entering the book directory are explicitly told to use this skill.
6. Produce `00_config/idea_seed.md`, `target_profile.md`, `style_bible.md`, and `platform_strategy.md` based on the user's actual idea, plus the selected genre subfile when used, not generic templates.
7. Draft 3-5 title/introduction options if the project is intended for Fanqie release.

### 2. Plan the long book

Use when creating or rebuilding the roadmap, volume plan, chapter queue, or million-word runway.

1. Read `references/outline-anchor.md` and `references/fanqie-platform.md`.
2. Produce a roadmap with stage/volume anchors, expected word counts, cool-down chapters, and major reveal limits.
3. Fill `02_outline/chapter_queue.yaml` for the next 10-30 chapters only; keep far-future plans coarse.
4. Mark Fanqie checkpoints: golden three chapters, 8w review, 10w launch readiness, 15w automatic review.

### 3. Continue the next chapter

Use for "继续写", "写下一章", "今天N章", or any single/batch chapter drafting request.

Default continuation is a lean single-chapter transaction:

1. Read `references/chapter-pipeline.md`, determine the next chapter from `03_memory/novel_state.json` or `04_chapters/final/`, and check `next_required_review`. If the next chapter would pass a due review, run the stage review first.
2. Read the minimal context set listed in `chapter-pipeline.md`. Lazy-load `story-memory.md`, `quality-gates.md`, `outline-anchor.md`, or `references/genres/` only for uncertainty, failed gates, chapters 1-3, new arcs, checkpoints, or a specific prose problem.
3. Save a compact chapter card to `05_reviews/第N章-beat.md`, then save draft正文 to `04_chapters/drafts/第N章.md`.
4. Run `scripts/gate_check.py` and save JSON to `05_reviews/第N章-gate.json`; repair blocking mechanical findings before final.
5. Save accepted正文 to `04_chapters/final/第N章.md`, then update `03_memory/chapter_summaries.md`, `03_memory/novel_state.json`, and `03_memory/pacing_ledger.csv`. Only then may the next chapter start.

Write `05_reviews/第N章-review.md` only in strict review mode: chapters 1-3, every 10-chapter audit, 8w/10w/15w, volume boundaries, gate failure, user dissatisfaction, major plot or continuity changes, or publish/export preparation.

For batch requests, repeat the lean transaction in order for each chapter. Do not draft later chapters before the current chapter's gate, final, and memory updates are complete.

### 4. Repair a chapter

Use when a gate fails, the user dislikes a chapter, or a review identifies concrete defects.

1. Preserve the intended chapter function before rewriting.
2. Repair the smallest layer that fixes the issue: beat sheet, scene order, dialogue, hook, or full chapter.
3. Re-run the same gates that failed.
4. Update memory only after the repaired final chapter is accepted.

### 5. Review a stage

Use every 10 chapters and at Fanqie checkpoints.

1. Read `references/fanqie-platform.md` and `references/quality-gates.md`.
2. At every 10-chapter review, read `references/consistency-audit.md` and write the consistency report to `05_reviews/consistency/chapter-XXX.md` before continuing.
3. Check: golden three chapters, title/introduction promise, character consistency, pacing ledger, unresolved hooks, AI-pattern residue, and toxicity/risk points.
4. Use `references/reader-review.md` only for Fanqie checkpoints, 10-chapter reviews where quality is uncertain, or direct reader-style feedback. Its output is advisory under `05_reviews/reader/`.
5. Use `references/cross-review.md` at 8w/10w/15w, volume endings, or persistent review disagreement. Parse saved external reports with `scripts/cross_agent_reviewer.py parse`.
6. Produce a prioritized fix list. Separate "must repair before continuing" from "can improve later". Treat consistency-audit blocking conflicts and cross-review P0 findings as blocking before continuing.

### 6. Export to Fanqie

Use before posting or when the user asks for 番茄格式.

1. Read `references/export-fanqie.md`.
2. Run `scripts/export_fanqie.py` or manually apply the same rules. The script runs mechanical gates by default; use `--no-gate` only for diagnostics, never for publish-ready export.
3. Verify there are no Markdown markers, blank-line gaps, indentation, metadata blocks, or non正文 notes in the exported text.

## Project Layout

Use this layout unless an existing project already has a clear structure.

```text
book/
├── AGENTS.md
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
- `references/consistency-audit.md`: 10-chapter outline/memory/正文 drift review and repair rules.
- `references/genres/`: genre, hook, opening, and style craft library. Always enter through `genres/INDEX.md` and load only selected leaf files.
- `references/reader-review.md`: advisory reader simulation protocol for 10-chapter and Fanqie checkpoint reviews.
- `references/cross-review.md`: cross-agent review protocol for volume endings and commercial checkpoints.
- `assets/project_AGENTS.md`: template for project-root `AGENTS.md`, created during book setup.

## Scripts

- `scripts/gate_check.py`: run mechanical chapter checks (URL/contact/meta contamination, blocking character count, hook signal) and optionally write JSON.
- `scripts/export_fanqie.py`: gate final chapters, then convert Markdown/text into Fanqie-ready `.txt`.
- `scripts/fanqie_audit.py`: adapt fanqie-plus project layout to advisory reader/cross-review scripts and export reports back to `05_reviews/`.
- `scripts/reader_simulator.py`: heuristic reader-perspective scoring. Advisory only; use through `fanqie_audit.py` for fanqie-plus projects.
- `scripts/cross_agent_reviewer.py`: generate prompts for a separate LLM and parse P0/P1/P2 issue reports. Advisory review layer, not a self-review substitute.

Scripts are reserved for deterministic pattern matching and text transformation. Project setup, chapter discovery, and memory updates are handled directly by the agent with its file tools — see the workflow steps above.

Semantic checks such as emotional pull, hidden pacing acceleration, trope fit, and character voice must be performed by the agent. Reader simulation and cross-agent review assist stage review; they do not replace judgment.
