---
name: nature-figure-design
description: |
  面向中国 AI / ML 研究者的 Nature 系 figure 设计 skill v0.2。姊妹文件是 SKILL.md（写作 v4）。
  本文件回答一个具体问题：你写得不差，但你的图为什么一眼像 arXiv 而不像 Nature？
  覆盖 Fig. 1 schematic 构图、配色、字体字号、panel 布局、数据图选型、误差棒与显著性、
  从 matplotlib 到 Illustrator 的工作流、文件格式与大小（已核实硬约束）、子门类风格差异、
  arXiv→Nature 反模式 checklist、caption 写法、rcParams / ggplot theme template。
  v0.2 已用 Nature Research Figure Guide（在线版 + final-artwork PDF）交叉验证字号、栏宽、
  DPI、颜色空间、文件格式、文件大小、字体格式、Panel letter 大小写等硬约束（见 §18）。
  Scope 限制：不教 Illustrator 操作、不教 BioRender icon library、不替代各子刊 submission guidelines。
  本 FIGURE-SKILL.md 为瘦索引：保留 §0 起手对照表、§16 quick card、§17–18 已核实硬约束 / 未核实清单、§1 routing；其余按主题拆到 `figure-references/01-fig1-schematic.md` … `12-bridge-to-writing.md`。
---

# Nature 系 figure 设计 v0.2（拆分版）
## How a Nature-quality figure is built, not just drawn

> **资料来源**：与 SKILL.md 共享 `extracts/01-singlecell.md` … `06-ml.md`（36 篇 OA 论文，
> 含 figure caption / call-out 引文）；色板基础来自 Wong 2011 *Points of View: Color blindness*,
> Nature Methods 8:441，及 Okabe & Ito (2008) Color Universal Design 同一谱系。
> **读者**：能读懂自己 matplotlib 输出但说不清"为什么不像 Nature"的中国 AI / ML 研究者。
> **范围**：本 skill 只负责把图提到 Nature 系投稿门槛；图的最后 30%（Illustrator 手感、
> icon 节制、视觉直觉）只能靠看图 / 临摹 / 反复改稿养成，参见 §13。
> **Caveat**：所有具体数字（mm 宽度、pt 字号、bleed、DPI、CMYK 政策）请以投稿当年的
> 官网 author guidelines 为准。本文件给的是 corpus 内多见的工作区间，不是 spec。
> **与写作 skill 的关系**：figure 决定 caption 节奏；caption 决定 Results 段落顺序；
> Fig. 1 是 reviewer 进入故事的门，对应 SKILL.md §1.3 "Fig. 1 的四种功能"。

---

## 0. 先记住这句话：figure 是 reviewer 第二个读到的东西

**Patron sentence** — Wong 2011, *Points of View: Color blindness*:
> "To ensure that the points are easily distinguishable, we choose a palette of colors
> that differ in lightness as well as in hue."

这句话好在哪？它没有讲 design philosophy，它只讲一个机制：颜色不能只靠 hue 区分。
8% 的男性是红绿色盲（Wong 2011），印刷转灰阶后 hue 全失。一句话就把 jet / rainbow /
matplotlib 默认 tab10 的命门点出来：它们靠 hue 分类，灰阶下全糊。

reviewer 读论文的真实顺序（编辑也是一样）：

```text
1. title
2. 第一张图（Fig. 1）
3. abstract
4. 看 figure 决定要不要继续读
5. 抽样读 Results
6. 如果还感兴趣，读 Methods
```

写作 skill 教你怎么写 1、3、5、6。这份 figure skill 教你怎么让第 2 步不掉链子。

### 0.1 Nature-quality 图与 arXiv 图的差距（corpus 观察，不是规则）

