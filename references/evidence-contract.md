# Evidence contract

Use this contract whenever reading or drafting a paper note. Treat the Zotero PDF—not an abstract page or generated summary—as the authority for the paper's content.

## Provenance labels

Attach one of these labels to every consequential statement in working evidence. The final prose may render the label compactly, but its status must remain recoverable.

| Label | Meaning | Required support |
|---|---|---|
| `paper_claim` | What the authors state | page, section, figure, or table anchor |
| `paper_evidence` | Data, observation, derivation, quotation, or result offered by the paper | exact source anchor and relevant value/context |
| `claim_boundary` | What the evidence does not establish | linked claim/evidence plus the limiting condition |
| `reader_inference` | Interpretation derived by the reader/model | reasoning and supporting anchors; never attribute to authors |
| `research_proposal` | A new design, test, or question | the gap/assumption that motivates it |

## Evidence record

For each central method, result, and limitation, retain: `label`, concise content, PDF page (or stable section/figure/table), and confidence. Preserve the original technical term when translation could blur meaning.

Do not infer a result from the abstract alone. Stop and report the missing evidence when full text is absent, unreadable, encrypted, mismatched to the Zotero item, or too incomplete to support the central claims. Never silently convert missing evidence into fluent prose.

Prefer a small set of decisive anchors over exhaustive quotation. Verify numerical comparisons against their metric, dataset, split, baseline, and direction. Mark author-reported results as such when independent validation is absent.
