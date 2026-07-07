---
name: nature-writing
description: 以 AI / ML 研究者为主要读者，写作 Nature 系（NMI 主，NC / NCS / Nature 次，必要时 Nature Methods / Medicine 跨域参考）顶刊论文的修辞与结构骨架。基于 36 篇开放获取论文的逐句抽取与跨刊归纳，提供可复用的章节模板、动词与连接词词库、子门类剧本、AI-specific 反模式与提交前自检表。所有"verbatim"短语都可在 `extracts/0X-*.md` 回查。
---

# Nature 系论文写作技巧（AI / ML 视角）

> **资料**：6 类领域 × 各 6 篇 OA 论文的逐句抽取在 `extracts/01-singlecell.md` … `06-ml.md`，框架见 `_framework.md`。
> **使用方法**：写到哪一节查哪一节；模板里的尖括号 `<X>` 是要你填的占位符；引文里 `[…]` 是删节、`…` 是省略号。
> **重要约定**：本文档把规律按强度分三级——
>   - **常见模式**（majority pattern）：在 36 篇里多数论文遵循，可作为默认；
>   - **子门类倾向**（subgenre tendency）：只在 foundation-model / benchmark / 应用 等特定子门类里成立；
>   - **强约定**（strong convention）：罕有例外，违反通常是新人写法。
> 不再使用"铁律 / 必须 / 绝不"等绝对化表述——同行评议中的写作没有铁律。

---

## 0. 一篇 Nature 系论文的"骨架公式"

不论领域，多数论文遵循同一条骨架（**常见模式**）：

```
TITLE                               ← 4–5 种定式之一（见 §1）
Abstract                            ← 多数 5–8 句，固定句式图（见 §2）
  s1  BIG-PICTURE / 重要性
  s2  GAP（"However" / "Yet"）
  [s3  GAP-2 — 双缺口 / 反例]
  s4  HERE-WE pivot：「Here we / We introduce / We propose / We report」 + <NAME>
  s5  METHOD-SPEC（数字最密的一句：规模 / 参数 / 模态 / 用时）
  s6  KEY-RESULT（一个抢眼数字 + 锚定 baseline）
  [s7  VALIDATION / 第二个轴向的结果 / generalization]
  s8  IMPLICATION（"paves the way / opens the door / democratizes…"）

Introduction                        ← 漏斗：宽 → 窄 → pivot → 预告结果
Results                             ← 4–10 个子节，每节有标题 + 开句模板（见 §4）
Methods（或合并到 supplementary）   ← AI 论文必须含复现要素（见 §6）
Discussion                          ← 复述核心贡献 → 与既有工作比较 → 局限 → 展望
Data / Code / Model availability    ← 独立段落，AI 论文几乎必备（见 §6）
```

**AI 视角下的关键差异**：
- 物理 / 化学 / 临床论文偏好 Nature 排版的 Results-then-Methods；NMI 与 NC 的方法论文允许 Methods 在前，或把"Architecture"小节合并进 Results 第 1 节。
- AI 论文的可信度有相当一部分由 §6（复现要素 + 公开承诺）撑起，**不要把它当末段附录**。
- 不必所有 8 句 abstract 都有：方法学/理论性强的论文（如 HINTS / DIMON / SemanticLens）常以"机制描述"代替 KEY-RESULT 的纯数字。

---

## 1. 标题（Title）

五种定式（按 36 篇频次 + AI 子集偏好排序）：

| 定式 | 例子 | 何时用 |
|---|---|---|
| **A. 工具名 / 极简短语** | "Foldseek" / "Segment anything in medical images" | 工具本身就是品牌，且名字够新；Brief Communication |
| **B. 工具名 + 冒号 + 描述** | "DynamicBind: predicting ligand-specific protein-ligand complex structure with a deep equivariant generative model" / "MolE: a foundation model for molecular graphs using disentangled attention" / "GenCast: Diffusion-based ensemble forecasting for medium-range weather" | 工具名 + 一句话方法描述。AI 论文最常用的安全牌 |
| **C. 陈述性发现（X enables Y / X improves Y）** | "Transfer learning enables predictions in network biology" / "In-context learning enables multimodal large language models to classify cancer pathology images" / "Highly accurate protein structure prediction with AlphaFold" | 主结论清晰、数字漂亮的方法/应用论文；Nature 旗舰偏好 |
| **D. 抱负式（Towards a … for … / A … for …）** | "Towards a general-purpose foundation model for computational pathology" / "A foundation model for clinical-grade computational pathology and rare cancers detection" | 基础模型论文承认未到完美但要占领领域名片 |
| **E. 发现领头（X discoveries from Y）** | "Mathematical discoveries from program search with large language models" / "Discovery of a structural class of antibiotics with explainable deep learning" | 发现型论文（DeepMind 风 + 生命科学风） |

**关于 "novel" 的真实情况**（codex 已纠正）：
- 标题中**作为有内容的形容词使用 "novel"** 是允许的：SyntheMol "structurally novel antibiotics"（描述化合物属性）、GNoME 摘要 s1 "Novel functional materials"、AlphaFold 摘要 "novel machine learning approach" 都用过。
- 真正的反模式是**空心化的 "A novel method for X"**——novel 在这里没有承担信息量，只是占位形容词。改成具体说"X enables Y"或"a method that <does Y by Z>"。

---

## 2. Abstract（核心战场）

### 2.1 句式图（多数 5–8 句）

下面是"罐头模板"，每句的角色相对固定（**常见模式**）：

```
[s1 BIG-PICTURE]    <Topic> is critical/central/fundamental for <Field>.
[s2 GAP]            However, <existing approaches> are limited by/bottlenecked by/fall short of <X>.
[s3 GAP-2 / 可选]    Yet, <a complementary failure of another paradigm>.
[s4 HERE-WE]        Here we [introduce/present/show/report/propose] <NAME>, <one-line characterization>.
[s5 METHOD-SPEC]    <NAME> <verbs> <quantitative spec: data scale, params, modalities, runtime>.
[s6 KEY-RESULT]     We show that <NAME> <outperforms / achieves> <baseline> by <ΔX% / X.X-fold> on <named benchmark>.
[s7 SECOND-RESULT]  Furthermore / In addition, <NAME> <generalization or qualitative novelty>.
[s8 IMPLICATION]    <NAME> <paves the way / opens the door / democratizes / represents an important step toward> <broader vision>.
```

### 2.2 三条强约定

1. **多数论文有一句明确的 pivot 句**——把方法名、定位、一句机制装进去。词法上有几种活法：
   - "Here we [introduce/present/develop/show/report]"——Nature/DeepMind 旗舰偏好；
   - "We introduce / We present / We propose / We report"——NMI / NC 的 ML 方法论文也常用；
   - "This paper introduces …"——少数；
   - 极少数（如 Pai et al. 的医学影像基础模型）干脆不在 abstract 设 pivot，把 pivot 放在 intro 末段。
   只要存在一处明确的"我做了什么"句，**不要硬塞到必须 'Here we'**。重点是**只用一句**完成 pivot，不要连续两句都在自我介绍。

