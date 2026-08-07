# 01 · Fig. 1 Schematic 的六种主导构图

（FIGURE-SKILL Part I §1；总索引见 `../FIGURE-SKILL.md`）

## 1. Fig. 1 schematic 的六种主导构图

**Patron sentence** — RFdiffusion (extracts/02-protein.md):
> "As shown in Fig. 2a–c and Supplementary Fig. 3c,d, starting from random noise,
> RFdiffusion can readily generate elaborate protein structures…"

写作 call-out 用 "as shown in Fig. 2a–c"，意味着 Fig. 2a–c 必须能独立支撑 "from random
noise to elaborate structures" 这条 claim 的视觉证据。schematic 不是装饰——它和正文
claim 是 1:1 锁死的。SKILL.md §5.4 的 figure call-out 句法在这里换成对偶要求：
**call-out 句中的每个名词必须在 schematic 中找得到 visual anchor**。

下面六种是 36 篇 corpus 里 Fig. 1 schematic 的主导构图。每篇通常用 1 种主构图 +
最多 1 种副构图。把 6 种全塞进一张图，是新手最常见的死法。

### 1.1 数据流型（data-flow / pipeline）

**用途**：方法是端到端 pipeline，输入输出明确，中间几个标志性 module。
**Layout**：单向箭头链（左→右或上→下）；每个 box 是 module 的最小可识别图标，不是文字框；
末端是 task gallery / output examples。

**Corpus 实例**：
- AlphaFold Fig. 1：sequence → MSA + templates → Evoformer → Structure module → 3D structure；
  每个 module 用一种几何隐喻（grid / triangle / atom）。
- DynamicBind (extracts/04-drug.md)："As illustrated in Fig. 1a, at each step, the features and
  the coordinates of the protein and the ligand are fed into an SE(3)-equivariant interaction
  module" — 单向数据流，step 是迭代的。
- Tangram (extracts/01-singlecell.md)：scRNA-seq + spatial → "puzzle pieces" alignment →
  spatial expression / cell type → spatial reconstruction。

**设计要点**：
- 箭头只表示数据流，不表示循环 / loss / gradient。
- module box 高度对齐，宽度可变；不要让最重要的 module 最小。
- 末端 output 给读者"啊原来是做这个"的解释力——这往往比中间 architecture 更值钱。

**常见错误**：
- 把 loss function 也画进数据流——`L_recon + λ L_KL` 进 box，读者立刻迷路。损失函数留给
  Fig. 2 或 Methods。
- 箭头双向 / 交叉 / 回环——读者无法判断先后。
- 每个 module 都用 "MLP" "Transformer" 文字框——失去 schematic 的意义。

### 1.2 模块组装型（modular assembly）

**用途**：方法是若干已知组件的非平凡组合；contribution 是组合本身，不是任一单一 module。
**Layout**：方块拼图感，组件清楚分区，靠 shared embedding / shared weights 连线；
通常近似正方形布局。

**Corpus 实例**：
- ChemCrow (extracts/06-ml.md)：LLM 中心 + 多个 tool node 围成放射 / 环状。
- SyntheMol (extracts/04-drug.md)：building blocks bank + reaction templates + MCTS search +
  property predictor。每个组件是一个 panel 内的小区。
- CONCH (extracts/05-medical.md)：image encoder + text encoder + contrastive loss——典型
  CLIP-style modular schematic。

**设计要点**：
- 组件之间的"接口"画明确：embedding 维度、shared weight、frozen vs trainable 用 icon 区分。
- frozen 组件用淡灰、trainable 用品牌色——读者一眼判断"我能微调哪部分"。
- 不要让组件大小代表它的"重要性"，会误导。

**常见错误**：
- 所有 module 都满色——读者不知道你的 contribution 在哪。
- 模块组装画成 6×4 网格——太工整反而失焦。

### 1.3 漏斗型（discovery funnel）

**用途**：discovery paper（Wong 抗生素、GNoME、SyntheMol）；大候选集层层筛选到小验证集。
**Layout**：上宽下窄梯形；每级标 N（候选数），级间标过滤条件；末端是"我们真的合成了 X 个"
的实物 / 显微 / 结构示意。

**Corpus 实例**：
- Wong 2024 antibiotics (extracts/04-drug.md) 隐含 funnel：39,312 → 12,076,365（生成）→
  283（合成）→ 1 strong MRSA candidate。
- M3GNet (extracts/03-physics.md)：31M hypothetical → 1,578 verified stable。
- FunSearch caps set discovery (extracts/06-ml.md): "Using this approach we discovered cap sets
  of sizes shown in Figure 4 (a)" — 末端是离散数学 object 的可视化。

