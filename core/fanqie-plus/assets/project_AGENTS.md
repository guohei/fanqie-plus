# AGENTS.md

This is a `fanqie-plus` Fanqie/Tomato long-novel project.

## Required Skill

- Use the `fanqie-plus` skill before opening, planning, writing, continuing, reviewing, repairing, or exporting this novel.
- If the skill is not automatically selected, explicitly load it and follow its `SKILL.md` workflow.
- Do not treat chapters as one-off chat drafts. This project is file-backed and must keep outline, memory, reviews, and正文 separate.

## Chapter Rules

- Keep正文 and meta separate. Never put beat sheets, TODOs, gate notes, analysis, author comments, or review text inside chapter正文.
- Draft accepted chapter正文 under `04_chapters/final/`. Draft work may live under `04_chapters/drafts/`.
- Follow chapter length and blocking gate rules from the project config and `references/quality-gates.md`.
- Do not continue to the next chapter while the current chapter fails any blocking gate.

## Required Checks

- Before drafting, read only the minimal context: `00_config/style_bible.md`, the relevant `02_outline/chapter_queue.yaml` entry, `03_memory/novel_state.json`, the previous final chapter, and relevant memory snippets.
- Create a beat sheet outside正文 before writing the chapter.
- Run the fanqie-plus mechanical gate from the skill package with `scripts/gate_check.py` after drafting, then follow the semantic checks in `references/quality-gates.md`.
- Update `03_memory/chapter_summaries.md`, `03_memory/novel_state.json`, and `03_memory/pacing_ledger.csv` only after the chapter passes gates.

## Long-Book Control

- Preserve runway. Do not resolve final conflicts, core secrets, or major relationship turns before the current outline anchor allows them.
- Follow outline anchors and pacing quotas in `references/outline-anchor.md`.
- Use every 10 chapters and Fanqie checkpoints for review: golden three, 8w, 10w, and 15w.

## 10-Chapter Consistency Audit

- After every 10 accepted final chapters, do not continue to the next chapter until a consistency audit is complete.
- Read and follow the full audit workflow in the `fanqie-plus` skill reference `references/consistency-audit.md`.
- Write the audit to `05_reviews/consistency/chapter-XXX.md`, replacing `XXX` with the latest reviewed chapter number.
- If the audit finds a blocking conflict, repair the smallest source of truth before continuing.

## Export

- Use fanqie-plus export rules before publishing.
- Exported正文 must contain no Markdown markers, metadata, notes, URLs, contact methods, ads, or off-platform diversion.