2. **数字密度峰值通常落在 s5（METHOD-SPEC）那一句**。例：
   - GenCast s5：*"generates an ensemble of stochastic 15-day global forecasts, at 12-hour steps and 0.25 degree latitude-longitude resolution, for over 80 surface and atmospheric variables, in 8 minutes."*
   - UNI s4–s5：*"pretrained using more than 100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data) across 20 major tissue types."*
   - M3GNet（**经构造的漏斗汇总**，不是单句引用；原文是两句相邻）：摘要里先有 *"About 1.8 million materials were identified from a screening of 31 million hypothetical crystal structures …"* 紧跟 *"Of the top 2000 materials with the lowest energies above hull, 1578 were verified to be stable using DFT calculations."*

3. **s6 通常锚定一个有名字的 baseline / dataset / human reference**，不是孤零零的百分数：
   - *"greater skill than ENS on 97.4% of 1320 targets we evaluated"*（GenCast vs ENS）
   - *"sequence recovery of 52.4%, compared to 32.9% for Rosetta"*（ProteinMPNN）
   - *"0.95 specimen-level area under the (receiver operating characteristic) curve across nine common and seven rare cancers"*（Virchow，原文未缩写为 AUROC）
   - *"AlphaGeometry solves 25 [out of 30 IMO problems], outperforming the previous best method that only solves ten problems and approaching the performance of an average International Mathematical Olympiad gold medallist"*（多重锚定：先前 SOTA + 人类标准）

### 2.3 双缺口（two-gap）模板 — 方法-融合型论文最常用

```
However, <prior approach A> <weakness 1>.
[Yet,/Meanwhile/Generative models, by contrast,] <prior approach B> <weakness 2>.
Here we introduce <X>, which <unifies / synthesizes / overcomes both>.
```

实例（SyntheMol）：
> "Property prediction models, which evaluate molecules one-by-one for a given property, scale poorly to large chemical spaces. Generative models, which directly design molecules, rapidly explore vast chemical spaces but generate molecules that are challenging to synthesize. **Here, we introduce SyntheMol, a generative model that designs easily synthesizable compounds from a chemical space of 30 billion molecules.**"

实例（HINTS）：
> "Neural networks suffer from spectral bias having difficulty in representing the high frequency components of a function while relaxation methods can resolve high frequencies efficiently but stall at moderate to low frequencies. We exploit the weaknesses of the two approaches by combining them synergistically …"

这种"两个 prior approach 都不够好，我把它们的优点合起来"的修辞，能让审稿人最快看清贡献。AI 论文里特别常见，因为 ML 方法论文的卖点常是"把别人的两条路线缝在一起"。

### 2.4 Abstract 里慎做的事

- **Hedge 集中在末段（s8）的 outlook 句**（"holds great potential to / paves the way / is expected to"），中间叙述句用直陈实义动词（outperforms / achieves / enables）。**完全零 hedge** 在临床 AI 与高风险应用反而是坏事——overclaim 会被审稿人 / ethics committee 钉。**子门类倾向**：纯 ML 方法论文 hedge 极少，临床 AI 论文 hedge 比例可达 1–2 处。
- **不要把方法细节写到第二级**——只名字 + 一句特性即可，细节进 Methods。
- **重复用 "novel" 是反模式**（参 §1）。
- **不要把 limitation 放进 abstract**。Abstract 是 positioning / claim-selection 区——你只在这里挑要 sell 的几个 claim 摆在最前面，limitation 留 Discussion。注意不是"销售 = 夸大"——临床/高风险 AI 应用的 abstract 反而要避免 overclaim。

---

## 3. Introduction（漏斗 → pivot → 预告）

### 3.1 漏斗结构（典型 4–6 段）

```
¶1  HOOK：领域重要性 / 危机 / 老问题 / 工程类比
¶2  背景：相关方向最近的进展（"Recent advances in X have …"）
¶3  GAP：然而，"However, …" / "Yet, …" — 为什么现有工作不够
¶4  PIVOT：「Here we [verb] X」 + 一句方法概览
¶5  贡献预览或结果路线图（"Specifically, we show that …, that …, and that …"）
```

**子门类倾向**：foundation-model 与 benchmark 论文常把 ¶5 写成"Results 子节的小型 abstract"（pre-announce 每节结论）；纯 ML 方法论文（如 MolE / SemanticLens）经常压缩到 ¶4 一段就直接进 Results。

### 3.2 五种 Hook 风格（按场景选）

| Hook 类型 | 何时用 | 例子 |
|---|---|---|
| **领域重要性** | 安全牌，方法论文通用 | "Single-cell RNA sequencing has revolutionized molecular biology …" / "Pathologic analysis of tissue is essential for the diagnosis and treatment of cancer." |
| **社会/医学危机** | 抗生素发现、临床 AI、气候 | "The global dissemination of antibiotic resistance determinants is one of the most significant challenges of modern medicine."（SyntheMol）/ "Global medium-range weather forecasting is critical to decision-making across many social and economic domains."（GraphCast） |
| **几十年老问题 / 数据稀缺** | 蛋白折叠、theorem proving、PDE、几何 | "Predicting the three-dimensional structure that a protein will adopt … has been an important open research problem for more than 50 years."（AlphaFold）/ "severe scarcity of training data"（AlphaGeometry） |
| **跨工程类比** | 可解释性、agent、新兴方向（NMI 2024–25 特别明显） | "Unlike human-engineered systems such as aeroplanes, where each component's role and dependencies are well understood, the inner workings of AI models remain largely opaque …"（SemanticLens）/ "Many problems in mathematical sciences are 'easy to evaluate,' despite being typically 'hard to solve.'"（FunSearch） |
| **日常决策具象化** | 应用 / 影响导向 | "we rely on accurate weather forecasts to plan ahead — whether to carry an umbrella, how to route an aeroplane, or even how to optimize the use of renewable energy in a power grid."（GenCast） |

**反模式**：
- "Recently, deep learning has achieved great success in …"——被 reviewer 嘲讽十年的开头。
- "With the rapid development of AI / LLMs, …"——同样空洞。
- 直接堆 citations："In recent years [1,2,3,4,5,6,7] …"——把领域脉络拆成第二段。

### 3.3 GAP signaling — 词库

把这些短语贴在桌上：写 GAP 段落时排列组合即可。

- 启动连接：`However, …` / `Yet, …` / `Despite this progress, …` / `Nevertheless, …`
- 限制描述：`is bottlenecked by` / `falls far short of` / `is limited by` / `remains constrained by` / `lacks generality` / `is computationally expensive` / `remains underexplored` / `has not been extensively developed and evaluated` / `existing methods are either A or B` / `is hard to explain, like a 'black box'` / `cannot directly use historical … data` / `treats X as rigid`
- 知识空白：`of unknown clinical significance` / `has yet to be described` / `no general method exists` / `remains an open problem`
- AI-specific：`scales poorly to <large dataset>` / `requires expensive task-specific labels` / `does not generalize across <distribution shift>` / `lacks reproducibility` / `closed-source / not openly accessible`

