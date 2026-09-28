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

## Automatic pass for a new paper

For every new paper-note task, search candidate notes automatically after the new paper is evidence-grounded. Inspect only plausible candidates, add supported typed relations to the new note, and continue to save without asking for a separate weaving command. A request such as “do not connect existing notes” is a one-run opt-out.

Do not modify counterpart notes during this automatic pass. The link in the new note already appears through Obsidian backlinks in the counterpart's view, so automatic reciprocal writes add risk without adding discoverability. Modify a counterpart file only when the user explicitly requests a stored reciprocal edge and authorizes that file's current hash.

## Incremental update

Search candidate notes by identifiers, explicit citations, methods, datasets, metrics, and claims. Update the new note first. Modify an affected counterpart only after a separate hash-authorized preflight for that existing note; without authorization, rely on the backlink or report the proposed reciprocal edge. Preserve manual prose and unrelated links. Never rewrite the whole library, invent a missing note, or downgrade a contradiction into vague “similarity”.

If the candidate evidence is insufficient, record it as an unresolved reading question instead of a relation.
