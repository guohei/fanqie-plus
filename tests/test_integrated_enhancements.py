from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "core" / "fanqie-plus"
GENRES = SKILL_ROOT / "references" / "genres"
AUDIT = SKILL_ROOT / "scripts" / "fanqie_audit.py"


class IntegratedEnhancementTests(unittest.TestCase):
    def test_genre_library_is_indexed_and_links_resolve(self) -> None:
        indexes = [
            GENRES / "INDEX.md",
            GENRES / "INDEX-genre-frameworks.md",
            GENRES / "INDEX-hook-techniques.md",
            GENRES / "INDEX-style-modules.md",
            GENRES / "INDEX-opening-design.md",
        ]

        for index in indexes:
            self.assertTrue(index.is_file(), f"missing genre index: {index}")

        leaf_files = [
            path
            for path in GENRES.rglob("*.md")
            if path.name not in {index.name for index in indexes}
        ]
        self.assertGreaterEqual(len(leaf_files), 200)

        missing: list[tuple[Path, str]] = []
        for index in indexes:
            text = index.read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^)#]+)", text):
                if not (index.parent / link).exists():
                    missing.append((index, link))
        self.assertEqual(missing, [])

    def test_fanqie_audit_exports_cross_review_and_keeps_reader_diagnostic_compatibility(self) -> None:
        self.assertTrue(AUDIT.is_file(), "fanqie_audit.py should be installed")
        self.assertTrue(os.access(AUDIT, os.X_OK), "fanqie_audit.py should be executable")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "02_outline").mkdir()
            (root / "04_chapters" / "final").mkdir(parents=True)
            (root / "05_reviews").mkdir()
            (root / "02_outline" / "novel_roadmap.md").write_text(
                "# 路线\n\n第1卷：低谷得牌。\n",
                encoding="utf-8",
            )
            chapter = root / "04_chapters" / "final" / "第1章_测试.md"
            chapter.write_text(
                "第1章 测试\n" + "门外忽然传来脚步声，他盯着短信上的名字，意识到真相没有结束！\n" * 120,
                encoding="utf-8",
            )

            reader = subprocess.run(
                [sys.executable, str(AUDIT), "--project-root", str(root), "reader", "--chapter", "1", "--threshold", "1"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cross = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT),
                    "--project-root",
                    str(root),
                    "cross-review",
                    "--chapter",
                    "1",
                    "--reviewer",
                    "gpt-5",
                    "--round",
                    "1",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cross_batch = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT),
                    "--project-root",
                    str(root),
                    "cross-batch",
                    "--chapter-start",
                    "1",
                    "--chapter-end",
                    "1",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            reader_report = root / "05_reviews" / "reader" / "gate_artifacts" / "ch001" / "reader_report.md"
            cross_prompt = root / "05_reviews" / "cross" / "cross_review" / "ch001_review_prompt.md"
            cross_batch_prompt = root / "05_reviews" / "cross" / "cross_review" / "batch_ch001-001_review_prompt.md"
            reader_report_exists = reader_report.is_file()
            cross_prompt_exists = cross_prompt.is_file()
            cross_batch_prompt_exists = cross_batch_prompt.is_file()

        self.assertEqual(reader.returncode, 0, reader.stderr)
        self.assertEqual(cross.returncode, 0, cross.stderr)
        self.assertEqual(cross_batch.returncode, 0, cross_batch.stderr)
        self.assertTrue(reader_report_exists)
        self.assertTrue(cross_prompt_exists)
        self.assertTrue(cross_batch_prompt_exists)

    def test_fanqie_audit_parses_external_review_into_fanqie_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "05_reviews" / "cross").mkdir(parents=True)
            report = root / "05_reviews" / "cross" / "ch001_review_report.md"
            report.write_text(
                "\n".join(
                    [
                        "# 第 1 章 · 外部审核报告",
                        "",
                        "| # | 严重度 | 位置 | 类型 | 问题描述 | 修复建议 |",
                        "|---|:------:|------|------|---------|---------|",
                        "| 1 | P0 | 第3段 | 时间线 | 主角上午死亡下午出现 | 改成昏迷或删除下午出场 |",
                        "| 2 | P2 | 第9段 | AI味 | 情绪总结偏多 | 改成动作细节 |",
                        "",
                        "- 整体评分：60/100",
                        "- 建议：□修复后通过",
                    ]
                ),
                encoding="utf-8",
            )

            parsed = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT),
                    "--project-root",
                    str(root),
                    "cross-parse",
                    "--report-file",
                    "ch001_review_report.md",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            issues = root / "05_reviews" / "cross" / "ch001_issues.json"
            issues_exists = issues.is_file()
            issues_text = issues.read_text(encoding="utf-8") if issues_exists else ""

        self.assertEqual(parsed.returncode, 1, parsed.stderr)
        self.assertTrue(issues_exists)
        self.assertIn('"p0_count": 1', issues_text)
        self.assertIn("主角上午死亡下午出现", issues_text)

    def test_fanqie_audit_generates_multi_review_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "00_config").mkdir()
            (root / "02_outline").mkdir()
            (root / "03_memory").mkdir()
            (root / "04_chapters" / "final").mkdir(parents=True)
            (root / "00_config" / "style_bible.md").write_text(
                "# Style Bible\n\n- POV: third-person limited\n- Tone: 爽文\n",
                encoding="utf-8",
            )
            (root / "02_outline" / "chapter_queue.yaml").write_text(
                "- chapter: 1\n  function: first pressure and visible hook\n",
                encoding="utf-8",
            )
            (root / "03_memory" / "chapter_summaries.md").write_text(
                "## 第0章 前情\n- Hook: 门外有人敲门\n",
                encoding="utf-8",
            )
            chapter = root / "04_chapters" / "final" / "第001章.md"
            chapter.write_text(
                "第001章 测试\n" + "他推开门，看见那封不该出现的录取通知书。\n" * 80,
                encoding="utf-8",
            )

            generated = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT),
                    "--project-root",
                    str(root),
                    "multi-review",
                    "--chapter",
                    "1",
                    "--preset",
                    "roundtable",
                    "--mode",
                    "prompt-pack",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            out_dir = root / "05_reviews" / "cross" / "multi_review" / "ch001"
            manifest = out_dir / "manifest.json"
            gold_author = out_dir / "gold-author.prompt.md"
            chief_editor = out_dir / "chief-editor.prompt.md"
            veteran_reader = out_dir / "veteran-reader.prompt.md"
            synthesis = out_dir / "00_synthesis.prompt.md"
            manifest_exists = manifest.is_file()
            gold_author_exists = gold_author.is_file()
            chief_editor_exists = chief_editor.is_file()
            veteran_reader_exists = veteran_reader.is_file()
            synthesis_exists = synthesis.is_file()
            manifest_text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""
            gold_text = gold_author.read_text(encoding="utf-8") if gold_author.is_file() else ""

        self.assertEqual(generated.returncode, 0, generated.stderr)
        self.assertTrue(manifest_exists)
        self.assertTrue(gold_author_exists)
        self.assertTrue(chief_editor_exists)
        self.assertTrue(veteran_reader_exists)
        self.assertTrue(synthesis_exists)
        self.assertIn('"requested_mode": "prompt-pack"', manifest_text)
        self.assertIn('"resolved_mode": "prompt-pack"', manifest_text)
        self.assertIn("番茄金番作家", gold_text)
        self.assertIn("只输出 P0/P1/P2", gold_text)
        self.assertIn("不要改写整章", gold_text)


if __name__ == "__main__":
    unittest.main()