### 3.4 Pivot 段落 — 模板

```
Here we [introduce/present/develop/report/propose] <NAME>, a <category> that <does X by Y>.
<NAME> [unifies / addresses / circumvents / overcomes] <the limitation in §3.3> by <one-sentence mechanism>.
We [demonstrate/show/apply] <NAME> on <benchmark/task list>, where it <key result with anchor>.
```

实例（Geneformer，**作为模板示范**——你写自己的论文时不能直接搬同一个 NLP-parallel 句子，要换说法）：
> "Here, we developed a context-aware, attention-based deep learning model, Geneformer, pretrained on a large-scale corpus of ~30 million single cell transcriptomes … Fine-tuning towards a diverse panel of downstream tasks … demonstrated that Geneformer consistently boosted predictive accuracy."

### 3.5 Intro 末段：路线图 / 结果目录（**子门类倾向**）

Geneformer / scIB / Halicin 把 Intro 最后一段写成"Results 子节的小型 abstract"——每个子节的结论都预先列一遍。

实例（Halicin）：
> "Our approach consists of three stages. First, we trained a deep neural network model … Second, we applied the resulting model to several discrete chemical libraries … lastly selected a list of candidates based on a pre-specified prediction score threshold, chemical structure, and availability."

实例（scIB）：
> "If cell annotations are available, scGen and scANVI outperform most other methods across tasks, and Harmony and LIGER are effective for scATAC-seq data integration on window and peak feature spaces."

但 **MolE / SemanticLens / DIMON** 的 Intro 末段更紧凑，只一句 pivot——基础模型 / 可解释性 / 理论方法论文允许更短的 Intro。**用哪种取决于你的 Results 是否多轴**。

---

## 4. Results — 顶刊工程化的部分

### 4.1 子节标题：三种风格 + 选择规则

| 风格 | 模板 | 适用 |
|---|---|---|
| **A. 陈述性发现（claim header）** | "X improves Y" / "Tangram maps cells with MERFISH measurements" / "Scaling shifts integration performance toward batch removal" / "Virchow enables pan-cancer detection" / "In-context learning enables multimodal LLMs to classify cancer pathology images" | 单一明确结论的子节；Nature 旗舰、Brief Communications、benchmark 论文偏好 |
| **B. 方法名为主语（method-as-subject）** | "DRAGONFLY enables …" / "DynamicBind achieves …" / "CellFM improves …" / "MedSAM can improve the annotation efficiency" | 工具/品牌驱动；想让方法名成为"故事的主角"；NC 方法论文偏爱 |
| **C. 任务/能力名词短语（task-neutral）** | "Weakly supervised slide classification" / "Generalization across platforms" / "The AlphaFold network" / "Zero-shot classification of diverse tissues" / "Pretraining strategy selection" | 多任务并列；基础模型论文 / 临床 AI / 物理计算（容易被读者扫描） |

**经验**：
- 一篇论文最好**主用一种风格**，混用读起来挤。Geneformer 是个反例（混用），但仍然过审。
- **Benchmark 论文几乎全用 A**。方法论文 B/C 各半。基础模型论文偏 C。
- 不要用问句标题——36 篇里没出现过。

### 4.2 子节开句：三类模板

| 类型 | 模板 | 例 |
|---|---|---|
| **method-first** | "<NAME> <verbs> <description>." | "DynamicBind executes 'dynamic docking', a process that performs prediction of the protein–ligand complex structure while accommodating substantial protein conformational changes." |
| **motivation-first** | "To <test/investigate/rule out/gain insight into> <X>, we <action>." 或 "<Field-fact / context sentence>; we therefore <action>." | "To investigate how the model was learning network dynamics during the pretraining stage, we examined the pretrained Geneformer attention weights." / "A grand challenge in protein design is to scaffold minimal descriptions of enzyme active sites …" |
| **claim-first** | "We find/show that <result>." | "We find that GraphCast has greater weather forecasting skill than HRES …" / "RFdiffusion readily generates diverse unconditional designs up to 600 residues in length that are accurately predicted by AF2, far exceeding …" |

**第一个 Results 子节通常介绍架构 / overview / Fig. 1，多见 method-first**，但**不是规律**。反例：GraphCast 第 1 子节用 claim-first（"We find that GraphCast has greater weather forecasting skill than HRES …"）；MedSAM 第 1 子节用 claim-first（"MedSAM aims to fulfill the role of a foundation model …"）；CellFM 用 motivation-first；ChemCrow 用 scenario-driven 演示开场。**铁规律不存在**——能让读者一眼看到"这一节做什么 / 得到什么"就行。

### 4.3 Figure 引用方式

inline 短引：
- `(Fig. 1a)` / `(Fig. 2a–c and Supplementary Fig. 3c,d)` — 紧贴在被支持的句末。
- `as shown in Fig. 3` / `as illustrated in Fig. 4` / `as depicted in Fig. 1` — 可读性更好，但稍传统。
- 现代旗舰倾向："We found that … (Fig. 1a)" 而不是 "Figure 1a shows that …"——前者把发现放在主语位置。

Figure 标题（caption）：
- **现代 Nature 系趋势是陈述性 caption title**——例 Virchow caption："Virchow embeddings yielded the best cancer detection performance on all cancer types."（**结构示范，不是 verbatim 引用**）
- 老式描述性标题也可："Overview of the AlphaFold model architecture."
- panel-by-panel 内容用 **a, b, c, …** 标注，每个 panel 独立可读。Panel caption 推荐结构：
  ```
  a, <一句声明这个 panel 的发现>。<数据来源 / 队列 / N=…>。<视觉编码：boxplot / heatmap / scatter，center line 含义，error bar 是 SD/SE/CI>。<统计检验类型 + P 值阈值>。
  ```
  目标是审稿人**只看 caption 不看正文**也能复述这个 panel 在说什么。
- **Fig. 1 schematic** 是 AI 论文的高频惯例：左边 input，中间架构 / pipeline，右边 output，箭头连接。它是审稿人最先看的东西，单独打磨。

引用密度（**子门类经验，不是硬规则**）：
- Intro hook 段引用通常 1–3 篇高经典度的论文支撑大主张。
- ¶2"Recent advances …"段引用密度最高（5–15 篇 cluster），按子主题分组。
- ¶3 GAP 段每个 limitation claim 通常带 1–3 篇引用，避免单个短语后挂 5+ 引用。
- Results / Methods 主要引用具体技术 / dataset / baseline 出处，不重复 Intro 引用。

### 4.4 数字 + 统计的写法

**常见格式**：

