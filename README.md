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
- Run cross-agent review at Fanqie checkpoints, volume endings, and high-risk review moments.
- Keep heuristic reader simulation available as an optional diagnostic, not a default gate.
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
    install_project_skill.py      # embed/upgrade skill inside a book project
    git_checkpoint.py             # commit and push project checkpoints
    fanqie_doctor.py              # project/chapter workflow completeness check
    export_fanqie.py              # Markdown → Fanqie plain text
    fanqie_audit.py               # fanqie layout adapter for optional/external review
    reader_simulator.py           # optional heuristic reader-perspective scoring
    cross_agent_reviewer.py       # external-review prompt and issue parser

adapters/gemini/                  # Gemini CLI extension (slash commands)
adapters/windsurf/                # Windsurf workflows
```

The agent handles project setup, chapter discovery, and memory updates directly with its file tools. Scripts are reserved for deterministic gates, embedded-skill installation, Git checkpointing, workflow completeness checks, text transformation, optional diagnostics, and external-review prompts.

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

### Embedded Project Skill

For portable book projects, embed the skill into the project itself:

```bash
core/fanqie-plus/scripts/install_project_skill.py --project-root ./my-novel \
  --source core/fanqie-plus
```

This creates `.fanqie-plus/`, creates or updates project-root `AGENTS.md` without deleting existing custom instructions, adds a `manifest.json`, and updates `.gitignore`. Agents should use `.fanqie-plus/SKILL.md` before any global skill installation.

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
.fanqie-plus/     embedded skill used when moving between agents or machines
00_config/        idea_seed.md, target_profile.md, style_bible.md, platform_strategy.md
01_bible/         characters.yaml, world.md, timeline.yaml, foreshadowing.yaml
02_outline/       novel_roadmap.md, volume_plan.md, chapter_queue.yaml, outline_anchors.yaml
03_memory/        novel_state.json, chapter_summaries.md, pacing_ledger.csv
04_chapters/      drafts/, final/
05_reviews/
06_export/fanqie/
```

The agent embeds `fanqie-plus` into `.fanqie-plus/` and creates or updates project-root `AGENTS.md` from `.fanqie-plus/assets/project_AGENTS.md` so future agents entering the book directory use the same workflow. Existing project-specific `AGENTS.md` content is preserved. This project-level file is intentionally minimal: it keeps hard workflow boundaries and points agents back to embedded skill references. Style, chapter hooks, chapter length, AI-pattern cleanup, and pacing quota details stay in project config and references such as `00_config/style_bible.md`, `.fanqie-plus/references/quality-gates.md`, and `.fanqie-plus/references/outline-anchor.md`.

The agent fills the seed files based on the user's actual idea, not a generic template.
When the genre is clear, the agent may enter `.fanqie-plus/references/genres/INDEX.md`, choose one relevant index, and load only the matching leaf file for genre structure.

### 2. Continue The Next Chapter

The agent runs each chapter as a lean transaction: check `next_required_review`, load minimal context, save a compact `05_reviews/第N章-beat.md`, write `04_chapters/drafts/第N章.md`, run mechanical gates to `05_reviews/第N章-gate.json`, repair blocking findings, then save accepted正文 to `04_chapters/final/第N章.md` and update memory.
Full `05_reviews/第N章-review.md` files are strict-mode artifacts only: chapters 1-3, 10-chapter audits, 8w/10w/15w, volume boundaries, failed gates, user dissatisfaction, major continuity changes, or publish/export preparation.
For craft support, it loads genre files only for chapters 1-3, new arcs, failed gates, checkpoints, or a specific prose problem.

### 3. Run Mechanical Gates

