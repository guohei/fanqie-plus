---
name: fanqie-plus
description: Use when opening, planning, writing, continuing, reviewing, repairing, or exporting a Chinese long-form Fanqie/Tomato web novel project; especially for 番茄小说, 黄金三章, 日更, 百万字长篇, 章节续写, 去AI味, 推荐评估, 8万字/15万字节点, 伏笔/角色/时间线长期一致性, and platform-ready plain-text export.
---

# Fanqie Plus

Build and maintain a long-form Chinese web novel optimized for Fanqie-style mobile reading. Keep the core workflow platform-neutral so Codex, Gemini CLI, Windsurf, and similar coding agents can follow it with their own file tools.

## Operating Contract

- Treat every novel as a file-backed project, not a one-off chat draft.
- Prefer project-embedded `.fanqie-plus/` when it exists. Global skill installation is only a fallback.
- Keep正文 and meta separate. Never place analysis, TODOs, gate notes, bracketed instructions, or author comments inside chapter正文.
- Load the smallest useful context: project state, current anchor, chapter brief, relevant characters, last chapter, and selected memory snippets.
- Do not advance to the next chapter while the current chapter gate fails. Repair first.
- Draft at most one chapter per user request. Do not batch write, auto-continue, or run unattended writing loops.
- Keep routine drift control inside existing outline, memory, pacing, and 10-chapter audit files. Do not add new tracking artifacts unless the user explicitly asks.
- Put craft details in project config or references, not in project-root `AGENTS.md`.
- Use scripts for deterministic checks and exports; use agent judgment for semantic quality.
- In ephemeral or cloud workspaces, commit and push completed chapters, reviews, repairs, exports, or outline changes with `scripts/git_checkpoint.py` or embedded `.fanqie-plus/scripts/git_checkpoint.py`. A local commit without a remote is not enough.
- Before long work or handoff, run `scripts/fanqie_doctor.py --project-root . project-check --require-git-remote` when available to verify embedded skill, workflow files, and remote checkpoint readiness. For local experiments, plain `project-check` warns about missing Git instead of blocking.

## Workflow

### 1. Open a new book

Use when the user has an idea, trope, genre, title, or only says they want to write a Fanqie novel.

1. Read `references/open-book.md`.
2. Confirm or infer the five seed fields: target reader, style, forbidden zones, approval cadence, and target scale.
3. Identify the dominant genre. If the genre is clear, read `references/genres/INDEX.md`, then `references/genres/INDEX-genre-frameworks.md`, then load only the matching genre subfile. Do not read the whole `genres/` tree.
4. Create the directory structure under `Project Layout` with your file tools.
5. Embed the skill into project-root `.fanqie-plus/` with `scripts/install_project_skill.py --project-root <book>` when available; otherwise copy this skill directory there manually.
6. Create project-root `AGENTS.md` from `.fanqie-plus/assets/project_AGENTS.md` so future agents entering the book directory use the embedded skill. If `AGENTS.md` already exists, preserve existing project-specific instructions.
7. Establish three-digit zero-padded chapter file names for future artifacts: `第001章.md`, `第001章-beat.md`, and `第001章-gate.json`.
8. Produce `00_config/idea_seed.md`, `target_profile.md`, `style_bible.md`, and `platform_strategy.md` based on the user's actual idea, plus the selected genre subfile when used, not generic templates.
9. Draft 3-5 title/introduction options if the project is intended for Fanqie release.

### 2. Plan the long book

Use when creating or rebuilding the roadmap, volume plan, chapter queue, or million-word runway.

1. Read `references/outline-anchor.md` and `references/fanqie-platform.md`.
2. Produce a roadmap with stage/volume anchors, expected word counts, cool-down chapters, and major reveal limits.
3. Fill `02_outline/chapter_queue.yaml` for the next 10-30 chapters only; keep far-future plans coarse.
4. Mark Fanqie checkpoints: golden three chapters, 8w review, 10w launch readiness, and 15w platform review.

### 3. Continue the next chapter

Use for "继续写", "写下一章", or any request to draft the current next chapter.

Default continuation is a lean single-chapter transaction: at most one chapter may be drafted per user request. Do not satisfy multi-chapter or automatic-writing requests; if the user asks for several chapters or unattended writing, draft only the immediate next chapter and stop after the checkpoint.