**设计要点**：
- 每一级 N 必须显眼（10pt 以上），是漏斗的脊梁。
- 过滤条件用一行短句而不是大段文字（"in vivo activity"，"DFT-verified stable"）。
- 末端的 "1 / 几个" payload 要有质感——分子结构、晶体结构、生物图像，而不是数字。

**常见错误**：
- 漏斗画对称三角形但每级 N 比例失真——读者会按面积估读，所以面积比应大致对应 log10(N)
  比例。
- 漏斗每级颜色都不同——读者以为级与级之间有类型区别。统一品牌色、用宽度表达就够。

### 1.4 任务地图型（task gallery / capability map）

**用途**：foundation model / benchmark paper；contribution 是"一个模型做 N 件事"。
**Layout**：中心模型 + 放射状 task panel；或 top: 模型 / bottom: task 网格。
每个 task panel 是该任务的最小可识别 example。

**Corpus 实例**：
- ESMFold Fig. 1 (extracts/02-protein.md)：language model 中心 + 结构预测 task。
- UNI / Virchow / CONCH (extracts/05-medical.md)：foundation model + 14+ histology
  benchmark task。
- ChemCrow Fig. 1 + 2 (extracts/06-ml.md)：LLM + tool gallery + 化学任务案例。

**设计要点**：
- task panel 数量在 6–14 之间是 sweet spot。少于 6 不够"foundation"，多于 14 视觉过载。
- 每个 task 用 1 个 icon + 1 行 label。不要在 Fig. 1 里塞数字结果——数字进 Fig. 2 / 3。
- 中心模型用品牌色与 logo style，task 用统一中性色，避免和模型抢戏。

**常见错误**：
- task 之间难度 / 重要性差异大但视觉同等——给最强 task 微微大一格 / 加 highlight。
- task panel 用 screenshot 而不是 icon——视觉密度爆炸。

### 1.5 双轴 / before-after 对比型

**用途**：bottleneck-broken 故事（SKILL.md §1.1 shape A）；左轴"以前"，右轴"现在"。
**Layout**：垂直 / 横向分线；左右 layout 对称但 visual emphasis 不对称（右侧饱和）；
末端带 quantitative anchor（before AUC vs after AUC）。

**Corpus 实例**：
- AlphaFold (extracts/02-protein.md): "structural coverage is bottlenecked by the months to
  years of painstaking effort" — Fig. 1 概念上是 wet-lab pipeline vs computational pipeline。
- Foldseek (extracts/02-protein.md)：sequence search 慢 vs structure search 快；左老右新。
- GraphCast (extracts/06-ml.md)：NWP 物理模拟 vs ML 预测，6 小时 / 1 分钟。

**设计要点**：
- 左侧"以前"用低饱和灰阶 + 真实工具图（pipette / cluster icon）；右侧用品牌色。
- 中间分线不画显眼框，靠空白留白即可。
- 量级差异（months → minutes）必须有数字 anchor，否则只是修辞。

**常见错误**：
- 左右两侧字号 / line weight 不一致——读者会觉得是两张拼起来的图。
- 不留量级 anchor，画完读者不知道差距是 2× 还是 1000×。

### 1.6 时间线 / 演化型（timeline / iteration）

**用途**：agent / RL / iterative refinement / search；时间或迭代步是核心维度。
**Layout**：左→右时间轴；每个时间点取 snapshot；snapshot 间用淡箭头连接；末端 snapshot 高亮。

**Corpus 实例**：
- DynamicBind (extracts/04-drug.md): "at each step, the features and the coordinates… are
  fed into an SE(3)-equivariant interaction module" — 隐含时间步轴。
- RFdiffusion (extracts/02-protein.md)：从随机噪声到 elaborate structure 的去噪轨迹。
- FunSearch program search timeline (extracts/06-ml.md)：generation 0 → N → discovery moment。

**设计要点**：
- 时间轴要有刻度（step / iteration / wall-clock time）；不要只画箭头。
- snapshot 之间的视觉差异要可见——若几乎一样，只画首末两点 + 一句"intermediate omitted"。
- 末端 snapshot 配 quantitative tag（loss / reward / score / structure quality）。

**常见错误**：
- 等距取 snapshot 但视觉变化集中在前几步——后段空。改成 log-spaced 或在首段密集采样。
- 时间方向不一致——上一行从左到右，下一行从右到左，读者迷失。

### 1.7 其他识别到的辅助构图

corpus 中还出现作为副构图（几乎不单独当 Fig. 1 主图）：**Hierarchy / tree**（Geneformer 用过）、
**Geographic / map**（MedPerf "32 sites across six continents" 落在地图上）、
**Network graph**（节点超过 ~30 就糊，慎用）。副构图占 Fig. 1 不超过 1/4 面积；喧宾夺主就改成 Fig. 2。

---

