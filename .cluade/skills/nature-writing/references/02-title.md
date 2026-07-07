# 02 · Title

（v4 SKILL Part II §2；总索引见 `../SKILL.md`）

## 2. Title：标题不是标签，是第一句故事

**Patron title** — AlphaGeometry:  
> "Solving olympiad geometry without human demonstrations"

这个标题的 taste 在 **negative definition**：它不是说“with AlphaGeometry”，而是说“without human demonstrations”。方法约束成了贡献本身。

### 2.1 六种标题定式

| 定式 | 例子 | 何时用 | Taste 判断 |
|---|---|---|---|
| **A. 工具名 / 极简短语** | "Foldseek"；"Segment anything in medical images" | 工具本身能成为品牌；Brief / tool paper | 短标题必须有识别度，否则显得空 |
| **B. 工具名 + 冒号 + 描述** | "DynamicBind: predicting ligand-specific protein-ligand complex structure with a deep equivariant generative model"；"MolE: a foundation model for molecular graphs using disentangled attention"；"GenCast: Diffusion-based ensemble forecasting for medium-range weather" | AI 方法最安全；NMI / NC 常用 | 描述要说机制或对象，不要写 “a novel framework” |
| **C. 陈述性发现** | "Transfer learning enables predictions in network biology"；"In-context learning enables multimodal large language models to classify cancer pathology images"；"Highly accurate protein structure prediction with AlphaFold" | 主结论清楚，结果强 | `X enables Y` 适合 claim 很稳的论文 |
| **D. 抱负式 / hedged aspirational** | "Towards a general-purpose foundation model for computational pathology"；"A foundation model for clinical-grade computational pathology and rare cancers detection" | foundation model 未到 universal，但想占领域名片 | `Towards` 是自知，不是软弱 |
| **E. 发现领头** | "Mathematical discoveries from program search with large language models"；"Discovery of a structural class of antibiotics with explainable deep learning" | 发现比方法更重要 | 先放 discovery，方法作来源 |
| **F. Negative-definition / constraint-as-contribution** | "Solving olympiad geometry without human demonstrations" | 你消除了一个传统必要条件 | 只在 constraint 真正重要时用；否则像噱头 |
| **G. Empirical-law / measurement title**（v5 新加）| "Densing law of LLMs"；"Detecting hallucinations using semantic entropy" | 贡献是新 ruler / 新观测规律 | **必须**有跨模型 / 跨时间 / 跨任务的趋势证据，否则进 §13 "Law-title without law evidence"。Whitelam 风的 paradigm-rebuttal title 仅作 single-case caution，不进定式 |

### 2.2 关于 "novel"

可以用，但要有内容。

允许：
- SyntheMol: "structurally novel antibiotics" —— novel 描述化合物属性。
- GNoME: "Novel functional materials" —— novel 是材料发现语境中的对象属性。
- AlphaFold: "novel machine learning approach" ——在方法上下文中承载差异。

反模式：
```text
A novel method for <task>
A novel deep learning framework for <domain>
```

这里的 novel 没有信息量。改成具体贡献：

```text
<Method> enables <capability>
<Method>: <mechanism> for <task>
<Discovery> from <method>
Solving <problem> without <traditional requirement>
```

### 2.3 Title before / after

**Pair 1 — 空心 novelty → 约束成贡献**

Bad template:
> "A novel theorem prover for olympiad geometry"

Better, AlphaGeometry:
> "Solving olympiad geometry without human demonstrations"

What changed: “novel theorem prover” 是标签；“without human demonstrations” 是故事冲突。读者马上知道这不是又一个 prover，而是绕开了数据瓶颈。

**Pair 2 — 方法名堆料 → 发现领头**

Bad template:
> "A graph neural network model for antibiotic discovery"

Better, Wong:
> "Discovery of a structural class of antibiotics with explainable deep learning"

What changed: 先说 discovery，再说方法。Nature 旗舰读者关心的是新 structural class，不是你用了 GNN。

**Pair 3 — foundation model 自夸 → hedged aspiration**

Bad template:
> "A universal pathology foundation model"

Better, UNI:
> "Towards a general-purpose foundation model for computational pathology"

What changed: `Towards` 承认还没 universal。这个克制让后文的 34 tasks、>77 TB data 更可信。

**Pair 4 — 工具名孤立 → 工具名 + 可扫描描述**

Bad template:
> "DynamicBind"

Better, DynamicBind:
> "DynamicBind: predicting ligand-specific protein-ligand complex structure with a deep equivariant generative model"

What changed: 标题直接回答三件事：预测什么、有什么 domain specificity、用什么机制。

---