```
<metric> of <point> [(IQR/CI/SD: …–…)], <ΔX% / X.X-fold> over <named baseline>, [<P < 1e-X>, <test name>, <n=…>]
```

实例：
- *"MedSAM obtained median DSC scores of 87.8% (IQR: 85.0-91.4%) on the nasopharynx cancer segmentation task, demonstrating 52.3%, 15.5%, and 22.7 improvements over SAM, the specialist U-Net, and DeepLabV3+, respectively."*（医学影像，有 IQR；改进数字给的是绝对百分点）
- *"On OT-43 and OT-108, we observe a +4.2% performance increase (P < 0.001, two-sided paired permutation test) in top-1 accuracy when scaling UNI …"*（病理基础模型，明确给出 paired permutation test）
- *"Overall the pan-cancer model achieved an AUC of 0.950 with Virchow embeddings, 0.940 with UNI, 0.932 with Phikon and 0.907 with CTransPath (Fig. 2b); all significantly different with P < 0.0001)."*（多 baseline 横向对比，统一一个 P 值范围）

**子门类差异（注：这是当前审稿人期待的"安全做法"汇总，不是从 36 篇里跑出的统一 Nature 风格）**：
- **临床 / 病理 / 医学影像 AI**：抽样里多数比较带 P 值或 CI（UNI / Virchow / Ferber），审稿人会逐个检查。
- **蛋白结构 / 物理计算 AI**：抽样里更多只给绝对数（AlphaFold 0.96 Å 对比 2.8 Å；ESMFold TM-score 0.72；AlphaGeometry 25/30 vs 10/30；FunSearch 0.03% off lower bound），不带 P 值。当 scaling 是核心卖点时，通常另外加 multiple-seed std 或 paired-comparison（如 ESMFold 报模型 size × CASP14 TM-score 曲线，UNI 报数据规模 × downstream accuracy 曲线）——但这不是该子门类的统一规则。
- **ML 方法论文 / NMI**：现实期待是——要么 multiple-seed mean ± std，要么 P 值/CI，要么 bootstrap，**至少给出一种 uncertainty quantification 或多次重复**。
- **Foundation-model 对比基准**：常用 box plot + paired comparison（"on N tasks, foundation model wins on M"）。

**常见错误**：
- 只写"显著高于" 没具体 P 值；
- 只跑一次 seed 报 SOTA；
- 把"5.86% 提升"和"+5.86 个百分点"混用——前者是相对改进，后者是绝对改进，差别可能很大；
- 选择性报告自己赢的 metric / dataset。

### 4.5 Baseline 比较的措辞

强：
- "compared to X for Y"（"compared to 2.8 Å for the next-best method"）
- "X.X times higher than the best baseline"（"is 1.7 times higher than the best baseline DiffDock"）
- "two orders of magnitude improvement over"
- "outperforming the previous best method that only solves ten"
- "first computational method that can …"
- "matches or exceeds the performance of <named baseline> while requiring only <fraction> of the compute"

弱（避免）：
- "performs better than other methods" — 没数字、没名字
- "achieves competitive performance" — 这是承认你输了
- "comparable to state-of-the-art" — 没具体哪个 SOTA、没 delta

### 4.6 Robustness / Ablation 的"过场词"

写每一个 robustness / control / 跨数据集验证段落时，从下面挑一个开头：

- `We next tested whether …`
- `We next asked …`
- `To rule out <alternative explanation>, we …`
- `As a control, we …` / `As a negative control, …`
- `We hypothesized that …`（后接 `Supporting this hypothesis, …`）
- `To verify that <result> was not an artifact of <X>, we …`
- `To further investigate …` / `To further assess …`
- `To make a fair comparison, we adopted <protocol> …`
- AI-specific：`To probe the contribution of <component>, we ablated …` / `We trained the same architecture without <X> on the same data and find …`

实例（SyntheMol）：
> "**As a control**, we tested 58 randomly selected molecules from the Enamine REAL Space. None of these compounds displayed antibacterial activity against A. baumannii ATCC 17978 …"

实例（Tangram）：
> "**To verify that** these distributions were not an artifact of our probabilistic approach, …"

### 4.7 漏斗修辞 — 发现型 / 大规模筛选论文专用

screening 数 → filter 数 → tested 数 → verified 数，每一级都写明数字。

- M3GNet（材料发现）：31M hypothetical → 1.8M potentially stable → top 2000 → **1578 DFT-verified**
- Wong (Nature 2024 antibiotics)：12,076,365 compounds → 3,646 passing filters (0.03%) → 283 empirically tested → **4 of 9 (44%)** active → **1 structural class** in MRSA mouse model
- Halicin：107,349,233 ZINC15 → 23 tested → **8 active**
- SyntheMol：30B chemical space → 24,335 generated → 70 selected → 58 synthesized → **6 hits**

**AI 类比版本**——你在做大规模 candidate / proposal / hypothesis 生成 + 验证时也可用：
- LLM 生成 K 个候选 → 自动评估筛掉 K' 个 → 人类专家评审 K'' 个 → 实测验证 m 个有效。
- Embedding 检索 M 项 → 重排 M' → 人工/下游测试 M'' → 命中 m 项。

模板：
> "Of <large N>, we <filter> to <medium N>; we <test> <small N> empirically and find <hit count> active, of which <X> showed <strongest property> in <validation protocol>."

### 4.8 综合（synthesis）句

- `Together, these results show that <NAME> <general claim>.`
- `Taken together, …`
- `Collectively, …`
- `Altogether, …`
- `Overall, …`

实例（CellOracle）：
> "**Together, these results show** that CellOracle can be used to analyse the regulation of cell identity by transcription factors, and can provide mechanistic insights into development and differentiation."

注：`Taken together` 在 2024–25 NMI / Nature Medicine 论文里常被 `Collectively` 和 `Altogether` 替代。**不必每个 Results 子节都加一句**——多见的做法是在 2–3 个核心发现节末加一次综合句，避免审美疲劳。

---

## 5. Discussion / Conclusion

### 5.1 开句：两条路径

**A. 复述发现（restate-finding，最常用）**：
- "We have presented <NAME>, a … that …"（GenCast）
- "In this study, we demonstrate the versatility of <NAME> …"（UNI）
- "We benchmarked 16 integration methods …"（scIB）
- "<NAME> unifies two conventionally separated steps, …"（DynamicBind）
- "In sum, we developed <NAME> …"（Geneformer）
- "In this study, we have demonstrated the development of <NAME>, an LLM-powered method for …"（ChemCrow）

**B. 框架化领域（frame-in-field）**：
- "The gold standard for diagnosis of many diseases remains examination of tissue by a pathologist."（CONCH）
- "Foundation models have demonstrated substantial promise in medical image processing."（Ferber）
- "The need to discover novel structural classes of antibiotics is pressing given the antibiotic resistance crisis. This challenge has manifested in the 38-year interval between the introduction of the fluoroquinolone class of antibiotics in 1962 and the next new structural class, the oxazolidinones, in 2000."（Wong——historical anchor 类型）

