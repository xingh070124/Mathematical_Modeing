# 04 · Introduction

（v4 SKILL Part III；总索引见 `../SKILL.md`）

## 4. Introduction：漏斗不是礼貌，是控制读者注意力

**Patron sentence** — SemanticLens:  
> "Unlike human-engineered systems such as aeroplanes, where each component's role and dependencies are well understood, the inner workings of AI models remain largely opaque…"

这句好，因为它不用 “AI interpretability is important”。它先给一个读者熟悉的 engineered system，再让 neural network 显得危险地不透明。

### 4.1 典型 4–6 段漏斗

```text
¶1  HOOK
    领域重要性 / 老问题 / 社会危机 / 工程类比 / 日常决策

¶2  RECENT ADVANCES
    最近的技术进展；按子主题分组，不要 citation pile

¶3  GAP
    However / Yet / Despite this progress, …
    说明为什么现有方法不够

¶4  PIVOT
    Here we / We introduce / We propose <NAME>, a <category> that <does X by Y>.

¶5  ROADMAP / RESULT PREVIEW
    Specifically, we show that …, that …, and that …
```

Foundation model / benchmark 论文常把 ¶5 写成 mini-abstract。  
纯方法 / theory 论文可以更短，pivot 后直接进 Results。

### 4.2 Hook 的七种风格

| Hook 类型 | 何时用 | Verbatim anchor | Taste 判断 |
|---|---|---|---|
| **领域重要性** | 安全牌，通用 | AlphaFold: "Proteins are essential to life…"；CONCH: "The gold standard for diagnosis…" | 不要写成百科全书开头 |
| **社会 / 医学危机** | 抗生素、临床、气候 | Wong: "The ongoing antibiotic resistance crisis threatens…"；SyntheMol: "The global dissemination of antibiotic resistance determinants…" | 危机句要具体，不要喊口号 |
| **几十年老问题** | theorem proving、protein folding、PDE | AlphaFold: "more than 50 years"；Wong discussion: "38-year interval…" | 历史 anchor 让贡献有时间尺度 |
| **跨工程类比** | interpretability / agent / trust | SemanticLens aeroplane sentence | 类比必须解释 gap，不是装饰 |
| **日常决策具象化** | weather / deployment | GenCast: "whether to carry an umbrella, how to route an aeroplane…" | 从 umbrella 到 power grid，尺度自然放大 |
| **Technical paradox** | AI-for-science / math | FunSearch: "easy to evaluate…hard to solve" | 好 paradox 会直接生成方法设计；**paradigm-rebuttal 变种**（Whitelam: "optimization-based training is misguided"）属高风险单例，只在反驳 dominant paradigm 真有跨场景证据时用 |
| **Measurement / new-ruler hook**（v5 新加，AI 测量学）| AI evaluation / uncertainty / scaling-law 论文 | Xiao: "capacity density…new metric"；Farquhar: "entropy-based uncertainty estimators"；Zhou: "general scales for AI evaluation" | 贡献是新标尺，不是新工具。**必须**展示 predictive / explanatory / cross-model trend 证据，否则进 §13 "Law-title without law evidence" |

### 4.3 不要这样开头

```text
Recently, deep learning has achieved great success in …
With the rapid development of artificial intelligence …
In recent years, large language models have attracted increasing attention …
```

这些句子的问题不是老，而是没有 antagonist。  
它们既没有 stakes，也没有 gap，更没有 story。

### 4.4 GAP signaling 词库

启动：

```text
However,
Yet,
Despite this progress,
Nevertheless,
By contrast,
Despite these advances,
```

限制：

```text
is bottlenecked by
falls far short of
is limited by
remains constrained by
lacks generality
is computationally expensive
scales poorly to <large space>
remains underexplored
has not been extensively developed and evaluated
cannot directly use <data source>
typically treat <X> as rigid
is hard to explain, like a 'black box'
```

知识空白：

```text
of unknown clinical significance
has yet to be described
no general method exists
remains an open problem
severe scarcity of training data
```

AI-specific：

```text
requires expensive task-specific labels
does not generalize across <distribution shift>
lacks reproducibility
closed-source models provide limited control
requires application-specific reinforcement, transfer, or few-shot learning
```

### 4.5 Pivot 段落模板

```text
Here we [introduce/present/develop/report/propose] <NAME>, a <category> that <does X by Y>.
<NAME> [unifies / addresses / circumvents / overcomes] <gap> by <one-sentence mechanism>.
We [demonstrate/show/apply/evaluate] <NAME> on <task list>, where it <key result with anchor>.
```

Geneformer 的 pivot 是 foundation model 论文的标准示范：

> "Here, we developed a context-aware, attention-based deep learning model, Geneformer, pretrained on a large-scale corpus of ~30 million single cell transcriptomes…"

DynamicBind 的 pivot 是 two-step unification：

> "Unlike traditional docking methods that treat proteins as mostly rigid entities, DynamicBind efficiently adjusts the protein conformation…"

MedPerf 的 pivot 是 platform + two pillars：

> "MedPerf is an open benchmarking platform that combines: (1) a lower-risk approach…; with (2) the appropriate infrastructure…"

### 4.6 Intro 末段的两种 taste

#### A. Results preview 型

适合 foundation model、benchmark、多任务论文。

scIB 在 intro 最后直接告诉读者 ranking：

> "If cell annotations are available, scGen and scANVI outperform most other methods across tasks…"

Halicin 把三阶段写出来：

> "Our approach consists of three stages. First… Second… lastly…"

这种写法的好处是：读者进 Results 前已经拿到地图。

#### B. Tight pivot 型

适合机制强、故事单线清晰的论文。

Tangram 的 intro 短到几乎只剩 pivot：

> "Here, we present Tangram, a deep-learning framework to address two challenges…"

这种写法的好处是：不拖。缺点是：如果 Results 多轴，读者可能迷路。

### 4.7 Intro before / after

**Pair 10 — 空泛 field hype → 具体 bottleneck**

Bad template:
> "Recently, AI has transformed chemistry and drug discovery."

Better, SyntheMol:
> "Property prediction models…scale poorly to large chemical spaces."  
> "Generative models…generate molecules that are challenging to synthesize."

What changed: “AI transformed X” 没有张力；两条 failure 直接逼出 SyntheMol。

**Pair 11 — 老问题没有时间尺度 → 历史 anchor**

Bad template:
> "Protein structure prediction is a challenging problem."

Better, AlphaFold:
> "Predicting the three-dimensional structure that a protein will adopt…has been an important open research problem for more than 50 years."

What changed: challenging 是形容词；50 years 是证据。数字让句子落地。

**Pair 12 — interpretability 陈词滥调 → 工程类比**

Bad template:
> "Neural networks are black boxes and hard to interpret."

Better, SemanticLens:
> "Unlike human-engineered systems such as aeroplanes… the inner workings of AI models remain largely opaque…"

What changed: aeroplane 让 “component-level understanding” 变成自然需求。类比承担了论证功能。

**Pair 13 — method dump → design argument**

Bad template:
> "We fine-tune SAM on medical datasets to segment images."

Better, MedSAM:
> "Considering these challenges, we argue that a more practical approach is to develop a promptable 2D segmentation model."

What changed: 作者先说 design decision，而不是直接汇报工程行为。读者看到的是判断力。

---

