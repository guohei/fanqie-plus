# fanqie-plus

`fanqie-plus` is a cross-agent skill package for writing and managing long-form Fanqie/Tomato-style Chinese web novels.

The single source of truth is the standard Agent Skill in `core/fanqie-plus/`. Any skill-compatible agent can install that directory directly. Adapter folders for Gemini CLI and Windsurf only contain platform-specific entry points (slash commands, workflows) and reuse the same skill via a symlink.

## What It Does

- Open a Fanqie novel project with reader profile, style bible, platform strategy, and project structure.
- Plan long-book roadmaps, outline anchors, volume plans, and near-term chapter queues.
- Continue chapters with beat sheets, memory retrieval, quality gates, and memory updates.
- Repair chapters that fail gates.
- Review golden three chapters, 8w/10w/15w checkpoints, pacing, continuity, and platform compliance.
- Use an indexed genre/hook/opening/style craft library on demand, without loading the whole corpus.
- Run advisory reader simulation and cross-agent review at 10-chapter and Fanqie checkpoints.
- Run 10-chapter consistency audits for outline, memory, chapter queue, pacing ledger, and final chapter drift.
- Export clean Fanqie-ready plain text.

## Repository Layout

```text
core/fanqie-plus/                 # the skill — single source of truth
  SKILL.md
  agents/openai.yaml
  assets/
    project_AGENTS.md             # template copied into each novel project root
  references/
  scripts/
    gate_check.py                 # deterministic mechanical gate
    export_fanqie.py              # Markdown → Fanqie plain text
    fanqie_audit.py               # fanqie layout adapter for advisory review
    reader_simulator.py           # advisory reader-perspective scoring
    cross_agent_reviewer.py       # external-review prompt and issue parser

adapters/gemini/                  # Gemini CLI extension (slash commands)
adapters/windsurf/                # Windsurf workflows
```

The agent handles project setup, chapter discovery, and memory updates directly with its file tools. Scripts are reserved for deterministic gates, text transformation, and advisory review reports.

## Install

### Universal Skill Package

Install `core/fanqie-plus/` into the skill directory used by your agent:

```bash
mkdir -p <agent-skill-dir>
rsync -a --delete --exclude '__pycache__/' core/fanqie-plus/ <agent-skill-dir>/fanqie-plus/
```

Then ask the agent naturally:

```text
用 fanqie-plus 帮我开一本都市脑洞番茄长篇。
继续写下一章。
检查第1-3章黄金三章和平台合规。
导出番茄格式。
```

The installed skill root should contain `SKILL.md`, `references/`, `scripts/`, and `assets/`.

### Known Integrations

#### Codex

```bash
mkdir -p ~/.codex/skills
rsync -a --delete --exclude '__pycache__/' core/fanqie-plus/ ~/.codex/skills/fanqie-plus/
```

#### Gemini CLI

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

#### Windsurf

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
AGENTS.md         project-level instruction file that forces future agents to use fanqie-plus
00_config/        idea_seed.md, target_profile.md, style_bible.md, platform_strategy.md
01_bible/         characters.yaml, world.md, timeline.yaml, foreshadowing.yaml
02_outline/       novel_roadmap.md, volume_plan.md, chapter_queue.yaml, outline_anchors.yaml
03_memory/        novel_state.json, chapter_summaries.md, pacing_ledger.csv
04_chapters/      drafts/, final/
05_reviews/
06_export/fanqie/
```

The agent also creates project-root `AGENTS.md` from `core/fanqie-plus/assets/project_AGENTS.md` so future agents entering the book directory are told to use `fanqie-plus`. This project-level file is intentionally minimal: it keeps hard workflow boundaries and points agents back to skill references. Style, chapter hooks, chapter length, AI-pattern cleanup, and pacing quota details stay in project config and references such as `00_config/style_bible.md`, `references/quality-gates.md`, and `references/outline-anchor.md`.

The agent fills the seed files based on the user's actual idea, not a generic template.
When the genre is clear, the agent may enter `core/fanqie-plus/references/genres/INDEX.md`, choose one relevant index, and load only the matching leaf file for genre structure.

### 2. Continue The Next Chapter

The agent runs each chapter as a single transaction: check `next_required_review`, load minimal context, save `05_reviews/第N章-beat.md`, write `04_chapters/drafts/第N章.md`, run mechanical gates to `05_reviews/第N章-gate.json`, write semantic review to `05_reviews/第N章-review.md`, then save accepted正文 to `04_chapters/final/第N章.md` and update memory.
For craft support, it loads genre files only for chapters 1-3, new arcs, failed quality gates, or a specific prose problem.

### 3. Run Mechanical Gates

```bash
core/fanqie-plus/scripts/gate_check.py ./my-novel/04_chapters/drafts/第1章.md \
  --json-out ./my-novel/05_reviews/第1章-gate.json