**避免**：limitation-first 开局。

### 5.2 与既有工作比较

模板：
- "<NAME> solves <problem> in a small fraction of the time (<X> vs <Y>) required for physically based approaches such as <prior method>."（ProteinMPNN）
- "Unlike <prior approach>, <NAME> …"
- "Most previous tools in <field> have <limitation>; in contrast, <NAME> …"
- AI-specific："In contrast to closed-source <X>, <NAME> is openly available, allowing reproduction and extension."

### 5.3 Limitation —— 紧凑、命名约束

**两种活法**：

1. **单句直陈 + 反转或补救**（最常用）：
   - DynamicBind：先说"limited generalization to proteins with low sequence homology"，紧接 "By adopting a self-distillation approach analogous to AlphaFold, we could augment our training set …" 把 limitation 转成 future work。
   - DIMON 反转："Although one can measure the similarity/distance between domains using a metric, **this is not a prerequisite** for successfully adopting this learning framework."
   - GraphCast 直陈："One key limitation of our approach is in how uncertainty is handled."

2. **列表式 limitation**（**子门类倾向**：interpretability / theory-heavy / 应用边界明确的论文，2024–25 NMI 多见）：
   - FunSearch：*"FunSearch currently works best for problems having the following characteristics: a) availability of an efficient evaluator; b) a 'rich' scoring feedback quantifying the improvements (as opposed to a binary signal); c) ability to provide a skeleton with an isolated part to be evolved."*
   - Pai et al. 把 limitations 写成显式的多子句（retrospective design / demographic diversity / pretraining corpus / clinical metadata / interpretability）。

### 5.4 展望与收尾

**收尾句常含一个"望远镜动词"**：

| 动词短语 | 常见搭配 |
|---|---|
| `paves the way toward` | "fast prediction of … in engineering and precision medicine" |
| `opens the door to` | "the possibility of generating orders of magnitude larger ensembles" |
| `helps open the next chapter in` | "operational weather forecasting" |
| `represents an important step toward` | "ML-based weather forecasting" |
| `is a key advance in` | "accurate and efficient weather forecasting" |
| `democratizes access to` | "generalist AI models for medical experts" |
| `holds great potential to accelerate` | "the advancement of new diagnostic and therapeutic tools" |
| `will become essential tools of modern biology` | (AlphaFold) |
| `to approach and, in some cases, surpass what natural evolution has achieved` | (RFdiffusion) |

**资源/社区收尾**（适合 benchmark / 基础模型 / tool 类论文）：
- "as a resource to the community, we provide …"（高频通用模板）
- "We share our foundation model and reproducible workflows so that more studies can investigate our methods, determine their generalizability and incorporate them into their research studies."（**verbatim from Pai et al., NMI 2024**）
- "<NAME> is free open-source software available at <url> …"（结构模板，例 Foldseek）
- "We invite participation at <link>."（结构模板，MedPerf 在 abstract / Discussion 都用了 call-to-action 风）

实例（CONCH——罕见的谦虚收尾，谨慎使用）：
> "These observations suggest we still potentially have long way to go before achieving goal of building foundation model capable of truly universal zero-shot recognition."

---

## 6. Methods + 复现性（AI 论文的隐形评分项）

这是 codex review 指出我第一版漏掉的最重要章节。AI 论文的可信度有相当一部分**不在 Results 里，而在 Methods + Data/Code Availability**。审稿人 reject 一篇方法论文最常见的理由不是"结果不好"而是"无法复现 / 无法独立验证"。

### 6.1 Methods 章节标准子目（根据论文类型组合）

```
Datasets and preprocessing
  - 来源、版本、发布年份；train/val/test split 比例和切分原则
  - 是否有 leakage 检查（temporal split / patient-level split / by-cluster split）
  - 排除标准、缺失值处理

Model architecture
  - 主架构 + 关键超参 + Fig. 1 schematic 的对应
  - 与最相关 prior work 的差异（diff，不是 redo）

Training
  - 优化器、学习率与调度、batch size、epoch 数
  - Compute：GPU 型号 + 数量 + 训练时长 + peak memory
  - Random seeds：跑了几个 seed？报 mean ± std 还是单点？
  - Pretraining vs fine-tuning 流程

Evaluation
  - 用了哪些 metrics，metric 的精确定义（多种 micro/macro F1 时尤其要点出）
  - Baselines：版本号、训练超参、是否复现还是用原文报告
  - 统计检验：paired t-test / permutation / bootstrap CI
  - External validation / held-out cohort 是否有

Ethics / IRB / data governance（医学 / 临床 / 真实人群数据）
  - IRB approval, consent
  - PHI / PII 去标识

LLM-Agent / API-driven 论文专属补充
  - 用的模型版本（gpt-4-0125-preview / claude-opus-4-7 / 等具体快照名）
  - API 访问日期 + 访问期间是否曾切换 underlying model
  - 完整 prompt 模板（system / user / few-shot 例都列出，supplementary 里给齐）
  - decoding 参数：temperature / top-p / max_tokens / stop sequences
  - tool 列表 + tool description schema（agent 论文必给）
  - retry / fallback policy（API 错误 / refusal / hallucination 时怎么处理）
  - safety filter / content moderation 的版本和触发率（涉及生成式应用时）
```

### 6.2 复现要素（abstract / Discussion / availability 段三处呼应）

AI 论文有 3 处需要呼应可重复性：

1. **Abstract 末段**（可选）：例如直接给 code / demo URL（SemanticLens 摘要中就明示了 GitHub + demo URL；这是越来越多 NMI 论文的做法）。
2. **Discussion 收尾**：verbatim from Pai："We share our foundation model and reproducible workflows so that more studies can investigate our methods, determine their generalizability and incorporate them into their research studies."
3. **独立的 Data / Code / Model availability 段落**（**强约定**）：每篇 Nature 系论文都有，独立成段或独立标题。下面是**结构模板（不是 verbatim 引文）**，按各刊投稿指南填入：
   - Data availability：训练数据来源 + url + license；原始 X 沉积在 <repository>，accession 号 <id>。
   - Code availability：源码 url（GitHub / Zenodo）+ license；预训练权重 url（Zenodo / HuggingFace）+ DOI。
   - Computing resources：训练所用 GPU 型号 × 数量 + 总训练时长 + 推理 reproduce 所需最低硬件。

### 6.3 AI 论文复现性的常见漏报项