```bash
cd ./my-novel
.fanqie-plus/scripts/gate_check.py 04_chapters/drafts/第1章.md \
  --json-out 05_reviews/第1章-gate.json
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

Semantic checks (pacing, emotional pull, continuity, style drift, hidden acceleration, platform risk) still require agent judgment. Write them to `05_reviews/第N章-review.md` only in strict mode; otherwise keep the default path lightweight and let the mechanical gate plus memory update carry the routine chapter transaction.

### 4. Update Memory After A Passed Chapter

The agent appends a summary to `03_memory/chapter_summaries.md`, including an `Outline sync:` line only when the accepted正文 requires future queue/anchor repair. It also bumps `current_chapter` and `current_words` in `novel_state.json`, and adds a row to `03_memory/pacing_ledger.csv` (columns: `chapter,title,pace,quota,hook_type,words,gate_passed,notes`). Only update memory after the chapter passes gates or the user accepts the repaired version.

After a due 10-chapter audit passes, advance `next_required_review` in `novel_state.json` to the next review point, such as `第20章`.

### 5. Check Workflow Completeness

Use the doctor script as a hard stop before asking an agent to continue or handing the project to another agent:

```bash
cd ./my-novel
.fanqie-plus/scripts/fanqie_doctor.py --project-root . chapter-check --chapter 12
.fanqie-plus/scripts/fanqie_doctor.py --project-root . project-check --require-git-remote
```

It reports missing embedded skill files, missing beat/draft/gate/final/memory artifacts, failed gate JSON, stale `novel_state.json`, and due 10-chapter consistency reviews. With `--require-git-remote`, it also blocks missing Git repo or remote; without that flag, missing Git is a warning for local experiments. `BLOCKED` findings return exit code `1`.

### 6. Save A Git Checkpoint

In temporary or cloud agent workspaces, commit and push after completed chapters, reviews, repairs, exports, or outline changes:

```bash
cd ./my-novel
.fanqie-plus/scripts/git_checkpoint.py --project-root . --message "第12章完成：核心事件简述"
```

The script stages all project changes, commits them, and pushes. If no remote exists, it exits nonzero because a local-only commit does not protect a temporary workspace. Use `--no-push` only for local testing.
If there are no new working-tree changes, it still attempts to push existing local commits so a retry after a failed push can protect a temporary workspace.

### 7. Run 10-Chapter Consistency Audit

After every 10 accepted final chapters, the project-level `AGENTS.md` tells future agents to stop before continuing and run the consistency audit in `.fanqie-plus/references/consistency-audit.md`.

The audit compares:

- roadmap, volume plan, outline anchors, and chapter queue
- `novel_state.json`, chapter summaries, and pacing ledger
- recent accepted正文 in `04_chapters/final/`
- character, timeline, and foreshadowing files when needed

Write the report to `05_reviews/consistency/chapter-XXX.md`. Blocking conflicts must be repaired before the agent drafts the next chapter. If正文 improved a stale细纲, update the downstream outline and memory instead of forcing正文 backward.
Routine drift control stays in the existing memory, outline, pacing, and audit files; do not create separate planned-vs-actual ledgers unless the user asks for one.

### 8. Export Fanqie Text

```bash
cd ./my-novel
.fanqie-plus/scripts/export_fanqie.py . --combined
```

Runs mechanical gates first, then exports clean `.txt` files under `06_export/fanqie/`. Use `--no-gate` only for diagnostic cleanup, not for publish-ready packages.

### 9. Run External AI Review

Use external AI review when a checkpoint actually needs an independent read: 8w, 10w, 15w, volume endings, major repair decisions, persistent quality doubts, or user-requested review. The reviewer must be a different model/session from the writing agent.

```bash
cd ./my-novel
.fanqie-plus/scripts/fanqie_audit.py --project-root . cross-review --chapter 50
```

For a 10-chapter span or volume/checkpoint review:

```bash
.fanqie-plus/scripts/fanqie_audit.py --project-root . cross-batch \
  --chapter-start 41 --chapter-end 50
```

Cross-review prompts are copied to `05_reviews/cross/`. Paste the prompt into a separate LLM, save its report under `05_reviews/cross/`, then parse saved reports with:

```bash
.fanqie-plus/scripts/fanqie_audit.py --project-root . cross-parse \
  --report-file 05_reviews/cross/ch050_review_report.md
```

The parser writes `05_reviews/cross/ch050_issues.json`.

P0 findings block the next chapter until repaired. P1 findings should be handled at the current checkpoint or volume boundary. P2 findings go to backlog.

`reader_report.md` still exists for quick heuristic checks, but it is not part of the default 10-chapter or Fanqie checkpoint gate:

```bash
.fanqie-plus/scripts/fanqie_audit.py --project-root . reader --chapter 50
```

Reader reports are copied to `05_reviews/reader/` and should be treated as hints only.

## Quality Gates

Inside a book project, the main gate file is `.fanqie-plus/references/quality-gates.md`. Platform compliance is in `.fanqie-plus/references/platform-compliance.md`.

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

## Save Book Project Checkpoints

For embedded book projects, prefer:

```bash
.fanqie-plus/scripts/git_checkpoint.py --project-root . --message "第12章完成：核心事件简述"
```

It commits and pushes to the configured remote, which protects temporary AI-agent workspaces from being reclaimed.

## Update This Skill Repo

```bash
git add .
git commit -m "feat: add project agents contract"
git push
```
