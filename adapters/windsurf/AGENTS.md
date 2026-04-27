# Fanqie Plus for Windsurf

Use the generated `.windsurf/skills/fanqie-plus/` for Fanqie/Tomato Chinese long-form web novel work.

If the skill directory is missing, run from the repository root:

```bash
python3 scripts/build_adapters.py
```

Do not edit generated skill files. Edit `core/fanqie-plus` and rebuild.

The workflows in `.windsurf/workflows/` are thin entry points:

- `fanqie-new.md`
- `fanqie-plan.md`
- `fanqie-next.md`
- `fanqie-review.md`
- `fanqie-export.md`

Keep all novel work file-backed. Store正文 in `04_chapters/`, memory in `03_memory/`, and review artifacts in `05_reviews/`.
