---
name: nature-writing
description: 面向中国 AI / ML 研究者，主投 Nature Machine Intelligence、次投 Nature Communications / Nature Computational Science、必要时冲刺 Nature 的论文写作技能（craft + taste + story-craft）。v5 在 v4 拆分版上吸收了 8 篇 2024–2026 NMI/NC/Nature 纯 AI 方法论文（DeepSeek-R1、Densing law、AligNet、ADeLe、Webb-MAP、DiscoRL、Farquhar semantic-entropy、Whitelam Simmering），新增 measurement / new-ruler hook、correctness-gap limitation、pure-AI 数字密度 carve-out、SI black hole 反模式、AI evaluation/measurement 子门类剧本等。本 SKILL.md 为瘦索引：骨架公式、写作顺序、按任务加载的 routing table、提交前 checklist、屏幕边 quick card、附录。详细章节按需 Read `references/01-story.md` … `references/15-taste-development.md`。视觉/figure 设计见姊妹 skill `FIGURE-SKILL.md`。所有 verbatim 引文可回查 `extracts/01-singlecell.md` … `extracts/07-ai-methods.md` 7 个文件 / 共 44 篇论文。
---

# Nature 系 AI / ML 论文写作技巧 v4（拆分版）
## Craft, Taste, and Story-Craft for NMI / NC / NCS / Nature

> **资料来源**：7 类领域共 44 篇开放获取论文的逐句抽取在 `extracts/01-singlecell.md` … `07-ai-methods.md`；抽取框架见 `_framework.md`（v5：补 8 篇 2024–2026 NMI/NC/Nature 纯 AI 方法论文）。  
> **读者**：中文母语或中文工作语境中的 AI / ML 研究者。主投 **Nature Machine Intelligence**；次投 **Nature Communications** 与 **Nature Computational Science**；少数旗舰工作冲 **Nature**。  
> **目标**：不只是“能过审”，而是让审稿人读完后说：*well-written, clearly motivated, compelling, careful, and hard to put down.*  
> **约定**：  
> - 英文引号里的句子是 corpus verbatim，除非标注为“模板 / 构造 / 改写”。  
> - `<X>` 是占位符。  
> - `[…]` 是删节；`…` 是原文或节选中的省略。  
> - 本文档把规律分为三档：  
>   - **常见模式**：44 篇里多数遵循，可作为默认。  
>   - **子门类倾向**：只在 foundation model / benchmark / AI-for-X / clinical AI 等特定类型里成立。  
>   - **强约定**：罕有例外，违反通常会显得生硬或不可信。  
> - 不使用“铁律 / 必须 / 绝不”。好论文知道规矩，也知道何时破规矩。
> **本文档为瘦索引**：保留全篇都需要看到的部分（骨架公式、写作顺序、提交前 checklist、Quick card、附录），其余按主题拆到 `references/01-story.md` … `references/15-taste-development.md`。详细加载规则见 §1。



---

## 0. 先记住这句话：论文不是实验清单，是阅读体验

**Patron sentence** — FunSearch:  
> "Many problems in mathematical sciences are 'easy to evaluate,' despite being typically 'hard to solve.'"

这句话好，因为它不是“我们提出一个方法”。它把整篇论文的戏剧张力先说出来：有一类问题，答案很难找，但好坏很容易判。于是 FunSearch 的 LLM + evaluator 设计变成必然，而不是作者硬塞给读者的系统图。

v3 教你 craft：title 怎么写，abstract 怎么排，Results 怎么开句，Methods 报什么。  
v4 还要教 taste：**哪个结果该当 Fig. 1，哪个该进 Supplementary，哪句话该收住，哪句话该响一点，哪种故事配得上 “paves the way”。**

### 0.1 一篇 Nature 系 AI 论文的默认骨架

多数论文仍遵循这一条骨架：

