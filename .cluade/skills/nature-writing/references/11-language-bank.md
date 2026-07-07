# 11 · 语言装备

（v4 SKILL Part X：强动词 / hedge / 段间连接词 / 高复用句型；总索引见 `../SKILL.md`）

## 13. Abstract / Intro / Results 语言装备

### 13.1 强动词

```text
outperforms, surpasses, exceeds, solves
achieves, establishes, identifies, discovers
enables, empowers, facilitates, accelerates
demonstrates, validates, confirms
recovers, rescues, evades, reduces
unifies, integrates, sidesteps, scales
maps, audits, explains, aligns
democratizes, advances

# v5 新增（来自纯 AI methodology corpus）
incentivizes   # DeepSeek-R1：RL 激励推理能力涌现
unlocks        # Xiao / Zhou：把"达不到的能力"框架化
extracts       # 从 LLM 内部抽出 capability / signal
predicts       # measurement 论文常用："metric predicts X across Y"
distils        # AligNet：把 large-model knowledge 蒸到 small model
harnesses      # capability-leveraging
underpin       # infrastructure / measurement 类 outlook
```

### 13.2 Hedges

```text
may, can, could
suggest, indicate, consistent with
to our knowledge
in a majority of cases
shows potential
is expected to
likely, probably
we hope, we believe, we envision
holds great potential to
paves the way toward
opens the door to
represents an important step toward

# v5 新增（来自 alignment / safety / measurement corpus）
explicitly does not directly address <X>   # Farquhar 式诚实
modest                                      # "modest number of benchmarks"
approximately                               # 用在 trend / law claim
may underlie                                # 机制猜测
in- and out-of-distribution                 # 评估覆盖声明
a subset of                                 # 范围限定
we hope to inspire / encourage              # 早期 methodology outlook
```

Asymmetry rule：

```text
Abstract body + Results: strong verbs.
Discussion + limitation + outlook: calibrated hedges.
```

### 13.3 段间连接词

| 功能 | 词 |
|---|---|
| 加叠 | `Furthermore,` `In addition,` `Moreover,` |
| 强调 | `Notably,` `Importantly,` `Critically,` `Strikingly,` `Remarkably,` |
| 转折 | `However,` `Yet,` `Nevertheless,` `In contrast,` `By contrast,` |
| 结果 | `Consequently,` `As a result,` `Therefore,` `Thus,` |
| 意外 | `Interestingly,` `Surprisingly,` `Intriguingly,` |
| 综合 | `Together,` `Taken together,` `Collectively,` `Altogether,` `Overall,` `In sum,` |
| 推进 | `Building on this,` `Beyond <X>,` `We next asked,` `We then …,` `Next,` |
| 对比定向 | `Unlike <prior>,` `Contrary to,` |

Taste warning: 不要每段都用连接词开头。连续 `Furthermore / Moreover / In addition` 是 checklist 味。

### 13.4 高复用句型

```text
To <verb>, we <method>. We found that <result> (Fig. <X>).

<NAME> <verb> <object> with <metric>=X.XX (<test>, P<X, n=<N>), <X.X-fold> over <baseline>.

Although <prior X>, <NAME> <does Y>; this <enables/suggests> <Z>.

To rule out <alternative explanation>, we <control>, finding <result>.

Together, these results show that <NAME> <bounded general claim>.

# v5 新增（measurement / evaluation 风）
Averaged across <N combinations of tasks and models>, <method> achieves <metric>, with stable performance across <families/scales>.

Our method does not directly address <systematic failure mode>, where <reason>.

We provide <evaluator/scale/rubric> as <ruler/standard> for <community/regulator>.
```

---

