# Fanqie Plus

When the user asks to open, plan, write, continue, review, repair, or export a 番茄小说/Chinese long-form web novel, use `skills/fanqie-plus/SKILL.md` as the source of truth. If an adapter command conflicts with the skill, follow the skill.

Gemini commands are thin entry points. Keep workflow details in the skill and project-embedded `.fanqie-plus/`.

If `skills/fanqie-plus/` is missing, link the core skill from the repository root:

```bash
mkdir -p adapters/gemini/skills
ln -sfn ../../../core/fanqie-plus adapters/gemini/skills/fanqie-plus
```

Recommended commands:

- `/fanqie:new` for opening a project.
- `/fanqie:plan` for roadmap and anchors.
- `/fanqie:next` for continuation.
- `/fanqie:review` for checkpoint review.
- `/fanqie:export` for Fanqie plain text.
