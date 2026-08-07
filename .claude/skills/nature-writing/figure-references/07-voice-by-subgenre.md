# 07 · 不同期刊的视觉口音

（FIGURE-SKILL Part VII §8：Nature 旗舰 / NMI / NC / NCS / 临床 5 种 voice；总索引见 `../FIGURE-SKILL.md`）

## 8. 不同期刊的视觉口音

**Patron principle** — 同一篇论文投不同期刊，figure 的呼吸感是不同的。

### 8.1 Nature 旗舰 / DeepMind 风（极简主义）

特征：
- 单一品牌色 + 大量灰白；
- icon 手绘感，无阴影 / 无渐变；
- schematic 留白多，单 panel 信息密度低；
- 每张 figure 通常对应一条强 claim。

corpus 例：AlphaFold、AlphaGeometry、GenCast。
对应文风：SKILL.md §1.1 "limit-redrawn" / "scale-emergent"。

### 8.2 NMI methods 风（信息密度高）

特征：
- schematic 信息密度高，数据流箭头多；
- 多 module 拼图感强（§1.2）；
- panel 数量多（4–8 在 Fig. 1 里常见）；
- 颜色用 Wong 8 色板挑 3–4 种区分 module。

corpus 例：DynamicBind、ChemCrow、SyntheMol、HINTS。
对应文风：SKILL.md §1.1 "two-gap synthesis"。

### 8.3 Nature Communications 风（跨学科）

特征：
- 视觉语言由子领域决定：生物 schematic 偏 BioRender 风（细胞 / 分子 icon 库）；
  physics 偏 LaTeX TikZ 风（公式 + 几何）；ML 偏现代 vector schematic。
- 同一期刊不同论文的"长相"差很多——不要参照单一篇做模板。

corpus 例：SyntheMol（生物）、HINTS（physics）、SemanticLens（ML 解释）。

### 8.4 Nature Computational Science (NCS) 风

特征：
- 公式与数值结果共存——schematic 里允许出现 inline equation；
- Methods 与 Results 的视觉 register 接近——"工程严谨"是默认气质；
- 多 metric / 多 split 表格化呈现常见。

corpus 例：Geneformer、scIB、Tangram。

### 8.5 临床 AI 风

特征：
- real-world image grid（histology patch / radiology / dermatology）+ AUC ROC + reader study
  bar；
- institution / cohort 地理分布是 Fig. 1 标配；
- 误差棒、CI、N 标注密度比纯 ML 论文高一个量级。

corpus 例：MedSAM、UNI、CONCH、Virchow、MedPerf。
对应 SKILL.md §1.1 "human-anchored benchmark" / "trust bridge"。

### 8.6 投稿前的"风格匹配"检查

打开目标期刊近 12 个月内 3–5 篇相邻领域 paper，看：Fig. 1 构图（§1）、字号 / line width
量级、error bar / N / 显著性标法、颜色饱和度区间。把你的图放进去看会不会"违和"。
违和的不一定错，但要清楚自己在打破什么。

---

