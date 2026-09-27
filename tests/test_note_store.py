import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.note_store import (
    IdentityConflictError,
    OverwriteDeniedError,
    default_config_path,
    load_config,
    preflight,
    save_config,
    save_note,
)


IDENTITY = {
    "item_key": "ABCD1234",
    "title": "图神经网络: A Study",
    "doi": "10.1000/example",
    "citekey": "li2026graph",
    "pdf_sha256": "a" * 64,
}


class NoteStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name) / "研究 Vault"
        self.vault.mkdir()
        self.config = {
            "vault": str(self.vault),
            "papers_root": "Research/Papers",
            "default_language": "zh-CN",
            "note_naming": "slug-language",
        }

    def test_load_config_requires_absolute_existing_vault(self):
        path = Path(self.temp.name) / "config.json"
        path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(load_config(path)["vault"], str(self.vault.resolve()))
        path.write_text(json.dumps({**self.config, "vault": "."}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_config(path)

    def test_load_config_accepts_bilingual_default(self):
        path = Path(self.temp.name) / "config-both.json"
        path.write_text(
            json.dumps({**self.config, "default_language": "both"}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.assertEqual(load_config(path)["default_language"], "both")

    def test_default_config_path_honors_private_environment_override(self):
        configured = Path(self.temp.name) / "private" / "research-weaver.json"
        with mock.patch.dict(os.environ, {"RESEARCH_WEAVER_CONFIG": str(configured)}):
            self.assertEqual(default_config_path(), configured.resolve())

    def test_save_config_creates_private_parent_and_round_trips(self):
        path = Path(self.temp.name) / "private" / "config.json"
        result = save_config(self.config, path)
        self.assertEqual(Path(result["config_path"]), path.resolve())
        self.assertEqual(load_config(path)["papers_root"], "Research/Papers")
        self.assertEqual(list(path.parent.glob(".research-weaver-*.tmp")), [])

    def test_configure_cli_saves_first_run_configuration(self):
        path = Path(self.temp.name) / "settings" / "config.json"
        script = Path(__file__).resolve().parents[1] / "scripts" / "note_store.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "configure",
                "--config",
                str(path),
                "--vault",
                str(self.vault),
                "--papers-root",
                "论文阅读",
                "--default-language",
                "both",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["papers_root"], "论文阅读")
        self.assertEqual(saved["default_language"], "both")

    def test_new_note_and_unicode_paths(self):
        admission = preflight(self.config, IDENTITY, "zh-CN")
        self.assertEqual(admission["status"], "new")
        self.assertIn("图神经网络", admission["note_path"])
        result = save_note(admission, "# 中文笔记\n", None, config=self.config)
        self.assertEqual(result["action"], "created")
        self.assertEqual(Path(result["note_path"]).read_text(encoding="utf-8"), "# 中文笔记\n")

    def test_language_variants_share_identity_directory(self):
        zh = preflight(self.config, IDENTITY, "zh-CN")
        save_note(zh, "# 中文\n", None, config=self.config)
        en = preflight(self.config, IDENTITY, "en")
        self.assertEqual(Path(zh["paper_dir"]), Path(en["paper_dir"]))
        self.assertNotEqual(zh["note_path"], en["note_path"])
        save_note(en, "# English\n", None, config=self.config)
        sidecar = json.loads((Path(en["paper_dir"]) / ".research-weaver.json").read_text(encoding="utf-8"))
        self.assertEqual(set(sidecar["variants"]), {"zh-CN", "en"})

    def test_exact_identity_reuses_directory(self):
        first = preflight(self.config, IDENTITY, "zh-CN")
        save_note(first, "one", None, config=self.config)
        second = preflight(self.config, dict(IDENTITY), "en")
        self.assertEqual(first["paper_dir"], second["paper_dir"])

    def test_existing_note_requires_matching_hash(self):
        first = preflight(self.config, IDENTITY, "zh-CN")
        created = save_note(first, "version one", None, config=self.config)
        existing = preflight(self.config, IDENTITY, "zh-CN")
        self.assertEqual(existing["status"], "existing")
        with self.assertRaises(OverwriteDeniedError):
            save_note(existing, "version two", None, config=self.config)
        with self.assertRaises(OverwriteDeniedError):
            save_note(existing, "version two", "0" * 64, config=self.config)
        updated = save_note(
            existing, "version two", created["note_sha256"], config=self.config
        )
        self.assertEqual(updated["action"], "updated")

    def test_identity_conflict_stops(self):
        first = preflight(self.config, IDENTITY, "zh-CN")
        save_note(first, "one", None, config=self.config)
        conflict = {**IDENTITY, "item_key": "DIFFERENT"}
        with self.assertRaises(IdentityConflictError):
            preflight(self.config, conflict, "en")

    def test_failed_replace_preserves_existing_and_cleans_temp(self):
        first = preflight(self.config, IDENTITY, "zh-CN")
        created = save_note(first, "stable", None, config=self.config)
        existing = preflight(self.config, IDENTITY, "zh-CN")
        with mock.patch("scripts.note_store.os.replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                save_note(
                    existing, "partial", created["note_sha256"], config=self.config
                )
        self.assertEqual(Path(existing["note_path"]).read_text(encoding="utf-8"), "stable")
        self.assertEqual(list(Path(existing["paper_dir"]).glob(".research-weaver-*.tmp")), [])

    def test_interruption_before_note_commit_preserves_existing_note(self):
        first = preflight(self.config, IDENTITY, "zh-CN")
        created = save_note(first, "stable", None, config=self.config)
        existing = preflight(self.config, IDENTITY, "zh-CN")
        real_replace = __import__("os").replace
        calls = 0

        def interrupt_second_replace(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt("simulated process interruption")
            return real_replace(source, destination)

        with mock.patch("scripts.note_store.os.replace", side_effect=interrupt_second_replace):
            with self.assertRaises(KeyboardInterrupt):
                save_note(
                    existing, "uncommitted", created["note_sha256"], config=self.config
                )
        self.assertEqual(Path(existing["note_path"]).read_text(encoding="utf-8"), "stable")

    def test_title_correction_reuses_existing_language_file(self):
        original = preflight(self.config, IDENTITY, "zh-CN")
        save_note(original, "manual edits", None, config=self.config)
        corrected = preflight(
            self.config, {**IDENTITY, "title": "Corrected Paper Title"}, "zh-CN"
        )
        self.assertEqual(corrected["status"], "existing")
        self.assertEqual(corrected["note_path"], original["note_path"])

    def test_save_rejects_tampered_preflight_path(self):
        admission = preflight(self.config, IDENTITY, "zh-CN")
        admission["note_path"] = str(Path(self.temp.name) / "outside.md")
        with self.assertRaises(IdentityConflictError):
            save_note(admission, "escape", None, config=self.config)

    def test_cli_emits_unicode_preflight_as_utf8(self):
        config_path = Path(self.temp.name) / "config.json"
        identity_path = Path(self.temp.name) / "identity.json"
        config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
        identity_path.write_text(json.dumps(IDENTITY, ensure_ascii=False), encoding="utf-8")
        script = Path(__file__).resolve().parents[1] / "scripts" / "note_store.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "preflight",
                "--config",
                str(config_path),
                "--identity",
                str(identity_path),
                "--language",
                "zh-CN",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("图神经网络", result.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
