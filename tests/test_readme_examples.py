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
        self.assertIn("zh-CN", readme)
        self.assertIn("both", readme)
        self.assertIn("Zotero retains the PDF", readme)

    def test_readme_recommends_verified_skills_cli_and_keeps_manual_fallback(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("推荐：使用 Skills CLI", readme)
        self.assertIn(
            "npx skills add LL-lmh/Research-Weaver --global --agent codex --skill research-weaver",
            readme,
        )
        self.assertIn("备用：手动安装到 Codex", readme)
        self.assertIn('${CODEX_HOME:-$HOME/.codex}/skills/research-weaver', readme)
        self.assertIn("尚未打包为 Claude Code 插件", readme)

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
        self.assertIn("## 🤝 贡献说明", readme)
        self.assertIn("Pull Request 提交到 `main`", readme)
        self.assertIn("tests/test_skill_contract.py", readme)
        self.assertIn("tests/test_smoke_workflow.py", readme)
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

    def test_readme_opens_with_a_direct_value_proposition_without_duplicate_hero(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = "\n".join(readme.splitlines()[:45])
        self.assertIn('<div align="center">', opening)
        self.assertIn("把 Zotero 里的论文", opening)
        self.assertIn("值得长期保留的 Obsidian 笔记", opening)
        self.assertIn("Research Weaver 是一个论文笔记生成 Skill", opening)
        self.assertIn("## 示例", readme)
        self.assertIn("TODO: Add a real before-and-after example", readme)
        self.assertNotIn("assets/research-weaver-hero.jpeg", readme)
        self.assertFalse((ROOT / "assets" / "research-weaver-hero.jpeg").exists())

    def test_why_section_explains_note_architecture_and_update_steps(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        why = readme.split("## Why Research Weaver", 1)[1].split("## 示例", 1)[0]

        self.assertIn("assets/research-weaver-why.png", why)
        why_image = ROOT / "assets" / "research-weaver-why.png"
        self.assertTrue(why_image.is_file())
        self.assertEqual(why_image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

        for concept in (
            "论文定位",
            "问题与核心贡献",
            "方法或论证主线",
            "证据与关键结果",
            "批判性阅读",
            "研究连接",
            "引用",
        ):
            self.assertIn(concept, why)

        self.assertIn("references/note-architecture.md", why)
        self.assertIn("references/library-weaving.md", why)
        self.assertIn("自动更新", why)
        self.assertIn("不是后台定时任务", why)
        self.assertIn("不需要额外配置", why)
        self.assertIn("自动检查已有论文笔记", why)
        self.assertIn("Obsidian 反向链接", why)
        self.assertIn("本次不要连接已有笔记", why)
        self.assertIn("1.4 首次配置", why)
        self.assertNotIn("#### 首次只配置一次", why)
        self.assertNotIn("#### 你需要做什么", why)
        self.assertNotIn("#### 什么时候需要重新配置", why)

    def test_readme_credits_verified_direct_inspirations(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 致谢与灵感", readme)
        for url in (
            "https://github.com/917Dhj/DeepPaperNote",
            "https://github.com/guyumengyue/zotero-obsidian-codex-workflow",
        ):
            self.assertIn(url, readme)
        self.assertNotIn("github.com/OWNER/research-weaver", readme)
        self.assertIn("github.com/LL-lmh/Research-Weaver", readme)
        self.assertNotIn("github.com/jvrczt8hvt-byte/Research-Weaver", readme)

    def test_readme_uses_scannable_section_icons_and_actionable_contribution_steps(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in (
            "## Why Research Weaver 🧭",
            "## 示例 📝",
            "## 1. 安装指南 🚀",
            "## 2. 如何使用 📖",
            "## Safety and privacy 🛡️",
            "## 🤝 贡献说明",
        ):
            self.assertIn(heading, readme)

        self.assertIn("### 如何提交修改", readme)
        self.assertIn("git switch -c", readme)
        self.assertIn("python -m unittest discover -s tests -v", readme)
        self.assertIn("### 修改位置速查", readme)
        self.assertNotIn("### Pull Request 检查清单", readme)


if __name__ == "__main__":
    unittest.main()
