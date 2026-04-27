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
- Specific ending hook.
- One emotional target for the reader.
- Required continuity points from previous chapter.

## Beat Sheet First

Write a beat sheet before正文:

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
- Must not resolve: [...]
- Memory updates expected: [...]
```

If the beat sheet violates anchor quota, fix it before writing正文.

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
