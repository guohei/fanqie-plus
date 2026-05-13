# Chapter Pipeline

Use this reference for single-chapter continuation only.

## Default Chapter Transaction

Run each chapter as a lean file-backed transaction. Do not start the next chapter until the current chapter has passed required gates, landed in `04_chapters/final/`, and updated memory.

At most one chapter may be drafted per user request. Do not batch draft, auto-continue, or run unattended writing loops. If the user asks for multiple chapters, write only the immediate next chapter, finish its transaction, and stop.

Use `第NNN章` file names for chapter artifacts, where NNN is the three-digit zero-padded chapter number, such as `第001章` or `第024章`. This keeps file browsers and plain lexicographic lists in chapter order. Existing unpadded projects may remain as-is; `fanqie_doctor.py` accepts either style.

1. Check `next_required_review` in `03_memory/novel_state.json`. If the next chapter would pass a due 10-chapter or Fanqie checkpoint review, run the review first.
2. Read the minimal context set below.
3. Save a Micro Beat to `05_reviews/第NNN章-beat.md`.
4. Save `04_chapters/drafts/第NNN章.md`.
5. Run `scripts/gate_check.py` and save `05_reviews/第NNN章-gate.json`.
6. Repair blocking mechanical findings before continuing.
7. Run the internal Style QA pass after gate_check and before final: protagonist fit, dialogue distinction, escalation, concrete hook, and AI residue. If the runtime exposes a real delegation/subagent tool, this pass may use one editor subagent to check logic, continuity, character motivation, and chapter promise. The subagent does not directly edit正文; it returns P0/P1/P2 notes to the writing agent, which repairs the smallest issue before final. Do not run a roundtable or multi-review by default during routine chapter drafting.
8. Only copy or rewrite into `04_chapters/final/第NNN章.md` after mechanical gates pass and any required strict review has passed.
9. Run one Memory Commit after final is accepted.
10. Run `scripts/fanqie_doctor.py --project-root . chapter-check --chapter N` when available as the final transaction check.
11. In ephemeral or cloud workspaces, run `scripts/git_checkpoint.py --project-root . --message "第N章完成：..."` after the transaction completes.

## Strict Review Mode

Write `05_reviews/第NNN章-review.md` only when strict mode is triggered:

- chapters 1-3
- every 10-chapter audit
- 8w, 10w, or 15w checkpoint
- volume ending or new volume opening
- `gate_check.py` fails
- user rejects or questions the chapter quality
- major plot, character relationship, timeline, ability, or foreshadowing change
- publish/export preparation

Strict review should identify blocking findings, advisory fixes, pace/quota issues, continuity changes, and the smallest repair path. If strict review finds a blocking issue, repair before final save or before continuing.

## Context Budget

Default read set before drafting:

1. `00_config/style_bible.md`
2. `02_outline/chapter_queue.yaml` entry for the chapter
3. `03_memory/novel_state.json`
4. Previous final chapter
5. Relevant character/world/foreshadowing snippets

Avoid loading the whole book. Summarize if the context grows.

## Micro Beat

Before drafting, write a short chapter card into `05_reviews/第NNN章-beat.md`. Keep the default Micro Beat tight:

- Function:
- Beats: 3-5 bullets.
- Must not resolve:
- Ending hook:
- Expected memory updates:

Use a fuller beat only for chapters 1-3, new arcs, checkpoints, failed gates, user dissatisfaction, or major plot/continuity turns. Never paste beat notes into `04_chapters/final/` or exported正文. If the Micro Beat violates anchor quota, fix it before writing正文.

## Memory Commit

After accepted正文 lands in `04_chapters/final/`, update memory as one post-final operation:

- append `03_memory/chapter_summaries.md`
- update `03_memory/novel_state.json`
- append `03_memory/pacing_ledger.csv`
- update `01_bible/characters.yaml`, `timeline.yaml`, or `foreshadowing.yaml` only when accepted正文 changes durable facts

Do not update memory from draft text. If the chapter is repaired before final, run Memory Commit only after the repaired final is accepted.

## Ending Hook Types

Choose one concrete hook type before drafting the chapter ending. Do not end with a vague summary such as "更大的危险正在靠近" unless the danger has a visible carrier.

| Type | Use when | Concrete signal |
| --- | --- | --- |
| Crisis | Safety breaks at the end | Stronger enemy, countdown, exposed location, trap trigger |
| Suspense | A question opens but answer is withheld | Box, message, name, bloodline, missing person, abnormal rule |
| Reversal | The apparent result flips | Enemy survives, ally changes side, win becomes bait |
| Opportunity | A new path appears | Resource, invitation, clue, mentor, system reward |
| Conflict | A clash becomes unavoidable | Challenge, threat, public provocation, deadline duel |
| Reveal | Truth is promised or partly exposed | Identity clue, old secret, hidden motive, larger conspiracy |

The hook should connect to the chapter's pressure or payoff, not appear as a detached teaser.

## Drafting Standards

- Start close to pressure; do not warm up with neutral routine.
- Make every scene contain friction, desire, discovery, or emotional contrast.
- Let character voice differ by vocabulary, rhythm, worldview, and tactics.
- Use sensory details to ground the scene, not to decorate every sentence.
- Keep paragraphs mobile-friendly.
- End on a concrete hook, not a vague "danger was coming" summary unless that line is supported by a specific reveal.

## No Batch Or Auto Writing

- At most one chapter may be drafted per user request.
- Do not batch draft, auto-continue, or run unattended writing loops.
- Do not treat "今天N章", "连续写", or "自动写" as permission to draft multiple chapters.
- After `fanqie_doctor.py` and any checkpoint commit finish, stop and wait for the user's next explicit request.
- Planning, review, export, and multi-chapter audit may cover multiple chapters;正文 drafting may not.

## Output Discipline

Save draft正文 in `04_chapters/drafts/第NNN章.md`.
Save accepted final正文 in `04_chapters/final/第NNN章.md`.
Save mechanical gate output in `05_reviews/第NNN章-gate.json`. Save `05_reviews/第NNN章-review.md` only for strict review mode.
Run Memory Commit once after final acceptance.
Use `scripts/fanqie_doctor.py` as a final transaction check; it must not replace the writing agent's semantic judgment.
Use `scripts/git_checkpoint.py` after completed chapter transactions when the workspace may be temporary.

Default publishable chapter length is 2000-4000 Chinese characters unless the project config sets a different range. Treat length failure as a repair item, not a harmless warning, because recommendation-facing Fanqie chapters need stable update units.
