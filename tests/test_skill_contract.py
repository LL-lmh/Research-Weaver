import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = [
    "configuration.md",
    "evidence-contract.md",
    "note-architecture.md",
    "output-languages.md",
    "paper-types.md",
    "library-weaving.md",
    "research-reuse.md",
]


class SkillContractTests(unittest.TestCase):
    def test_skill_directly_routes_every_reference_and_stays_small(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in REFERENCES:
            self.assertIn(f"references/{name}", skill)
        body = skill.split("---", 2)[-1]
        words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", body)
        self.assertLessEqual(len(words), 500)

    def test_skill_contains_actionable_contracts_and_stop_conditions(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "evidence contract",
            "research-translation chain",
            "weaving contract",
            "Stop when",
            "Never copy",
            "Run",
            "Read",
        ):
            self.assertIn(phrase, skill)

    def test_first_run_configuration_is_a_triggered_admission_step(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        self.assertIn("set up or change", frontmatter)
        for phrase in (
            "If no valid saved configuration exists",
            "Ask for",
            "Save the answers",
            "Show the resolved destination",
        ):
            self.assertIn(phrase, skill)

        configuration = (ROOT / "references" / "configuration.md").read_text(encoding="utf-8")
        for phrase in (
            "RESEARCH_WEAVER_CONFIG",
            "Obsidian Vault absolute path",
            "paper-notes directory",
            "default output language",
        ):
            self.assertIn(phrase, configuration)

    def test_note_architecture_has_confirmed_sections_in_both_languages(self):
        note = (ROOT / "references" / "note-architecture.md").read_text(encoding="utf-8")
        for phrase in (
            "论文定位",
            "问题与核心贡献",
            "方法或论证主线",
            "证据与关键结果",
            "批判性阅读",
            "研究连接",
            "可参考内容",
            "引用",
            "Paper Positioning",
            "Problem and Core Contributions",
            "Method or Argument",
            "Evidence and Key Results",
            "Critical Reading",
            "Research Connections",
            "Referenceable Content",
            "Citations",
        ):
            self.assertIn(phrase, note)

    def test_evidence_and_experiment_contracts_are_explicit(self):
        evidence = (ROOT / "references" / "evidence-contract.md").read_text(encoding="utf-8")
        reuse = (ROOT / "references" / "research-reuse.md").read_text(encoding="utf-8")
        for label in (
            "paper_claim",
            "paper_evidence",
            "claim_boundary",
            "reader_inference",
            "research_proposal",
        ):
            self.assertIn(label, evidence)
        for slot in ("intervention", "comparison", "metrics", "decision"):
            self.assertIn(slot, reuse)

    def test_weaving_contract_uses_typed_reasoned_relations(self):
        weaving = (ROOT / "references" / "library-weaving.md").read_text(encoding="utf-8")
        for relation in (
            "extends",
            "challenges",
            "supports",
            "contradicts",
            "alternative_method",
            "shared_dataset",
            "shared_metric",
            "replication_of",
            "useful_baseline",
        ):
            self.assertIn(relation, weaving)
        self.assertIn("reason", weaving)
        self.assertIn("research_use", weaving)
        self.assertIn("hash-authorized preflight", weaving)

    def test_new_paper_tasks_automatically_weave_without_rewriting_counterparts(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        weaving = (ROOT / "references" / "library-weaving.md").read_text(encoding="utf-8")
        configuration = (ROOT / "references" / "configuration.md").read_text(
            encoding="utf-8"
        )

        for phrase in (
            "For every new paper-note task",
            "unless the user opts out",
            "Obsidian backlinks",
        ):
            self.assertIn(phrase, skill)

        for phrase in (
            "Automatic pass for a new paper",
            "Do not modify counterpart notes",
            "one-run opt-out",
        ):
            self.assertIn(phrase, weaving)

        self.assertIn("requires no additional configuration", configuration)

    def test_language_contract_is_not_translation_first(self):
        languages = (ROOT / "references" / "output-languages.md").read_text(encoding="utf-8")
        self.assertIn("zh-CN", languages)
        self.assertIn("en", languages)
        self.assertIn("both", languages)
        self.assertIn("same evidence model", languages)
        self.assertIn("not translate", languages)


if __name__ == "__main__":
    unittest.main()
