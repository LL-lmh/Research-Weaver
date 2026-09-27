# Library weaving contract

Connect a saved note only to verified notes in the current Obsidian library. A shared keyword is not a relationship. Add a link only when the source notes or their Zotero PDFs support the relation.

## Relation types

Use exactly one primary type per proposition: `extends`, `challenges`, `supports`, `contradicts`, `alternative_method`, `shared_dataset`, `shared_metric`, `replication_of`, or `useful_baseline`.

Record each edge as:

```yaml
- target: "[[Existing paper note]]"
  type: supports
  reason: "Both report the same directional effect under comparable settings."
  research_use: "Use together to justify the literature-review claim on robustness."
  evidence: "new note §3; target note §3"
```

`reason` states the specific proposition or resource connecting the papers. `research_use` states how the edge helps comparison, experiment design, review synthesis, or writing. If either is generic, omit the edge.

## Incremental update

Search candidate notes by identifiers, explicit citations, methods, datasets, metrics, and claims. Inspect only plausible candidates. Update the new note first. Modify an affected counterpart only after a separate hash-authorized preflight for that existing note; without authorization, report the proposed reciprocal edge instead. Preserve manual prose and unrelated links. Never rewrite the whole library, invent a missing note, or downgrade a contradiction into vague “similarity”.

If the candidate evidence is insufficient, record it as an unresolved reading question instead of a relation.