| 维度 | arXiv 默认 | Nature 系常见 |
|---|---|---|
| 颜色 | matplotlib tab10 / jet / 鲜艳 | 自家方法 1 饱和品牌色 + baseline 灰 / Wong 8 色板 |
| 字体 | DejaVu Sans / Computer Modern | Helvetica / Arial |
| 字号 | 默认 10pt 全图同字号 | panel letter 8pt bold lowercase / 其他全部 5–7pt |
| 标题 | `ax.set_title(...)` | figure 内不放 title，title 进 caption |
| 边框 | top + right spine | 只留 bottom + left |
| 图例 | inside, 默认背景 | outside / inline label / 共享 legend |
| Panel 标记 | (a) (b) 居中或在 caption | a b c 加粗，左上对齐 plot area |
| 背景 | 灰底（seaborn 默认） | 白底，no grid 或极淡 |
| Schematic | PowerPoint icon + 立体阴影 | 矢量手绘感，单色 stroke，无阴影 |
| 误差 | error bar 不说是什么 | caption 写明 mean ± SD / SE / 95% CI |

这张表本身就是 §9 反模式 checklist 的预告。

### 0.2 v0.1 的核心判断

写作 skill 教 craft 与 taste。Figure skill 区分：

- **Mechanics**：字体 / 字号 / 间距 / 矢量 / DPI——可以教，本文档教完。
- **Taste**：哪个 panel 该当 Fig. 1d、哪个 schematic 太满、哪个颜色太吵——只能靠看图、
  临摹、reviewer 反馈养成（§13）。

不要指望读完一份 doc 就画出 AlphaFold Fig. 1。读完这份 doc 你能：

- 让你的图不再因为"matplotlib 默认味"被审稿人扣 presentation 分；
- 知道哪些做法是 Nature 系强约定（违反会被 production team 打回）；
- 拥有一套 rcParams / theme，每张新图起手就在合理基线上。

---

## 1. Routing — 按任务加载 figure-references

每张图都不一样；查 1–2 个对应的细节文件即可。

### 1.1 按场景加载

| 场景 / 困境 | 主 load | 辅 load |
|---|---|---|
| 设计 Fig. 1 / overview schematic | `figure-references/01-fig1-schematic.md` | `figure-references/12-bridge-to-writing.md`（story shape ↔ Fig. 1 对应） |
| 选颜色 / 自家方法用什么色 / heatmap colormap | `figure-references/02-color.md` | — |
| 字号字体不知道怎么定 / Panel 字母怎么放 | `figure-references/03-typography-layout.md` | — |
| 数据该用 bar 还是 box 还是 violin | `figure-references/04-chart-selection.md` | `figure-references/05-stats-in-figure.md` |
| error bar / P 值 / N 怎么标 | `figure-references/05-stats-in-figure.md` | — |
| matplotlib 出图 → Illustrator → PDF 流程 / 文件格式 / 大小 | `figure-references/06-workflow-and-files.md` | `figure-references/10-templates.md` |
| 同一张图投不同期刊该怎么调 | `figure-references/07-voice-by-subgenre.md` | `references/14-journals.md`（写作 skill） |
| 自查 figure 反模式 | `figure-references/08-antipatterns.md` | — |
| 写 caption | `figure-references/09-caption.md` | `references/05-results.md` §5.5（写作 skill） |
| 要 matplotlib rcParams / ggplot theme / Illustrator 拼版 checklist | `figure-references/10-templates.md` | — |
| 长期培养 figure taste | `figure-references/11-taste-development.md` | — |
| Figure 与 Results 节奏怎么对偶 | `figure-references/12-bridge-to-writing.md` | `references/01-story.md`（写作 skill） |

### 1.2 figure-references 目录

