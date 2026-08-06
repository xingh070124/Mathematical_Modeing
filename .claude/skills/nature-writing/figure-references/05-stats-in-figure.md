# 05 · Statistics 在 figure 内的最小集合

（FIGURE-SKILL Part V §6：error bar / 显著性 / N / boxplot 约定；总索引见 `../FIGURE-SKILL.md`）

## 6. Statistics 在 figure 内的最小集合

**Patron principle** — corpus 内多见：error bar 不写定义就是 reviewer 必问的第一条。

### 6.1 error bar 选什么

```text
mean ± SD        → 描述样本分布的离散程度
mean ± SEM       → 描述对均值估计的不确定性（依赖 N）
95% CI           → 推断性，含 N 与分布假设
median + IQR     → 非高斯 / 偏态分布；clinical AI 标配
bootstrap 95% CI → 复杂统计量、不假设分布
```

Caption 必须显式写。corpus 例：

- MedSAM (extracts/05-medical.md): "median DSC scores of 87.8% (IQR: 85.0-91.4%)"
- UNI (extracts/05-medical.md): "+4.2% performance increase (P < 0.001, two-sided paired
  permutation test)"
- Virchow (extracts/05-medical.md): "AUC of 0.950 ... all significantly different with P < 0.0001"

### 6.2 N 的标注

- 主图 caption 给 N（数据集大小、被试数、独立 run 数）。
- 多个 N 不同时，每 panel 给 N。
- 如果图里画的是 mean of K runs，K 必须在 caption。

### 6.3 显著性

两种主流写法：

- **Bracket + P-value**：在两 bar 之间画 bracket，标 `P = 0.003` 或 `P < 0.001`。
  现代 Nature 系倾向显式 P-value 而不是星号。
- **星号约定**：`* P < 0.05`, `** P < 0.01`, `*** P < 0.001`, `ns` for not significant；
  必须在 caption 解释。
- 多重比较校正（Bonferroni / Holm / FDR）必须在 caption 注明。

### 6.4 Box plot 约定

caption 必须写明：

```text
center line = median;
box = 25–75% IQR;
whiskers = 1.5 × IQR (Tukey) [or min–max];
points = outliers (or all data points if N small).
```

否则不同读者按不同惯例看你的 box，结论失真。

### 6.5 不要做的事

- 只画 mean line 不画分布——尤其 N 小时。
- error bar 占用 line width 0.3 以下——印刷后看不见。
- 显著性 bracket 重叠 / 跨 4 组以上——简化或拆 panel。

---

