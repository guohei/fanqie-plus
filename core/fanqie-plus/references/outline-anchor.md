# Outline Anchors And Long-Book Runway

Use this reference when planning or changing the roadmap.

## Anchor Model

Long novels need anchor constraints so the story does not resolve too early.

Create `02_outline/outline_anchors.yaml` with entries like:

```yaml
- id: arc-001
  range: "第1-30章"
  words: "6-10万"
  stage: "新手期/开局立钩"
  core_promise: "主角从最低点获得第一张底牌"
  allowed_major_payoffs:
    - "第3章小爽点"
    - "第12-15章第一次中爽点"
    - "第28-30章第一阶段收束"
  forbidden_resolution:
    - "不得揭开最终身世"
    - "不得解决主线终极反派"
  next_stage_hook: "更大地图/更强对手/更深秘密"
```

## Pace Tiers

Every chapter should have a pace tier:

| Tier | Use | Rule |
| --- | --- | --- |
| Slow | bonding, setup, recovery, foreshadowing, daily-life contrast | main conflict does not resolve |
| Medium | obstacle escalation, clue, small confrontation, preparation | most chapters live here |
| Fast | major reveal, decisive relationship turn, stage boss, public reversal | use sparingly; follow with slow/medium |

## A/B/C Quota

A chapter may trigger at most one major quota item:

- A: main conflict materially advances.
- B: major relationship decisively changes.
- C: core secret is fully revealed.

If two or more happen in one non-finale chapter, rewrite the beat sheet. This is a pacing failure, not a style issue.

## Chapter Queue

Keep `02_outline/chapter_queue.yaml` detailed for the next 10-30 chapters and coarse after that.

```yaml
- chapter: 12
  title_hint: "旧账上门"
  pace: "medium"
  function: "push first antagonist into direct conflict"
  must_include:
    - "房东/债主/宗门执事上门施压"
    - "主角用新能力解决一半问题"
  hook: "真正幕后人第一次露出名字"
  quota: "A"
```

## Rewrite Planning

For major user-requested changes:

1. State which anchors change.
2. Update `novel_roadmap.md`, `outline_anchors.yaml`, and `chapter_queue.yaml`.
3. Update memory files for affected characters, timeline, and foreshadowing.
4. Mark any already-written chapters that need repair.
5. Continue only after the new runway is coherent.
