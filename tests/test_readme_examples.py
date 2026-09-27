import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeExamplesTests(unittest.TestCase):
    def test_readme_has_public_install_usage_and_safety_sections(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in (
            "## Why Research Weaver",
            "## 1. 安装指南",
            "### 1.1 环境要求",
            "### 1.2 安装 Skill",
            "### 1.3 确认安装成功",
            "### 1.4 首次配置",
            "## 2. 如何使用",
            "### 2.1 最短用法",
            "### 2.2 常用示例",
            "## Output layout",
            "## Safety and privacy",
            "## Troubleshooting",
            "## Limitations",
        ):
            self.assertIn(heading, readme)
        self.assertIn("MCP-free", readme)
        self.assertIn("zh-CN", readme)
        self.assertIn("both", readme)
        self.assertIn("Zotero retains the PDF", readme)

    def test_readme_does_not_publish_author_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for private_fragment in ("15354", "D:\\Obsidian", "Desktop\\vibecoding"):
            self.assertNotIn(private_fragment, readme)

    def test_documented_repository_paths_exist(self):
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "examples/research-weaver.example.json",
            "references/configuration.md",
            "scripts/zotero_local.py",
            "scripts/note_store.py",
            "LICENSE",
        ):
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_readme_maps_skill_documentation_and_contains_contribution_guidance(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Skill documentation map", readme)
        self.assertIn("## Contributing", readme)
        for relative in (
            "references/evidence-contract.md",
            "references/paper-types.md",
            "references/note-architecture.md",
            "references/output-languages.md",
            "references/research-reuse.md",
            "references/library-weaving.md",
        ):
            self.assertIn(relative, readme)

    def test_example_configuration_parses(self):
        config = json.loads(
            (ROOT / "examples" / "research-weaver.example.json").read_text(encoding="utf-8")
        )
        self.assertEqual(config["note_naming"], "slug-language")
        self.assertFalse(Path(config["vault"]).is_absolute())

    def test_documented_cli_help_commands_work(self):
        for script in ("scripts/zotero_local.py", "scripts/note_store.py"):
            result = subprocess.run(
                [sys.executable, str(ROOT / script), "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout.lower())

    def test_readme_opens_with_a_direct_value_proposition_and_example_slot(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = "\n".join(readme.splitlines()[:35])
        self.assertIn("不是把论文变成摘要", opening)
        self.assertIn("为什么选择", opening)
        self.assertIn("## 示例", opening)
        self.assertIn("TODO: Add a real before-and-after example", opening)

    def test_readme_credits_verified_inspirations_and_ecosystem(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 致谢与灵感", readme)
        for url in (
            "https://github.com/917Dhj/DeepPaperNote",
            "https://github.com/guyumengyue/zotero-obsidian-codex-workflow",
            "https://github.com/zotero/zotero",
            "https://github.com/retorquere/zotero-better-bibtex",
            "https://github.com/obsidianmd/obsidian-releases",
            "https://github.com/openai/codex",
        ):
            self.assertIn(url, readme)
        self.assertNotIn("github.com/OWNER/research-weaver", readme)
        self.assertIn("github.com/jvrczt8hvt-byte/Research-Weaver", readme)


if __name__ == "__main__":
    unittest.main()
