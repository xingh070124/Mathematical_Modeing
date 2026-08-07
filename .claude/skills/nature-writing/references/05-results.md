# 05 · Results, Figures, Evidence

（v4 SKILL Part IV；总索引见 `../SKILL.md`；视觉端见 `../FIGURE-SKILL.md`）

## 5. Results：顶刊工程化最强的部分

**Patron sentence** — ProteinMPNN Discussion opener:  
> "ProteinMPNN solves sequence design problems in a small fraction of the time (1.2 sec vs 258.8 sec on a single CPU for a 100 residue protein) required for physically based approaches such as Rosetta…"

这句好，因为它把 conclusion、速度、hardware、task size、baseline 都塞进一个可复述单位。

### 5.1 Results 子节标题：四种主风格

| 风格 | 模板 | 代表 | 何时用 |
|---|---|---|---|
| **A. Claim header** | `X improves Y` / `X enables Y` | scIB: "Scaling shifts integration performance toward batch removal"；Virchow: "Virchow enables pan-cancer detection"；Ferber: "In-context learning…improves classification accuracy" | 单一明确结论；benchmark / clinical / flagship |
| **B. Method-as-subject** | `<NAME> <verb> <capability>` | DynamicBind: "DynamicBind achieves higher accuracy…"；DRAGONFLY: "DRAGONFLY outperforms…"；CellFM: "CellFM enables…" | 工具要成为 protagonist |
| **C. Task-neutral / capability noun phrase** | `Weakly supervised slide classification` / `Zero-shot classification` | UNI, CONCH, RFdiffusion, FunSearch | 多任务并列；foundation model；field-specific case ladder |
| **D. RQ / analysis-scaffold header**（v5 新加） | `RQ1: does <X> explain <Y>?` / `<Capability>: <task>` | Webb (NC 2025): "Problem solving: Tower of Hanoi"；Zhou (Nature 2026): "RQ1 examines…"；Muttenthaler: "Alignment improves generalization…" | AI evaluation / measurement / analysis 论文；想把 Results 变成"系统回答几个 RQ"的结构 |

经验：

```text
- 一篇论文最好主用一种 header 风格。
- Benchmark 论文偏 A。
- NC 方法论文常用 B。
- Foundation model / pathology 常用 C。
- AI evaluation / measurement / analysis 论文（v5）偏 D——把 Results 写成 RQ 序列。
- 不要用问句标题；corpus 中几乎没有（D 例外：RQ format 的"问句"是结构信号，不是真的问句）。
```

Taste 判断：  
如果 Results header 全是 neutral noun phrase，读者会不知道你赢了没有。  
如果 header 全是 `Method X achieves…`，但方法并不够强，会像广告。  
选择风格时先问：**读者需要扫描能力，还是扫描结论？**

### 5.2 Results 子节开句：三类模板

#### A. Method-first

```text
<NAME> <verbs> <one-sentence description>.
```

DynamicBind:
> "DynamicBind executes 'dynamic docking', a process that performs prediction of the protein–ligand complex structure while accommodating substantial protein conformational changes."

Geneformer:
> "Geneformer is a context-aware, attention-based deep learning model pretrained on large-scale transcriptomic data…"

适合第一个 Results 子节 / architecture overview。

#### B. Motivation-first

```text
To <test/investigate/rule out/gain insight into> <X>, we <action>.
```

Geneformer:
> "To investigate how the model was learning network dynamics during the pretraining stage, we examined the pretrained Geneformer attention weights."

RFdiffusion:
> "A grand challenge in protein design is to scaffold minimal descriptions of enzyme active sites…"

适合 ablation、mechanism、new task。

#### C. Claim-first

```text
We find/show that <result>.
```

GraphCast:
> "We find that GraphCast has greater weather forecasting skill than HRES…"

RFdiffusion:
> "RFdiffusion readily generates diverse unconditional designs up to 600 residues in length…"

适合强结果先行。

### 5.3 Results 顺序按 story shape 调

| Story shape | Results 推荐顺序 |
|---|---|
| Bottleneck-broken | overview → main benchmark vs bottleneck baseline → robustness → hard cases → implication |
| Two-gap synthesis | prior route A failure → prior route B failure → method synthesis → benchmark on both axes → ablation |
| Scale-emergent | data/model scale → scaling law → downstream breadth → emergent capability → efficiency / limitations |
| Discovery funnel | dataset/screen → filters → candidate selection → empirical validation → mechanism / in vivo / structure |
| Human-anchored benchmark | system overview → benchmark design → human / prior SOTA comparison → qualitative examples → failure cases |
| Trust/audit bridge | opacity problem → mapping/explanation method → audit operations → case studies → limitations |
| Limit-redrawn | method → first capability → harder capability → previously impossible task → boundary statement |

### 5.4 Figure call-out：把发现放主语位置

现代 Nature 系更常写：

```text
We found that <result> (Fig. 1a).
```

而不是：

```text
Figure 1a shows that <result>.
```

前者把发现放在主语位置，figure 是证据。  
后者把图片当主语，句子更像 lab report。

可用形式：

```text
<claim> (Fig. 1a).
as shown in Fig. 2a–c
as illustrated in Fig. 4
as depicted in Fig. 1
```

例：

Virchow:
> "Virchow embeddings yielded the best cancer detection performance on all cancer types (Fig. 2a)."

DynamicBind:
> "As shown in Fig. 2a and b, DynamicBind predicts more cases with ligand RMSD below various thresholds…"

### 5.5 Caption：让 reviewer 只看 caption 也能复述

推荐 panel caption 结构：

```text
a, <这个 panel 的发现>.
<数据来源 / 队列 / N>.
<视觉编码：boxplot / heatmap / scatter>.
<统计检验：test, P value, CI/IQR/SD>.
```