- **Random seed 数与方差**——审稿人最关注的可信度信号。可行时跑 3 / 5 / 10 个 seed 报 mean ± std；预训练成本巨大、无法多 seed 时退而求其次：bootstrap CI、cross-cohort 重复、repeated splits、对关键超参的 sensitivity analysis。无 uncertainty quantification 直接报 SOTA 是最常被打回的点。
- **Compute cost 透明度**——总 GPU hours、peak memory、推理成本。这影响审稿人对"democratization 声明"的信任。
- **数据切分 leakage 检查**——尤其当数据来自时间序列 / 同一病人 / 同一蛋白家族时。
- **Baseline 训练公平性**——是否给 baseline 同样的 epoch 数、同样的 search space、同样的 prompt（LLM）。审稿人最爱挑 unfair comparison。
- **超参搜索 protocol**——你的 hyperparam search 是 train-set 上做还是 val-set 上做？search 了多少组？是否报告 search budget？

---

## 7. 跨章节的语言学装备

### 7.1 强动词（results / abstract 用）

```
outperforms, surpasses, exceeds, far exceeds
achieves, establishes, identifies, discovers
enables, empowers, facilitates, accelerates
demonstrates, validates, confirms
recovers, rescues, dissipates
unifies, integrates, scales
democratizes, advances
```

### 7.2 Hedges（discussion / outlook / 边界声明用）

```
may, can, could, suggest, indicate, consistent with
to our knowledge, in a majority of cases
shows potential, is expected to
likely, probably
we hope, we believe, we envision
holds great potential to / paves the way / opens the door to
```

**asymmetry rule**（**常见模式**）：abstract 主体 + Results 用强动词，discussion 末段 + outlook 集中堆 hedge。**完全没 hedge** 在临床 / 高风险 AI 应用是问题；**满篇 hedge** 是新人写法。

### 7.3 段间连接词（按功能分类）

| 功能 | 词 |
|---|---|
| 加叠 | `Furthermore,` `In addition,` `Moreover,` |
| 强调 | `Notably,` `Importantly,` `Critically,` `Strikingly,` `Remarkably,` |
| 转折 | `However,` `Yet,` `Nevertheless,` `In contrast,` `By contrast,` `Despite this,` |
| 结果 | `Consequently,` `As a result,` `Therefore,` `Thus,` |
| 意外 | `Interestingly,` `Surprisingly,` `Intriguingly,` |
| 综合 | `Together,` `Taken together,` `Collectively,` `Altogether,` `Overall,` `In sum,` |
| 推进 | `Building on this,` `Beyond <X>,` `We next asked,` `We then …,` `Next,` |
| 对比定向 | `Unlike <prior>,` `Contrary to,` |

**经验**：合理使用连接词让段间过渡更明确，但**不要每段都用一个连接词起头**——机械化读起来僵。

### 7.4 高复用句型

- 「To <verb>, we <method>. We found that <result> (Fig. <X>).」 — 一个发现一个段的最快开局。
- 「<NAME> <verbs> <object> with <metric>=X.XX (<test>, P<X>, n=<X>), <X.X-fold> over <baseline>.」 — 一句装一个完整 result claim。
- 「Although <prior X>, <NAME> <does Y>; this <enables/suggests> <Z>.」 — 一句把对比 + 贡献 + 含义都装下。

---

## 8. AI / ML 子门类剧本

按你的论文类型选一个剧本。以 NMI 为主目标。

### 8.1 ML 方法论文（如 ProteinMPNN / RetroExplainer / MolE / DynamicBind / DIMON / HINTS）

- **Title** 用 **B**（工具名 + 冒号 + 描述）或 **C**（陈述发现）。
- **Abstract**：BIG → GAP → HERE-WE → METHOD-SPEC → KEY-RESULT → IMPLICATION（6 句够用）。
- **Results 子节**：4–6 个。第 1 节描述架构 + 流程图（Fig. 1），第 2–3 节是 benchmark + baseline，第 4 节起做 ablation / 多种子方差 / 跨数据 generalization / 一个真实下游 case。
- **Methods**：完整复现要素（§6.1）；尤其 baselines 公平性 + compute 报告。
- **Discussion**：A 路径开局 + 与最相关 prior work 一句对比 + 单句 limitation + 望远镜动词。
- **Closing**：资源/社区句 + outlook 双轨。

### 8.2 基础模型 / Foundation Model（如 Geneformer / UNI / CONCH / MedSAM / CellFM / MolE / Cancer-Imaging-FM）

- **Title** 偏 **D**（"A foundation model for X" / "Towards a … for X"）。
- **Abstract** 套路化高：(1) NLP-parallel 句（**借用框架但务必改写措辞**——不要照抄 Geneformer 的 NLP-parallel 原句）；(2) 规模声明（M 数据 + N 参数 + K 模态）；(3) 下游任务 list；(4) 解释性 / embedding / 可视化的 1 个 mention。
- **Results** 子节：常用 task-neutral（C 风格）。**强约定的几节**：
  - Architecture + pretraining
  - Downstream task 1, 2, 3 …（zero-shot / few-shot / fine-tuned）
  - Embedding analysis / interpretability / saliency
  - **Pretraining scaling experiments**（**子门类倾向**：UNI 单独成节，MedSAM 用"effect of training dataset size"，Virchow 在 Discussion 里讨论。**不是规则**——你要看自己的故事是否需要它来 sell scaling claim）
- **Closing**：democratization / shift research direction。

### 8.3 LLM-Agent / AI-for-science（如 ChemCrow / FunSearch / AlphaGeometry）

- **Title** 偏 **E**（"X discoveries from Y"）或 **C**（"Solving X without Y"）。负向定语（"without human demonstrations"）是 DeepMind 的标志手法，把方法论约束当卖点。
- **Hook 多样，不是单一模板**：
  - ChemCrow 走"技术变革引子"（"In the last few years, large language models (LLMs) have transformed various sectors …"）；
  - AlphaGeometry 走"数据稀缺 + 翻译瓶颈"（"high cost of translating human proofs … severe scarcity of training data"）；
  - FunSearch 走"易验证 vs 难求解"（"Many problems in mathematical sciences are 'easy to evaluate,' despite being typically 'hard to solve.'"）；
  - SemanticLens 走"跨工程类比"（aeroplane vs neural network）。
- **Abstract** 较长（FunSearch 10 句），每句承担独立角色（capability → flaw → here-we → mechanism → result-1 → result-2 → 反差点 → meta-property → impact）；ChemCrow 7 句更紧凑。
- **Results** 常用领域名 + 案例（FunSearch："Extremal combinatorics → Cap sets / Admissible sets" → "Bin packing"）；ChemCrow 用 capability noun phrase（"Autonomous chemical synthesis" / "Risk-mitigation strategies"）。
- **Limitation 列表式**（FunSearch / Pai 风）："X currently works best when (a) … (b) … (c) …"
- **Methods 必含**：见 §6.1 LLM-Agent 补充清单（prompt / API 版本 / 日期 / decoding 参数 / 工具表）。
- **Closing**：envision / call-to-action / 把方法论上升为新范式（"automatically-tailored algorithms will soon become common practice"）。

### 8.4 可解释性 / 模型审计 / 联邦评估（如 SemanticLens / MedPerf；与传统"benchmark 论文"§8.5 部分重叠但 hook 与定位不同）

