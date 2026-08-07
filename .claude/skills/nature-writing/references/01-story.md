# 01 · Story Architecture

（v4 SKILL Part I 节选；总索引见 `../SKILL.md`）

## 1. Story architecture toolkit：先选故事，再排实验

**Patron sentence** — AlphaFold:  
> "Predicting the three-dimensional structure that a protein will adopt…has been an important open research problem for more than 50 years."

这不是背景句。这是故事 architecture。50 年问题一旦成立，后面的 “first computational method” 就有了重量。

### 1.1 七种 canonical story shapes

从 36 篇 corpus 里，AI / ML 论文最常见的是下面七种形状。选一个主形状，最多加一个副形状。不要把所有形状都塞进去。

| Story shape | 核心戏剧 | 代表论文与 verbatim anchor | Fig. 1 应该做什么 | 应删 / 降级什么 |
|---|---|---|---|---|
| **A. Bottleneck-broken** | 一个老 bottleneck 卡住领域；你的方法打穿它 | AlphaFold: "Structural coverage is bottlenecked by the months to years of painstaking effort…"；Foldseek: "searching these databases is becoming a bottleneck"；GraphCast: "cannot directly use historical weather data…" | 左边显示 bottleneck，右边显示你的路线如何绕开 / 打穿；最好有 before/after 数字 | 与 bottleneck 无关的 secondary benchmark；不能改变“打穿”判断的 ablation |
| **B. Two-gap synthesis** | 两条 prior route 各有致命缺陷；你合成优点 | SyntheMol: "Property prediction models…scale poorly…" + "Generative models…generate molecules that are challenging to synthesize."；HINTS: "Neural networks suffer from spectral bias…" + "relaxation methods…stall…" | Fig. 1 画出 A fails / B fails / ours synthesizes；让读者看到“为什么非你不可” | 只证明你比 A 好、没证明你也解决 B 的实验 |
| **C. Scale-emergent** | 规模不是炫耀，而是产生新能力 | ESMFold: "As language models of protein sequences are scaled up to 15 billion parameters, an atomic-resolution picture…emerges"；GNoME: "graph networks trained at scale can reach unprecedented levels of generalization"；UNI: ">77 TB of data" | scaling curve + emergent capability；数据地图要服务于能力，不是炫 collection | 没有 scaling 逻辑的“我们数据很大”图；只列参数不连结果的表 |
| **D. Discovery funnel** | 海量候选 → 严格过滤 → 小规模验证 → 一个强 payload | Wong: "39,312 compounds…" → "12,076,365 compounds" → "283 compounds" → one MRSA class；M3GNet: "31 million hypothetical crystal structures" → "1578…verified" | Funnel 是主角：每一级筛掉什么、保留什么、最后验证什么 | 模型训练细节过长；主故事不是 architecture，而是 verified discovery |
| **E. Human-anchored benchmark** | 结果不只赢模型，还接近 / 改变人类参照 | AlphaGeometry: "approaching the performance of an average International Mathematical Olympiad gold medallist"；MedPerf: "32 sites across six continents"；Ferber: "medical experts without technical background" | benchmark bar 要有人类 / deployment / institution anchor；不要只放 accuracy | 只跟弱 baseline 比的表；没有 human / real-world anchor 的夸张句 |
| **F. Trust / audit bridge** | 黑箱 → 可解释 / 可验证 / 可部署 | SemanticLens: "hindering verifiability and undermining trust"；Wong: "models are typically black box in nature and do not provide chemical insights"；MedPerf: "prioritizing privacy" | Fig. 1 画出 opaque model 到 audit / explanation / federated evaluation 的路径；**v5：measurement papers 的 antagonist 是 *bad ruler / low predictive power***（Xiao Densing-law、Farquhar semantic-entropy、Zhou ADeLe），故事变成"现有 ruler 错→新 ruler 解释/预测更好"——这不是新 story shape，是 F 的子型 | 只说 interpretability，不展示可操作 audit 的例子 |
| **G. Limit-redrawn / paradigm shift** | 不是多赢几个点，而是边界变了 | RFdiffusion: "surpass what natural evolution has achieved"；GNoME: "stable materials known to humanity"；FunSearch: "first discoveries made for established open problems using LLMs" | Fig. 1 或 final figure 要显示新边界：以前不能做什么，现在能做什么 | 小 benchmark 赢法；过多 incremental SOTA 会冲淡边界感 |

### 1.2 如何选择你的 story shape

用下面 8 个问题逼自己选：

