# 09 · Reviewer Modeling

（v4 SKILL Part VIII：5-pass harsh referee protocol；总索引见 `../SKILL.md`）

## 11. 把最严厉的 reviewer 放进你的草稿

**Patron sentence** — GraphCast:
> "Rather our work should be interpreted as evidence that MLWP is able to meet the challenges of real-world forecasting problems, and has potential to complement and improve the current best methods."

这句话会让 reviewer 点头，因为它没有说 ML replaces NWP。它说 complement and improve。作者提前避免 overclaim。

### 11.1 Harsh referee protocol

每一轮自审只戴一顶帽子。不要混着看。

#### Pass 1 — Editor scan, 10 minutes

问题：

```text
1. 标题让我知道故事了吗？
2. Abstract s4 是否一句说清 contribution？
3. s6 是否有 named benchmark / baseline / human anchor？
4. 这篇是否适合 NMI / NC / NCS / Nature？
5. 有没有一句让我愿意送审？
```

危险信号：

```text
- abstract 读完只知道用了 transformer，不知道发现什么。
- title 像 arXiv workshop。
- contribution 像 engineering integration。
```

#### Pass 2 — Domain reviewer

问题：

```text
1. 你打的 gap 是真的 gap，还是 straw man？
2. baseline 是领域认可的强 baseline 吗？
3. dataset split 有没有 leakage？
4. 你的 hard cases 真 hard 吗？
5. 你有没有忽略 obvious prior work？
6. （v5）如果你的方法依赖 evaluator / supervision target / human label / metric：这把 ruler 本身可信吗？
   "Is the evaluator / supervision target itself valid?" 
   AI evaluation / alignment / hallucination detection / measurement 论文必查。
   参 references/07-discussion.md §7.2.C correctness-gap 模板。
```

在 intro gap 段旁边写 reviewer 可能说的话：

```text
"X already did this."
"This benchmark is not accepted."
"This is not the right comparison."
"The task is toy."
```

然后在正文提前处理。

#### Pass 3 — ML / statistics reviewer

问题：

```text
1. 单 seed?
2. random split 是否泄漏？
3. P 值 / CI / IQR 是否合理？
4. hyperparameter search 是否公平？
5. baseline 是否同样调参？
6. compute budget 是否相当？
7. error bars 是否显示方差？
```

如果你没法多 seed，写替代信号：

```text
- bootstrap CI
- external cohort
- repeated split
- prospective validation
- sensitivity analysis
- calibration
```

#### Pass 4 — Reproducibility reviewer

问题：

```text
1. 我能不能重跑 main table？
2. code / weights / data 是否可得？
3. API 模型版本是否可追踪？
4. prompt 是否完整？
5. preprocessing 是否足够具体？
```

ChemCrow 式 API-based work 尤其要主动承认：
> "closed-source models provide limited control."

#### Pass 5 — Skeptical sentence reviewer

逐段标记：

```text
SNEER: reviewer 会冷笑的句子。
NOD: reviewer 会点头的句子。
ASK: reviewer 会写 margin question 的句子。
CUT: 不服务主 story 的句子。
```

SNEER 常见来源：

```text
- "revolutionary"
- "universal" 但只测 3 个 dataset
- "democratizes" 但不开源 / 高算力
- "clinical-grade" 但无外部 cohort
- "interpretable" 但只有 saliency map
```

### 11.2 Concede vs anticipate

| 情况 | 做法 |
|---|---|
| reviewer 一定会发现 | 正文 anticipates |
| limitation 不影响主 claim | Discussion concede |
| limitation 会影响主 claim | Results 加实验 |
| limitation 暂时无法实验 | 明确 boundary，不写过强 claim |
| reviewer 可能误解方法 | Fig. 1 / Methods / first Results opener 澄清 |

例：

- GraphCast 不说 replaces NWP，而说 complement and improve。  
- FunSearch 不说 solves all math problems，而列 evaluator / rich feedback / skeleton 条件。  
- CONCH 不说 universal zero-shot，而承认还很远。  
- DynamicBind 承认 low sequence homology generalization，再给 self-distillation remedy。

### 11.3 Reviewer exercise：每段末尾写一行 invisible answer

草稿时在每段末尾临时加一句注释：

```text
[Reviewer should believe: <one claim>.]
```

如果你写不出这一行，这段可能没有功能。  
如果连续三段的 invisible answer 相同，合并或删掉。  
如果一个 Results 子节没有 invisible answer，它不该在主文。

---

