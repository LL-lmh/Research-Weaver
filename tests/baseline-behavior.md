# Baseline behavior without Research Weaver

Two fresh-context reviewers evaluated generic paper-note behavior without reading this repository or using a paper workflow Skill.

## Scenario A: abstract-only GraphRAG paper

The generic completion invented architecture details, experiments, multi-hop benefits, and application suitability. It presented an abstract claim as a verified finding, mixed assistant interpretation with author claims, offered four disconnected suggestions (“larger datasets”, “more baselines”, “another domain”), and linked “similar” papers without a relation type, reason, or verified research use.

Observable failure: a polished note appeared complete even though full-text evidence, metrics, limitations, and page anchors were unavailable.

## Scenario B: bilingual Zotero-to-Obsidian run

The generic workflow risked overwriting a manually edited Chinese note, filename collisions, independently drifting Chinese and English claims, repeated download/extraction of the Zotero PDF, and provenance loss between source text, interpretation, and proposal. It also produced keyword-level literature links and non-operational “reusable ideas”.

Observable failure: the workflow lacked identity admission, content-hash authorization, shared evidence for both languages, idempotent variants, and typed relations.

## Required improvement

Research Weaver must stop on abstract-only evidence, keep explicit provenance labels, build a connected design → assumption → experiment → question chain, preserve language variants, reuse one evidence model, and admit only typed relations with an explicit reason and research use.

## Post-Skill behavior check

A third fresh-context reviewer loaded `SKILL.md` and its direct references. All five target behaviors passed: abstract-only completion stopped; `both` preserved the existing Chinese note and shared one evidence model; research suggestions required the connected chain and operational experiment slots; vague similarity failed the weaving contract; and `reader_inference` remained distinct from `paper_claim`.
