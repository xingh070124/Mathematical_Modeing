# 03 · Abstract

（v4 SKILL Part II §3；总索引见 `../SKILL.md`）

## 3. Abstract：核心战场，也是节奏最紧的地方

**Patron sentence** — GenCast:  
> "GenCast generates an ensemble of stochastic 15-day global forecasts, at 12-hour steps and 0.25 degree latitude-longitude resolution, for over 80 surface and atmospheric variables, in 8 minutes."

这句好，因为数字密，但不散。每个数字都在扩大读者对任务规模的理解：15-day、12-hour、0.25 degree、80 variables、8 minutes。

### 3.1 默认 5–8 句骨架

```text
[s1 BIG-PICTURE]
<Topic> is critical/central/fundamental for <field>.

[s2 GAP]
However, <existing approaches> are limited by/bottlenecked by/fall short of <X>.

[s3 GAP-2 / optional]
Yet / Meanwhile / By contrast, <another paradigm> <complementary limitation>.

[s4 HERE-WE PIVOT]
Here we [introduce/present/show/report/propose] <NAME>, a <one-line characterization>.

[s5 METHOD-SPEC]
<NAME> <verbs> <quantitative spec: data scale, params, modalities, runtime>.

[s6 KEY-RESULT]
We show that <NAME> <outperforms / achieves / solves / discovers> <baseline> by <Δ> on <benchmark>.

[s7 SECOND-RESULT / VALIDATION / GENERALIZATION]
Furthermore / In addition / Notably, <NAME> <generalization or qualitative novelty>.

[s8 IMPLICATION]
<NAME> <paves the way / opens the door / democratizes / represents an important step toward> <broader vision>.
```

### 3.2 三条强约定

#### 3.2.1 必须有一个 pivot，但不必总是 "Here we"

常见 pivot：

- AlphaFold:  
  > "Here we provide the first computational method that can regularly predict protein structures with atomic accuracy…"
- MedSAM:  
  > "Here we present MedSAM, a foundation model designed for bridging this gap…"
- ChemCrow:  
  > "We introduce ChemCrow, an LLM chemistry agent designed to accomplish tasks…"
- AlphaGeometry:  
  > "We propose AlphaGeometry, a theorem prover for Euclidean plane geometry…"
- SemanticLens:  
  > "This paper introduces SemanticLens, a universal explanation method for neural networks…"

Taste rule: pivot 句只做一件事：**告诉读者你给了什么，以及它为何与 gap 对齐。**  
不要连续两句都在自我介绍。

#### 3.2.2 数字密度峰值通常在 METHOD-SPEC 句（默认；纯 AI 方法可后移）

**默认（AI-for-X / foundation / data-scale 论文）**：好句子的数字不是堆积，而是压缩 task scale。

- GenCast:  
  > "15-day global forecasts, at 12-hour steps and 0.25 degree…for over 80…variables, in 8 minutes."
- UNI:  
  > "more than 100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data)…"
- MedSAM:  
  > "1,570,263 image-mask pairs, covering 10 imaging modalities and over 30 cancer types."
- M3GNet funnel:  
  > "31 million hypothetical crystal structures" → "1.8 million materials" → "1578 were verified…"

**Carve-out：纯 AI 方法 / safety / reasoning / evaluation 论文**——数字货币不是 data-scale delta，而是 **evaluation breadth、progress rate、measurement reliability**。数字峰值常迁到 KEY-RESULT 或 VALIDATION 句。例（来自 `extracts/07-ai-methods.md`）：

- Webb (NC 2025) S6：*"three challenging planning tasks"* — 不是数据规模，是 task 多样性。
- Xiao (NMI 2025) S8：*"doubles approximately every three months"* — progress rate 而非参数量。
- Zhou (Nature 2026) S4–S5：*"18 rubrics", "15 LLMs and 63 tasks"* — evaluation breadth headline。
- Farquhar (Nature 2024)：abstract 无 method-spec 数字，强数字 *"30 combinations"* 留给 Results。
- DeepSeek-R1 (Nature 2025)：abstract 留 conceptual hook（emergent reasoning），强数字 *"15.6% to 71.0% … 86.7%"* 在 Results。

Taste rule：纯 AI 方法 abstract 可只用 conceptual hook，但 Results 必须给可审计数字。**不要用这条 carve-out 来逃避数字**——只是数字位置允许后移。

#### 3.2.3 KEY-RESULT 要有 named anchor

不要写孤零零的百分数。要锚定 baseline / benchmark / human reference。

- GenCast:  
  > "greater skill than ENS on 97.4% of 1320 targets"
- ProteinMPNN:  
  > "sequence recovery of 52.4%, compared to 32.9% for Rosetta"
- Virchow:  
  > "0.95 specimen-level area under the (receiver operating characteristic) curve across nine common and seven rare cancers"
- AlphaGeometry:  
  > "solves 25, outperforming the previous best method that only solves ten problems and approaching the performance of an average International Mathematical Olympiad gold medallist"

### 3.3 Two-gap abstract：AI 方法论文的黄金结构