```text
1. 如果只能让审稿人记住一句话，它是什么？
2. 这句话里的 antagonist 是什么？
   - bottleneck?
   - data scarcity?
   - black box?
   - scale?
   - compute cost?
   - human expert bottleneck?
   - synthetic intractability?
3. 你的 strongest evidence 是：
   - benchmark number?
   - experimental validation?
   - human-level anchor?
   - scaling law?
   - deployment across institutions?
   - discovery of new entity?
4. 这篇论文的 climax 在哪一张图？
5. 哪个实验如果删掉，主 claim 仍然成立？
6. 哪个实验如果删掉，主 claim 会塌？
7. 读者会在哪一句开始相信你？
8. 审稿人会在哪一句开始怀疑你？
```

主 story shape 由第 2–4 题决定。  
删减由第 5–6 题决定。  
Results 顺序由第 7–8 题决定。

### 1.3 Fig. 1 的四种功能

Fig. 1 不是“把 pipeline 画完”。Fig. 1 是读者进入故事的门。

| Fig. 1 类型 | 何时用 | Corpus anchor | Taste 判断 |
|---|---|---|---|
| **Machine map** | 方法机制是贡献，如 DynamicBind / AlphaFold / SemanticLens | DynamicBind opener: "DynamicBind executes 'dynamic docking'…" | 画输入、核心模块、输出；不要把所有 loss 都画成主路径 |
| **Bottleneck breaker** | contribution 是绕开老瓶颈 | AlphaFold: "Structural coverage is bottlenecked…" | 左边痛点，右边解法；让非本领域 editor 也懂 |
| **Discovery funnel** | 重点是筛选和验证 | SyntheMol: "chemical space of 30 billion molecules" → "58 generated molecules" → "six…" | funnel 数字必须准确；最终 verified payload 放大 |
| **Capability map** | foundation model / benchmark / agent 多任务 | MedSAM: "86 internal validation tasks and 60 external validation tasks"；ChemCrow: "18 expert-designed tools" | 多任务不是堆图标；按能力族分层 |
| **Human / real-world anchor** | human benchmark 或 deployment 是主戏 | AlphaGeometry: "average IMO gold medallist"；MedPerf: "32 sites across six continents" | 人类参照要一眼可见，不要藏在 caption |

### 1.4 哪些实验进主文，哪些进 Supplementary，哪些删掉

主文实验要满足至少一个条件：

```text
A. 它支撑 abstract 里的一个主 claim。
B. 它改变 reviewer 对主 claim 的可信度。
C. 它处理一个可预见的强质疑。
D. 它推进 story 的 climax。
E. 它解释一个 surprising result。
```

进 Supplementary 的实验通常是：

```text
- 扩展表：更多 dataset / task / hyperparameter / implementation details。
- 次要 ablation：方向一致但不改变机制解释。
- 额外 baseline：不是 reviewer 必问的主要 competitor。
- 重复 case study：展示 breadth，但不改变主故事。
```

应该删掉的实验：

```text
- 做了很多但没有结论的 sweep。
- 自己赢，但任务不重要。
- 解释不清为什么出现。
- 需要一整段防御，却不支撑主 claim。
- 会引出比它解决的问题更大的问题。
```

Taste 的难点是：**不是所有正确的结果都值得展示。**  
RFdiffusion 的主文不是所有 design case 的 inventory，而是一路推到 “enzyme active site scaffolding / binder design / natural evolution” 的边界。  
Wong 的主线不是“我们训练了 GNN”，而是“explainable deep learning 找到一个 structural class，并在 mouse model 里成立”。

### 1.5 Climax 的位置

不要把最强结果埋到第 7 个 Results 子节的末尾。Nature 系论文通常在 abstract 先告诉你 climax，再在 Results 中逐步让你相信它。

- AlphaGeometry abstract 直接给 climax：  
  > "AlphaGeometry solves 25, outperforming the previous best method that only solves ten problems…"
- GenCast abstract 直接给 climax：  
  > "It has greater skill than ENS on 97.4% of 1320 targets…"
- Wong abstract 把 climax放在 s8：  
  > "one is selective against methicillin-resistant S. aureus (MRSA)…and reduces bacterial titers…"

但 Results 的顺序不一定先给 climax。常见策略：

```text
1. Fig. 1 / architecture：先让读者知道机器是什么。
2. Main benchmark：让读者相信它强。
3. Mechanism / ablation / robustness：让读者相信不是偶然。
4. Generalization / discovery / human anchor：放 climax。
5. Limitation-aware close：让读者觉得作者可信。
```

Discovery funnel 例外：可以先讲数据和模型，再逐步收紧到 payload。  
Foundation model 也例外：可以先讲 pretraining/scaling，再讲 tasks。

---