```

The script flags:

- missing chapter title
- character count out of range (default 2000-4000 CJK characters, blocking)
- meta contamination
- URL/contact/ad/off-platform diversion patterns
- AI-pattern fingerprints and degree-adverb overuse
- Markdown artifacts
- excessive blank lines
- weak hook signal warning

Semantic checks (pacing, emotional pull, continuity, style drift, hidden acceleration, platform risk) are written to `05_reviews/第N章-review.md`. A chapter is not accepted until both mechanical and semantic gates pass.

### 4. Update Memory After A Passed Chapter

The agent appends a summary to `03_memory/chapter_summaries.md`, including an `Outline sync:` line only when the accepted正文 requires future queue/anchor repair. It also bumps `current_chapter` and `current_words` in `novel_state.json`, and adds a row to `03_memory/pacing_ledger.csv` (columns: `chapter,title,pace,quota,hook_type,words,gate_passed,notes`). Only update memory after the chapter passes gates or the user accepts the repaired version.

After a due 10-chapter audit passes, advance `next_required_review` in `novel_state.json` to the next review point, such as `第20章`.

### 5. Run 10-Chapter Consistency Audit

After every 10 accepted final chapters, the project-level `AGENTS.md` tells future agents to stop before continuing and run the consistency audit in `core/fanqie-plus/references/consistency-audit.md`.

The audit compares:

- roadmap, volume plan, outline anchors, and chapter queue
- `novel_state.json`, chapter summaries, and pacing ledger
- recent accepted正文 in `04_chapters/final/`
- character, timeline, and foreshadowing files when needed

Write the report to `05_reviews/consistency/chapter-XXX.md`. Blocking conflicts must be repaired before the agent drafts the next chapter. If正文 improved a stale细纲, update the downstream outline and memory instead of forcing正文 backward.
Routine drift control stays in the existing memory, outline, pacing, and audit files; do not create separate planned-vs-actual ledgers unless the user asks for one.

### 6. Export Fanqie Text

```bash
core/fanqie-plus/scripts/export_fanqie.py ./my-novel --combined
```

Runs mechanical gates first, then exports clean `.txt` files under `06_export/fanqie/`. Use `--no-gate` only for diagnostic cleanup, not for publish-ready packages.

### 7. Run Advisory Review

At 10-chapter reviews, 8w, 10w, 15w, and volume endings:

```bash
core/fanqie-plus/scripts/fanqie_audit.py --project-root ./my-novel reader --chapter 50
core/fanqie-plus/scripts/fanqie_audit.py --project-root ./my-novel cross-review --chapter 50
```

Reader reports are copied to `05_reviews/reader/`; cross-review prompts are copied to `05_reviews/cross/` for a separate LLM to review.

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

Run regression tests:

```bash
python3 -m unittest discover -s tests -v
```

Validate the core skill with the Codex skill creator validator:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py core/fanqie-plus
```

Third-party notices for bundled MIT-licensed review scripts and craft references are in `core/fanqie-plus/THIRD_PARTY_NOTICES.md`.

## Update The GitHub Repo

```bash
git add .
git commit -m "feat: add project agents contract"
git push
```
