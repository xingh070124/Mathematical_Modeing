# 12 · 子门类剧本

（v4 SKILL Part XI：ML 方法 / Foundation / LLM-agent / Interpretability / Benchmark / AI-for-X / 临床；总索引见 `../SKILL.md`）

## 14. AI / ML 子门类剧本

按你的论文类型选一个主剧本。不要混搭太多。

---

## 14.1 ML 方法论文  
如 ProteinMPNN / RetroExplainer / MolE / DynamicBind / DIMON / HINTS

**主 story shape**：Bottleneck-broken / Two-gap synthesis / Paradigm synthesis。  
**Title**：工具名 + 冒号；或陈述性发现。  
**Abstract**：BIG → GAP → HERE-WE → METHOD-SPEC → KEY-RESULT → IMPLICATION。6 句通常够。  
**Results**：

```text
§1 Architecture / method overview + Fig. 1
§2 Main benchmark + named baselines
§3 Ablation / mechanism
§4 Robustness / generalization
§5 Downstream case / hard case
```

**Methods 必须强**：baselines 公平性、compute、seeds、hyperparameter search。  
**Discussion**：与最相关 prior work 一句对比 + limitation + concrete remedy。

Taste cues：

- ProteinMPNN 用 Rosetta 作 antagonist，速度和 rescue 是 main story。  
- DynamicBind 用 rigid docking vs expensive MD 的 two-gap。  
- HINTS 用 spectral bias vs relaxation stall 的 two-gap。

Avoid：

```text
- 只报 leaderboard，没有解释机制。
- ablation 表很大，但没有回答“为什么有效”。
- baseline 不公平。
```

---

## 14.2 Foundation model 论文  
如 Geneformer / UNI / CONCH / MedSAM / CellFM / Virchow / Cancer-Imaging-FM

**主 story shape**：Scale-emergent / Capability map / Trust-aware foundation。  
**Title**：`A foundation model for <domain>` / `Towards a general-purpose…` / tool-name if品牌足够强。  
**Abstract 必含**：

```text
1. domain need / label scarcity / task diversity
2. scale sentence：data + model + modalities
3. downstream task breadth
4. generalization / data efficiency / zero-shot / few-shot
5. cautious implication
```

**Results 常见子节**：

```text
Architecture / pretraining
Pretraining scaling laws or dataset-size effect
Downstream task 1
Downstream task 2
Few-shot / zero-shot / data efficiency
Embedding analysis / interpretability
External validation / robustness
```

Corpus anchors：

UNI:
> "Pretraining Scaling Laws in CPath"

MedSAM:
> "The effect of training dataset size"

Virchow:
> "Toward clinical-grade performance"

Taste cues：

- `foundation model` 不是因为模型大，而是因为它能 transfer。  
- scaling experiment 不是装饰，是 foundation claim 的证据。  
- `Towards` 往往比 `universal` 更有 taste。

Avoid：

```text
- 前 6 段都在复述 transformer / foundation model 历史。
- 只有一个下游任务却自称 foundation model。
- 没有 external validation / data split 说明。
- 说 democratize 但不放权重 / workflow。
```

---

## 14.3 LLM-agent / AI-for-science  
如 ChemCrow / FunSearch / AlphaGeometry

**主 story shape**：Human-anchored benchmark / Discovery / Evaluator-guided search。  
**Title**：发现领头或 negative definition。  
**Hook**：

- FunSearch:
  > "easy to evaluate…hard to solve"
- AlphaGeometry:
  > "without human demonstrations"
- ChemCrow:
  > "LLMs…struggle with chemistry-related problems"

**Abstract 可较长**，但每句必须有角色：

```text
capability → flaw → here-we → mechanism → result 1 → result 2 → benchmark/human anchor → interpretability/resource/impact
```

**Methods 必含**：prompt、API version、tool schema、decoding、evaluator、retry、safety、human expert evaluation。

**Results**：

```text
System overview
Task / domain case 1
Task / domain case 2
Human / expert / benchmark comparison
Failure and risk mitigation
```

Taste cues：

- LLM-agent 论文最怕像 demo。必须有 hard evaluator。  
- AlphaGeometry 用 25/30 + previous best 10 + IMO gold medallist；这是三重 anchor。  
- FunSearch 说 discovered programs, not raw solutions；这是 method taste。

