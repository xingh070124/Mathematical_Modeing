# 10 · Voice & Register

（v4 SKILL Part IX：DeepMind / NMI / NC / NCS / 临床 voice 对比；总索引见 `../SKILL.md`）

## 12. Voice：不同子门类的“说话方式”不同

**Patron contrast**：

AlphaFold:
> "will become essential tools of modern biology."

MolE:
> "an initial step towards a foundation model for chemical property prediction."

两句话都好，但不能互换。AlphaFold 有 CASP14 + 50-year problem + field adoption；MolE 是 NC methods paper，`initial step` 是正确 register。

### 12.1 DeepMind / Nature flagship voice

特征：

```text
- 大问题：50-year problem, established open problems, human-level reasoning
- 强 benchmark：human anchor / previous best / first discovery
- 句子短而有力
- 敢用 "first", "surpass", "essential tools"，但常配 hedge
```

Anchors:

AlphaGeometry:
> "approaching the performance of an average International Mathematical Olympiad gold medallist"

FunSearch:
> "first discoveries made for established open problems using LLMs"

AlphaFold:
> "essential tools of modern biology"

RFdiffusion:
> "approach and, in some cases, surpass what natural evolution has achieved"

使用条件：你的 evidence 真能撑起 field-level claim。否则不要学腔调。

### 12.2 NMI methods voice

特征：

```text
- trust / reproducibility / evaluation-conscious
- mechanism 和 benchmark 同等重要
- 允许 analogy hook
- limitation 比 flagship 更显式
- code/demo/workflow 是 credibility signal
```

Anchors:

SemanticLens:
> "helps bridge the 'trust gap' between AI models and traditional engineered systems."

ChemCrow:
> "lack of reproducibility…under the current API-based approach…"

HINTS:
> "We exploit the weaknesses of the two approaches by combining them synergistically…"

NMI 的好 voice 不是谦卑，而是审计感强：知道风险、知道边界、知道怎么验证。

### 12.3 Nature Communications interdisciplinary voice

特征：

```text
- domain problem clear
- method sufficient, not necessarily paradigm shift
- Results 常用 method-as-subject
- experimental validation / downstream case 很重要
- language务实
```

Anchors:

DynamicBind:
> "DynamicBind unifies two conventionally separated steps…"

DRAGONFLY:
> "Crystal structure determination of the ligand-receptor complex confirms the anticipated binding mode."

MolE:
> "perform better than the best published results on 10 of the 22 ADMET…tasks"

NC voice 适合：“我解决了一个具体科学 / 工程问题，并验证充分。”

### 12.4 Nature Computational Science voice

特征：

```text
- computation and scientific domain equal weight
- numerical method / physical system / engineering application清楚
- abstract 数字密
- 常出现 theorem / operator / solver / simulation / DFT / NWP
```

Anchors:

DIMON:
> "paves the way toward the fast prediction of PDE solutions on a family of domains…"

M3GNet:
> "1578 were verified to be stable using DFT calculations."

HINTS:
> "parallel efficiency and algorithmic scalability for a wide class of PDEs…"

NCS 不喜欢 AI-only hype。AI 是 scientific computation 的工具，不是唯一主角。

### 12.5 Clinical / medical AI voice

特征：

```text
- clinical relevance + caution
- external validation, CI/IQR/P values
- limitation 明确：cohort, scanner, modality, demographic diversity
- 不轻易说 deployment-ready
```

Anchors:

MedSAM:
> "holds great potential to accelerate the advancement of new diagnostic and therapeutic tools…"

Virchow:
> "clinical-grade models in cancer pathology"

CONCH:
> "we still potentially have long way to go…"

Clinical voice 的边界：confident but governed。

### 12.5a Pure AI methodology voice（v5 新加）

区别于 §12.2 NMI methods voice：贡献对象是 **AI 本身**——training algorithm、reasoning、measurement、alignment，而不是 AI 用在某个领域的工具链。代表：DeepSeek-R1、Xiao Densing-law、Farquhar semantic-entropy、Whitelam Simmering、Oh DiscoRL、Zhou ADeLe、Muttenthaler AligNet。

特征：

```text
- conceptual noun 强：law / scale / rubric / entropy / simmering / density。
- benchmark breadth 强：cross-model / cross-time / cross-task。
- limitation 更 self-critical：correctness gap / target-validity gap (§7.2.C)。
- open release 常前置：abstract 末段或 Discussion 收尾即给 code/weights。
- 数字位置后移：abstract 不堆 data scale，强数字进 Results (§3.2.2 carve-out)。
- outlook 用 underpin / inspire / encourage / led by machines 类（§7.3 v5 新增）。
```

并不一定发在 NMI——DeepSeek-R1、DiscoRL、AligNet、Farquhar 都是 Nature 主刊；Whitelam 在 NC。要点是**贡献的对象**，不是 venue。

样例对比：

- AI-for-X voice（§12.3 NC 跨学科）："*we apply <method> to <domain> and find…*"
- Pure AI methodology voice："*we propose <new ruler / new training paradigm> and show it predicts <X> across <models / time / tasks>.*"

### 12.6 Confident vs arrogant；modest vs timid

| Bad arrogant | Better confident |
|---|---|
| "Our method revolutionizes medical AI." | "MedSAM…holds great potential to accelerate…" |
| "We solve molecular design." | "zero-shot construction of compound libraries tailored to…" |
| "This establishes universal interpretability." | "helps bridge the 'trust gap'…" |

| Bad timid | Better restrained |
|---|---|
| "Our method may possibly be useful." | "We show that <NAME> outperforms <baseline> on <benchmark>." |
| "The results seem to suggest…" | "These results show…" when evidence is direct |
| "A potential somewhat improved model…" | "an initial step towards…" when scope is real |

Taste is calibrated force.

---

