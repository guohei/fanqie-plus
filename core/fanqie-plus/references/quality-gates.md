# Quality Gates

Use gates after every chapter, but keep the default path lightweight. Mechanical checks run every chapter. Full semantic review files are reserved for strict review mode; otherwise apply judgment while deciding whether the chapter can move from draft to final.

## Blocking Gates

If any blocking gate fails, repair before continuing.

| Gate | Failure examples |
| --- | --- |
| Meta contamination | TODO, author note, analysis, beat labels, gate comments inside正文 |
| Chapter length | Below or above the project/default chapter range, normally 2000-4000 Chinese characters |
| Platform compliance | URL, email, social/contact account, QR code, off-platform group, ad, transaction guidance, or unsafe policy content |
| Missing hook | Ending has no concrete next-click reason |
| Anchor violation | Resolves forbidden main conflict or outruns current outline anchor |
| Quota violation | A/B/C major events triggered together |
| Continuity break | Character state, timeline, ability, or setting contradicts tracked memory |
| Style break | POV switches accidentally, character voice collapses, prose becomes explanatory |
| Golden three miss | Chapter 1-3 fails its required Fanqie opening function |

## Advisory Gates

These usually require improvement but may not block a slow setup chapter:

- Weak conflict intensity.
- Low emotional feedback.
- Too much exposition.
- Similar dialogue voices.
- Repeated transition phrases.
- Paragraphs too long for mobile reading.
- Ending hook exists but feels generic.

## Mechanical Check Patterns

Use `scripts/gate_check.py` for:

- Character count range. Default 2000-4000 CJK characters is blocking unless project config explicitly overrides it.
- Forbidden meta markers.
- URL/contact/ad/off-platform diversion patterns.
- Markdown artifacts.
- Blank-line/format issues.
- Missing title.
- Weak hook keywords as a warning.

## Strict Semantic Review

Save `05_reviews/第N章-review.md` only when strict review mode is triggered: chapters 1-3, every 10-chapter audit, 8w/10w/15w, volume boundaries, `gate_check.py` failure, user dissatisfaction, major continuity changes, or publish/export preparation.

Use this template:

```markdown
# 第N章 Quality Gate

## Verdict
passed: true/false

## Blocking Findings
- [none or concrete finding]

## Advisory Findings
- [issue and fix]

## Pace Review
- Tier: slow/medium/fast
- A/B/C triggered: A/B/C/none
- Quota violation: yes/no
- Hidden acceleration: yes/no

## Continuity
- Character state changes:
- Timeline changes:
- Foreshadowing added:
- Foreshadowing resolved:

## Repair Plan
If failed, list the smallest repair path.
```

## AI-Pattern Cleanup

Do not load a long prose blacklist into every chapter context. `scripts/gate_check.py` owns the mechanical fingerprint table (`AI_FINGERPRINTS`); run it and repair the reported findings.

For semantic review, scan only these high-signal categories:

- stock opening, transition, or atmosphere phrases that sound prewritten
- abstract summary or explanatory narration where a scene should carry the emotion
- told emotions that should become action, body response, dialogue, or sensory evidence
- repeated dialogue beats or stock actions shared by multiple characters
- translation-tone sentence frames and degree-adverb padding
- repeated sentence shapes, especially non-climactic parallelism

Repair rules:

1. Any blocking `ai_pattern` finding from `gate_check.py` must be rewritten before continuing.
2. A chapter with 6 or more advisory AI-pattern findings should go back to repair even if the plot works.
3. Repeated categories matter more than one isolated phrase. Fix the local prose habit, not just the flagged word.
4. If one character repeatedly uses stock action or dialogue beats, update that character's voice/action notes in `01_bible/characters.yaml`.

## Platform Compliance Review

Also read `platform-compliance.md` before publishing, signing, or checkpoint review. Mechanical scans can catch obvious URL/contact/ad patterns, but the agent must still judge policy risk, unsafe subject framing, illegal instruction content, privacy violations, and disguised diversion.