Avoid：

```text
- 只展示 cherry-picked conversations。
- 不公开 prompts。
- 用 GPT-4 judge GPT-4，不加 expert / rule-based evaluator。
- 不承认 API reproducibility 问题。
```

#### 14.3a RL-for-reasoning / algorithm-discovery 子块（v5 新加）

如 DeepSeek-R1（Nature 2025）/ Oh DiscoRL（Nature 2025）。这一支与 §14.3 邻近但有自己的写作风格：贡献是 **emergent capability** 或 **machine-discovered algorithm**，而非工具链。

- **Title**：常用 capability-emergence 或方法本体命名（"DeepSeek-R1: …" / "Discovering machine-discovered RL"）。
- **Hook**：reasoning bottleneck / human-bottleneck for algorithm design。
- **Pivot 句的强动词**：`incentivizes / unlocks / extracts / discovers / harnesses` 这类（来自 v5 corpus）；区别于 §14.3 的 `streamline / agent`。
- **Methods**：训练范式（RL recipe）+ 采样流 + 评估 protocol；prompt/decoding 仍主要进 SI。
- **Closing**：`led by machines` / `algorithm discovery` 类高强度愿景——但这是高风险 outlook，**只在工作真有跨任务 emergent 证据时用**，否则进 §13 antipatterns 的 over-reach。
- 已有对应 verbatim 在 `extracts/07-ai-methods.md` Paper 4（DeepSeek-R1）+ Paper 5（DiscoRL）。

---

## 14.4 Interpretability / audit / trustworthy AI  
如 SemanticLens / MedPerf / explainable drug discovery

**主 story shape**：Trust bridge / Black-box-to-audit。  
**Title**：`Mechanistic understanding and validation…` / `Federated benchmarking…` / `explainable deep learning`。  
**Hook**：适合 analogy / regulatory / trust gap。

Corpus anchors：

SemanticLens:
> "trust gap"

MedPerf:
> "bringing the model to the data"

Wong:
> "black box in nature and do not provide chemical insights"

**Results**：

```text
Explanation / audit operation taxonomy
Case study 1: search / describe / compare
Case study 2: audit against rule / domain requirement
Spurious correlation / failure analysis
User / institution / deployment evidence
```

Taste cues：

- 不要只说 interpretable。展示解释如何改变 decision / validation。  
- 用 operation names 做章节：Search / Audit / Compare / Describe，可比 “Experiment 1” 有生命。

Avoid：

```text
- saliency map gallery，没有 quantitative audit。
- trust rhetoric 很大，case study 很小。
- 不说明 human input / automation 程度。
```

---

## 14.5 Benchmark 论文  
如 scIB-style / MedPerf-style / evaluation infrastructure

**主 story shape**：Community map / Method choice guide。  
**Title**：`Benchmarking X in Y` / `Federated benchmarking of X with Y`。  
**Abstract 必含**：

```text
methods × tasks × datasets × metrics × scale
```

scIB:
> "68 method and preprocessing combinations on 85 batches…representing >1.2 million cells…"

**Results header** 多用 claim header：

```text
Scaling shifts integration performance toward batch removal
scANVI, Scanorama and scVI perform best…
Scalability and usability
```

**Discussion close**：community service。

scIB:
> "become a reference for method developers…"

Taste cues：

- Benchmark 的 protagonist 不是你的模型，是 field clarity。  
- 每个 Results header 应该告诉读者一个选择建议。  
- Ranking 要透明，metric trade-off 要诚实。

Avoid：

```text
- 只给 aggregate score，不解释 trade-off。
- metric 权重任意。
- 忽视 usability / compute。
- 不公开 pipeline。
```

---

## 14.6 AI-for-X 应用论文  
如 GraphCast / GenCast / Halicin / Wong / GNoME / M3GNet / AlphaMissense

**主 story shape**：Bottleneck-broken / Discovery funnel / Limit-redrawn。  
**Title**：`X enables Y` / `Discovery of…` / method-name if known。  
**Hook**：domain stakes，少讲 AI hype。

Weather:
> "whether to carry an umbrella, how to route an aeroplane…"

