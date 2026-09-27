# Note architecture

Build a research asset, not a section-by-section summary. Keep every major conclusion traceable through the [evidence contract](evidence-contract.md). Adapt depth to the paper; do not fill slots with generic prose.

## Shared YAML

Include at least: `title`, `authors`, `year`, `zotero_item_key`, `citekey`, `doi` when available, `language`, `paper_type`, `status`, `source_pdf`, and `tags`. The source PDF is a reference to Zotero's existing attachment, never a copied PDF.

## 中文结构 (`zh-CN`)

1. **论文定位** — 一句话结论；为什么值得读；与我的研究关系。
2. **问题与核心贡献** — 研究问题；核心贡献；相对已有工作的变化。
3. **方法或论证主线** — 整体思路；工作流程；关键机制；必要的公式或实现细节。
4. **证据与关键结果** — 实验/材料设置；决定性结果；结果意味着什么。
5. **批判性阅读** — 真正证明了什么；局限与风险；容易误读的地方。
6. **研究连接**
   - **可参考内容**：值得复用的设计；最值得质疑的假设；建议复现实验；后续阅读问题。
   - 与我的研究和知识库的关系。
   - 下一步行动。
7. **引用** — Citation Key、DOI/URL 和必要的页码锚点。

## English structure (`en`)

1. **Paper Positioning** — one-sentence conclusion; why it is worth reading; relation to my research.
2. **Problem and Core Contributions** — research problem; contributions; change from prior work.
3. **Method or Argument** — overall approach; workflow; mechanisms; necessary equations/implementation details.
4. **Evidence and Key Results** — setup/materials; decisive results; what they imply.
5. **Critical Reading** — what is actually shown; limitations/risks; likely misreadings.
6. **Research Connections**
   - **Referenceable Content**: reusable designs; most questionable assumptions; proposed replication experiments; follow-up reading questions.
   - Relation to my research and library.
   - Next actions.
7. **Citations** — citation key, DOI/URL, and necessary page anchors.

Place a selected method or result figure beside the paragraph it supports. Do not create a detached figure dump. If evidence is insufficient, preserve an explicit gap rather than inventing content.
