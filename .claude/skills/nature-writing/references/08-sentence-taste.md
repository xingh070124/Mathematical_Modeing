# 08 · Sentence-Level Taste

（v4 SKILL Part VII：memorable sentences、rhythm、negative space；总索引见 `../SKILL.md`）

## 8. Memorable sentences：好句子为什么会落地

这一节不是让你模仿句子，而是让你识别“句子为什么有力”。

### 8.1 RFdiffusion：宏大但有 hedge

> "should enable de novo protein design to achieve still higher levels of complexity, to approach and, in some cases, surpass what natural evolution has achieved."

Move:
- `should enable` 是 hedge。
- `approach and, in some cases, surpass` 先降后升。
- `what natural evolution has achieved` 是最高参照物。
- 这句话敢大，因为前文有 experimental characterization、cryoEM、binder design 等证据。

Lesson: 宏大句要带刹车。`in some cases` 是刹车。

### 8.2 Wong：历史 anchor

> "This challenge has manifested in the 38-year interval between the introduction of the fluoroquinolone class of antibiotics in 1962 and the next new structural class, the oxazolidinones, in 2000."

Move:
- 不是说 “antibiotic discovery is slow”。
- 用 `38-year interval` 让 slow 可见。
- 1962 / 2000 给句子以历史重量。
- 这句出现在 Discussion，不在 abstract；它是 re-framing，不是开场炫耀。

Lesson: 能用时间、数量、历史事实说的，不要用形容词。

### 8.3 FunSearch：paradox hook

> "Many problems in mathematical sciences are 'easy to evaluate,' despite being typically 'hard to solve.'"

Move:
- `easy` / `hard` 对称。
- evaluate / solve 正好对应 FunSearch 的 evaluator + search。
- 读者读完这句就理解方法为什么存在。

Lesson: 最好的 hook 不是背景，而是方法的逻辑种子。

### 8.4 SemanticLens：跨工程类比

> "Unlike human-engineered systems such as aeroplanes, where each component's role and dependencies are well understood, the inner workings of AI models remain largely opaque…"

Move:
- aeroplane 是具体物。
- `component's role and dependencies` 精准指向 interpretability。
- `remain largely opaque` 是 gap。
- 类比不是装饰；它定义 evaluation standard。

Lesson: 类比要导出评价标准，否则别用。

### 8.5 AlphaFold：open problem framing

> "Predicting the three-dimensional structure that a protein will adopt…has been an important open research problem for more than 50 years."

Move:
- 先定义 task。
- `open research problem` 给学术状态。
- `more than 50 years` 给时间尺度。
- 后文 “first computational method” 因此成立。

Lesson: 老问题不要只说 old。说它卡了多久、卡在哪里。

### 8.6 AlphaGeometry：negative definition

> "sidesteps the need for human demonstrations by synthesizing millions of theorems and proofs…"

Move:
- `sidesteps` 比 `reduces` 更有动作感。
- `human demonstrations` 是 bottleneck。
- `synthesizing millions…` 是 mechanism。
- 一句同时说 gap、mechanism、scale。

Lesson: 如果贡献是取消一个传统依赖，把 “without / sidesteps / no need for” 写到前面。

### 8.7 GenCast：数字节奏

> "15-day global forecasts, at 12-hour steps and 0.25 degree latitude-longitude resolution, for over 80 surface and atmospheric variables, in 8 minutes."

Move:
- 从 forecast horizon → temporal step → spatial resolution → variables → runtime。
- 数字顺序符合任务直觉。
- 句尾 `in 8 minutes` 是 punchline。

Lesson: 数字的顺序就是节奏。把最惊人的效率数字放句尾。

### 8.8 GNoME：civilizational scale

> "Our work represents an order-of-magnitude expansion in stable materials known to humanity."

Move:
- `order-of-magnitude expansion` 是科学尺度。
- `known to humanity` 是文明尺度。
- 句子短，动词普通，名词强。

Lesson: 大话不一定靠大形容词。强 noun phrase 更有力。

### 8.9 SyntheMol：two-gap compression

> "Property prediction models…scale poorly…"  
> "Generative models…generate molecules that are challenging to synthesize."

Move:
- 两句平行。
- 每句一个 prior paradigm，一个 fatal flaw。
- 之后 "Here, we introduce SyntheMol…" 变成自然解。

Lesson: 如果你要 synthesize two paradigms，先让读者感到两边都不够。

### 8.10 ProteinMPNN：comparison with hardware

> "1.2 sec vs 258.8 sec on a single CPU for a 100 residue protein"

Move:
- 不是 “fast”。
- `single CPU` 防止读者怀疑 hardware 不公平。
- `100 residue protein` 防止 task size 模糊。

Lesson: efficiency claim 必须带 hardware + task size。

### 8.11 Whitelam：paradigm-rebuttal with brake（v5 新加）

> "merely 'good enough', but which, paradoxically, outperforms leading optimization-based approaches"

Move:
- `merely` 主动降低姿态——"我们没追求极致"。
- `'good enough'` 引号让读者注意这是反直觉。
- `paradoxically` 制造张力，明示这是 unintuitive claim。
- `outperforms leading optimization-based approaches` 紧接给反差的具体方向——不是 vague "competitive"。