- **Title** 偏 "Mechanistic understanding and validation of …"（SemanticLens）/ "Federated benchmarking of … with X"（MedPerf）。
- **Hook** 偏跨工程类比（aeroplane vs neural network——SemanticLens）或 regulatory recap（"national agencies … started drafting regulatory frameworks"——MedPerf）。
- **Results 标题不收敛**：SemanticLens 用 capability 动词（Search / Audit / Compare / Describe）作为 4 个 operation 的章节锚点；MedPerf 用更中性的 "Evaluation on global federated datasets" / "MedPerf roadmap" / "Related work"。**别把 SemanticLens 的动词四联当成通用模板**。
- **Methods**：评估协议 / dataset / 复现实验包是核心；联邦评估论文还需描述 sites 数 / 跨大洲分布 / IRB 链。
- **Closing** 偏 community + 工具发布 + 标准化呼吁；MedPerf 直接给"call-to-action 链接"风格收尾（"we invite participation at ref. […]"）。

### 8.5 Benchmark 论文（如 scIB-style；NMI 上 benchmark 论文相对少，但 NC/Nature Methods 多）

- **Title** 用 "Benchmarking X in Y" 或陈述发现。
- **Results 子节标题清一色 claim header**（A 风格）——每个 header 自己就是发现。
- **Abstract 必含**：方法 × 任务 × 数据 三轴的乘积数（"68 method and preprocessing combinations on 85 batches… representing >1.2 million cells distributed in 13 atlas-level integration tasks"）。
- **Closing**：community service + tool/pipeline release。

### 8.6 AI-for-X 应用论文（你用 ML 解决某个具体科学问题，如 GraphCast / GenCast / Halicin / Wong-MRSA / GNoME / AlphaMissense）

- **Title** 偏 **C**（"X enables Y"）或 **E**（"Discovery of …"）。
- **Hook** 多为 societal / domain-stake（whether to carry an umbrella；antibiotic resistance crisis）。
- **METHOD-SPEC 句数字密**（分辨率 / 变量数 / 时间长度 / 计算时长）。
- **漏斗修辞**贯穿 Results：screening → filter → test → verify。
- **闭环验证**：实验阶梯（in silico → in vitro → in vivo / 结构 / 真实部署）越完整越好。AI 论文如果做的是纯计算且能拿到外部 / prospective 验证，强烈建议加。
- **Closing**："paves the way toward / opens the next chapter / order-of-magnitude expansion …"

---

## 9. AI 论文的反模式（来自被打回稿件 + AI-specific）

通用反模式：

1. **Abstract 写成 Methods 摘要**——堆架构细节没头条数字。Reviewer 不知道你做出了什么。
2. **Hedge 过度**：abstract 全是 "may help" / "could potentially" — 是没干完的信号。
3. **Results 标题全部 task-neutral**，导致每节读完不知道是赢是输。改成 claim header。
4. **Discussion 第一段是 limitation**——是新人写法。
5. **Closing 写"future work includes …"列表**——换成 outlook 句（paves the way / opens the door）。
6. **重复使用空心化的 "novel"**——novel-as-padding 是反模式，但 novel 作为有内容形容词（"structurally novel"）可用。
7. **写「To the best of our knowledge」3 次以上**——一篇里最多用一次。

AI-specific 反模式：

8. **单种子单 run 报 SOTA**。审稿人会要求 multiple-seed std。
9. **Cherry-picked benchmark / metric**：选择性报告自己赢的子集。NMI 审稿人尤其敏感。
10. **Compute cost 不报告**。这削弱"democratization / efficiency"之类声明的可信度。
11. **Baseline 训练不公平**：自己跑的 baseline 用 N epoch，自己模型用 10N epoch；自己模型用搜索过的最优 hyperparam，baseline 用默认值。
12. **数据 leakage 不查**：时间序列、同病人、同蛋白家族跨 split 都是常见 leak。
13. **Foundation-model 论文写成 LLM 文献综述**——前 6 段都在介绍 transformers 历史。
14. **过度依赖 closed-source baseline**（"we compare against GPT-4 in March 2024"）但不公开你的 prompt / API 版本——后人无法复现。
15. **没有公开 model weights / code 但仍然在 abstract 里说 "to enable reproduction"**。Reviewer 反感 false promise。
16. **Discussion 把所有 limitation 推给"future work"**——把限制说清楚是诚信，不是软弱。

---

## 10. 提交前自检表

按下面顺序过一遍。**这些项不是统一规律，只是常见落点**——如果你的论文结构合理但少几项，不要硬塞。

### 标题与摘要
- [ ] 标题是 §1 中的 5 种之一，**不写空心化的 "A novel method for …"**
- [ ] Abstract 多数 5–8 句，**有一句明确 pivot**（Here we / We introduce / We propose / We report / 等其一）
- [ ] **METHOD-SPEC 句**（s5）数字密度高于其他句
- [ ] **KEY-RESULT 句**（s6）有 "delta + 命名 baseline / benchmark"
- [ ] Abstract 末句是 outlook（paves the way / opens the door / democratizes / 等）
- [ ] Abstract hedge 集中在末句（s8），中段叙述用直陈动词

### Introduction
- [ ] Hook 不是"Recently, deep learning achieved great success in …" / "With the rapid development of LLMs"
- [ ] 至少 2 个 GAP 短语（However / Yet / remains limited / scales poorly to …）
- [ ] Pivot 段落明显占一段
- [ ] Intro 末段或预告 Results 子节（基础模型/benchmark）或给出紧凑路线图（方法论文）

### Results
- [ ] 子节标题风格主用一种（A / B / C 中选一种）
- [ ] 第 1 个 Results 子节让读者快速看到"架构 / overview / Fig. 1 schematic"
- [ ] 至少有一个 robustness / ablation 子节（用 §4.6 的过场词起头）
- [ ] 主要的 baseline 比较都有 uncertainty quantification（P 值 / CI / IQR / 多种子 std）至少其一
- [ ] 关键发现节末有 1–2 处综合句（"Together, these results show …"），不必每节都有

### Discussion
- [ ] Discussion 第一句是复述核心贡献 / 框架化领域，不是 limitation
- [ ] Limitation 一句直陈 + 紧接 remedy 或反转，**或** 列表式 ((a)(b)(c)) 给出适用边界
- [ ] 末句包含一个"望远镜动词"（§5.4 表格挑一个）

### Methods + 复现性（AI 论文必查）
- [ ] 数据集划分原则明确（train/val/test，是否有 leakage 检查）
- [ ] 训练 compute（GPU 型号/数量、训练时长、peak memory）已报告
- [ ] Random seeds 数 + mean ± std（或其他 uncertainty）已报告
- [ ] Baselines 训练公平性（同 epoch / 同 search budget / 同 evaluation protocol）说明
- [ ] **Code / model weights / data availability 段落**（独立段，含 url + DOI + license）

