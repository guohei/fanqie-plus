# Quality Gates

Use these gates after every chapter. Mechanical checks can be scripted; semantic checks require agent judgment.

## Blocking Gates

If any blocking gate fails, repair before continuing.

| Gate | Failure examples |
| --- | --- |
| Meta contamination | TODO, author note, analysis, beat labels, gate comments inside正文 |
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

- Word/character count range.
- Forbidden meta markers.
- URL/contact/ad/off-platform diversion patterns.
- Markdown artifacts.
- Blank-line/format issues.
- Missing title.
- Weak hook keywords as a warning.

## Semantic Review Template

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

Remove or rewrite:

- "他很愤怒/她很难过" without action or physiological evidence.
- "总而言之/与此同时/不知为何/命运的齿轮" overuse.
- Paragraphs that summarize what should be a scene.
- Dialogue where every character sounds like the same narrator.
- Excessive reflective explanation after an already clear action.

## Platform Compliance Review

Also read `platform-compliance.md` before publishing, signing, or checkpoint review. Mechanical scans can catch obvious URL/contact/ad patterns, but the agent must still judge policy risk, unsafe subject framing, illegal instruction content, privacy violations, and disguised diversion.