Lesson: 反驳 dominant paradigm 时，**先把反直觉 claim 写得让人一愣，再用 Results 把它压实**。如果你只敢写一半（"comparable to optimization"），paradox 没抓住；如果你写过头（"completely supersedes optimization"），reviewer 立刻 sneer。Whitelam 的 brake 在 `merely` 和 `paradoxically` 这两个词上——它们提示读者：作者知道这听起来像吹牛，所以才用低姿态对冲。

**慎用警告**：这是单例（`extracts/07-ai-methods.md` Paper 3 一篇）。除非你的工作真的跨多个 setting 反驳了主流范式，否则 paradigm-rebuttal 进 §13 antipatterns 的 over-reach。详见 `references/04-intro.md` §4.2 Technical paradox row 末段警告。

---

## 9. Rhythm and economy：句子要会呼吸

### 9.1 Read-aloud test

每段读出声，标记三处：

```text
1. 你在哪个词停顿？
2. 哪句话读完没有落点？
3. 哪个 noun phrase 超过 12 个词？
```

如果一句话读到中间忘了主语，重写。

### 9.2 Sentence length variance

Nature 系好段落通常不是全短句，也不是全长句。它常用：

```text
短句：给 claim。
长句：装 mechanism / evidence。
短句：收束。
```

例：

FunSearch hook 是短句。  
后面的 mechanism 可以更长。  
Discussion boundary 再用列表式短项。

模板：

```text
<Short claim>. 
<Longer sentence with mechanism, dataset, and comparison>. 
<Short synthesis>.
```

### 9.3 Verb-led prose beats nominalization

弱：

```text
The evaluation of the robustness of the model was performed.
The improvement of generalization was achieved.
```

强：

```text
We evaluated robustness by …
<NAME> improved generalization across …
```

Corpus 强动词：

```text
outperforms
surpasses
solves
discovers
enables
unifies
sidesteps
rescues
evades
reduces
generates
maps
audits
democratizes
```

ProteinMPNN 用 `rescues`：
> "rescues previously failed designs…"

Wong 用 `evades` / `reduces`：
> "evades substantial resistance, and reduces bacterial titers…"

这些动词比 “shows good performance” 强得多。

### 9.4 Name your noun

不要写：

```text
this problem
this approach
this issue
these results
```

太多。

写具体：

```text
the data-scarcity bottleneck
the rigid-protein assumption
the evaluator requirement
the synthetic-tractability constraint
the clinical-grade generalization claim
```

SemanticLens 不说 “this issue”。它说：
> "trust gap"

Foldseek 不说 “this is slow”。它说：
> "searching these databases is becoming a bottleneck"

### 9.5 One strong adjective beats three weak ones

弱：

```text
a powerful, efficient, robust, novel and general framework
```

强：

```text
a universal explanation method
a probabilistic weather model
a deep-metric-learning foundation model
a theorem prover for Euclidean plane geometry
```

Nature 系句子的力量通常来自 noun，而不是 adjective pile。

### 9.6 Let the number do the talking

弱：

```text
Our model is extremely fast and very accurate.
```

强：

Foldseek:
> "decreases computation times by four to five orders of magnitude…"

GenCast:
> "in 8 minutes"

AlphaFold:
> "0.96 Å r.m.s.d.₉₅"

如果数字足够强，不要再加 `extremely`。

### 9.7 Cadence patterns you can reuse

#### Pattern A — contrast + pivot

```text
Although <prior strength>, <limitation>.
Here we <verb> <NAME>, which <mechanism>.
```

#### Pattern B — scope + result + anchor

```text
Across <N tasks / cohorts / targets>, <NAME> <achieves> <metric>, <delta> over <baseline>.
```

#### Pattern C — claim + mechanism + implication

```text
<NAME> <does X> by <mechanism>, enabling <Y>.
```

#### Pattern D — restraint close

```text
These results suggest that <NAME> can <bounded capability>, while <limitation> remains <future challenge>.
```

---

## 10. Negative space：不说什么，和说什么一样重要

**Patron sentence** — CONCH closing:
> "These observations suggest we still potentially have long way to go before achieving goal of building foundation model capable of truly universal zero-shot recognition."

这句话克制到罕见。它没有毁掉论文，反而让作者可信。

### 10.1 什么时候该省略

```text
- 结果已经由数字清楚表达时，省略 "remarkably / dramatically"。
- baseline 太弱时，不要把胜利写成 field-level breakthrough。
- 次要实验方向不一致时，不要硬解释成支持主 claim。
- 没有外部验证时，不要写 clinical deployment readiness。
- 没有开源时，不要写 democratizes。
```

### 10.2 Restraint moves

#### A. Declarative-with-no-adjectives

```text
We benchmarked 16 integration methods…
We introduce UNI…
We present Virchow…
```

数字和对象承担力量。

#### B. Hedge only the scope, not the result

强结果：
> "AlphaGeometry solves 25…"

Hedge scope：
> "approaching the performance of…"

#### C. Limitation as boundary

FunSearch:
> "currently works best for problems having the following characteristics…"

#### D. Resource instead of hype

Pai:
> "We share our foundation model and reproducible workflows…"

### 10.3 声音太吵的信号

```text
remarkably / significantly / substantially / dramatically
```

如果一页里出现太多，句子会像 grant proposal。  
保留一两个真正需要 emphasis 的地方。

DynamicBind abstract 用：
> "Remarkably, it demonstrates state-of-the-art performance…"

可用，因为前面是 dynamic docking 的技术难点。  
但如果每个结果都 “remarkable”，就没有一个 remarkable。

---

