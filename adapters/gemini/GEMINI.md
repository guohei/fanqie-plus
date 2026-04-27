# Fanqie Plus

When the user asks to open, plan, write, continue, review, repair, or export a 番茄小说/Chinese long-form web novel, use the generated `fanqie-plus` skill from `skills/fanqie-plus/`.

Keep the project file-backed. Do not put beat sheets, review notes, or metadata inside chapter正文. Run the relevant helper scripts from the skill when deterministic file operations are needed.

If `skills/fanqie-plus/` is missing, run `python3 scripts/build_adapters.py` from the repository root before using this adapter. Do not edit generated skill files; edit `core/fanqie-plus` and rebuild.

Recommended commands:

- `/fanqie:new` for opening a project.
- `/fanqie:plan` for roadmap and anchors.
- `/fanqie:next` for continuation.
- `/fanqie:review` for checkpoint review.
- `/fanqie:export` for Fanqie plain text.
