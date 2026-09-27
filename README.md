<div align="center">

# Research Weaver

**把 Zotero 里的论文，变成一篇有证据、能复用、值得长期保留的 Obsidian 笔记。**

[![status](https://img.shields.io/badge/status-stable-16a34a)](#)
[![license](https://img.shields.io/badge/license-MIT-c9a227)](LICENSE)
[![agent](https://img.shields.io/badge/agent-Codex-7c3aed)](agents/openai.yaml)
[![source](https://img.shields.io/badge/source-Zotero-cc2936)](https://github.com/zotero/zotero)
[![output](https://img.shields.io/badge/output-Obsidian-6f42c1)](https://github.com/obsidianmd/obsidian-releases)
[![language](https://img.shields.io/badge/notes-中文%20%7C%20English-0f766e)](references/output-languages.md)

</div>

[![Research Weaver：从论文到研究笔记](assets/research-weaver-hero.jpeg)](assets/research-weaver-hero.jpeg)

Research Weaver 是一个论文笔记生成 Skill：从 Zotero 原位读取论文 PDF，在 Obsidian 中生成结构清晰、证据可追溯的中文、英文或双语笔记。

## Why Research Weaver

**为什么选择它？** 因为一篇好笔记不只要“总结完整”，还要能回到证据，并能继续服务研究。

- 原始 PDF 留在 Zotero，不重复下载、不复制进 Vault；
- 论文主张、证据边界和你的推断不会混在一起；
- 先生成一篇可长期保留的论文笔记，再从中形成假设、实验和文献关系。

## 示例

<!-- TODO: Add a real before-and-after example here. -->

```text
paper evidence
  → traceable research asset
  → questionable assumption
  → testable experiment
  → literature network
  → research writing
```

Research Weaver 通过三个契约实现这条路径：

- **证据契约**：区分作者主张、论文证据、结论边界、读者推断和研究建议；
- **研究转译契约**：把“值得复用的设计 → 所依赖的假设 → 可检验实验 → 后续问题”连成一条因果链；
- **文献编织契约**：只建立有类型、有理由、有研究用途的论文关系，不用模糊的“相似”链接。

Zotero retains the PDF. Obsidian 只保存派生的 Markdown 笔记与关系；Skill 不把完整 PDF 复制进 Vault。

## 1. 安装指南

### 1.1 环境要求

开始前请准备：

- 支持本地 Skills 与文件访问的 Codex；
- Python 3.10 或更高版本；如果现有 `python --version` 已满足要求，直接使用当前环境，无需另装。本仓库当前已在 Python 3.12.7（Anaconda）验证；
- 正在运行且允许本地 API 的 Zotero Desktop；
- 至少一个带有可读本地 PDF 附件的 Zotero 条目；
- 一个已经创建好的 Obsidian Vault；
- 可选：Better BibTeX，用于生成稳定的 Citation Key。

### 1.2 安装 Skill

#### 推荐：使用 Skills CLI

这是最接近 DeepPaperNote 等公开 Agent Skill 的安装方式。它会从 GitHub 识别 `research-weaver`，并安装到用户级 Codex Skills 目录：

```powershell
npx skills add LL-lmh/Research-Weaver --global --agent codex --skill research-weaver
```

如果希望由 CLI 交互选择安装范围和 Agent，也可以使用较短的命令：

```powershell
npx skills add LL-lmh/Research-Weaver
```

注意：不带 `--global` 时，在项目目录中运行可能安装为项目级 Skill。对日常跨项目使用，推荐保留上面的 `--global --agent codex`。

Research Weaver 当前是独立 Agent Skill，尚未打包为 Claude Code 插件，因此不要使用 `claude plugin marketplace add` 或 `claude plugin install` 命令。

#### 备用：手动安装到 Codex

不使用 Skills CLI 时，可以直接克隆到 Codex 的个人 Skills 目录。

Windows PowerShell：

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
git clone https://github.com/LL-lmh/Research-Weaver.git (Join-Path $codexHome "skills\research-weaver")
```

macOS / Linux：

```bash
git clone https://github.com/LL-lmh/Research-Weaver.git "${CODEX_HOME:-$HOME/.codex}/skills/research-weaver"
```

安装完成后，重新启动 Codex 或新建一个任务，让 Codex 重新发现 Skill。

### 1.3 确认安装成功

在 Codex 中输入：

```text
$research-weaver 告诉我你能处理哪些论文输入，以及会生成什么结果。不要写入任何文件。
```

如果 Codex 能识别 `$research-weaver` 并说明 Zotero 读取、证据分析和 Obsidian 输出能力，说明安装已经生效。

也可以在仓库目录检查两个辅助脚本：

```powershell
python scripts/zotero_local.py status
python scripts/note_store.py --help
```

第一条命令用于确认 Zotero Local API 是否可访问；第二条命令只显示帮助，不会写入文件。

### 1.4 首次配置

第一次执行需要读取或写入 Obsidian 文献库的任务时，Skill 会询问：

1. Obsidian Vault 的绝对路径；
2. Vault 内的论文笔记子目录；
3. 默认输出语言：`zh-CN`、`en` 或 `both`。

确认后，配置保存在用户私有配置目录，而不是 GitHub Skill 文件夹。Windows 默认为 `%APPDATA%/research-weaver/config.json`；也可以通过 `RESEARCH_WEAVER_CONFIG` 指定位置。以后运行会先显示实际保存目录和语言，一次性覆盖不会修改默认设置。

也可以手动配置：

```powershell
python scripts/note_store.py configure --vault "C:/path/to/your/ObsidianVault" --papers-root "Research/Papers" --default-language zh-CN
python scripts/note_store.py show-config
```

[`examples/research-weaver.example.json`](examples/research-weaver.example.json) 仅用于展示字段结构：

```json
{
  "vault": "C:/path/to/your/ObsidianVault",
  "papers_root": "Research/Papers",
  "default_language": "zh-CN",
  "note_naming": "slug-language",
  "index_note": "Research/Paper Index.md"
}
```

`default_language` 可为 `zh-CN`、`en` 或 `both`。完整字段及安全规则见 [`references/configuration.md`](references/configuration.md)。不要把包含私人绝对路径的配置提交到 Git。

## 2. 如何使用

### 2.1 最短用法

确保 Zotero Desktop 正在运行，并且目标论文已经保存在 Zotero 中且带有本地 PDF。随后在 Codex 中直接输入：

```text
$research-weaver 读取 Zotero 中这篇论文，生成中文研究笔记并保存到我的 Obsidian Vault：<DOI、标题或 Zotero Item Key>
```

你可以使用以下任一方式指定论文：

| 输入 | 适用情况 | 示例 |
| --- | --- | --- |
| DOI | 最稳定的公开论文标识 | `10.xxxx/xxxxx` |
| Zotero Item Key | 已知本地条目的精确标识 | `ABCD1234` |
| 论文标题 | 不知道 DOI 或 Item Key | 完整、尽量精确的标题 |

如果标题对应多个 Zotero 条目，Skill 会停止并请你选择，不会自行猜测。

### 2.2 常用示例

生成中文笔记：

```text
$research-weaver 读取 Zotero 中 DOI 为 10.xxxx/xxxxx 的论文，生成 zh-CN 笔记并保存到我的 Vault。
```

只解析一次证据，同时生成中英文笔记：

```text
$research-weaver 读取 Zotero item key ABCD1234，只解析一次证据，生成 both 双语版本。
```

从论文证据继续设计研究：

```text
$research-weaver 基于这篇论文的证据，提取可复用设计、关键假设，设计一个可证伪的复现实验，并连接到已有论文笔记。
```

只分析、不保存：

```text
$research-weaver 读取 DOI 为 10.xxxx/xxxxx 的论文并分析证据，但这次不要写入 Obsidian。
```

不写 `$research-weaver` 也可以直接说明任务，例如：“读取 Zotero 中这篇论文并保存为 Obsidian 双语研究笔记”。显式写出 Skill 名称通常更容易确保调用正确。

首次写入前，Skill 会显示实际的 Vault 目录、论文子目录和输出语言。任务完成后，它会报告解析到的论文身份、生成的文件以及建立的文献关系。

`zotero_local.py` 只发出 GET 请求。`note_store.py` 会先执行 preflight，再以当前文件 SHA-256 作为覆盖授权，并使用同目录临时文件原子写入。

## Skill documentation map

Research Weaver 按“核心工作流 → 按需加载的领域合约 → 确定性辅助脚本”组织：

| 文件 | 用途 |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Skill 入口：定义触发范围、主工作流、停止条件和完成回报。 |
| [`agents/openai.yaml`](agents/openai.yaml) | ChatGPT/Codex 界面元数据与默认提示。 |
| [`references/configuration.md`](references/configuration.md) | 首次运行、私有配置、路径解析和单次覆盖规则。 |
| [`references/evidence-contract.md`](references/evidence-contract.md) | 区分作者主张、论文证据、结论边界、读者推断与研究建议。 |
| [`references/paper-types.md`](references/paper-types.md) | 针对实证、方法、综述、理论等论文类型调整证据标准。 |
| [`references/note-architecture.md`](references/note-architecture.md) | 中文与英文研究笔记的 YAML 和正文结构。 |
| [`references/output-languages.md`](references/output-languages.md) | `zh-CN`、`en`、`both` 的解析与双语生成规则。 |
| [`references/research-reuse.md`](references/research-reuse.md) | 将证据转译为可复用设计、可检验假设、实验与后续问题。 |
| [`references/library-weaving.md`](references/library-weaving.md) | 定义有类型、有理由、有研究用途的文献关系及安全回写规则。 |
| [`scripts/zotero_local.py`](scripts/zotero_local.py) | 只读访问 Zotero Local API，解析论文身份、附件与本地 PDF 路径。 |
| [`scripts/note_store.py`](scripts/note_store.py) | 校验配置、执行 preflight、防止身份冲突，并将笔记原子写入 Vault。 |
| [`examples/research-weaver.example.json`](examples/research-weaver.example.json) | 不含个人路径的可移植配置示例。 |

## Output layout

```text
<Vault>/<papers_root>/
└─ <paper-title>--<citekey>/
   ├─ <paper-title>.zh-CN.md
   ├─ <paper-title>.en.md
   ├─ images/
   └─ .research-weaver.json
```

只创建本次请求的语言版本。`both` 共享同一论文身份与证据模型，但分别用目标语言撰写；英文不是中文成品的机械翻译。笔记结构见 [`references/note-architecture.md`](references/note-architecture.md)。

## Safety and privacy

- Zotero 是论文身份、元数据、附件和 PDF 的事实源；访问为只读。
- Obsidian 是派生研究资产的写入目标；写入限制在配置的 Vault 内。
- 标题搜索有多个候选时停止，不自动猜选。
- 只有摘要、PDF 不可读或身份冲突时停止，不生成伪精读。
- 已有同语言笔记默认不覆盖；只有当前 SHA-256 精确匹配授权时才更新。
- 仓库不包含个人路径、论文 PDF、Zotero 数据库或笔记内容。

## Troubleshooting

- **无法连接 Zotero**：保持 Zotero Desktop 运行，执行 `python scripts/zotero_local.py status`。
- **出现多个候选条目**：改用 Zotero item key、DOI 或更精确标题。
- **找不到 PDF**：在 Zotero 中确认条目有本地 PDF 附件且文件存在。
- **配置被拒绝**：运行时 `vault` 必须是现有绝对路径；示例中的 `.` 只是可移植占位符。
- **拒绝覆盖**：重新执行 preflight，审阅现有笔记，并显式提供它当前的 SHA-256。
- **Windows 中文路径**：脚本以 UTF-8 和 `pathlib` 处理；不要手工转义 JSON 中的正斜杠路径。

## Limitations

- 当前版本面向单篇精读与增量关系编织，不是批量系统综述工具。
- PDF 理解与研究判断由运行 Skill 的模型完成；辅助脚本不自带 OCR 或 PDF 解析引擎。
- 不自动导入新论文、不写回 Zotero、不创建 Zotero 标签/Collection。
- 不自动重写整个 Obsidian 文献库，也不替代投稿前的人工证据核验。

## 致谢与灵感

Research Weaver 是独立实现，但它的设计建立在以下开源项目和工具所提供的经验之上。

### 直接设计灵感

- [DeepPaperNote](https://github.com/917Dhj/DeepPaperNote) — 启发了单篇论文深度阅读、证据优先和长期可用的 Obsidian 笔记设计。
- [Zotero + Obsidian + Codex Literature Workflow](https://github.com/guyumengyue/zotero-obsidian-codex-workflow) — 启发了 Zotero、Obsidian 与 Codex 的环境协同、初始化和日常文献工作流。

Research Weaver 在此基础上聚焦于自己的核心方向：把论文证据继续转译为可质疑假设、可检验实验、有语义的文献关系与引用写作。上述项目的版权与许可证分别归其原作者所有。

### 基础生态

- [Zotero](https://github.com/zotero/zotero) — 文献身份、元数据与本地 PDF 的事实源。
- [Better BibTeX for Zotero](https://github.com/retorquere/zotero-better-bibtex) — BibTeX、Citation Key 与写作工作流生态。
- [Obsidian Releases](https://github.com/obsidianmd/obsidian-releases) — 研究笔记与长期知识库的承载环境。
- [OpenAI Codex](https://github.com/openai/codex) — 执行 Research Weaver Skill 的智能代理环境。

## Contributing

感谢改进 Research Weaver。请保持项目的核心边界：Zotero 只读、PDF 原位读取、Obsidian 安全写入、证据与推断分离。

### Development workflow

1. 从最新分支创建小范围分支。
2. 使用 Python 3.10+ 标准库实现最小、可回滚的变更。
3. 在 Pull Request 中说明安全边界、验证证据和兼容性影响。

### Contract changes

更改证据标签、笔记架构、语言布局、关系类型、身份规则或覆盖策略时，同时更新相应的 `references/` 文档和契约代码。不要在 `SKILL.md` 重复完整规则；保持渐进式披露和所有 reference 的直接链接。

### Privacy and fixtures

不要提交真实 Vault 路径、用户名、Zotero 数据库、受版权保护的 PDF、私人批注或 API 凭据。开发样本应使用临时目录、合成元数据和本地假 HTTP server。

### Scope

欢迎修复 Windows/macOS/Linux 路径兼容、Zotero Local API 读取、安全写入、证据契约、语言版本和文献关系问题。引入网络服务、MCP、第三方依赖、写回 Zotero 或批量修改 Vault 的提案，应先解释必要性和可撤销方案。

许可证见 [`LICENSE`](LICENSE)。
