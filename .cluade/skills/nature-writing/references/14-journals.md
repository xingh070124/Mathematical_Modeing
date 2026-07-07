# 14 · 期刊定位差异

（v4 SKILL Part XIV：Nature / NMI / NC / NCS / NM / Nat Med；总索引见 `../SKILL.md`）

## 17. 期刊定位差异

> 本节是基于 36 篇取样的风格观察 + 投稿策略经验，不是官方指南。字数、图数、article type、data/code policy 必须查官网最新 author guidelines。

### 17.1 Nature

适合：

```text
- field-level breakthrough
- old problem / human-level benchmark / new scientific discovery
- external validation beyond ML metrics
- result changes what domain scientists can do
```

Voice：

```text
- confident
- historically framed
- strong but calibrated
```

Corpus anchors：

AlphaFold:
> "more than 50 years"

FunSearch:
> "first discoveries made for established open problems using LLMs"

RFdiffusion:
> "surpass what natural evolution has achieved"

不要投 Nature 如果只是：
```text
+2% on benchmark with standard transformer
```

**v5 update**：2025–2026 Nature 主刊接收了若干 AI methodology 论文（DeepSeek-R1、DiscoRL、AligNet、Farquhar semantic entropy、ADeLe）。共同特点：field-level claim 配 human / strong-benchmark / open release 三件套——*不是说 Nature 现在喜欢 ML 方法论文，而是 ML 方法论文若想进 Nature 必须证明 field-level 影响 + 公开发布*。

### 17.2 Nature Machine Intelligence

你的主战场。

适合：

```text
- AI / ML conceptual method
- trustworthy AI / interpretability / audit
- LLM-agent with rigorous evaluation
- foundation model with strong benchmark and reproducibility
- AI-for-science where AI contribution本身突出
```

NMI reviewer 看重：

```text
- 方法新意
- evaluation rigor
- reproducibility
- ethics / trust / limitation
- clear relation to AI field
```

Voice：

```text
- precise, audit-aware, mechanism-conscious
- analogy hook 可用
- limitation 显式
```

**v5 update**：NMI 的 evaluation / measurement 论文（Xiao Densing-law, Zhou ADeLe）特别看重 **rubric reliability、validity、SI reproducibility**——比方法论文的 benchmark accuracy 更重要的是"你这把 ruler 真的 ruler 吗"。投这一支时务必把 cross-model / cross-time validation 做足。

### 17.3 Nature Communications

适合：

```text
- 跨学科 AI 应用
- 方法扎实、领域验证充分
- 不一定是 ML paradigm shift
- drug discovery / biology / chemistry / clinical / physics application
```

Voice：

```text
- practical
- method-as-subject
- validation-heavy
```

NC 的好稿件常像：
> "我们用 AI 解决了一个具体科学问题，并把验证链做完。"

**v5 update**：NC 也容纳 narrow but sharp methodological rebuttal（Whitelam Simmering：反驳 optimization-based training），或 brain-inspired agent architecture（Webb MAP）。这一支共同点：**狭窄但锋利**，明确反驳/补充某个 dominant practice，而不是 broadly application-driven。Whitelam 风的 paradigm-rebuttal **不要泛化**——是 NC 给单例反驳留的窗口，不是通用模板。

### 17.4 Nature Computational Science

适合：

```text
- computational science 方法
- PDE / materials / weather / physics / engineering
- AI 是 scientific computation 的一部分
- 与传统 numerical / physical / simulation baseline 比较
```

Voice：

```text
- computation-first
- theory / solver / simulation / validation 清楚
- less AI hype
```

NCS 不适合纯 “new neural network architecture on generic benchmark”。

### 17.5 Nature Methods

适合：

```text
- biology / biomedical method
- tool broadly useful
- strong usability / benchmark / community uptake
```

Voice：

```text
- tool clarity
- method reproducibility
- concise
```

Brief Communication 往往更短，Discussion 可无。Foldseek 3-sentence abstract 是压缩典范。

### 17.6 Nature Medicine / clinical outlets

适合：

```text
- clinical relevance
- robust cohort design
- external validation
- patient-care implication
```

Voice：

```text
- cautious
- statistically explicit
- governance-aware
```

不要用 ML conference 风格去写 clinical AI。

---

