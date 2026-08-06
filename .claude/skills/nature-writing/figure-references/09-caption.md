# 09 · Caption 写法

（FIGURE-SKILL Part IX §10；与 SKILL.md `references/05-results.md` §5.5 衔接）

## 10. Caption 不是图注垃圾桶

**Patron sentence** — Virchow (extracts/05-medical.md):
> "Virchow embeddings yielded the best cancer detection performance on all cancer types
> (Fig. 2a)."

call-out 把发现放主语，figure 是证据（SKILL.md §5.4）。caption 同理：caption title
是 declarative，panel 描述是机械结构。

### 10.1 Caption 的层级

```text
Fig. N | <Caption title — declarative, ≤ 1 句>.
a, <这个 panel 的发现 / 内容>. <数据来源 + N>. <视觉编码 + error bars>. <统计检验>.
b, <…>.
c, <…>.
```

corpus 内两种 caption title 风格：

- **Declarative（现代）**：`"Virchow embeddings yielded the best cancer detection
  performance on all cancer types"` — 自带结论。
- **Noun phrase（传统）**：`"Overview of the AlphaFold model architecture"` — 中性描述。

Fig. 1 schematic 通常是 noun phrase（"Schematic of the approach"）；后续 result figure
更适合 declarative。

### 10.2 每个 panel 必写的字段

```text
- 这个 panel 在画什么（一句 claim 或 description）；
- 数据源 / cohort / 数据集 / split；
- N（或每组 N）；
- 视觉编码：bar / box / line / heatmap；颜色对应；
- error bar 的定义；
- 统计检验：test name + P-value + 多重校正；
- 数据点是否独立、是否经过 averaging、是否 bootstrap。
```

### 10.3 不该写的

- 正文已经讲清的 mechanism / 故事——caption 不是再讲一遍。
- 模型 architecture 详情——进 Methods。
- 整段叙述 / "we found that"——caption 是 figure 自描述，不是 narrative。
- 个人感想 / "remarkably, ..."——留给 Results 正文。

### 10.4 与写作 skill 的衔接

SKILL.md §5.5 给了 caption 推荐结构：

```text
a, <这个 panel 的发现>. <数据来源 / 队列 / N>. <视觉编码：boxplot / heatmap / scatter>.
<统计检验：test, P value, CI/IQR/SD>.
```

本 skill 在视觉端补：caption title 应与 figure 的 visual climax 对齐——读者扫 figure 形成
直觉，再读 caption title 得到 declarative 锁定。两者错位时，读者会迷惑（"图给的是 A，
caption 说的是 B"）。

---

