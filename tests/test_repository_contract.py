import json
import re
import unittest
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_skill_frontmatter_is_discoverable(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertRegex(text, r"(?m)^name: research-weaver$")
        description = re.search(r"(?ms)^description:\s*>-\n(.+?)^---$", text)
        self.assertIsNotNone(description)
        self.assertIn("Use when", description.group(1))

    def test_public_metadata_and_license_exist(self):
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "LICENSE").is_file())

    def test_example_configuration_is_portable(self):
        path = ROOT / "examples" / "research-weaver.example.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            set(config),
            {"vault", "papers_root", "default_language", "note_naming", "index_note"},
        )
        self.assertIn(config["default_language"], {"zh-CN", "en", "both"})
        self.assertFalse(PureWindowsPath(config["vault"]).is_absolute())
        self.assertNotIn("15354", path.read_text(encoding="utf-8"))

    def test_repository_has_no_mcp_manifest(self):
        self.assertFalse((ROOT / ".mcp.json").exists())
        self.assertFalse((ROOT / "mcp.json").exists())


if __name__ == "__main__":
    unittest.main()