```text
TITLE
  ← 4–6 种定式之一：工具名 / 工具名+冒号 / X enables Y / Towards a… / Discovery of…

ABSTRACT
  s1  BIG-PICTURE / 重要性
  s2  GAP
  [s3 GAP-2 / contrast / opportunity]
  s4  HERE-WE pivot：Here we / We introduce / We propose / We report / This paper introduces
  s5  METHOD-SPEC：数字最密的一句（默认；纯 AI 方法 / safety / evaluation 论文可把数字峰值后移到 KEY-RESULT 或 VALIDATION——见 `references/03-abstract.md` §3.2.2 carve-out）
  s6  KEY-RESULT：一个强数字 + 命名 baseline / benchmark / human anchor
  [s7 VALIDATION / GENERALIZATION / 第二轴结果]
  s8  IMPLICATION：paves the way / opens the door / democratizes / represents a step

INTRODUCTION
  宽 hook → recent advances → gap → pivot → results preview

RESULTS
  4–10 个子节：每节一个 claim / task / capability；Fig. 1 建立阅读地图

METHODS
  复现细节、数据切分、baseline、公平性、compute、statistics、code/model/data availability

DISCUSSION
  重述贡献 → 与 prior work 比较 → limitation → outlook / community / deployment
```

### 0.2 v4 的核心判断

Craft 问：  
> “Nature 系论文通常怎么写？”

Taste 问：  
> “这篇论文的最强阅读路线是什么？”

Craft 给你模板。Taste 决定你何时不用模板。  
AlphaGeometry 的标题 **"Solving olympiad geometry without human demonstrations"** 没有工具名、没有冒号、没有 `X enables Y`，但它把贡献的张力放在标题里：不是“solving geometry”，而是 **without human demonstrations**。  
FunSearch 的 abstract 有 10 句，明显超过 5–8 句默认骨架，但每一句都推进：capability → hallucination flaw → here-we → result 1 → result 2 → mechanism contrast → interpretability value。  
SemanticLens 用 aeroplane analogy 开篇：  
> "Unlike human-engineered systems such as aeroplanes, where each component's role and dependencies are well understood, the inner workings of AI models remain largely opaque…"

这些都不是破坏规矩。它们是在更高层面服从故事。

### 0.3 写作顺序不要反过来

不要先把所有实验按时间顺序贴进 Results，再想标题。正确顺序是：

```text
1. 选 story shape：这篇论文到底是什么故事？
2. 选 climax：哪个结果是读者必须记住的？
3. 选 Fig. 1：读者第一眼看到的是 bottleneck、machine、funnel、scaling law，还是 human benchmark？
4. 删弱枝：不能服务主故事的实验，进 Supplementary 或删掉。
5. 再写 abstract / intro / results。
6. 最后逐句打磨 rhythm、verb、restraint、overclaim boundary。
```

---

## 1. Routing — 按任务加载

写作不是线性的；读 SKILL 也不该线性。每个写作阶段或具体困境，按下面表格只 Read 1–2 个 reference 文件。

### 1.1 按写作阶段加载

| 阶段 / 困境 | 主 load | 辅 load |
|---|---|---|
| 构思 / 还在选 story shape，未决定 climax | `references/01-story.md` | `references/12-subgenres.md`, `references/14-journals.md` |
| 选 venue / 不知道投哪个刊 | `references/14-journals.md` | `references/12-subgenres.md` |
| 写标题 | `references/02-title.md` | — |
| 写 abstract | `references/03-abstract.md` | `references/11-language-bank.md` |
| 写 introduction | `references/04-intro.md` | `references/11-language-bank.md` |
| 写 Results 子节 / figure call-out / 数字+统计 | `references/05-results.md` | `FIGURE-SKILL.md`（视觉端） |
| 写 Methods / 复现性 / LLM-agent prompt 报告 | `references/06-methods.md` | — |
| 写 Discussion / limitation / outlook | `references/07-discussion.md` | `references/08-sentence-taste.md`（outlook 动词等级） |
| 一句话卡了：节奏 / 经济 / restraint / overclaim 边界 | `references/08-sentence-taste.md` | `references/11-language-bank.md` |
| 自审稿 / 模拟 reviewer | `references/09-reviewer-protocol.md` | `references/13-antipatterns.md` |
| 文风像 arXiv 不像 Nature / 不知子刊 voice 差异 | `references/10-voice.md` | `references/14-journals.md` |
| 词不准 / 强动词 / hedge / 段间连接 | `references/11-language-bank.md` | — |
| 写 ML 方法 / Foundation / LLM-agent / Interpretability / Benchmark / AI-for-X 任一具体子门类 | `references/12-subgenres.md` | `references/01-story.md` |
| 自查反模式 | `references/13-antipatterns.md` | — |
| 长期 taste 培养 / 读法 / 临摹 | `references/15-taste-development.md` | — |
| 提交前总扫 | 本文 §2 checklist + `references/13-antipatterns.md` | `references/09-reviewer-protocol.md` |