### 跨章节
- [ ] 强动词集中在 abstract 主体 + Results；hedges 集中在 outlook
- [ ] 段间过渡自然，不堆砌也不机械
- [ ] 自己读一遍每个 figure 的 caption——caption 自身能否独立讲清这个 figure 在说什么

---

## 11. 期刊定位差异（决定你投哪、写法怎么调）

> **Caveat**：本节是基于 36 篇取样的"风格观察 + 投稿策略经验"，不是官方指南。**字数 / 图数 / 章节限制 / Submission category 一定要去各刊官网的 author guidelines 核对**——这些规则每年都会调整。

**Nature**（旗舰级 AI——AlphaFold / AlphaGeometry / FunSearch / GNoME 级别；GraphCast 在 Science 但同档次）
- 论文要有外部影响力（科学发现 / 范式转换 / 产业级部署），不止 SOTA 数字。
- 写作风格：宏大 hook（50 年问题 / 文明级愿景），closing 用"essential tools of modern biology"级语言。
- AI 单凭 SOTA 不容易过；通常需要外部领域影响。

**Nature Machine Intelligence**（NMI——AI 方法 / agent / 可解释性 / 应用方法的主战场）
- 你的主要目标。NMI 审稿人最看重：方法有概念新意、benchmark 严谨、复现可信、伦理 / 可信赖度有讨论。
- 写作风格：cross-engineering analogy hook 在 NMI 越来越多（aeroplane / "easy to evaluate, hard to solve"）；abstract 末段常 mention code 与 demo URL；Results 多见 task-neutral header（C 风格）；Methods 详尽。
- 子门类：基础模型 / agent / 可解释性 / AI-for-science 都欢迎。
- 文章类型：Articles 与 Briefs 并存（具体字数 / 图数限制以官网为准）。

**Nature Communications**（NC——跨学科 AI 应用 + 方法）
- 接受范围最广。AI 在生物 / 化学 / 物理 / 临床的应用论文最常发。
- 方法严谨即可，不必一定是 ML 范式革命。许多 NC 论文是"在某个具体科学问题上把 AI 跑通了"。
- 写作风格：method-as-subject Results header（B 风格）很流行；abstract 务实；closing 偏 community / 工具发布。

**Nature Computational Science**（NCS——计算驱动的科学问题）
- 偏物理 / 化学 / 工程 / 数学 / 系统生物的计算方法。AI 是工具不是主角。
- 写作风格：abstract 数字密；NCS 部分论文带 "1 Significance" 编号小节；理论 / 算法贡献明确；与传统数值方法 / NWP / DFT 比较。
- AI-only 论文（不结合 physics / chemistry / engineering 实质）在 NCS 不容易过。

**Nature Methods**（NM——主要是生物医学方法学）
- 你做 AI for biology 时偶尔投。Brief Communications 格式对 AI 方法论文友好。
- 写作风格：tool-name title 多见；Brief Communication 没有 Discussion 节。

**Brief Communication vs Article**（一般倾向，具体限额请查官网）：Brief 通常显著更短、更少图、无 Discussion 节；Article 是标准长度。如果你的 AI 方法论文核心实验只有 1–2 个、故事线高度凝练，Brief 是值得考虑的形式。

---

## 12. 浓缩快速套路（贴在屏幕边）

```
TITLE: <X: …描述...> 或 <X enables Y> 或 <Towards a foundation model for Z>
ABSTRACT (5–8 句):
  <Topic> is <central/critical> for <field>.
  However, <existing methods> are <bottlenecked by / scale poorly to> <X>.
  [Yet, <complementary failure of paradigm B>.]
  Here we [introduce/present/propose] <NAME>, a <one-line characterization>.
  <NAME> <verb> <numerically dense spec>.
  We show that <NAME> <outperforms / achieves> <baseline> by <ΔX% on N tasks>.
  [Furthermore, <generalization or qualitative novelty>.]
  <NAME> <paves the way / opens the door / democratizes> <broader vision>.
  [Code / weights / data are available at <url>.]

INTRO (4–5 段):
  ¶1 Hook：领域重要性 / 老问题 / 跨工程类比
  ¶2 Recent advances …
  ¶3 However, … remains … (gap × 2-3)
  ¶4 Here we [verb] <NAME> + 路线图（"Specifically, we show that …, that …, and that …"）

RESULTS (4–6 子节):
  §1 让读者一眼看到架构 + Fig. 1 schematic
  §2–3 主 benchmark，每个比较带 baseline + uncertainty
  §4 ablation / robustness（"To rule out … we …" / "To probe the contribution of …, we ablated …"）
  §5 generalization / case study（"We next applied <NAME> to … and found that …"）
  关键节末：1–2 处 "Together, these results show that <NAME> <general claim>."

METHODS（独立章节 + 独立 Code/Data Availability 段）

DISCUSSION (3–4 段):
  ¶1 复述贡献（"We have presented … that …"）
  ¶2 与 prior work 对比，强调差异
  ¶3 Limitation 一句 + 反转/补救  或  列表式 (a)(b)(c) 适用边界
  ¶4 Outlook：望远镜动词收尾。
```

---

## 附录 A：36 篇取样清单

| # | 领域 | 论文 | 刊物 | 取样文件 |
|---|---|---|---|---|
| 1–6 | 单细胞 | Geneformer, SCimilarity, Tangram, scIB, CellOracle, CellFM | Nature × 3, Nat Methods × 2, NC × 1 | `extracts/01-singlecell.md` |
| 7–12 | 蛋白 / 结构 AI | AlphaFold2, ESM-2/ESMFold, ProteinMPNN, RFdiffusion, AlphaMissense, Foldseek | Nature × 2, Science × 3, Nat Biotechnol × 1 | `extracts/02-protein.md` |
| 13–18 | 物理 / 气候 / 材料 | GraphCast, GenCast, DIMON, M3GNet, HINTS, GNoME | Science, Nature × 2, NCS × 2, NMI | `extracts/03-physics.md` |
| 19–24 | 药物发现 | DynamicBind, Wong-MRSA, Halicin, SyntheMol, RetroExplainer, DRAGONFLY | NC × 4, Nature, Cell | `extracts/04-drug.md` |
| 25–30 | 临床 AI | MedSAM, UNI, CONCH, Virchow, MedPerf, Ferber-GPT4V | Nat Med × 3, NC × 2, NMI | `extracts/05-medical.md` |
| 31–36 | ML 通用 / 基础模型 | ChemCrow, AlphaGeometry, MolE, SemanticLens, Cancer-Imaging-FM, FunSearch | NMI × 4, Nature × 2, NC | `extracts/06-ml.md` |

每篇都按 `_framework.md` 的 30 余字段做了 verbatim 抽取——本 SKILL 所有 verbatim 引文都可在那里查到出处；本 SKILL 标注为"构造 / 模板示范"的句子是综合自多句或为模板演示，不是单一 verbatim。