Caption title 现代趋势是 declarative：

```text
Virchow embeddings yielded the best cancer detection performance on all cancer types.
```

老式 noun phrase 也可：

```text
Overview of the AlphaFold model architecture.
```

Taste rule: caption 不是图注垃圾桶。不要把正文没讲清的东西塞到 caption。

### 5.6 数字 + 统计写法

基础模板：

```text
<metric> of <point> [(IQR/CI/SD: …–…)],
<ΔX% / X.X-fold> over <named baseline>,
[<P < 1e-X>, <test name>, <n=…>].
```

医学影像 / clinical AI：

MedSAM:
> "median DSC scores of 87.8% (IQR: 85.0-91.4%)…demonstrating 52.3%, 15.5%, and 22.7 improvements…"

UNI:
> "+4.2% performance increase (P < 0.001, two-sided paired permutation test)…"

Virchow:
> "AUC of 0.950 with Virchow embeddings, 0.940 with UNI, 0.932 with Phikon and 0.907 with CTransPath…P < 0.0001"

Protein / physical AI：

AlphaFold:
> "median backbone accuracy of 0.96 Å r.m.s.d.₉₅"

ProteinMPNN:
> "52.4%, compared to 32.9% for Rosetta"

GenCast:
> "97.4% of 1320 targets"

ML / NMI 方法论文：

```text
- multiple seeds mean ± std
- bootstrap CI
- paired permutation test
- repeated splits
- sensitivity analysis
```

至少给一种 uncertainty quantification。单 seed 报 SOTA 是高危。

### 5.7 Baseline 比较的措辞

强：

```text
compared to <baseline> for <metric>
X.X times higher than <baseline>
two orders of magnitude improvement over
outperforming the previous best method that only solves ten
matches or exceeds <baseline> while requiring <fraction> compute
```

弱：

```text
performs better than other methods
achieves competitive performance
comparable to state-of-the-art
```

“competitive” 常常等于你没赢。  
“comparable” 如果不用具体 baseline 和 delta，会像退让。

### 5.8 Robustness / ablation 的过场词

```text
We next tested whether …
We next asked …
To rule out <alternative explanation>, we …
As a control, …
As a negative control, …
We hypothesized that …
Supporting this hypothesis, …
To verify that <result> was not an artifact of <X>, we …
To probe the contribution of <component>, we ablated …
To make a fair comparison, we adopted <protocol> …
```

Corpus anchors：

SyntheMol:
> "As a control, we tested 58 randomly selected molecules from the Enamine REAL Space."

Tangram:
> "To verify that these distributions were not an artifact of our probabilistic approach…"

MolE:
> "we conducted ablation studies to understand the impact…"

### 5.9 Discovery funnel 模板

```text
Of <large N>, we <filter> to <medium N>;
we <test> <small N> empirically and find <hit count> active,
of which <X> showed <strongest property> in <validation protocol>.
```

Corpus funnels：

- M3GNet: `31M hypothetical → 1.8M potentially stable → top 2000 → 1578 DFT-verified`
- Wong: `12,076,365 compounds → 3,646 passing filters → 283 tested → 4/9 active → one structural class`
- Halicin: `107,349,233 ZINC15 → 23 tested → 8 active`
- SyntheMol: `30B chemical space → 24,335 generated → 70 selected → 58 synthesized → 6 hits`

Taste rule: funnel 的最后一级必须可信。  
大数负责 awe；小数负责 trust。

### 5.10 综合句：少用，但要准

```text
Together, these results show that <NAME> <general claim>.
Taken together, …
Collectively, …
Altogether, …
Overall, …
In sum, …
```

CellOracle:
> "Together, these results show that CellOracle can be used to analyse the regulation of cell identity…"

MedPerf:
> "Collectively, all studies were intentionally designed to include a diverse set of clinical areas…"

UNI:
> "Altogether, our findings highlight the strength of…"

Taste rule: 不要每个 Results 子节都 `Together`。  
综合句应该出现在一组证据之后，而不是每段结尾自动触发。

### 5.11 Results before / after

**Pair 14 — Figure 主语 → 发现主语**

Bad template:
> "Figure 2 shows the performance comparison between our method and baselines."

Better, Virchow:
> "Virchow embeddings yielded the best cancer detection performance on all cancer types (Fig. 2a)."

What changed: 读者先看到 claim，再看到证据位置。

**Pair 15 — baseline 模糊 → baseline 可审计**

Bad template:
> "Our method is faster than existing approaches."

Better, ProteinMPNN:
> "1.2 sec vs 258.8 sec on a single CPU for a 100 residue protein"

What changed: 速度、硬件、任务大小、baseline 都具体。审稿人能复现判断。

**Pair 16 — robustness 空话 → control 有牙齿**

Bad template:
> "We performed controls to verify the robustness of our method."

Better, SyntheMol:
> "As a control, we tested 58 randomly selected molecules… None of these compounds displayed antibacterial activity…"

What changed: control 不是姿态，而是对 alternative explanation 的直接攻击。

**Pair 17 — ablation 机械 → 机制问题驱动**

Bad template:
> "We ablated each module and report results."

Better, Geneformer:
> "To investigate how the model was learning network dynamics during the pretraining stage, we examined the pretrained Geneformer attention weights."

What changed: ablation 从“表格义务”变成机制问题。

**Pair 18 — 多任务堆叠 → capability map**

Bad template:
> "We evaluate our model on many downstream tasks."

Better, CONCH:
> "Evaluated on a suite of 14 diverse benchmarks, CONCH transfers to wide range of downstream tasks involving histopathology images and/or text."

What changed: 任务数量、diversity、transfer 对象都明确。

---