1. Read `references/chapter-pipeline.md`, determine the next chapter from `03_memory/novel_state.json` or `04_chapters/final/`, and check `next_required_review`. If the next chapter would pass a due review, run the stage review first.
2. Read the minimal context set listed in `chapter-pipeline.md`. Lazy-load `story-memory.md`, `quality-gates.md`, `outline-anchor.md`, or `references/genres/` only for uncertainty, failed gates, chapters 1-3, new arcs, checkpoints, or a specific prose problem.
3. Use `第NNN章` file names for chapter artifacts, where NNN is the three-digit zero-padded chapter number, such as `第024章`.
4. Save a Micro Beat to `05_reviews/第NNN章-beat.md`, then save draft正文 to `04_chapters/drafts/第NNN章.md`.
5. Run `scripts/gate_check.py` and save JSON to `05_reviews/第NNN章-gate.json`; repair blocking mechanical findings before final.
6. Save accepted正文 to `04_chapters/final/第NNN章.md`, then run one Memory Commit.
7. Run `scripts/fanqie_doctor.py --project-root . chapter-check --chapter N` when available. Only a later explicit user request may start another chapter.
8. In ephemeral or cloud workspaces, run `scripts/git_checkpoint.py --project-root . --message "第N章完成：..."` after the chapter transaction is complete.

Write `05_reviews/第NNN章-review.md` only in strict review mode: chapters 1-3, every 10-chapter audit, 8w/10w/15w, volume boundaries, gate failure, user dissatisfaction, major plot or continuity changes, or publish/export preparation.

Reject batch writing and auto-writing as workflow violations. Never draft a later chapter in the same request, even if the current chapter passes.

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
4. Use `references/cross-review.md` for 8w/10w/15w, volume endings, major repair decisions, persistent quality doubts, or user-requested independent review. For high-risk chapters, it may generate single-review, multi-review prompt packs, or live subagent instructions when the runtime truly supports subagents. The reviewer must be a different model/session unless explicitly using low-trust simulated diagnostics. Parse saved external reports with `scripts/fanqie_audit.py cross-parse`.
5. Use `references/reader-review.md` only as an optional heuristic diagnostic when chapter hook, pace, or AI-pattern risk is uncertain and no external review is warranted. It is not a default 10-chapter or checkpoint gate.
6. Produce a prioritized fix list. Separate "must repair before continuing" from "can improve later". Treat consistency-audit blocking conflicts and cross-review P0 findings as blocking before continuing. Treat reader-report findings as hints, never as blocking by themselves.

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
├── .fanqie-plus/
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
- `references/cross-review.md`: external AI review usage doc for checkpoints, volume endings, and independent review.
- `references/reader-review.md`: optional heuristic reader simulation diagnostic; not part of the default review path.
- `assets/project_AGENTS.md`: template for project-root `AGENTS.md`, created during book setup.

## Scripts

- `scripts/gate_check.py`: run mechanical chapter checks (URL/contact/meta contamination, blocking character count, hook signal) and optionally write JSON.
- `scripts/install_project_skill.py`: embed or upgrade fanqie-plus under a book project's `.fanqie-plus/`, write `AGENTS.md`, and update `.gitignore`.
- `scripts/git_checkpoint.py`: commit and push project changes after completed chapters, reviews, repairs, exports, or outline changes.
- `scripts/fanqie_doctor.py`: check project/chapter workflow completeness and optional Git remote readiness. It reads artifacts only and returns nonzero when a chapter transaction, due review, or required checkpoint prerequisite is incomplete.
- `scripts/export_fanqie.py`: gate final chapters, then convert Markdown/text into Fanqie-ready `.txt`.
- `scripts/fanqie_audit.py`: adapt fanqie-plus project layout to optional reader diagnostics, cross-review prompt export, multi-review prompt packs, and external report parsing.
- `scripts/cross_agent_reviewer.py`: generate prompts for a separate LLM and parse P0/P1/P2 issue reports. Primary external review layer, not a self-review substitute.
- `scripts/reader_simulator.py`: optional heuristic reader-perspective scoring. Use only through `fanqie_audit.py` when a quick diagnostic is worth the extra artifact.

Scripts are reserved for deterministic pattern matching and text transformation. Project setup, chapter discovery, and memory updates are handled directly by the agent with its file tools — see the workflow steps above.

Semantic checks such as emotional pull, hidden pacing acceleration, trope fit, and character voice must be performed by the agent. Reader simulation and cross-agent review assist stage review; they do not replace judgment.