### 1.2 References 目录（主题索引）

| 文件 | 主题 | 大致行数 |
|---|---|---|
| `references/01-story.md` | Story Architecture：7 种 canonical shapes、Fig. 1 四种功能、climax 选择、降级与删枝 | 130 |
| `references/02-title.md` | Title 6 种定式、关于 "novel" 的真相、Title before/after | 90 |
| `references/03-abstract.md` | 5–8 句句式图、三条强约定、Two-gap、何时打破默认、Abstract before/after | 195 |
| `references/04-intro.md` | 漏斗 4–6 段、6 种 hook、GAP 词库、pivot 模板、末段 taste、Intro before/after | 200 |
| `references/05-results.md` | 标题三风格、开句三模板、figure call-out、caption、统计写法、baseline、ablation、discovery funnel、综合句、Results before/after | 340 |
| `references/06-methods.md` | Methods 子目、LLM-agent 专用清单、复现三处呼应、常漏报项、Methods 也要有 taste | 140 |
| `references/07-discussion.md` | Discussion 开句两条路径、Limitation、Outlook 动词等级表、Overclaim 边界、Closing、Discussion before/after | 185 |
| `references/08-sentence-taste.md` | 10 句 memorable sentences 解剖、rhythm、经济、name-your-noun、negative space | 370 |
| `references/09-reviewer-protocol.md` | 5-pass harsh referee protocol、SNEER/NOD/ASK/CUT、每段末尾 invisible answer | 150 |
| `references/10-voice.md` | DeepMind / NMI / NC / NCS / 临床 5 种 voice、confident vs arrogant、modest vs timid | 160 |
| `references/11-language-bank.md` | 强动词 / hedge / 6 类段间连接词 / 高复用句型 | 75 |
| `references/12-subgenres.md` | 7 个子门类剧本：ML 方法 / Foundation / LLM-agent / Interpretability / Benchmark / AI-for-X / 临床 | 335 |
| `references/13-antipatterns.md` | craft + AI-specific + taste 三类反模式 | 90 |
| `references/14-journals.md` | Nature / NMI / NC / NCS / NM / Nat Med 各自 voice 与策略 | 160 |
| `references/15-taste-development.md` | 读法 / rewrite-by-hand / taste notebook / mentor / OpenReview review / 返回旧草稿 | 80 |

### 1.3 与 FIGURE-SKILL.md 的衔接

视觉设计是另一回事，由独立的 `FIGURE-SKILL.md`（v0.2）覆盖：Fig. 1 schematic 6 种构图、配色（Wong/Okabe-Ito 8 色板）、字体字号（**panel letter 8pt bold lowercase + 其他 5–7pt**，已按 Nature Research Figure Guide 核实）、panel 布局、数据图选型、统计在图内的呈现、matplotlib/ggplot template、Illustrator 拼版流程、arXiv→Nature 反模式 19 条、文件格式与大小（≤50MB / RGB / Type 42 / lowercase a/b/c）。写 Results 与做图常需同时打开两本 skill。

### 1.4 与 extracts/ 的关系

所有 verbatim 引文（如 AlphaFold "Here we provide the first computational method…"，FunSearch "easy to evaluate, hard to solve"）都可在 `extracts/01-singlecell.md` … `extracts/07-ai-methods.md` 7 个文件 / 共 44 篇里通过 grep 查到上下文。当 SKILL 或某 reference 引用一句话且你想看出处全文时，到对应 extract 文件搜即可。

