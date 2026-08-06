# 06 · 工作流、文件格式、文件大小

（FIGURE-SKILL Part VI §7：matplotlib→Illustrator pipeline / DPI / RGB-CMYK / 主图格式白名单 / 50MB 限制；总索引见 `../FIGURE-SKILL.md`）

## 7. 从代码到投稿 PDF

**Patron principle** — corpus 内多见：final figure 必须矢量。

### 7.1 推荐工作流

```text
Python (matplotlib / seaborn) → SVG
              ↓
       Illustrator / Inkscape / Affinity Designer
              ↓
       (拼版、字体一致化、icon 微调、annotation)
              ↓
              PDF (vector preserved)
              ↓
       投稿 figure submission system
```

或者：

```text
R (ggplot2) → SVG / PDF → Illustrator → PDF
LaTeX TikZ → PDF（适合 physics / theory schematic）
BioRender → SVG / PDF（生物 schematic icon library）
ChemDraw → SVG / PDF（化学结构）
```

### 7.2 为什么 PNG 直交是反模式

- 缩放糊：评审 PDF 在 200% zoom 下糊掉，editor 体感差。
- 期刊 production 要求矢量重排：你给 PNG，他们要重画，往返多。
- 字体不可调：production 想换字号 / 字体时无法处理。

例外：照片 / 显微镜 / 病理图本身是 raster；这是合法的 raster 区域。把 raster 嵌入 vector
container（PDF / SVG），不要把整张图 rasterize。

### 7.3 字体嵌入

- 投稿 PDF 必须把字体 embed 或 outline。Illustrator: File → Save As → PDF, 勾选 "Embed all
  fonts" 或 outline 文字（outline 更保险但失去可编辑性）。
- matplotlib 直接 `savefig('fig.pdf')` 默认会 embed Type 3 字体，生产侧通常要求 Type 42 /
  TrueType；rcParams 设 `pdf.fonttype: 42`（§11）。

### 7.4 DPI / 颜色空间（**已按 Nature Research Figure Guide 核实**）

- **Raster 嵌入区域 ≥ 300 dpi**（强制最低）；Nature 推荐 **450 dpi** 以保证 online proof
  与印刷质量。Line art 矢量本身无 dpi 概念。
- **颜色空间**：
  - **原创研究（research articles）→ RGB 提交**。Nature 印刷端会自动转 CMYK。
  - **Reviews / Perspectives / 综述类 → CMYK 提交**。
  - 提交 RGB 时不要用太饱和的荧光色——印刷转 CMYK 后会大幅暗化，提交前在 Acrobat 看 CMYK 预览。
- 提交前在 Acrobat 里 zoom 400% 检查 raster 是否糊、字体是否 embed。

### 7.5 文件格式与大小（**已核实，硬约束**）

主图首选格式（按官方推荐顺序）：
```
.ai (Illustrator)   .eps   .pdf
```
也接受：`.psd`（Photoshop）、`.ppt/.pptx`（前提：完全可编辑，不能 flatten）、`.svg`、`.ps`。

**不接受作为主图本体**：`.bmp` `.gif` `.jpg` `.png` `.tiff` `.tex`。Raster 只能作为 PDF/EPS/AI
**容器内嵌入的位图**（嵌入时 ≥ 300 dpi）。

文件大小：
- 主图 ≤ **50 MB**
- Extended Data figure ≤ **10 MB**

不要做的事：
- 给元素加 **drop shadow / 3D / bevel / glow** 等 layer effects——投稿处理时这些会被
  rasterize 成低分辨率位图。
- 用 raster (PNG/JPG) 直接当主图——审稿系统不会拒，但生产端会要求重投，浪费一周。
- Excel 图直接拖入——必须先导出 PDF 再置入。

### 7.6 BioRender / ChemDraw 的位置

- BioRender：生物 schematic icon library；导出 SVG 进 Illustrator 再调字体。直接用其默认
  字体（Arial）勉强 ok，但 Inkscape 编辑性更好。
- ChemDraw：化学结构标准。Nature 化学相关期刊几乎要求 ChemDraw 风格。
- 直接用工具输出 PNG 是反模式，理由同 §7.2。

---

