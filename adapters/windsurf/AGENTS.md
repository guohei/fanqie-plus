# Fanqie Plus for Windsurf

Use the `fanqie-plus` skill at `.windsurf/skills/fanqie-plus/` for Fanqie/Tomato Chinese long-form web novel work.

If the skill directory is missing, link it from the core skill, from the repository root:

```bash
mkdir -p adapters/windsurf/.windsurf/skills
ln -sfn ../../../../core/fanqie-plus adapters/windsurf/.windsurf/skills/fanqie-plus
```

The workflows in `.windsurf/workflows/` are thin entry points:

- `fanqie-new.md`
- `fanqie-plan.md`
- `fanqie-next.md`
- `fanqie-review.md`
- `fanqie-export.md`

Keep all novel work file-backed. Store正文 in `04_chapters/`, memory in `03_memory/`, and review artifacts in `05_reviews/`.
