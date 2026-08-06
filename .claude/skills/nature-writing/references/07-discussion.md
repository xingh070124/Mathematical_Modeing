# 07 · Discussion / Limitation / Outlook

（v4 SKILL Part VI；总索引见 `../SKILL.md`）

## 7. Discussion：收束，不是复读 abstract

**Patron sentence** — Wong Discussion opening:  
> "The need to discover novel structural classes of antibiotics is pressing given the antibiotic resistance crisis. This challenge has manifested in the 38-year interval between the introduction of the fluoroquinolone class of antibiotics in 1962 and the next new structural class, the oxazolidinones, in 2000."

这两句好，因为 Discussion 没有机械说 “In this study, we…”。它用历史间隔重新加重贡献。

### 7.1 Discussion 开句两条路径

#### A. Restate-finding

最常用，安全。

- GenCast:  
  > "We have presented GenCast, a new approach for global medium range ensemble weather forecasting…"
- UNI:  
  > "In this study, we demonstrate the versatility of UNI…"
- scIB:  
  > "We benchmarked 16 integration methods…"
- ChemCrow:  
  > "In this study, we have demonstrated the development of ChemCrow…"
- DynamicBind:  
  > "DynamicBind unifies two conventionally separated steps…"

#### B. Frame-in-field

更有味道，适合旗舰 / 应用 / clinical。

- CONCH:  
  > "The gold standard for diagnosis of many diseases remains examination of tissue by a pathologist."
- Ferber:  
  > "Foundation models have demonstrated substantial promise in medical image processing."
- Wong historical anchor 如上。

Taste rule: 如果你的 Results 已经很强，Discussion 可以稍微后退一步，把领域重新框起来。  
如果你的 Results 复杂，Discussion 第一段先复述贡献，别玩花样。

### 7.2 Limitation：具体、短、可被尊重

两种写法。

#### A. 单句直陈 + remedy / inversion

GraphCast:
> "One key limitation of our approach is in how uncertainty is handled."

DynamicBind:
> "still presents opportunities for improvement, especially in enhancing its ability to generalize to proteins with low sequence homology…"

接着给 remedy：
> "By adopting a self-distillation approach analogous to AlphaFold, we could augment our training set…"

DIMON 的 inversion：
> "Although one can measure the similarity/distance between domains using a metric…, this is not a prerequisite…"

#### B. 列表式 boundary

FunSearch:
> "FunSearch currently works best for problems having the following characteristics: a) availability of an efficient evaluator; b) a 'rich' scoring feedback…; c) ability to provide a skeleton…"

Pai et al. 使用 clinical-paper 风格：retrospective design、demographic diversity、pretraining corpus、clinical metadata、interpretability。

#### C. Correctness / target-validity gap（v5 新加，subgenre 倾向）

适用：**hallucination detection / alignment / AI evaluation / human-supervision** 类论文——你的方法依赖某个 evaluator 或 supervision target，而那个 ruler 本身可能不可靠。承认这一点是诚信信号，不是软弱。

Farquhar (Nature 2024，semantic entropy)：
> "explicitly does not directly address … the systematic failure mode of confidently wrong"

Muttenthaler (Nature 2025，AligNet)，承认 supervision target 本身有问题：
> "human judgment is full of flaws"

Zhou (Nature 2026，ADeLe)：承认 evidence-scope gap：
> "modest number of benchmarks … limiting empirical evidence"

写法模板：

```
Our method does not directly address <systematic failure mode>, where <reason>.
[或]
The supervision target / evaluator we use is itself imperfect: <specific flaw>.
```

**不要**把这条当成所有论文都该有的 limitation——它只在你的 contribution 与"评估 / 对齐 / 监督 / 检测"本身相关时成立。AI-for-X 应用论文不必照搬。

Taste rule: limitation 不是忏悔，也不是藏起来。它是你告诉 reviewer：**我知道边界在哪里。**

### 7.3 Outlook 动词的等级

