# Fanqie Plus for Codex

Use the shared skill generated at `skills/fanqie-plus/` for any request about opening, planning, writing, continuing, reviewing, repairing, or exporting a Fanqie/Tomato long-form Chinese web novel.

## Install

The source of truth is:

```text
core/fanqie-plus -> ~/.codex/skills/fanqie-plus
```

For project-local adapter packaging, run from the repository root:

```bash
python3 scripts/build_adapters.py
```

That generates:

```text
adapters/codex/skills/fanqie-plus
```

Do not edit the generated copy. Edit `core/fanqie-plus` and rebuild.

## Usage

Natural language triggers are enough:

- "帮我开一本番茄长篇"
- "继续写下一章"
- "检查第1-3章黄金三章"
- "导出番茄格式"

When creating or editing files, use the project layout defined by the skill. Keep正文 under `04_chapters/` and memory under `03_memory/`.