```text
However, <approach A> <limitation A>.
By contrast / Yet / Meanwhile, <approach B> <limitation B>.
Here we introduce <X>, which <synthesizes / unifies / avoids both>.
```

SyntheMol 是 textbook：

> "Property prediction models, which evaluate molecules one-by-one for a given property, scale poorly to large chemical spaces."  
> "Generative models, which directly design molecules, rapidly explore vast chemical spaces but generate molecules that are challenging to synthesize."  
> "Here, we introduce SyntheMol, a generative model that designs easily synthesizable compounds from a chemical space of 30 billion molecules."

HINTS 是更 technical 的版本：

> "Neural networks suffer from spectral bias…"  
> "relaxation methods can resolve high frequencies efficiently but stall…"  
> "We exploit the weaknesses of the two approaches by combining them synergistically…"

CONCH / Ferber 用 status-quo gap + opportunity gap：

- CONCH: image-only pathology models vs human language reasoning。  
- Ferber: task-specific training expensive；in-context learning underexplored in medical images。

Taste rule: two-gap 结构只有在两条 prior route 真有互补 failure 时才用。不要机械制造两个 gap。

### 3.4 何时故意打破 5–8 句 skeleton

| 破格方式 | 代表 | 为什么成立 |
|---|---|---|
| **长 abstract** | FunSearch 10 句 | 多个 discovery + mechanism contrast + interpretability property，每句有独立功能 |
| **HERE-WE 提前** | GenCast s2 就 pivot | probabilistic weather forecasting 的 stakes 很清楚，先给 model，再用 "Unlike traditional approaches" 补 gap |
| **没有 "Here we"** | SemanticLens: "This paper introduces…" | NMI interpretability paper偏正式、tool-like；analogy 已完成 hook |
| **negative-definition title + abstract** | AlphaGeometry | 数据稀缺是核心 antagonist，"without human demonstrations" 必须提前 |
| **abstract 无强数字** | HINTS / DIMON / SemanticLens | mechanism / theory / audit capability 比单个 benchmark 更重要 |
| **conceptual / measurement abstract** | Whitelam（无数字 paradigm rebuttal）/ Xiao（rate-law）/ Zhou（rubrics + tasks 而非数据规模） | 贡献是新标尺 / 新机制 / 新视角时，数字让位 |

破格条件：

```text
1. 破格是否让主故事更清楚？
2. 每个额外句子是否推进一个新角色？
3. 是否还能在 15 秒内让 editor 复述你的 contribution？
4. 破格是否来自内容需要，而不是作者不会压缩？
```

### 3.5 Abstract 里慎做的事

- 不要把 architecture 细节写到第二级；只保留机制名和关键特性。
- 不要重复空心化 "novel"。
- 不要把 limitation 写成 abstract 主体，除非临床 / 安全语境必须限定适用边界。
- Hedge 集中在 outlook：`holds potential`, `paves the way`, `could enable`。Results claim 用强动词。
- 高风险应用不能完全无 hedge；临床 AI 论文要显得谨慎而不是胆怯。

### 3.6 Abstract before / after

**Pair 5 — 背景泛泛 → 具体 stakes**

Bad template:
> "Weather forecasting is important for many applications."

Better, GenCast:
> "Weather forecasts are fundamentally uncertain, so predicting the range of probable weather scenarios is crucial for important decisions, from warning the public about hazardous weather, to planning renewable energy use."

What changed: “important” 被替换成一条机制化 stakes：uncertainty → probable scenarios → decisions。读者知道为什么 ensemble matters。

**Pair 6 — 方法自述 → bottleneck 对齐**

Bad template:
> "We developed a deep learning model for protein structures."

Better, AlphaFold:
> "Here we provide the first computational method that can regularly predict protein structures with atomic accuracy even in cases in which no similar structure is known."

What changed: 句子不只是 introduce method；它把 claim、frequency、accuracy、hard case 都放进 pivot。

**Pair 7 — 数字堆叠 → 数字有方向**

Bad template:
> "Our model uses 100 million images, 100,000 slides, 77 TB data, and 20 tissue types."

Better, UNI:
> "pretrained using more than 100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data) across 20 major tissue types."

What changed: 数字被组织成一个 noun phrase：images → slides → data size → tissue breadth。读起来像 scale 论证，不像表格。

**Pair 8 — 泛化自夸 → named benchmark anchor**

Bad template:
> "Our method significantly outperforms previous methods."

Better, AlphaGeometry:
> "AlphaGeometry solves 25, outperforming the previous best method that only solves ten problems and approaching the performance of an average International Mathematical Olympiad gold medallist."

What changed: 数字 + prior best + human anchor 三重锚定。审稿人很难说“so what”。

**Pair 9 — Outlook 过虚 → 具体 community value**

Bad template:
> "This work has broad applications and will benefit the community."

Better, Pai et al.:
> "We share our foundation model and reproducible workflows so that more studies can investigate our methods, determine their generalizability and incorporate them into their research studies."

What changed: 没说“broad”。说 share what、for whom、to do what。

---