---

## 2. 提交前 checklist

提交前一次性扫一遍。条目按章节分组——任何一项落空，先回到对应 reference 修。

### 2.1 Story

```text
[ ] 我能用一句话说出 story shape。
[ ] antagonist 明确：bottleneck / data scarcity / black box / scale / compute / human bottleneck / synthetic constraint。
[ ] Fig. 1 服务主 story，而不是零件堆。
[ ] 每个主文实验支撑 abstract claim、处理强质疑、或推进 climax。
[ ] 至少有一个实验被降到 Supplementary 或删掉。
[ ] Results 顺序不是实验时间顺序，而是阅读顺序。
```

### 2.2 Title

```text
[ ] 标题属于 A–F 定式之一。
[ ] 没有空心化 "A novel method for…"。
[ ] 如果用 "foundation model"，下游任务 / transfer / scale 足够支撑。
[ ] 如果用 "without / first / universal / clinical-grade"，证据足够支撑。
[ ] 标题能让 editor 在 5 秒内知道冲突和贡献。
```

### 2.3 Abstract

```text
[ ] 5–8 句为默认；若更长，每句有独立功能。
[ ] 有一个明确 pivot。
[ ] METHOD-SPEC 句数字密度最高（默认）；或已有意采用 pure-AI-methodology carve-out（数字在 KEY-RESULT / VALIDATION）。
[ ] KEY-RESULT 有 named baseline / benchmark / human anchor。
[ ] Outlook 动词与证据强度匹配。
[ ] 中段用强动词；末段适度 hedge。
[ ] 没有把 architecture details 写成 mini Methods。
```

### 2.4 Introduction

```text
[ ] Hook 不是 "Recently, deep learning…"。
[ ] 第一段有 stakes / old problem / analogy / paradox。
[ ] GAP 说明 limited by what。
[ ] Pivot 段落明显。
[ ] Intro 末段给 roadmap 或 tight pivot。
[ ] 每个 major claim 有适量 citation，不是 citation pile。
```

### 2.5 Results and figures

```text
[ ] Results header 风格统一。
[ ] 每个子节开句让读者知道：为什么做 / 做了什么 / 得到什么。
[ ] Fig. call-out 把发现放主语位置。
[ ] Main benchmark 有 named baseline。
[ ] 主要比较有 uncertainty：CI / IQR / std / P / bootstrap / repeated splits。
[ ] 至少有 robustness / ablation / control 处理 alternative explanation。
[ ] Discovery paper 有 funnel。
[ ] Foundation model paper 有 scaling / data-size / transfer 证据。
[ ] Clinical paper 有 external validation 或明确说明没有。
[ ] Caption 可独立复述 figure。
```

### 2.6 Methods and reproducibility

```text
[ ] 数据来源、版本、split 原则清楚。
[ ] leakage 检查说明。
[ ] training compute 报告。
[ ] random seeds 或替代 uncertainty 报告。
[ ] baseline 训练公平性说明。
[ ] hyperparameter search budget 说明。
[ ] LLM/API 论文：prompt、version、date、decoding、tool schema 完整放在 SI；主文显式指向 SI（"详见 SI"）。
[ ] Code / data / model availability 独立段。
[ ] License / DOI / access restriction 说明。
```

### 2.7 Discussion

```text
[ ] 开句不是 limitation-first，除非有意采用 frank concession。
[ ] 第一段重新框定贡献。
[ ] 与 prior work 比较具体，不泛泛。
[ ] Limitation 具体命名。
[ ] Limitation 后有 boundary / remedy / future direction。
[ ] Outlook phrase 与证据强度匹配。
[ ] Closing 不喊口号。
```

### 2.8 Sentence-level taste

