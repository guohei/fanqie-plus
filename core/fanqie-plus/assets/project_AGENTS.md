# AGENTS.md
This is a file-backed `fanqie-plus` Fanqie/Tomato long-novel project. Use the embedded workflow in `.fanqie-plus/` before any global skill.

## Required
- Use `.fanqie-plus/SKILL.md` before opening, planning, writing, continuing, reviewing, repairing, or exporting.
- Keep accepted正文 in `04_chapters/final/`, drafts in `04_chapters/drafts/`, memory in `03_memory/`, and reviews in `05_reviews/`.
- Keep正文 and meta separate. Never put beat sheets, TODOs, gate notes, analysis, author comments, or review text inside正文.
- Do not continue to the next chapter while the current chapter fails any blocking gate.
- Before long work or handoff, run `.fanqie-plus/scripts/fanqie_doctor.py --project-root . project-check --require-git-remote`.
- For chapters, follow `.fanqie-plus/references/chapter-pipeline.md`, `.fanqie-plus/references/story-memory.md`, `.fanqie-plus/references/quality-gates.md`, and `.fanqie-plus/references/outline-anchor.md`; run `.fanqie-plus/scripts/gate_check.py`; update memory only after gates pass; run `.fanqie-plus/scripts/fanqie_doctor.py --project-root . chapter-check --chapter N`.
- After completed chapters, reviews, repairs, exports, or outline changes, run `.fanqie-plus/scripts/git_checkpoint.py --project-root . --message "..."` to commit and push; local-only commits do not protect temporary workspaces.

## Chapter Continuation Gate

Before starting the next chapter, the current chapter must have:
- `05_reviews/第N章-beat.md`
- `04_chapters/drafts/第N章.md`
- `05_reviews/第N章-gate.json`
- `04_chapters/final/第N章.md`
- updated `03_memory/chapter_summaries.md`, `novel_state.json`, and `pacing_ledger.csv`

For batch writing, repeat this gate per chapter. Do not write later chapters first and check them afterward.
Write `05_reviews/第N章-review.md` only when strict review mode is triggered.

## 10-Chapter Consistency Audit

- After every 10 accepted final chapters, do not continue to the next chapter until `.fanqie-plus/references/consistency-audit.md` is complete.
- Write `05_reviews/consistency/chapter-XXX.md` and repair blocking conflicts before continuing.

## Export

- Before publishing, follow `.fanqie-plus/references/export-fanqie.md` and `.fanqie-plus/references/platform-compliance.md`.