| 文件 | 主题 | 行数 |
|---|---|---|
| `figure-references/01-fig1-schematic.md` | Fig. 1 六种主导构图 + corpus 实例 + 设计要点 | 160 |
| `figure-references/02-color.md` | 三类 colormap、Wong 8 色板（hex 已 verified）、分组高亮、不要做的事 | 90 |
| `figure-references/03-typography-layout.md` | Helvetica/Arial、**panel letter 8pt bold lowercase + 其他 5–7pt**（官方 verified）、不放 figure 内 title、Panel 布局规则 | 110 |
| `figure-references/04-chart-selection.md` | 数据图选型决策树、错误图型组合 | 60 |
| `figure-references/05-stats-in-figure.md` | error bar / 显著性 / N / boxplot 约定 | 60 |
| `figure-references/06-workflow-and-files.md` | matplotlib→Illustrator pipeline、PNG 反模式、字体 embed、DPI 300/450、RGB vs CMYK、主图格式白名单、50MB 上限 | 90 |
| `figure-references/07-voice-by-subgenre.md` | Nature 旗舰 / NMI / NC / NCS / 临床 5 种视觉口音 | 70 |
| `figure-references/08-antipatterns.md` | 19 条 arXiv→Nature 症状 + 修法 | 35 |
| `figure-references/09-caption.md` | Caption title 风格、panel 必写字段、不该写的 | 65 |
| `figure-references/10-templates.md` | matplotlib rcParams / ggplot2 theme_nature / Illustrator 拼版 10 步 | 145 |
| `figure-references/11-taste-development.md` | 看图练习 / 临摹 / 工具熟练度 / 反馈来源 | 50 |
| `figure-references/12-bridge-to-writing.md` | story shape × Fig. 1 构图对应表 + caption-Results 对偶 | 60 |

### 1.3 与写作 SKILL 的衔接

写作端在姊妹 skill `SKILL.md` 中。关键对偶：figure 决定 caption 节奏 → caption 决定 Results 段落顺序 → Fig. 1 是 reviewer 进入故事的门（写作 SKILL §1.3）。常见同时打开两本：写 Results 节就同时 Read `references/05-results.md` + `figure-references/01-fig1-schematic.md`。

---

## 2. 起手 / 收尾两张速查表（屏幕边贴条）

### 2.1 起手 5 步（每张新 figure 开始时）

```text
1. 这张 figure 服务哪条 abstract claim？写出来。
2. 它属于 §1 哪种构图，或它是 quantitative result figure？
3. apply rcParams（§11）。figsize 按投稿尺寸 1:1。
4. 颜色分配：你的方法 1 个品牌色（Wong palette），baseline 灰阶。
5. 删 title。删 top + right spine。删 grid（或极淡）。
```

### 2.2 收尾 checklist（每张 figure 提交前）

```text
[ ] 字体全部 Helvetica / Arial。
[ ] 字号：panel letter **8pt bold lowercase** + 其他全部 **5–7pt**（Nature Research Figure Guide 强制）。
[ ] 没有 figure 内 title。
[ ] 没有 top / right spine（除非有功能）。
[ ] 颜色：Wong 8 色板内或与之兼容；categorical / sequential / diverging 选对。
[ ] error bar 在 caption 写明定义。
[ ] N 在 caption 给出（每 panel 都给）。
[ ] 显著性 / P-value 标注一致（bracket 或星号 + caption 解释）。
[ ] panel 字母左上对齐 plot area，加粗。
[ ] 多 panel grid 对齐（顶 / 底 / 左 / 右）。
[ ] 共享坐标轴 / 共享 legend 已合并。
[ ] PDF / SVG 矢量；字体 embed（pdf.fonttype: 42 或 outline）。
[ ] Acrobat 400% zoom 检查无糊 / 无字体替换。
[ ] 打印 1:1 看 30 秒，最小字号仍可读。
[ ] caption title 风格与 Results 子节标题对偶。
[ ] caption 不重复正文叙事。
[ ] 没有 logo / lab name / screenshot 残留。
```

### 2.3 跨 figure 一致性

```text
[ ] 同一类对象（method A）在所有 figure 同色。
[ ] 同一指标（AUC / DSC）在所有 figure 同 y 轴格式。
[ ] 字号梯度、caption style、panel letter 风格在所有 figure 一致。
```

---