```text
[ ] 每段 read aloud 不拗口。
[ ] 没有 noun phrase 过长。
[ ] 删除多余 adjective。
[ ] 强 verb 替换 nominalization。
[ ] 数字顺序符合读者理解。
[ ] 最强结果没有被 "remarkably/dramatically" 淹没。
[ ] 每段有一个落点。
```

### 2.9 Reviewer modeling

```text
[ ] 写了 top 5 reviewer objections。
[ ] 每个 objection 已在 Results / Methods / Discussion 某处处理。
[ ] 没有 reviewer 会认为 baseline unfair。
[ ] 没有 reviewer 会认为 claim overreaches evidence。
[ ] 没有 reviewer 需要猜测 key implementation detail。
[ ] 如果你的方法依赖 evaluator / 监督目标 / human label / benchmark：评估这把 ruler 本身是否可信。reviewer 可能问 "Is the evaluator / supervision target itself valid?"
```

---

---

## 3. Quick field manual（屏幕边贴条）

### 3.1 Story

```text
This paper is a <story shape> story:
  bottleneck-broken / two-gap synthesis / scale-emergent / discovery funnel /
  human-anchored benchmark / trust bridge / limit-redrawn.

The antagonist is <X>.
The climax is Fig. <Y>.
The sentence readers must remember is:
  "<one sentence>"
```

### 3.2 Abstract

```text
<Topic> is <critical> for <field>.
However, <existing methods> are <limited by X>.
[Yet, <second paradigm> <fails by Y>.]
Here we <introduce/present/propose> <NAME>, a <category> that <mechanism>.
<NAME> <does numerically dense thing>.
We show that <NAME> <outperforms/solves/discovers> <baseline> on <benchmark>.
[Furthermore, <generalization/validation>.]
<NAME> <bounded outlook phrase> <broader vision>.
```

### 3.3 Intro

```text
¶1 Hook: concrete stakes / old problem / analogy / paradox.
¶2 Recent advances: grouped, not piled.
¶3 Gap: limited by what?
¶4 Pivot: Here we <verb> <NAME>.
¶5 Roadmap: Specifically, we show that …
```

### 3.4 Results

```text
§1 Reader map: architecture / pipeline / benchmark design.
§2 Main result with named baseline.
§3 Mechanism / ablation.
§4 Robustness / external validation.
§5 Hard case / discovery / human anchor.
§6 Boundary / failure / generalization.
```

### 3.5 Methods

```text
data + split + leakage
architecture + training + compute
baselines + fairness
statistics + seeds
LLM prompts/API/tool schema if relevant
code/data/model availability
```

### 3.6 Discussion

```text
Opening: restate contribution or reframe field.
Compare: unlike <prior>, <NAME> <specific difference>.
Limit: one named boundary.
Remedy: concrete next step or scope condition.
Close: resource / vision / calibrated outlook.
```

### 3.7 Sentence

```text
Can I replace adjective with number?
Can I replace "this" with named noun?
Can I replace nominalization with verb?
Can I cut the first clause?
Does the sentence land on the strongest word?
```

---

---

# Appendix A — 44-paper corpus

| # | 领域 | 论文 | 刊物 | 取样文件 |
|---|---|---|---|---|
| 1–6 | 单细胞 | Geneformer, SCimilarity, Tangram, scIB, CellOracle, CellFM | Nature × 3, Nat Methods × 2, NC × 1 | `extracts/01-singlecell.md` |
| 7–12 | 蛋白 / 结构 AI | AlphaFold2, ESM-2/ESMFold, ProteinMPNN, RFdiffusion, AlphaMissense, Foldseek | Nature × 2, Science × 3, Nat Biotechnol × 1 | `extracts/02-protein.md` |
| 13–18 | 物理 / 气候 / 材料 | GraphCast, GenCast, DIMON, M3GNet, HINTS, GNoME | Science, Nature × 2, NCS × 2, NMI | `extracts/03-physics.md` |
| 19–24 | 药物发现 | DynamicBind, Wong-MRSA, Halicin, SyntheMol, RetroExplainer, DRAGONFLY | NC × 4, Nature, Cell | `extracts/04-drug.md` |
| 25–30 | 临床 AI | MedSAM, UNI, CONCH, Virchow, MedPerf, Ferber-GPT4V | Nat Med × 3, NC × 2, NMI | `extracts/05-medical.md` |
| 31–36 | ML 通用 / 基础模型 | ChemCrow, AlphaGeometry, MolE, SemanticLens, Cancer-Imaging-FM, FunSearch | NMI × 4, Nature × 2, NC | `extracts/06-ml.md` |
| 37–44 | **纯 AI 方法（v5 新加）** | Webb-MAP, Xiao-Densing-law, Whitelam-Simmering, DeepSeek-R1, Oh-DiscoRL, Farquhar-semantic-entropy, Muttenthaler-AligNet, Zhou-ADeLe | Nature × 5, NMI × 1, NC × 2 | `extracts/07-ai-methods.md` |

