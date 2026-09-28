---
name: research-weaver
description: >-
  Use when a user wants to set up or change a Zotero-to-Obsidian paper-note
  destination; read a Zotero-managed paper into Chinese, English, or bilingual
  Obsidian notes; turn paper evidence into traceable designs, assumptions,
  experiments, and questions; weave a paper into a literature library; or
  reuse linked notes for comparison, review, planning, or cited writing.
---

# Research Weaver

Turn paper evidence into a traceable research asset and then into research action. Treat Zotero as the authority for identity, metadata, citation keys, and the source PDF. Treat Obsidian as the home of derived notes and verified literature relations. Never copy the complete PDF into Obsidian or modify Zotero.

## Resolve

Read [configuration](references/configuration.md) whenever the task needs to read or write the Obsidian literature library. If no valid saved configuration exists, Ask for the Obsidian Vault absolute path, its paper-notes directory, and the default output language. Save the answers with `scripts/note_store.py configure` only after validating the directory. Do not infer them from unrelated folders.

On later runs, load the saved configuration and Show the resolved destination and language before paper work. Treat a user-specified path or language as a one-run override unless the user explicitly asks to change the saved default.

Resolve one Zotero item and its local PDF with `scripts/zotero_local.py`; reject ambiguous matches. Resolve `zh-CN`, `en`, or `both` using [output languages](references/output-languages.md). Run `scripts/note_store.py preflight` before drafting; preserve existing variants and require current-file hash authorization for an update.

Stop when identity is ambiguous, the attachment is missing or mismatched, full text is unreadable, only an abstract is available, the target conflicts with another identity, or an existing note lacks update authorization.

## Read and translate into research

Read the PDF in place once. Apply the [evidence contract](references/evidence-contract.md): distinguish paper claims, paper evidence, claim boundaries, reader inference, and research proposals. Read [paper-type guidance](references/paper-types.md) only when the evidence standard changes by paper type.

Draft with the [note architecture](references/note-architecture.md). Build one connected research-translation chain: reusable design → dependent assumption → testable experiment → follow-up question. Read [research reuse](references/research-reuse.md) for its experiment slots and for comparison, review, planning, or writing requests. Do not substitute generic future-work bullets.

## Weave and save

Apply the [weaving contract](references/library-weaving.md) only after the note is evidence-grounded. For every new paper-note task, automatically search plausible existing notes and add verified typed relations, each with a reason and research use, to the new note unless the user opts out. Do not ask for a second weaving prompt or modify counterpart notes during this automatic pass; Obsidian backlinks expose the reverse connection. Modify an existing counterpart only when the user explicitly requests it and after a separate preflight and hash authorization.

Save each requested language atomically with `scripts/note_store.py save`. Report the paper identity, language, citation key, saved path, relations added, evidence gaps, and warnings. Never claim completion before the save succeeds.
