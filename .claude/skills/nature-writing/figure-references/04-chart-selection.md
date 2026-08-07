# 04 · 数据图选型决策树

（FIGURE-SKILL Part IV §5；总索引见 `../FIGURE-SKILL.md`）

## 5. 数据图选型决策树

**Patron principle** — Tufte 改写："Show data, not chartjunk."

### 5.1 决策树（先选语义）

```text
我要表达什么？

(a) 比较少量类别的标量数值          → bar / dot plot（首选 dot 而非 bar，Wong 一贯立场）
(b) 比较少量类别的分布              → box plot / violin / strip + jitter
(c) 比较 N 个数据集 / split 上的同一指标 → grouped dot / forest plot 风格
(d) 两个连续变量的关系              → scatter（点 ≤ 1k）/ density 2D / hexbin（点 ≥ 10k）
(e) 多变量矩阵 / pairwise 关系      → heatmap（注意 colormap 类型）/ correlation matrix
(f) 高维比较                        → parallel coordinates（≤ 8 维）/ radar（慎用）
(g) 网络结构                        → graph（节点 ≤ 30）；超过用 heatmap 或 community plot
(h) 时间序列                        → line plot（line ≤ 10）；超过用 small multiples
(i) 不确定性的分布                  → violin / KDE / strip；不要只画 mean
```

### 5.2 各图型注意事项

**Bar plot**：类别 ≤ 6 尚可，多了改 dot / horizontal bar。永远从 0 起；截断 y 轴是欺骗
（除非显式标 break）。error bar 在 caption 写明（§6）。corpus 例：Virchow Fig. 2b 4 个
foundation model 的 AUC bar + P-value annotation。

**Box / Violin / Strip**：N < 20 直接画 strip + jitter，不要 box（箱线无数据基础）；
20 ≤ N ≤ 100 用 box + 重叠 strip（corpus 常见）；N > 100 用 box 或 violin。
center line / whisker / outlier 必须在 caption 约定（§6.4）。

**Scatter**：点 ≤ 200 实心 alpha=1；200–1000 alpha=0.4–0.6；> 1000 改 hexbin / density 2D。
预测 vs 真值永远画 y=x diagonal。corpus 例：scRNA-seq UMAP，颜色编码 cell type（Wong 8 色板）
+ dim 0.05。

**Heatmap**：categorical 行 / 列用 hierarchical clustering 排序，不要字母序。数值类型决定 colormap：
proportion → sequential，correlation → diverging。行 / 列标签 ≤ 30 才画，超过用 dendrogram +
color bar。corpus 例：SyntheMol Fig. 4a "heat map summarizing the minimum inhibitory
concentrations (MIC) of the 58 synthesized molecules"。

**Parallel coordinates / radar**：parallel ≤ 8 维 + ≤ 30 对象；超过糊。radar / spider 在 corpus
**几乎不见**，慎用。

**Network graph**：节点 > 30 force-directed 也糊；改 community block 或 adjacency heatmap。
边权用 line width，颜色留给节点类。

### 5.3 错误的图型组合

- **3D bar / 3D pie / 3D scatter（除非真 3D 数据）**：corpus 内零次。3D 透视扭曲读数。
- **Pie chart**：Nature 系几乎不用；改 horizontal bar。
- **Stacked bar 但段未排序**：每根 bar 内的段顺序不一致，读者无法跨 bar 对比。
- **Double y-axis（左右两条 y 轴）**：误导风险高；除非两轴是同一物理量的两单位（°C / °F），
  否则改 small multiples。

---