## 3. 本文件不教什么（caveat）

- **Illustrator / Inkscape 具体操作**：本 skill 假设你愿意学一种 vector editor。
- **BioRender icon 选择 / PyMOL 蛋白渲染 / ChemDraw 化学结构**：各有独立学问。
- **科学插画 commission**：旗舰 Fig. 1 偶尔由专业插画师画——本 skill 教你如何与插画师沟通，
  不教你如何画到那个水平。
- **统计方法本身**：本 skill 只教如何在 figure 内呈现 mean ± SD / 95% CI / P-value，
  不教何时用什么 test。
- **数据采集 / 实验设计**：figure 漂亮但实验有问题，救不回。

## 4. 已核实数字 / 未核实数字（v0.2 update）

**v0.2 已用 Nature Research Figure Guide 在线版 + "Guide to preparing final artwork" PDF
交叉验证**。以下表格区分：

### 已核实的硬约束

| 项 | 官方值 | 来源 |
|---|---|---|
| 单栏宽 | 88 mm（PDF）/ 89 mm（在线指南） | NRJs PDF + research-figure-guide.nature.com |
| 双栏宽 | 180 mm（PDF）/ 183 mm（在线指南） | 同上 |
| 1.5 栏 / 三栏 | 121 mm / 185 mm | NRJs PDF |
| Panel letter | **8 pt, bold, upright, lowercase** | research-figure-guide |
| 其他文字字号 | **max 7 pt / min 5 pt**（不区分 axis/tick） | research-figure-guide |
| Raster DPI | min 300，推荐 450 | 同上 |
| 颜色空间 | 原创研究 RGB / Reviews & Perspectives CMYK | NRJs PDF |
| Bleed | 官方未要求（两份文档均无任何 bleed 描述） | — |
| 字体格式 | TrueType 2 或 42；**禁 TrueType 3** | research-figure-guide |
| 字体家族 | Helvetica 或 Arial；序列 Courier；希腊字母 Symbol | 同上 |
| 主图文件大小 | ≤ 50 MB | building-and-exporting page |
| Extended Data | ≤ 10 MB | 同上 |
| 主图格式白名单 | AI / EPS / PDF（首选）、PSD / PPT / SVG / PS（接受）；**不接受** BMP/GIF/JPG/PNG/TIFF/TEX 作主图 | NRJs PDF |
| Wong 2011 引用 | Nature Methods **8(6):441**, June 2011, DOI 10.1038/nmeth.1618 | nature.com/articles/nmeth.1618 |

### 仍未单独核实

- **NMI / NCS / NComms 各自的子刊补充规范**：本次只验证了 Nature Research 通用 figure guide
  （明确"applies to all Nature-branded research journals"），未单独抓三个子刊的 submission
  guidelines 页面。极少情况下子刊有补充约束（如 NMI 是否对 schematic 有特殊要求），
  投稿前仍建议过一遍目标子刊的 "Submission guidelines" 与 "Figures and tables" 两页。
- **当年规范是否调整**：Nature 政策每年可能小调（typical 字号 / 栏宽不会改，但文件大小 /
  接受格式偶有更新）。投稿当周 30 秒 sanity check 仍必要。

### 已成功访问的官方资源

- https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/
- https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf
- https://www.nature.com/articles/nmeth.1618 （Wong 2011 著录页）
- https://clauswilke.com/dataviz/color-pitfalls.html （Wong / Okabe-Ito 8 色板 hex 交叉验证）

正式投稿当周建议作者本人到 nature.com → 目标子刊 → "For Authors" → "Submission
guidelines" 与 "Figures and tables" 两页核对当年具体数字。

---

## 5. 一句话收尾

> 写作 skill 教你写出"reviewer 愿意读"的句子。
> Figure skill 教你画出"reviewer 愿意停下来看"的图。
> 两者合起来——不是让你伪装成 Nature paper，而是让你的真东西不被 default matplotlib 葬送。
