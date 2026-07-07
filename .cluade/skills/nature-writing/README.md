# nature-writing-skill

> Claude Code / Codex skill — 面向中国 AI / ML 研究者，主投 **Nature Machine Intelligence**、次投 **Nature Communications / Nature Computational Science**、必要时冲刺 **Nature** 的论文写作技能。

把"能过审的 arXiv 风格"打磨成"Nature 系审稿人读完会说 *well-written, clearly motivated, compelling, careful, and hard to put down* 的论文"——本 skill 是 **44 篇开放获取论文逐句抽取**出来的 craft + taste + story-craft 手册，覆盖 abstract / intro / results / methods / discussion / figure 全链路。

---

## 是什么

| 部分 | 文件 | 内容 |
|---|---|---|
| 写作 skill | `SKILL.md` | 骨架公式、写作顺序、按任务加载的 routing table、提交前 checklist、屏幕边 quick card、44 篇语料附录 |
| 写作细节 | `references/01-story.md` … `15-taste-development.md` | 15 个主题文件，按需 Read |
| 配图 skill | `FIGURE-SKILL.md` | Fig. 1 schematic 6 种构图、Wong/Okabe-Ito 8 色、字体字号、matplotlib/ggplot 模板、Illustrator 拼版流程 |
| 配图细节 | `figure-references/01..12-*.md` | 12 个主题文件，按需 Read |
| 语料 | `extracts/01-singlecell.md` … `07-ai-methods.md` | 7 类领域 / 44 篇 OA 论文的 verbatim 抽取，所有引文可 grep 回原文 |
| 抽取方法 | `_framework.md` | 重建 / 扩充时参考 |

### 为什么"瘦索引 + 按需加载"

写作不是线性的。`SKILL.md` 只保留全局看得见的部分（骨架、顺序、checklist、quick card），其余 4000+ 行细节拆到 `references/`，按 routing 表只 Read 1–2 个文件——避免把整本手册塞进 context window。

| 你正在做什么 | Read |
|---|---|
| 写 abstract | `references/03-abstract.md` |
| 写 Results 子节 | `references/05-results.md` + `FIGURE-SKILL.md` |
| 自审稿 | `references/09-reviewer-protocol.md` + `references/13-antipatterns.md` |
| 选投哪个刊 | `references/14-journals.md` |
| 卡在一句话上 | `references/08-sentence-taste.md` |
| 长期 taste 培养 | `references/15-taste-development.md` |

完整 routing 表见 [`SKILL.md`](./SKILL.md) §1。

---

## 安装

### Claude Code

```bash
# 用户级（所有项目都能用）
git clone https://github.com/SyntaxSmith/nature-writing-skill.git ~/.claude/skills/nature-writing

# 或项目级（仅当前项目）
git clone https://github.com/SyntaxSmith/nature-writing-skill.git .claude/skills/nature-writing
```

Claude Code 启动后会自动读取 `SKILL.md` 的 frontmatter。在对话里输入 `/nature-writing` 触发，或直接自然语言："用 nature-writing skill 帮我打磨这段 abstract"。

### Codex CLI

Codex 没有 skill 概念，把仓库 clone 到任意位置，然后在项目 `AGENTS.md` 里加指针：

```bash
git clone https://github.com/SyntaxSmith/nature-writing-skill.git ~/skills/nature-writing
```

