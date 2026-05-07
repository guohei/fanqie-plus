# 10-Chapter Consistency Audit

Use this reference after every 10 accepted final chapters and at any later point where the outline, memory, or正文 may have drifted.

The goal is not to force正文 to match stale细纲. The goal is to keep every source of truth honest: if正文 improved the plan, update the downstream outline and memory; if正文 contradicted the plan by accident, repair the smallest source.

## Required Inputs

Read the smallest complete audit set:

- `02_outline/novel_roadmap.md`
- `02_outline/volume_plan.md`
- `02_outline/outline_anchors.yaml`
- `02_outline/chapter_queue.yaml`
- `03_memory/novel_state.json`
- `03_memory/chapter_summaries.md`
- `03_memory/pacing_ledger.csv`
- recent accepted chapters in `04_chapters/final/`
- `01_bible/characters.yaml`, `timeline.yaml`, or `foreshadowing.yaml` only when a suspected conflict needs confirmation

## Conflict Checks

Check conflicts between roadmap, outline anchors, chapter queue, memory, pacing ledger, and final正文:

- character state, relationship, timeline, or location contradictions
- events promised in the outline or chapter queue but missing from正文
- events written in正文 but not reflected in memory
- hooks or foreshadowing forgotten, resolved too early, or untracked
- outline anchor overrun, premature payoff, or A/B/C pacing quota drift
- final chapter count or word count differing from `novel_state.json`
- missing rows in `03_memory/pacing_ledger.csv` or missing summaries in `03_memory/chapter_summaries.md`

## Report Path

Write the audit to `05_reviews/consistency/chapter-XXX.md`, replacing `XXX` with the latest reviewed chapter number.

## Report Template

```markdown
# 第XXX章 一致性审计

## Verdict
passed: true/false

## Scope
- Reviewed chapters:
- Files read:

## Blocking Conflicts
- [none or exact conflict]

## Advisory Drift
- [none or drift that can be repaired later]

## Outline vs 正文
- Missing promised events:
- New正文 facts not in memory/outline:
- Stale细纲 that should be updated:

## Memory Sync
- `novel_state.json`:
- `chapter_summaries.md`:
- `pacing_ledger.csv`:
- characters/timeline/foreshadowing:

## Required Repair
- [none or smallest source-of-truth repair]
```

## Required Repair Behavior

- If a blocking conflict exists, do not continue to the next chapter.
- Repair the smallest source of truth first: chapter正文, memory, chapter queue, outline anchors, or foreshadowing ledger.
- Do not force正文 to match stale细纲.
- Do not rewrite accepted正文 just because the细纲 is stale. Prefer updating `chapter_queue.yaml`, `outline_anchors.yaml`, summaries, or foreshadowing when正文 is coherent and stronger.
- If the conflict changes future runway, update downstream outline files before drafting the next chapter.
- After repair, re-read the changed files and update the audit verdict.
