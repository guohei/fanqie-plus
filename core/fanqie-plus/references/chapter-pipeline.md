# Chapter Pipeline

Use this reference for single-chapter or batch continuation.

## Context Budget

Default read set before drafting:

1. `00_config/style_bible.md`
2. `02_outline/chapter_queue.yaml` entry for the chapter
3. `03_memory/novel_state.json`
4. Previous final chapter
5. Relevant character/world/foreshadowing snippets

Avoid loading the whole book. Summarize if the context grows.

## Preflight

Before drafting, state internally or in a brief work note:

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

- Draft in order.
- Gate and update memory after each chapter.
- Do not assume later chapters can fix a failed current chapter.
- Keep fast chapters separated by slow/medium buffers unless at a planned climax.

## Output Discipline

Save draft正文 in `04_chapters/drafts/第N章.md`.
Save accepted final正文 in `04_chapters/final/第N章.md`.
Save reviews in `05_reviews/第N章-gate.json` or `05_reviews/第N章-review.md`.

Default publishable chapter length is 2000-4000 Chinese characters unless the project config sets a different range. Treat length failure as a repair item, not a harmless warning, because recommendation-facing Fanqie chapters need stable update units.
