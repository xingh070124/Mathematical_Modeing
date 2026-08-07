# 06 · Methods + 复现性

（v4 SKILL Part V；总索引见 `../SKILL.md`）

## 6. Methods：AI 论文的隐形评分项

**Patron sentence** — ChemCrow limitation:  
> "One major challenge is the lack of reproducibility of individual results under the current API-based approach to LLMs, as closed-source models provide limited control."

这句话好，因为它主动说出 reviewer 最担心的事。尤其是 LLM-agent 论文，复现性不是附录问题，是可信度核心。

### 6.1 Methods 标准子目

根据论文类型组合：

```text
Datasets and preprocessing
  - 来源、版本、发布年份
  - train/val/test split 比例和切分原则
  - leakage 检查：temporal / patient-level / protein-family / by-cluster split
  - 排除标准、缺失值处理

Model architecture
  - 主架构 + 关键超参
  - 与 Fig. 1 schematic 对应
  - 与最相关 prior work 的差异：diff，不是 redo

Training
  - optimizer, learning rate, schedule, batch size, epochs
  - pretraining vs fine-tuning 流程
  - GPU 型号 + 数量 + 训练时长 + peak memory
  - random seeds
  - mixed precision / distributed training details

Evaluation
  - metric 定义，尤其 micro/macro F1、AUROC、AUPRC、top-k、calibration
  - baselines：版本、超参、是否复现或引用原文
  - statistical tests：paired t-test / permutation / bootstrap CI
  - external validation / held-out cohort

Ethics / IRB / governance
  - IRB approval
  - consent
  - PHI / PII de-identification
  - data-use restrictions

Data / Code / Model availability
  - repository URL
  - DOI / Zenodo
  - license
  - pretrained weights
  - inference script
  - minimum hardware
```

### 6.2 LLM-agent / API-driven 论文额外清单

**主文 / SI 分工**（来自 `extracts/07-ai-methods.md` 8 篇 2024–2026 NMI/Nature/NC AI 方法论文的共同惯例）：

- **主文**：报告 model family、version class（GPT-4 vs Claude vs Llama-2 70B）、evaluator 类型、task protocol 概览、关键实验结论。
- **SI（必须完整）**：完整 prompt（system / user / few-shot examples 全部）、API/model 精确版本（gpt-4-0125-preview）、access date、访问期间模型是否切换、decoding parameters（temperature / top-p / max_tokens / stop sequences）、tool list + schema、retry / fallback policy、safety filter 版本与触发率。
- **强约定**：主文若声明 "reproducible" / "agentic" / "API-based" / "deployed"，**必须显式指向 SI**——一句 "see SI section X for full prompts and decoding parameters" 是底线。否则进 §13 antipatterns 的 "SI black hole"。

完整字段清单（按上面分工切分到主文或 SI）：

```text
- 模型版本：例如 gpt-4-0125-preview，而不是只写 GPT-4
- API 访问日期
- 访问期间模型是否变化
- system / user / few-shot prompt 完整模板
- decoding parameters：temperature, top-p, max_tokens, stop sequences
- tool list + tool description schema
- retry / fallback policy
- refusal / hallucination / invalid output 处理
- evaluator 是人、模型、规则，还是混合
- LLM-as-judge 的局限
- safety filter / moderation 版本和触发率
```

ChemCrow 在 abstract 里明说：
> "including both LLM and expert assessments"

这很好，因为它没有把 LLM judge 当作唯一 truth source。

### 6.3 复现性三处呼应

#### A. Abstract / title-adjacent artifact

SemanticLens abstract：
> "We provide code for SemanticLens on [GitHub] and a demo on [link]."

适合 NMI methods / interpretability / tooling。

#### B. Discussion close

Pai et al.:
> "We share our foundation model and reproducible workflows so that more studies can investigate our methods, determine their generalizability and incorporate them into their research studies."

#### C. Availability 独立段

结构模板：

```text
Data availability:
<raw data> are available at <repository/accession/license>.
<restricted data> can be accessed under <condition>.

Code availability:
The source code is available at <GitHub/Zenodo> under <license>.
The pretrained weights are available at <repository> with DOI <id>.

Model availability:
Inference scripts and example notebooks are provided.
Minimum hardware for reproducing main inference results is <hardware>.
```

### 6.4 AI 论文最常漏报的复现项

```text
1. Random seed 数与方差
2. Compute cost：GPU hours, peak memory, inference latency
3. Data leakage 检查
4. Baseline fairness
5. Hyperparameter search budget
6. Prompt / API version / decoding params / SI pointer（"详见 SI 第 X 节"——主文不放但必须指向）
7. Dataset license
8. External validation split
9. Negative controls
10. Failure cases
```

Taste rule: Methods 不是把所有细节塞进去，而是让 reviewer 找不到“你可能作弊 / 偶然 / 不可复现”的口子。

### 6.5 Methods 的写法也要有 taste

Bad:
> "The model was trained with AdamW. The learning rate was 1e-4. The batch size was 256. The model was trained for 100 epochs."

Better template:
> "We trained <NAME> with AdamW for 100 epochs using a batch size of 256 and a peak learning rate of 1e-4, selected on the validation set. All reported results are averaged over five random seeds."

What changed: 把 list 合成可读句，并补上 selection / seeds。Methods 也可以有节奏。

---

