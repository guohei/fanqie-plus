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
DOCTOR = ROOT / "core" / "fanqie-plus" / "scripts" / "fanqie_doctor.py"
INSTALL_PROJECT_SKILL = ROOT / "core" / "fanqie-plus" / "scripts" / "install_project_skill.py"
GIT_CHECKPOINT = ROOT / "core" / "fanqie-plus" / "scripts" / "git_checkpoint.py"


def make_chapter(title: str, body: str, repeat: int = 1) -> str:
    return title + "\n" + ("\n".join([body] * repeat)) + "\n"


def make_embedded_skill(root: Path) -> None:
    embedded = root / ".fanqie-plus"
    (embedded / "scripts").mkdir(parents=True)
    (embedded / "references").mkdir()
    (embedded / "assets").mkdir()
    (embedded / "SKILL.md").write_text("---\nname: fanqie-plus\n---\n", encoding="utf-8")
    (embedded / "manifest.json").write_text('{"name":"fanqie-plus"}\n', encoding="utf-8")
    for script in ["gate_check.py", "fanqie_doctor.py", "git_checkpoint.py"]:
        (embedded / "scripts" / script).write_text("#!/usr/bin/env python3\n", encoding="utf-8")


def init_git_with_remote(root: Path) -> None:
    remote = root / "_remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=root, check=True)


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

    def test_doctor_project_check_passes_complete_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                "00_config",
                "01_bible",
                "02_outline",
                "03_memory",
                "04_chapters/drafts",
                "04_chapters/final",
                "05_reviews",
                "06_export/fanqie",
            ]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            init_git_with_remote(root)
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")
            (root / "05_reviews" / "第1章-beat.md").write_text("# beat\n", encoding="utf-8")
            (root / "04_chapters" / "drafts" / "第1章.md").write_text("第1章 测试\n", encoding="utf-8")
            (root / "04_chapters" / "final" / "第1章.md").write_text("第1章 测试\n", encoding="utf-8")
            (root / "05_reviews" / "第1章-gate.json").write_text(
                json.dumps({"passed": True, "blocking_findings": []}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "novel_state.json").write_text(
                json.dumps({"current_chapter": 1, "current_words": 10, "next_required_review": "第10章"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "chapter_summaries.md").write_text("## 第1章 测试\n- Summary: done\n", encoding="utf-8")
            (root / "03_memory" / "pacing_ledger.csv").write_text(
                "chapter,title,pace,quota,hook_type,words,gate_passed,notes\n1,测试,medium,none,suspense,10,true,\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "project-check"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK project-check", proc.stdout)

    def test_doctor_project_check_warns_missing_git_remote_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                "00_config",
                "01_bible",
                "02_outline",
                "03_memory",
                "04_chapters/drafts",
                "04_chapters/final",
                "05_reviews",
                "06_export/fanqie",
            ]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "project-check"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("WARN git remote is not configured", proc.stdout)

    def test_doctor_project_check_blocks_missing_git_remote_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                "00_config",
                "01_bible",
                "02_outline",
                "03_memory",
                "04_chapters/drafts",
                "04_chapters/final",
                "05_reviews",
                "06_export/fanqie",
            ]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "project-check", "--require-git-remote"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("BLOCKED git remote is not configured", proc.stdout)

    def test_doctor_chapter_check_blocks_missing_transaction_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "04_chapters" / "final").mkdir(parents=True)
            (root / "05_reviews").mkdir()
            (root / "03_memory").mkdir()
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")
            (root / "04_chapters" / "final" / "第2章.md").write_text("第2章 测试\n", encoding="utf-8")
            (root / "03_memory" / "novel_state.json").write_text(
                json.dumps({"current_chapter": 1, "next_required_review": "第10章"}, ensure_ascii=False),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "chapter-check", "--chapter", "2"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("BLOCKED missing 05_reviews/第2章-gate.json", proc.stdout)
        self.assertIn("BLOCKED novel_state.current_chapter is 1, expected 2", proc.stdout)

    def test_doctor_chapter_check_accepts_zero_padded_transaction_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "04_chapters" / "drafts").mkdir(parents=True)
            (root / "04_chapters" / "final").mkdir(parents=True)
            (root / "05_reviews").mkdir()
            (root / "03_memory").mkdir()
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")
            (root / "05_reviews" / "第024章-beat.md").write_text("# beat\n", encoding="utf-8")
            (root / "04_chapters" / "drafts" / "第024章.md").write_text("第024章 测试\n", encoding="utf-8")
            (root / "04_chapters" / "final" / "第024章.md").write_text("第024章 测试\n", encoding="utf-8")
            (root / "05_reviews" / "第024章-gate.json").write_text(
                json.dumps({"passed": True, "blocking_findings": []}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "novel_state.json").write_text(
                json.dumps({"current_chapter": 24, "next_required_review": "第30章"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "chapter_summaries.md").write_text("## 第024章 测试\n- Summary: done\n", encoding="utf-8")
            (root / "03_memory" / "pacing_ledger.csv").write_text(
                "chapter,title,pace,quota,hook_type,words,gate_passed,notes\n24,测试,medium,none,suspense,10,true,\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "chapter-check", "--chapter", "24"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("OK chapter-check", proc.stdout)

    def test_doctor_project_check_blocks_due_consistency_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                "00_config",
                "01_bible",
                "02_outline",
                "03_memory",
                "04_chapters/drafts",
                "04_chapters/final",
                "05_reviews",
                "06_export/fanqie",
            ]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            make_embedded_skill(root)
            (root / "AGENTS.md").write_text("Use `fanqie-plus` from `.fanqie-plus/`.\n", encoding="utf-8")
            (root / "05_reviews" / "第10章-beat.md").write_text("# beat\n", encoding="utf-8")
            (root / "04_chapters" / "drafts" / "第10章.md").write_text("第10章 测试\n", encoding="utf-8")
            (root / "04_chapters" / "final" / "第10章.md").write_text("第10章 测试\n", encoding="utf-8")
            (root / "05_reviews" / "第10章-gate.json").write_text(
                json.dumps({"passed": True, "blocking_findings": []}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "novel_state.json").write_text(
                json.dumps({"current_chapter": 10, "next_required_review": "第10章"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "03_memory" / "chapter_summaries.md").write_text("## 第10章 测试\n- Summary: done\n", encoding="utf-8")
            (root / "03_memory" / "pacing_ledger.csv").write_text(
                "chapter,title,pace,quota,hook_type,words,gate_passed,notes\n10,测试,medium,none,suspense,10,true,\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "project-check"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("BLOCKED next_required_review 第10章 is due", proc.stdout)
        self.assertIn("BLOCKED missing 05_reviews/consistency/chapter-010.md", proc.stdout)

    def test_doctor_project_check_blocks_missing_embedded_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                "00_config",
                "01_bible",
                "02_outline",
                "03_memory",
                "04_chapters/drafts",
                "04_chapters/final",
                "05_reviews",
                "06_export/fanqie",
            ]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            (root / "AGENTS.md").write_text("Use `fanqie-plus`.\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(DOCTOR), "--project-root", str(root), "project-check"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("BLOCKED missing .fanqie-plus/SKILL.md", proc.stdout)
        self.assertIn("BLOCKED AGENTS.md does not mention .fanqie-plus", proc.stdout)

    def test_install_project_skill_embeds_skill_agents_and_gitignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_PROJECT_SKILL),
                    "--project-root",
                    str(root),
                    "--source",
                    str(ROOT / "core" / "fanqie-plus"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            gitignore = (root / ".gitignore").read_text(encoding="utf-8")
            manifest = json.loads((root / ".fanqie-plus" / "manifest.json").read_text(encoding="utf-8"))
            embedded_skill_exists = (root / ".fanqie-plus" / "SKILL.md").is_file()
            embedded_doctor_exists = (root / ".fanqie-plus" / "scripts" / "fanqie_doctor.py").is_file()
            self_upgrade = subprocess.run(
                [
                    sys.executable,
                    str(root / ".fanqie-plus" / "scripts" / "install_project_skill.py"),
                    "--project-root",
                    str(root),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            embedded_install_survived = (root / ".fanqie-plus" / "scripts" / "install_project_skill.py").is_file()

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self_upgrade.returncode, 0, self_upgrade.stderr)
        self.assertTrue(embedded_skill_exists)
        self.assertTrue(embedded_doctor_exists)
        self.assertTrue(embedded_install_survived)
        self.assertIn(".fanqie-plus/SKILL.md", agents)
        self.assertIn(".fanqie-plus/scripts/git_checkpoint.py", agents)
        self.assertIn(".audit_workdir/", gitignore)
        self.assertEqual(manifest["name"], "fanqie-plus")

    def test_install_project_skill_preserves_existing_agents_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Existing\n\nKeep this project-specific rule.\n", encoding="utf-8")

            first = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_PROJECT_SKILL),
                    "--project-root",
                    str(root),
                    "--source",
                    str(ROOT / "core" / "fanqie-plus"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            second = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_PROJECT_SKILL),
                    "--project-root",
                    str(root),
                    "--source",
                    str(ROOT / "core" / "fanqie-plus"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(".fanqie-plus/SKILL.md", agents)
        self.assertIn("Keep this project-specific rule.", agents)
        self.assertLess(agents.index(".fanqie-plus/SKILL.md"), agents.index("Keep this project-specific rule."))
        self.assertEqual(agents.count(".fanqie-plus/SKILL.md"), 1)
        self.assertEqual(agents.count("Keep this project-specific rule."), 1)

    def test_git_checkpoint_commits_changes_without_push_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "04_chapters").mkdir()
            (root / "04_chapters" / "chapter.md").write_text("正文\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(GIT_CHECKPOINT),
                    "--project-root",
                    str(root),
                    "--message",
                    "第1章完成：测试",
                    "--no-push",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            log = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK committed", proc.stdout)
        self.assertIn("第1章完成：测试", log.stdout)

    def test_git_checkpoint_blocks_without_remote_when_push_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "chapter.md").write_text("正文\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(GIT_CHECKPOINT),
                    "--project-root",
                    str(root),
                    "--message",
                    "第1章完成：无远端",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 2)
        self.assertIn("OK committed", proc.stdout)
        self.assertIn("no git remote configured", proc.stderr)

    def test_git_checkpoint_pushes_existing_unpushed_commit_without_new_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            remote = Path(tmp) / "remote.git"
            root = Path(tmp) / "work"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "init", str(root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=root, check=True)
            (root / "checkpoint.md").write_text("已完成\n", encoding="utf-8")
            subprocess.run(["git", "add", "checkpoint.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "已有本地提交"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(GIT_CHECKPOINT),
                    "--project-root",
                    str(root),
                    "--message",
                    "无新增改动",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            remote_ref = subprocess.run(
                ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/main"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK no changes to commit", proc.stdout)
        self.assertIn("OK pushed", proc.stdout)
        self.assertEqual(remote_ref.returncode, 0, remote_ref.stderr)


if __name__ == "__main__":
    unittest.main()
