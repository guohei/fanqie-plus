from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "core" / "fanqie-plus"
SKILL = SKILL_ROOT / "SKILL.md"
PROJECT_AGENTS_TEMPLATE = SKILL_ROOT / "assets" / "project_AGENTS.md"
CONSISTENCY_AUDIT = SKILL_ROOT / "references" / "consistency-audit.md"
QUALITY_GATES = SKILL_ROOT / "references" / "quality-gates.md"
STORY_MEMORY = SKILL_ROOT / "references" / "story-memory.md"
CHAPTER_PIPELINE = SKILL_ROOT / "references" / "chapter-pipeline.md"
CROSS_REVIEW = SKILL_ROOT / "references" / "cross-review.md"
READER_REVIEW = SKILL_ROOT / "references" / "reader-review.md"
README = ROOT / "README.md"
GEMINI_NEW = ROOT / "adapters" / "gemini" / "commands" / "fanqie" / "new.toml"
WINDSURF_NEW = ROOT / "adapters" / "windsurf" / ".windsurf" / "workflows" / "fanqie-new.md"


def section(text: str, heading: str, next_heading: str) -> str:
    match = re.search(
        rf"{re.escape(heading)}(?P<body>.*?){re.escape(next_heading)}",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError(f"Could not find section {heading!r}")
    return match.group("body")


class ProjectAgentsContractTests(unittest.TestCase):
    def test_open_book_workflow_requires_project_agents_file(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        open_book = section(skill, "### 1. Open a new book", "### 2. Plan the long book")
        layout = section(skill, "## Project Layout", "## Resource Map")

        self.assertIn("AGENTS.md", open_book)
        self.assertIn("assets/project_AGENTS.md", open_book)
        self.assertIn(".fanqie-plus", open_book)
        self.assertIn("scripts/install_project_skill.py", open_book)
        self.assertIn("AGENTS.md", layout)
        self.assertIn(".fanqie-plus/", layout)

    def test_project_agents_template_anchors_future_agents_to_fanqie_plus(self) -> None:
        self.assertTrue(PROJECT_AGENTS_TEMPLATE.is_file(), "missing project AGENTS.md template")

        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")
        required_snippets = [
            ".fanqie-plus/SKILL.md",
            "Do not continue to the next chapter",
            ".fanqie-plus/scripts/gate_check.py",
            ".fanqie-plus/scripts/fanqie_doctor.py --project-root . project-check --require-git-remote",
            ".fanqie-plus/scripts/fanqie_doctor.py",
            ".fanqie-plus/scripts/git_checkpoint.py",
            "04_chapters/final/",
            "Keep正文 and meta separate",
            "AGENTS.md",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_project_agents_delegates_ten_chapter_audit_to_reference(self) -> None:
        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")
        required_snippets = [
            "10-Chapter Consistency Audit",
            "After every 10 accepted final chapters",
            "do not continue to the next chapter",
            ".fanqie-plus/references/consistency-audit.md",
            "05_reviews/consistency/chapter-XXX.md",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

        self.assertNotIn("events promised in the outline or chapter queue but missing from正文", text)
        self.assertNotIn("events written in正文 but not reflected in memory", text)
        self.assertLessEqual(len(text.splitlines()), 32)

    def test_project_agents_contains_chapter_continuation_gate_without_full_pipeline(self) -> None:
        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")
        required_snippets = [
            "Chapter Continuation Gate",
            "Before starting the next chapter",
            "05_reviews/第N章-beat.md",
            "04_chapters/drafts/第N章.md",
            "05_reviews/第N章-gate.json",
            "04_chapters/final/第N章.md",
            "updated `03_memory/chapter_summaries.md`, `novel_state.json`, and `pacing_ledger.csv`",
            "For batch writing, repeat this gate per chapter",
            "Write `05_reviews/第N章-review.md` only when strict review mode is triggered",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

        self.assertNotIn("Chapter function.", text)
        self.assertNotIn("3-5 beats.", text)
        self.assertNotIn("Ending hook type and concrete signal", text)

    def test_project_agents_keeps_style_and_hook_rules_in_skill_references(self) -> None:
        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")

        forbidden_snippets = [
            "Every chapter needs one concrete next-click ending hook",
            "ending hook",
            "hook quality",
            "style, AI-pattern residue",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, text)

        self.assertIn(".fanqie-plus/references/quality-gates.md", text)

    def test_project_agents_keeps_platform_and_pacing_details_in_references(self) -> None:
        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")

        forbidden_snippets = [
            "2000-4000",
            "Target publishable chapter length",
            "Each chapter may trigger at most one major quota item",
            "A main conflict advance",
            "B decisive relationship change",
            "C full core-secret reveal",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, text)

        self.assertIn(".fanqie-plus/references/quality-gates.md", text)
        self.assertIn(".fanqie-plus/references/outline-anchor.md", text)

    def test_project_agents_does_not_duplicate_reference_workflows(self) -> None:
        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")

        forbidden_snippets = [
            "Before drafting, read only the minimal context",
            "Create a beat sheet outside正文 before writing the chapter",
            "relevant `02_outline/chapter_queue.yaml` entry",
            "Exported正文 must contain no Markdown markers",
            "URLs, contact methods, ads",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, text)

        self.assertIn(".fanqie-plus/references/chapter-pipeline.md", text)
        self.assertIn(".fanqie-plus/references/story-memory.md", text)
        self.assertIn(".fanqie-plus/references/export-fanqie.md", text)
        self.assertIn(".fanqie-plus/references/platform-compliance.md", text)

    def test_consistency_audit_reference_defines_full_review_contract(self) -> None:
        self.assertTrue(CONSISTENCY_AUDIT.is_file(), "missing consistency audit reference")

        text = CONSISTENCY_AUDIT.read_text(encoding="utf-8")
        required_snippets = [
            "10-Chapter Consistency Audit",
            "02_outline/novel_roadmap.md",
            "02_outline/chapter_queue.yaml",
            "03_memory/pacing_ledger.csv",
            "04_chapters/final/",
            "05_reviews/consistency/chapter-XXX.md",
            "events promised in the outline or chapter queue but missing from正文",
            "events written in正文 but not reflected in memory",
            "blocking conflict",
            "Do not force正文 to match stale细纲",
            "## Report Template",
            "## Required Repair Behavior",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_story_memory_tracks_outline_sync_without_new_drift_artifact(self) -> None:
        text = STORY_MEMORY.read_text(encoding="utf-8")

        self.assertIn("- Outline sync:", text)
        self.assertIn("Use `Outline sync:` only for real plan drift", text)
        self.assertIn("Do not create extra drift ledgers", text)
        self.assertIn("chapter_summaries.md", text)
        self.assertIn("pacing_ledger.csv", text)

    def test_story_memory_uses_lightweight_continuity_guardrails(self) -> None:
        text = STORY_MEMORY.read_text(encoding="utf-8")

        self.assertIn("- Continuity notes / guardrails:", text)
        self.assertIn("concrete continuity risks", text)
        self.assertIn("not permanent bans", text)
        self.assertNotIn("Forbidden repeats", text)
        self.assertNotIn("events.json", text)

    def test_review_state_advances_after_due_audit(self) -> None:
        story_memory = STORY_MEMORY.read_text(encoding="utf-8")
        consistency_audit = CONSISTENCY_AUDIT.read_text(encoding="utf-8")

        self.assertIn("Advance `next_required_review`", story_memory)
        self.assertIn("Advance `next_required_review`", consistency_audit)
        self.assertIn("第20章", story_memory)

    def test_quality_gates_delegates_long_ai_fingerprint_list_to_script(self) -> None:
        text = QUALITY_GATES.read_text(encoding="utf-8")

        self.assertIn("AI_FINGERPRINTS", text)
        self.assertIn("6 or more advisory AI-pattern findings", text)
        self.assertLessEqual(len(text.splitlines()), 110)
        self.assertNotIn("命运的齿轮", text)
        self.assertNotIn("让...成为可能", text)

    def test_review_stage_invokes_consistency_audit_reference(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        review_stage = section(skill, "### 5. Review a stage", "### 6. Export to Fanqie")
        resource_map = section(skill, "## Resource Map", "## Scripts")

        self.assertIn("references/consistency-audit.md", review_stage)
        self.assertIn("05_reviews/consistency/chapter-XXX.md", review_stage)
        self.assertIn("references/consistency-audit.md", resource_map)

    def test_reader_report_is_optional_and_cross_review_is_primary_external_review(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        cross_review = CROSS_REVIEW.read_text(encoding="utf-8")
        reader_review = READER_REVIEW.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("major repair decisions", skill)
        self.assertIn("It is not a default 10-chapter or checkpoint gate", skill)
        self.assertIn("Treat reader-report findings as hints", skill)
        self.assertIn("scripts/fanqie_audit.py cross-parse", skill)

        self.assertIn("外部 AI 审稿使用文档", cross_review)
        self.assertIn("fanqie_audit.py --project-root . cross-parse", cross_review)
        self.assertIn("--report-file", cross_review)
        self.assertNotIn("--report 05_reviews", cross_review)
        self.assertNotIn("cross_agent_reviewer.py parse", cross_review)
        self.assertIn("不要因为 `reader_report` 分数低就自动触发外部审稿", cross_review)

        self.assertIn("optional heuristic", reader_review)
        self.assertIn("不要在每 10 章、8w/10w/15w、卷末默认运行它", reader_review)

        self.assertIn("Run External AI Review", readme)
        self.assertIn(".fanqie-plus/scripts/fanqie_audit.py --project-root . cross-parse", readme)
        self.assertIn("Reader reports are copied to `05_reviews/reader/` and should be treated as hints only", readme)
        self.assertNotIn("Run advisory reader simulation and cross-agent review at 10-chapter", readme)

    def test_continue_stage_uses_lean_default_transaction(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        continue_stage = section(skill, "### 3. Continue the next chapter", "### 4. Repair a chapter")

        required_snippets = [
            "lean single-chapter transaction",
            "`next_required_review`",
            "05_reviews/第N章-beat.md",
            "04_chapters/drafts/第N章.md",
            "05_reviews/第N章-gate.json",
            "04_chapters/final/第N章.md",
            "03_memory/chapter_summaries.md",
            "03_memory/pacing_ledger.csv",
            "scripts/fanqie_doctor.py",
            "scripts/git_checkpoint.py",
            "Only then may the next chapter start",
            "strict review mode",
            "Write `05_reviews/第N章-review.md` only in strict review mode",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, continue_stage)

        self.assertNotIn("perform semantic checks yourself", continue_stage)

    def test_chapter_pipeline_requires_lean_transaction_and_strict_review_triggers(self) -> None:
        text = CHAPTER_PIPELINE.read_text(encoding="utf-8")

        required_snippets = [
            "Default Chapter Transaction",
            "Check `next_required_review`",
            "Save `05_reviews/第N章-beat.md`",
            "save `05_reviews/第N章-gate.json`",
            "Strict Review Mode",
            "Write `05_reviews/第N章-review.md` only when strict mode is triggered",
            "Only copy or rewrite into `04_chapters/final/第N章.md` after mechanical gates pass and any required strict review has passed",
            "chapters 1-3",
            "every 10-chapter audit",
            "8w, 10w, or 15w",
            "`gate_check.py` fails",
            "Batch generation repeats this transaction for each chapter",
            "Do not draft later chapters first and gate them afterward",
            "fanqie_doctor.py",
            "git_checkpoint.py",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_new_project_adapters_also_create_agents_file(self) -> None:
        for path in [GEMINI_NEW, WINDSURF_NEW]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", text, f"{path} should mention project AGENTS.md")


if __name__ == "__main__":
    unittest.main()
