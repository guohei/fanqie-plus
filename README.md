# fanqie-plus

`fanqie-plus` is a cross-agent skill package for writing and managing long-form Fanqie/Tomato-style Chinese web novels.

It keeps one source of truth in `core/fanqie-plus` and generates tool-specific adapters for Codex, Gemini CLI, and Windsurf.

## Structure

```text
core/fanqie-plus/                 # source skill
adapters/codex/                   # Codex adapter notes
adapters/gemini/                  # Gemini CLI extension and commands
adapters/windsurf/                # Windsurf workflows
scripts/build_adapters.py         # generate adapter skill copies
```

## Build Adapters

```bash
python3 scripts/build_adapters.py
```

Generated adapter skill copies are ignored by git. Edit `core/fanqie-plus` and rebuild when packaging for a tool.

## Core Workflows

- Open a Fanqie novel project
- Plan a long-book roadmap and outline anchors
- Continue chapters with beat sheets and quality gates
- Repair failed chapters
- Review Fanqie checkpoints
- Export platform-ready plain text
