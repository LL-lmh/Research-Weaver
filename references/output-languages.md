# Output languages

Resolve the run language in this order: explicit user request, runtime option, configuration default, then `zh-CN`. Accept `zh-CN`, `en`, or `both`.

- For `zh-CN`, draft directly in Chinese while retaining important original technical terms.
- For `en`, draft directly in English.
- For `both`, extract and assess the PDF once. Build one same evidence model with shared anchors, then draft two language-specific notes. Do not translate one finished note into the other.

Each language variant has its own file and `language` value but shares Zotero identity and the paper directory. Never replace one language with another. Before updating an existing same-language file, run preflight and require the exact current SHA-256 as authorization.

Keep claims, numbers, boundaries, and citation anchors aligned across variants. Allow explanations and terminology choices to differ where the target language requires it. If one version reveals an evidence defect, correct the common evidence model before regenerating only the affected sections in both variants.
