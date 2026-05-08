# Chapter Pipeline

Use this reference for single-chapter or batch continuation.

## Chapter Transaction

Run each chapter as a file-backed transaction. Do not start the next chapter until the current chapter has passed gates, landed in `04_chapters/final/`, and updated memory.

1. Check `next_required_review` in `03_memory/novel_state.json`. If the next chapter would pass a due 10-chapter or Fanqie checkpoint review, run the review first.
2. Read the minimal context set below.
3. Save `05_reviews/第N章-beat.md`.
4. Save `04_chapters/drafts/第N章.md`.
5. Run `scripts/gate_check.py` and save `05_reviews/第N章-gate.json`.
6. Save `05_reviews/第N章-review.md` with semantic gate findings.
7. Repair blocking findings before continuing.
8. Only copy or rewrite into `04_chapters/final/第N章.md` after both gates pass.
9. Update `03_memory/chapter_summaries.md`, `03_memory/novel_state.json`, and `03_memory/pacing_ledger.csv`.

## Context Budget

Default read set before drafting:

1. `00_config/style_bible.md`
2. `02_outline/chapter_queue.yaml` entry for the chapter
3. `03_memory/novel_state.json`
4. Previous final chapter
5. Relevant character/world/foreshadowing snippets

Avoid loading the whole book. Summarize if the context grows.

## Preflight

Before drafting, write these fields into `05_reviews/第N章-beat.md`:

- Chapter number and target word count.
- Pace tier: slow, medium, or fast.
- A/B/C quota item, or "none".
- Hook type and specific ending hook.
- One emotional target for the reader.
- Required continuity points from previous chapter.

## Beat Sheet First

Write a beat sheet before正文. Save it as a work note or `05_reviews/第N章-beat.md`; never paste it into `04_chapters/final/` or exported正文.

```markdown
# 第N章 Beat Sheet

## Chapter Function
[What this chapter must achieve]

## Beats
1. [Opening pressure]
2. [Escalation or discovery]
3. [Choice, clash, or emotional turn]
4. [Partial payoff]
5. [Ending hook]

## Constraints
- Pace: [slow/medium/fast]
- Quota: [A/B/C/none]
- Hook type: [crisis/suspense/reversal/opportunity/conflict/reveal]
- Must not resolve: [...]
- Memory updates expected: [...]
```

If the beat sheet violates anchor quota, fix it before writing正文.

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

## Batch Generation

For multiple chapters:

- Batch generation repeats this transaction for each chapter.
- Draft in order.
- Gate, review, final-save, and update memory after each chapter.
- Do not assume later chapters can fix a failed current chapter.
- Do not draft later chapters first and gate them afterward.
- Keep fast chapters separated by slow/medium buffers unless at a planned climax.

## Output Discipline

Save draft正文 in `04_chapters/drafts/第N章.md`.
Save accepted final正文 in `04_chapters/final/第N章.md`.
Save reviews in `05_reviews/第N章-gate.json` or `05_reviews/第N章-review.md`.

Default publishable chapter length is 2000-4000 Chinese characters unless the project config sets a different range. Treat length failure as a repair item, not a harmless warning, because recommendation-facing Fanqie chapters need stable update units.
