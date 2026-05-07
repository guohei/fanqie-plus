from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "core" / "fanqie-plus"
SKILL = SKILL_ROOT / "SKILL.md"
PROJECT_AGENTS_TEMPLATE = SKILL_ROOT / "assets" / "project_AGENTS.md"
CONSISTENCY_AUDIT = SKILL_ROOT / "references" / "consistency-audit.md"
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
        self.assertIn("AGENTS.md", layout)

    def test_project_agents_template_anchors_future_agents_to_fanqie_plus(self) -> None:
        self.assertTrue(PROJECT_AGENTS_TEMPLATE.is_file(), "missing project AGENTS.md template")

        text = PROJECT_AGENTS_TEMPLATE.read_text(encoding="utf-8")
        required_snippets = [
            "Use the `fanqie-plus` skill",
            "Do not continue to the next chapter",
            "scripts/gate_check.py",
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
            "references/consistency-audit.md",
            "05_reviews/consistency/chapter-XXX.md",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, text)

        self.assertNotIn("events promised in the outline or chapter queue but missing from正文", text)
        self.assertNotIn("events written in正文 but not reflected in memory", text)
        self.assertLessEqual(len(text.splitlines()), 45)

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

        self.assertIn("references/quality-gates.md", text)

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

        self.assertIn("references/quality-gates.md", text)
        self.assertIn("references/outline-anchor.md", text)

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

    def test_review_stage_invokes_consistency_audit_reference(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        review_stage = section(skill, "### 5. Review a stage", "### 6. Export to Fanqie")
        resource_map = section(skill, "## Resource Map", "## Scripts")

        self.assertIn("references/consistency-audit.md", review_stage)
        self.assertIn("05_reviews/consistency/chapter-XXX.md", review_stage)
        self.assertIn("references/consistency-audit.md", resource_map)

    def test_new_project_adapters_also_create_agents_file(self) -> None:
        for path in [GEMINI_NEW, WINDSURF_NEW]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", text, f"{path} should mention project AGENTS.md")


if __name__ == "__main__":
    unittest.main()
