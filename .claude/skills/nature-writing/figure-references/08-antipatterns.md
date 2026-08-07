# 08 · arXiv → Nature 反模式 19 条

（FIGURE-SKILL Part VIII §9；总索引见 `../FIGURE-SKILL.md`）

## 9. 常见症状与修法

**Patron principle** — 大多数"不像 Nature"的图，问题不是品味，而是**默认设置没改**。

| # | 症状 | 修法 |
|---|---|---|
| 1 | matplotlib 默认 tab10 全图直用 | 用 §2.2 Wong 8 色板；自家方法 1 个饱和品牌色，其余灰阶 |
| 2 | 3D bar / 3D pie / 3D scatter（伪 3D） | 改 horizontal bar / dot plot / 2D scatter |
| 3 | figure 内 `ax.set_title("...")` 顶上挂 title | 删 title；title 进 caption |
| 4 | top + right spine 默认存在 | `ax.spines[['top','right']].set_visible(False)` |
| 5 | grid 默认开 + seaborn 灰底 | 白底，no grid 或极淡 horizontal grid |
| 6 | 跨 panel 字体 / 字号 / line width 不一致 | 统一 rcParams（§11）；Illustrator 最后扫一遍 |
| 7 | stacked bar 段未排序 | 按全局总量降序 / 按某个固定语义顺序排 |
| 8 | rainbow / jet heatmap 表 sequential | 改 viridis / cividis / magma |
| 9 | PNG 投稿 / PNG 嵌 PDF | 输出 SVG / PDF，确保矢量 |
| 10 | 字体未 embed（PDF 在审稿人机器上变 default） | rcParams `pdf.fonttype: 42`；或 Illustrator outline |
| 11 | 过密 grid annotation（每个点标 label） | 只标极端点 / 关键点；其余进 caption / supplementary |
| 12 | error bar 不写定义 | caption 写 mean ± SD / SEM / 95% CI |
| 13 | N 不标 | caption 给 N（每 panel 都给） |
| 14 | legend inside 遮数据 / line plot 用 legend 而不 inline label | inline label 在线尾；legend 移外 |
| 15 | "AlphaFold" 和 "Ours" 字体不同（拼图味） | 全图同字体；Illustrator outline 后字体仍要一致 |
| 16 | schematic 里 box 高度不齐 | 严格 grid align；Illustrator "Align top edges" |
| 17 | screenshot of Jupyter cell 拼进 figure | 重画。Jupyter screenshot 一秒暴露 |
| 18 | logo / banner / lab name 出现在 figure 里 | 删。投稿 figure 不允许 |
| 19 | panel 内放小 logo / 装饰 emoji | 删。除非有语义功能（如 BioRender 标准 icon） |

每一条都见过 reviewer 在 OpenReview 写"please redraw the figure with"。

---