---

# Appendix B — Before / After 对照练习索引

每个 pair 给"无 taste 版"和"有 taste 版"对比，附 1 句解释。打磨自己的稿子时，先选一对照之相近的 pair 读。

| # | 章节 | Lesson | 在哪里 |
|---|---|---|---|
| 1 | Title | constraint-as-contribution | `references/02-title.md` §2.3 |
| 2 | Title | discovery before method | `references/02-title.md` §2.3 |
| 3 | Title | hedged aspiration | `references/02-title.md` §2.3 |
| 4 | Title | tool + description | `references/02-title.md` §2.3 |
| 5 | Abstract | concrete stakes | `references/03-abstract.md` §3.6 |
| 6 | Abstract | bottleneck-aligned pivot | `references/03-abstract.md` §3.6 |
| 7 | Abstract | numerical noun phrase | `references/03-abstract.md` §3.6 |
| 8 | Abstract | named benchmark anchor | `references/03-abstract.md` §3.6 |
| 9 | Abstract | community value over hype | `references/03-abstract.md` §3.6 |
| 10 | Intro | two-gap over AI hype | `references/04-intro.md` §4.7 |
| 11 | Intro | historical anchor | `references/04-intro.md` §4.7 |
| 12 | Intro | analogy as argument | `references/04-intro.md` §4.7 |
| 13 | Intro | design argument | `references/04-intro.md` §4.7 |
| 14 | Results | claim as subject | `references/05-results.md` §5.11 |
| 15 | Results | hardware + task-size baseline | `references/05-results.md` §5.11 |
| 16 | Results | control with teeth | `references/05-results.md` §5.11 |
| 17 | Results | mechanism-driven ablation | `references/05-results.md` §5.11 |
| 18 | Results | capability map | `references/05-results.md` §5.11 |
| 19 | Discussion | limitation as boundary | `references/07-discussion.md` §7.6 |
| 20 | Discussion | remedy over vague future work | `references/07-discussion.md` §7.6 |
| 21 | Discussion | resource close | `references/07-discussion.md` §7.6 |
| 22 | Discussion | calibrated modesty | `references/07-discussion.md` §7.6 |

---

# Appendix C — One-page reviewer red-team sheet

打印一张贴桌上。提交前 30 分钟过一遍。

```text
Title:
  What story does it promise?
  Is any word overclaiming?

Abstract:
  s1 stakes:
  s2 gap:
  s3 gap-2:
  s4 pivot:
  s5 method-spec:
  s6 key-result:
  s7 validation:
  s8 outlook:
  Missing anchor?

Intro:
  Hook type:
  True antagonist:
  Straw-man risk:
  Prior work reviewer will cite:

Results:
  Fig. 1 function:
  Climax figure:
  Weakest main-text experiment:
  Experiment to move to supplement:
  Strongest alternative explanation:
  Control addressing it:

Methods:
  Leakage risk:
  Baseline fairness risk:
  Seed / uncertainty:
  Compute:
  Reproducibility artifact:

Discussion:
  Main contribution restated:
  Limitation named:
  Outlook phrase:
  Is it earned?

Sentence-level:
  Loud adjectives to cut:
  Nominalizations to replace:
  Vague nouns to name:
  Long sentence to split:
```
