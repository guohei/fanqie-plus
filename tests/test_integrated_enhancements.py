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

    def test_fanqie_audit_exports_reader_and_cross_review_artifacts(self) -> None:
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

            reader_report = root / "05_reviews" / "reader" / "gate_artifacts" / "ch001" / "reader_report.md"
            cross_prompt = root / "05_reviews" / "cross" / "cross_review" / "ch001_review_prompt.md"
            reader_report_exists = reader_report.is_file()
            cross_prompt_exists = cross_prompt.is_file()

        self.assertEqual(reader.returncode, 0, reader.stderr)
        self.assertEqual(cross.returncode, 0, cross.stderr)
        self.assertTrue(reader_report_exists)
        self.assertTrue(cross_prompt_exists)


if __name__ == "__main__":
    unittest.main()