| Outlook phrase | 适用强度 | Corpus anchor | 何时不要用 |
|---|---|---|---|
| `shows potential to` | pilot / early application | DynamicBind: "shows potential in accelerating…" | 已有强验证时太软 |
| `represents an important step toward` | method advances clear，但未改写领域 | GenCast: "represents an important step forward…" | 小 incremental SOTA 不配 |
| `paves the way toward` | 新路线可被他人扩展 | DIMON: "paves the way toward the fast prediction…" | 只有一个 dataset 赢了不能用 |
| `opens the door to` | 解除一个规模 / compute / access 限制 | GenCast: "opening the door to…orders of magnitude larger ensembles" | 没有明确 door 被打开 |
| `democratizes` | access 门槛确实降低 | Geneformer / Ferber 用于 broad access | 模型昂贵且不公开时不要用 |
| `essential tools of modern biology` | field-level adoption 级别 | AlphaFold: "will become essential tools of modern biology" | 除非你真的是 AlphaFold 级别 |
| `surpass what natural evolution has achieved` | boundary-redrawing flagship | RFdiffusion | 几乎不要模仿，除非证据非常强 |
| `we hope to inspire / encourage` | early methodology / community exchange（v5） | Farquhar / Zhou 类 measurement methodology | 用在 mature application 上显得软弱 |
| `underpin` | evaluation / measurement infrastructure with deployment relevance（v5） | Zhou ADeLe 类 measurement papers | 没有真的成为 infra 时不要用 |
| `led by machines` / 机器接管动词类 | AI autonomy flagship 级别（v5） | Oh DiscoRL: "led by machines" | **极高风险**——只有真有跨任务 emergent 证据时才用，否则进 §13 over-reach |

### 7.4 Overclaim boundary：什么时候能说 "paves the way"

`paves the way` 至少需要满足两条：

```text
1. 解决的不只是一个 benchmark，而是一类 bottleneck。
2. 你展示了至少一个下游方向，说明别人能沿着这条路走。
3. 方法 / 数据 / 权重 / workflow 可用，或机制清楚到可复用。
4. 你承认了边界，没有假装 universal。
```

DIMON 可说：
> "paves the way toward the fast prediction of PDE solutions on a family of domains…"

因为它定义的是 PDE solution operators on domain families，不是单个 toy problem。

SyntheMol 可说 utility，因为它 synthesize + validate：
> "This work demonstrates the utility of generative AI to design structurally novel, synthetically tractable, and effective small molecule antibiotic candidates."

如果你只有：
```text
We improve F1 by 1.7% on Dataset A.
```
不要写：
```text
This paves the way for revolutionizing healthcare.
```

### 7.5 Closing 的几种方式

#### Resource / community

AlphaMissense:
> "As a resource to the community, we provide a database of predictions…"

Pai:
> "We share our foundation model and reproducible workflows…"

MedPerf:
> "we invite participation at ref. [26]."

#### Vision / next chapter

GenCast:
> "helps open the next chapter in operational weather forecasting…"

FunSearch:
> "we envision that automatically-tailored algorithms will soon become common practice…"

#### Humble boundary

CONCH:
> "we still potentially have long way to go before achieving goal of building foundation model capable of truly universal zero-shot recognition."

SCimilarity:
> "may suggest that it can perform well for other tasks, but these need to be assessed in future studies."

Taste rule: strong paper can end humbly. Weak paper often ends loudly.

### 7.6 Discussion before / after

**Pair 19 — limitation as apology → limitation as boundary**

Bad template:
> "Our method has limitations and future work will address them."

Better, FunSearch:
> "FunSearch currently works best for problems having the following characteristics: a) availability of an efficient evaluator; b) a 'rich' scoring feedback…; c) ability to provide a skeleton…"

What changed: boundary 被命名，reader 可以判断 applicability。

**Pair 20 — vague future work → concrete remedy**

Bad template:
> "Future work will improve generalization."

Better, DynamicBind:
> "By adopting a self-distillation approach analogous to AlphaFold, we could augment our training set…"

What changed: remedy 有机制，不是愿望。

**Pair 21 — loud closing → restrained resource closing**

Bad template:
> "Our model will revolutionize medical AI."

Better, Pai:
> "We share our foundation model and reproducible workflows so that more studies can investigate our methods…"

What changed: 贡献通过可复用资源体现，不靠夸张动词。

**Pair 22 — underpowered result 过度展望 → scope-aware step**

Bad template:
> "This work establishes a universal foundation model for chemistry."

Better, MolE:
> "Overall we consider this work as an initial step towards a foundation model for chemical property prediction."

What changed: `initial step` 保护可信度；化学 foundation model 这个愿景保留，但不冒进。

---