Antibiotics:
> "antibiotic resistance crisis"

Materials:
> "clean energy to information processing"

**Abstract**：

```text
domain stakes
domain bottleneck
AI method pivot
numerically dense spec
domain benchmark / verified discovery
implication
```

**Results**：

```text
Model / pipeline
Main domain benchmark
Hard events / case studies
Prospective / experimental validation
Failure modes / limits
```

Taste cues：

- AI 是工具，domain payload 是主角。  
- Discovery paper 要闭环：in silico → in vitro → in vivo / structure / DFT / external deployment。  
- 大规模筛选要 funnel，不要只说 “we screened many candidates”。

Avoid：

```text
- AI 方法细节压过科学发现。
- 没有实验证据却写 discovery。
- 只用 retrospective benchmark。
```

---

## 14.7 Clinical AI / medical imaging  
如 MedSAM / UNI / CONCH / Virchow / Ferber

**主 story shape**：Clinical generalization / Data-efficiency / Trust-aware deployment。  
**Title**：foundation model 或 declarative finding。  
**Abstract**：

```text
clinical task importance
label / modality / generalization gap
model + data scale
internal + external validation
statistics with CI/IQR/P
clinical implication with hedge
```

**Results 必查**：

```text
internal + external cohort
rare / OOD / low-label cases
statistical testing
failure modes
scanner / center / modality diversity
data efficiency
```

Taste cues：

- `clinical-grade` 是高风险词。需要 external validation、strong baseline、统计检验。  
- 不要说 “ready for clinical deployment” 除非真有 prospective deployment。  
- CONCH 式 humility 在 clinical AI 特别有价值。

Avoid：

```text
- 无 CI / P 值。
- patient-level leakage 没交代。
- 只在单中心数据测试。
- conclusion 直接跳到 patient care。
```

---

## 14.8 AI evaluation / measurement methodology（v5 新加）  
如 Xiao Densing-law（NMI 2025）/ Farquhar semantic-entropy（Nature 2024）/ Zhou ADeLe（Nature 2026）

主角不是模型，而是**ruler**——metric、scale、rubric、entropy、capacity density。论文本身在改"我们怎么评价 AI"这件事，不在改模型本身。

**主 story shape**：Trust bridge 的特殊化——把 antagonist 写成 "bad ruler / low predictive power"。

**Title**：measurement / metric / law / scale 命名（"Densing law…", "Detecting hallucinations using semantic entropy", "general scales for AI evaluation"）。

**Hook**：**Measurement / new-ruler hook**——指出现有评估的失效模式，提出新 ruler。

- Xiao: *"capacity density…new metric"*
- Farquhar: *"entropy-based uncertainty estimators"*
- Zhou: *"general scales for AI evaluation"*

**Abstract 数字货币**：不是 data-scale，而是 evaluation breadth + reliability（"15 LLMs and 63 tasks"，"30 combinations"，"every three months"）。详见 `references/03-abstract.md` §3.2.2 carve-out。

**Results 子节**：常用 RQ / analysis-scaffold headers（"RQ1: does the metric explain X?"），见 `references/05-results.md` §5.1 D row。

```text
Reliability of the new ruler
Explanatory / predictive power vs prior metrics
OOD / cross-model / cross-time validation
Measurement-as-tool: forecasting, decision-making
Failure modes of the ruler
```

**Limitation**：高度依赖 §7.2 的 **C. Correctness / target-validity gap** 模式——承认 ruler 自身可能不可靠（systematic deception；human label flaws；agent-like task 证据不足）。

**Closing**：`underpin` / `inspire` / `encourage` 类低强度但基础设施式的动词，区别于 application 论文的 `paves the way`。

Taste cues：

- 标题用 law / scale / unlock 时，**必须**展示跨模型 / 跨时间 / 跨任务的趋势证据，否则进 §13 antipatterns 的 "Law-title without law evidence"。
- Reliability 与 explanatory power 是双轨——必须同时给。
- 自我承认 "ruler 可能错"是诚信信号，不是软弱（参见 §7.2.C）。

Avoid：

```text
- 只在 1–2 个 model family 上验证 metric / law。
- "我们的指标比旧指标更好"但没说在什么意义下更好。
- 把 metric 等同于 ground truth。
```

---

