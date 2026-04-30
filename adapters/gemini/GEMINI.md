# Fanqie Plus

When the user asks to open, plan, write, continue, review, repair, or export a 番茄小说/Chinese long-form web novel, use the `fanqie-plus` skill from `skills/fanqie-plus/`.

Keep the project file-backed. Do not put beat sheets, review notes, or metadata inside chapter正文. Run the helper scripts inside the skill (`gate_check.py`, `export_fanqie.py`) when deterministic file operations are needed.

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
