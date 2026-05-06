from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "core" / "fanqie-plus" / "scripts" / "gate_check.py"
EXPORT = ROOT / "core" / "fanqie-plus" / "scripts" / "export_fanqie.py"


def make_chapter(title: str, body: str, repeat: int = 1) -> str:
    return title + "\n" + ("\n".join([body] * repeat)) + "\n"


class FanqieScriptTests(unittest.TestCase):
    def test_gate_defaults_match_fanqie_chapter_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            chapter = Path(tmp) / "第1章.md"
            chapter.write_text(make_chapter("第1章 测试", "门外传来脚步声！", repeat=80), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(GATE), str(chapter)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertNotEqual(proc.returncode, 0)
        result = json.loads(proc.stdout)
        self.assertFalse(result["passed"])
        self.assertIn("short_chapter", {item["type"] for item in result["blocking_findings"]})

    def test_export_refuses_chapters_that_fail_mechanical_gate_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "04_chapters" / "final"
            final.mkdir(parents=True)
            (final / "第1章.md").write_text(
                make_chapter("第1章 坏样例", "TODO：这里补剧情。加微信看完整版。", repeat=80),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(EXPORT), str(root), "--min-chars", "1"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Export blocked", proc.stderr)
        self.assertFalse((root / "06_export" / "fanqie" / "第1章.txt").exists())

    def test_export_can_clean_and_order_gate_passing_chapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "04_chapters" / "final"
            final.mkdir(parents=True)
            (final / "第10章.md").write_text(
                make_chapter("# 第10章：后来的门", "他推开门，新的名字撞进眼底！", repeat=3),
                encoding="utf-8",
            )
            (final / "第2章.md").write_text(
                make_chapter("# 第2章：先来的信", "信纸背面只写着一个问题？", repeat=3),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(EXPORT),
                    str(root),
                    "--combined",
                    "--min-chars",
                    "1",
                    "--max-chars",
                    "1000",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            full = (root / "06_export" / "fanqie" / "full.txt").read_text(encoding="utf-8")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(full.index("第2章 先来的信"), full.index("第10章 后来的门"))
        self.assertNotIn("#", full)
        self.assertNotIn("：", full.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
