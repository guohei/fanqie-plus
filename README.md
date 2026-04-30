# fanqie-plus

`fanqie-plus` is a cross-agent skill package for writing and managing long-form Fanqie/Tomato-style Chinese web novels.

The single source of truth is the standard Agent Skill in `core/fanqie-plus/`. Adapter folders for Gemini CLI and Windsurf only contain the platform-specific entry points (slash commands, workflows) and reuse the same skill via a symlink.

## What It Does

- Open a Fanqie novel project with reader profile, style bible, platform strategy, and project structure.
- Plan long-book roadmaps, outline anchors, volume plans, and near-term chapter queues.
- Continue chapters with beat sheets, memory retrieval, quality gates, and memory updates.
- Repair chapters that fail gates.
- Review golden three chapters, 8w/10w/15w checkpoints, pacing, continuity, and platform compliance.
- Export clean Fanqie-ready plain text.

## Repository Layout

```text
core/fanqie-plus/                 # the skill — single source of truth
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
    gate_check.py                 # deterministic mechanical gate
    export_fanqie.py              # Markdown → Fanqie plain text

adapters/gemini/                  # Gemini CLI extension (slash commands)
adapters/windsurf/                # Windsurf workflows
```

The agent handles project setup, chapter discovery, and memory updates directly with its file tools. Only the two scripts above remain — they do regex pattern matching and text transformation, where determinism matters.

## Install For Codex

```bash
mkdir -p ~/.codex/skills
cp -R core/fanqie-plus ~/.codex/skills/fanqie-plus
```

Then ask Codex naturally:

```text
用 fanqie-plus 帮我开一本都市脑洞番茄长篇。
继续写下一章。
检查第1-3章黄金三章和平台合规。
导出番茄格式。
```

## Use With Gemini CLI

Link the skill into the Gemini extension folder, then point Gemini at it:

```bash
mkdir -p adapters/gemini/skills
ln -sfn ../../../core/fanqie-plus adapters/gemini/skills/fanqie-plus
```

`adapters/gemini/` then contains:

```text
GEMINI.md
gemini-extension.json
commands/fanqie/*.toml
skills/fanqie-plus -> ../../../core/fanqie-plus
```

Available slash commands:

```text
/fanqie:new      Open a new Fanqie novel project
/fanqie:plan     Plan roadmap, anchors, and chapter queue
/fanqie:next     Continue the next chapter
/fanqie:review   Review chapters or checkpoints
/fanqie:export   Export final chapters to Fanqie plain text
```

## Use With Windsurf

```bash
mkdir -p adapters/windsurf/.windsurf/skills
ln -sfn ../../../../core/fanqie-plus adapters/windsurf/.windsurf/skills/fanqie-plus
```

`adapters/windsurf/` then contains:

```text
AGENTS.md
.windsurf/workflows/fanqie-*.md
.windsurf/skills/fanqie-plus -> ../../../../core/fanqie-plus
```

Run the workflows for opening, planning, continuing, reviewing, and exporting.

## Project Workflow

### 1. Open A New Novel

Have the agent create the project skeleton based on the user's idea:

```text
00_config/        idea_seed.md, target_profile.md, style_bible.md, platform_strategy.md
01_bible/         characters.yaml, world.md, timeline.yaml, foreshadowing.yaml
02_outline/       novel_roadmap.md, volume_plan.md, chapter_queue.yaml, outline_anchors.yaml
03_memory/        novel_state.json, chapter_summaries.md, pacing_ledger.csv
04_chapters/      drafts/, final/
05_reviews/
06_export/fanqie/
```

The agent fills the seed files based on the user's actual idea, not a generic template.

### 2. Continue The Next Chapter

The agent finds the next chapter by reading `03_memory/novel_state.json` or listing `04_chapters/final/`, loads the minimal context, drafts a beat sheet, and writes the chapter into `04_chapters/drafts/`.

### 3. Run Mechanical Gates

```bash
core/fanqie-plus/scripts/gate_check.py ./my-novel/04_chapters/final/第1章.md \
  --json-out ./my-novel/05_reviews/第1章-gate.json
```

The script flags:

- missing chapter title
- character count out of range
- meta contamination
- URL/contact/ad/off-platform diversion patterns
- Markdown artifacts
- excessive blank lines
- weak hook signal warning

Semantic checks (pacing, emotional pull, continuity, style drift, hidden acceleration, platform risk) remain the agent's job.

### 4. Update Memory After A Passed Chapter

The agent appends a summary to `03_memory/chapter_summaries.md`, bumps `current_chapter` and `current_words` in `novel_state.json`, and adds a row to `03_memory/pacing_ledger.csv` (columns: `chapter,title,pace,quota,hook_type,words,gate_passed,notes`). Only update memory after the chapter passes gates or the user accepts the repaired version.

### 5. Export Fanqie Text

```bash
core/fanqie-plus/scripts/export_fanqie.py ./my-novel --combined
```

Exports clean `.txt` files under `06_export/fanqie/`.

## Quality Gates

The main gate file is `core/fanqie-plus/references/quality-gates.md`. Platform compliance is in `core/fanqie-plus/references/platform-compliance.md`.

Blocking gates include:

- meta contamination
- URL/contact/diversion/ad/transaction content
- missing hook
- outline anchor violation
- A/B/C quota violation
- continuity break
- style break
- golden three chapter failure

## Validate

Compile scripts:

```bash
python3 -m py_compile core/fanqie-plus/scripts/*.py
```

Validate the core skill with the Codex skill creator validator:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py core/fanqie-plus
```

## Update The GitHub Repo

```bash
git add .
git commit -m "refactor: trim helper scripts and adapter layer"
git push
```
