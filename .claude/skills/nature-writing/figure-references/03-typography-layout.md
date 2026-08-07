# 03 · 字体、字号、Panel 布局

（FIGURE-SKILL Part III §§3–4；已按 Nature Research Figure Guide 核实；总索引见 `../FIGURE-SKILL.md`）

## 3. 字体 / 字号

**Patron principle** — corpus 内多见：figure 内不放 title。

### 3.1 字体

- **首选**：Helvetica（Adobe Helvetica 系列）或 Arial（Windows / matplotlib 通用替代）。
  Helvetica 与 Arial 在小字号下几乎不可区分。corpus 内 Nature 旗舰、NMI、NCS 全部用此族。
- **次选**：Myriad Pro / Source Sans Pro，个别期刊接受。
- **不要用**：Times New Roman 全图（衬线在 panel 内会糊）；Computer Modern（LaTeX 默认；
  与 sans-serif 期刊正文不协调）；Comic Sans / Calibri / 各种创意体。
- **数学**：行内 inline math 与 figure 内变量保持一致字体；行间公式可用 Computer Modern 或
  STIX，但 figure 内的变量名（α、β、x_i）应与 axis label 同字体。

### 3.2 字号（**已按 Nature Research Figure Guide 核实**）

Nature 官方（research-figure-guide.nature.com）只规定**两个字号档**：

```text
panel letter (a, b, c)  : 8 pt, bold, upright (not italic), lowercase
all other text          : max 7 pt, min 5 pt
```

注意：**不是** axis label 7–8、tick 6–7 这样的细分梯度——是"panel letter 8pt + 其他 5–7pt"
二分制。常见配比：axis label 7pt、tick label 6pt、legend 6pt、in-figure label 6–7pt——
但只要落在 5–7 pt 区间内、保持视觉层级就合规。

最小可读字号 5 pt（在 88–89 mm 单栏宽度下印刷），低于就不可读。如果你画完缩到投稿尺寸
读不清——就是不合格。

### 3.3 不要在 figure 内放 title

强约定：Nature 系正文 figure **不在图本身放 title**。title 进 caption。原因：

- caption title 由编辑统一排版；figure 内自带 title 会与之冲突。
- figure 内 title 会推挤 plot area，缩小数据空间。
- caption title 是检索关键句，应由作者写、由编辑统一字号——不该藏在像素里。

matplotlib 默认 `ax.set_title("...")` 是 arXiv 味来源之一。**删掉**。

### 3.4 Spines 与 grid

- **去 top + right spine**：corpus 内极常见。`ax.spines[['top','right']].set_visible(False)`。
- **保留 bottom + left spine**，line width 0.5–0.8 pt。
- **grid**：默认不画。如果数据需要，画极淡 horizontal grid（color='#EEEEEE', lw=0.3，
  在 spine 之下）。垂直 grid 几乎不画。
- **背景白底**，不要 seaborn 默认灰底。

---

## 4. Panel 布局：(a)(b)(c) 不是装饰

### 4.1 Panel 字母（**已按 Nature Research Figure Guide 核实**）

- **位置**：左上角，对齐 plot area 左边而不是 figure 边。这样多 panel 排版时 letter 形成
  竖直对齐线。
- **样式**：**8 pt, bold, upright (not italic), lowercase** —— `a`, `b`, `c`。Nature Research
  Figure Guide 原文：*"Separate panels in multi-panelled figures should be labelled with
  8-pt bold, upright (not italic) and lowercase a, b, c, etc."*
- **不加括号 / 不加点**：直接 `a` 而不是 `(a)` 或 `a.`。caption 里可以写 "a, ..."。
- 用 `A` / `B` / `C` 大写是常见错误，会被 production team 退回改。

### 4.2 Grid alignment

多 panel 的视觉协议：

- 同一行 panel 的 plot area 顶 / 底对齐。
- 同一列 panel 的左 / 右对齐。
- 共享 x 轴的 panel 共用同一段 tick；上方 panel 的 x tick label 隐藏。
- 共享 y 轴同理。
- 不同 panel 的同一类对象（method A）必须同色；如果换色，读者会找不到。

### 4.3 阅读流

读者扫图的默认顺序：左上 → 右上 → 左下 → 右下（西方阅读流）。
策略：

- Fig. 1**a** 是 schematic（建立心智模型）；
- Fig. 1**b** 是主结果第一击；
- Fig. 1**c / d** 是 supporting / mechanism；
- Fig. 1 末 panel 是 punchline / qualitative example。

corpus 例：scIB (extracts/01-singlecell.md): "Fig. 1. Design of single-cell integration
benchmarking (scIB)" — Fig. 1 把 13 项 task + 16 个 method 的 benchmark 框架建立起来；
Fig. 2/3/4 才进各 task 的具体 quantitative。这是 benchmark paper 的标配。

### 4.4 Legend 与 annotation

- **共享 legend**：多 panel 同一类对象用同色，legend 放整张 figure 顶部或右侧一次，
  不在每 panel 重复。
- **inline label**：line plot 直接在线尾标 method 名，比 legend 易读，corpus 内常见。
- **legend 位置**：默认 plot area 外或 plot area 内空白角；不要遮数据。

### 4.5 多 panel 拼版的尺寸约束

corpus 内常见尺寸（以官网为准）：

- **single column**：约 89 mm 宽；适合 1–3 panel。
- **double column**：约 183 mm 宽；适合 4–8 panel。
- **full page / portrait**：约 247 mm 高；适合 schematic + 大型 task gallery。

字号是相对印刷尺寸定的。如果你在屏幕上以 200 mm 宽设计，最后缩到 89 mm，6pt tick 会
变成 ~3pt——不可读。**早期就以投稿尺寸 1:1 设计**，不要等 production 阶段再缩。

---