```markdown
<!-- AGENTS.md -->
## Writing for Nature-family journals
When drafting or revising papers for NMI / NC / NCS / Nature, first read
`~/skills/nature-writing/SKILL.md`, then load only the relevant
`references/*.md` per the routing table in §1.1.
```

或临时把对应章节作为附件丢给 Codex：

```bash
codex "@~/skills/nature-writing/references/03-abstract.md 用这一节检查我的 abstract"
```

### 其他 agent / chatbot

`SKILL.md` 是纯 Markdown，没有专属语法。任何能读文件的 LLM 工具（Cursor、Continue、Aider、ChatGPT custom GPT、Gemini Code Assist……）都可以把它当 system prompt 或附件用。

---

## 用法示例

**写 abstract**

```
> 我有一段 ML 方法论文的 abstract，请用 nature-writing skill 检查 pivot、
  KEY-RESULT 是否有 named baseline、outlook 动词是否与证据强度匹配。

[paste abstract]
```

**自审稿（5-pass harsh referee）**

```
> 用 references/09-reviewer-protocol.md 的 SNEER / NOD / ASK / CUT 协议
  审一遍我的 Results 章节，每段给 invisible answer。
```

**提交前总扫**

```
> 跑一遍 SKILL.md §2 的 checklist，每条标 ✅ / ⚠️ / ❌，
  ⚠️ 和 ❌ 给具体修改建议。
```

**子门类剧本**

```
> 这是一篇 LLM-agent 论文，按 references/12-subgenres.md 的剧本检查：
  prompt 报告完整性、tool schema 在不在 SI、外部 API 版本和 date 有没有写。
```

---

## 目录结构

```
.
├── SKILL.md                 # 写作 skill 瘦索引（必读）
├── FIGURE-SKILL.md          # 配图 skill 瘦索引
├── _framework.md            # 抽取方法论
├── references/              # 15 个写作细节文件
│   ├── 01-story.md          # 7 种 canonical story shapes、Fig. 1 四种功能
│   ├── 02-title.md          # Title 6 种定式
│   ├── 03-abstract.md       # 5–8 句句式图、Two-gap、carve-out
│   ├── 04-intro.md          # 漏斗 4–6 段、6 种 hook、GAP 词库
│   ├── 05-results.md        # 标题三风格、figure call-out、统计写法、ablation
│   ├── 06-methods.md        # 复现性三处呼应、LLM-agent 专用清单
│   ├── 07-discussion.md     # Outlook 动词等级、Limitation as boundary
│   ├── 08-sentence-taste.md # rhythm、经济、restraint、negative space
│   ├── 09-reviewer-protocol.md
│   ├── 10-voice.md          # DeepMind / NMI / NC / NCS / 临床 5 种 voice
│   ├── 11-language-bank.md  # 强动词 / hedge / 段间连接
│   ├── 12-subgenres.md      # 7 个子门类剧本
│   ├── 13-antipatterns.md
│   ├── 14-journals.md       # 各刊 voice 与策略
│   └── 15-taste-development.md
├── figure-references/       # 12 个配图细节文件
├── extracts/                # 7 个语料文件 / 44 篇 OA 论文 verbatim
└── archive/SKILL.v3.md      # 上一代 craft-only 版（保留供参考）
```

---

## 语料来源（44 篇 OA 论文）

| # | 领域 | 论文 | 刊物 |
|---|---|---|---|
| 1–6 | 单细胞基因组 | Geneformer · SCimilarity · Tangram · scIB · CellOracle · CellFM | Nature × 3 / Nat Methods × 2 / NC |
| 7–12 | 蛋白 / 结构 AI | AlphaFold2 · ESM-2 · ProteinMPNN · RFdiffusion · AlphaMissense · Foldseek | Nature × 2 / Science × 3 / Nat Biotechnol |
| 13–18 | 物理 / 气候 / 材料 | GraphCast · GenCast · DIMON · M3GNet · HINTS · GNoME | Science / Nature × 2 / NCS × 2 / NMI |
| 19–24 | 药物发现 | DynamicBind · Wong-MRSA · Halicin · SyntheMol · RetroExplainer · DRAGONFLY | NC × 4 / Nature / Cell |
| 25–30 | 临床 AI | MedSAM · UNI · CONCH · Virchow · MedPerf · Ferber-GPT4V | Nat Med × 3 / NC × 2 / NMI |
| 31–36 | ML 通用 / 基础模型 | ChemCrow · AlphaGeometry · MolE · SemanticLens · Cancer-Imaging-FM · FunSearch | NMI × 4 / Nature × 2 / NC |
| 37–44 | 纯 AI 方法 (v5 新增) | DeepSeek-R1 · Densing-law · AligNet · ADeLe · Webb-MAP · DiscoRL · Farquhar-semantic-entropy · Whitelam-Simmering | Nature × 5 / NMI / NC × 2 |

所有引文均来自开放获取论文（CC-BY 等 license），用于学术评论 / 写作教学。原作者保留版权。

---

## 如何扩展

新增第 8 类领域 / 第 45 篇论文：

1. 用 [`_framework.md`](./_framework.md) 的抽取格式，在 `extracts/` 下加新文件。
2. 把新句式 / 新模板回灌到对应 `references/*.md`（不是 `SKILL.md`，后者保持瘦索引）。
3. 更新 `SKILL.md` 附录 A 的 corpus 表 + `references/README.md` 的目录。

---

## License

- **代码 / Markdown 结构 / 抽取框架**：MIT
- **verbatim 引文**：原作者保留版权，使用时遵守对应 OA license。本仓库属于学术评论 / 教学用途。

---

## Patron sentence

> "Many problems in mathematical sciences are *easy to evaluate*, despite being typically *hard to solve*."  
> — FunSearch (Romera-Paredes et al., *Nature* 2024)

写论文这件事正相反：易写难精。这把 skill 的目标，是让写得"对"和写得"好"之间的 gap 缩短一些。
