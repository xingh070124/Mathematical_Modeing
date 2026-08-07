# 10 · 工具与 template

（FIGURE-SKILL Part X §§11–13：matplotlib rcParams / ggplot2 theme / Illustrator 拼版 10 步；总索引见 `../FIGURE-SKILL.md`）

## 11. matplotlib rcParams（起手 baseline）

不要手写一张图就调一遍参数。在项目 `figures/style.mplstyle` 或 setup module 里固化：

```python
# nature_figure_style.py
import matplotlib as mpl

NATURE_RCPARAMS = {
    # font
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    # Nature Research Figure Guide: panel letter 8pt bold lowercase;
    # 其他全部 5–7pt（不分 axis/tick 等级别）
    "font.size": 7,
    "axes.titlesize": 7,            # 不建议用 ax.set_title；如果用，封顶 7pt
    "axes.labelsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "figure.titlesize": 7,
    # spines
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.5,
    # ticks
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    # lines & markers
    "lines.linewidth": 1.0,
    "lines.markersize": 3.0,
    # legend
    "legend.frameon": False,
    "legend.handlelength": 1.5,
    # figure
    "figure.dpi": 150,
    "savefig.dpi": 600,             # raster fallback
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    # vector embedding
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    # color cycle: Wong / Okabe-Ito
    "axes.prop_cycle": mpl.cycler(color=[
        "#0072B2", "#D55E00", "#009E73", "#CC79A7",
        "#56B4E9", "#E69F00", "#F0E442", "#000000",
    ]),
}

def apply():
    mpl.rcParams.update(NATURE_RCPARAMS)
```

每张图开头：

```python
from nature_figure_style import apply
apply()

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(3.5, 2.6))   # ~89 mm wide, 单栏
# ... plot ...
ax.set_xlabel("Training tokens")
ax.set_ylabel("Validation loss")
# do NOT call ax.set_title(...)
fig.savefig("figs/fig1b.pdf")
fig.savefig("figs/fig1b.svg")
```

注意 `figsize=(3.5, 2.6)` inch 约 89 × 66 mm，对应单栏宽度。出 SVG / PDF，进 Illustrator 拼版。

## 12. ggplot2 theme snippet

```r
library(ggplot2)

theme_nature <- function(base_size = 7) {
  theme_classic(base_size = base_size, base_family = "Helvetica") +
    theme(
      axis.line = element_line(linewidth = 0.3),
      axis.ticks = element_line(linewidth = 0.3),
      axis.text = element_text(size = base_size - 1),
      axis.title = element_text(size = base_size),
      legend.title = element_text(size = base_size),
      legend.text = element_text(size = base_size - 1),
      legend.key.size = unit(0.3, "cm"),
      strip.background = element_blank(),
      strip.text = element_text(size = base_size, face = "plain"),
      plot.title = element_blank()           # 强制不画 title
    )
}

wong_colors <- c(
  "#0072B2", "#D55E00", "#009E73", "#CC79A7",
  "#56B4E9", "#E69F00", "#F0E442", "#000000"
)
scale_color_wong <- function(...) scale_color_manual(values = wong_colors, ...)
scale_fill_wong <- function(...) scale_fill_manual(values = wong_colors, ...)
```

用法：

```r
ggplot(df, aes(x, y, color = method)) +
  geom_line(linewidth = 0.6) +
  scale_color_wong() +
  theme_nature() +
  labs(x = "Training tokens", y = "Validation loss")
ggsave("figs/fig1b.pdf", width = 3.5, height = 2.6, units = "in", device = cairo_pdf)
```

`cairo_pdf` 保证字体 embed。

## 13. Illustrator 拼版最小流程

不教 Illustrator 操作，但给一份起手 checklist（Inkscape / Affinity Designer 类似）：

```text
1. 新建 artboard：单栏 88–89 mm 或双栏 180–183 mm 宽。Nature Research Figure Guide 在线版给 89/183，
   "Guide to preparing final artwork" PDF 给 88/180——两组都是官方值，落在区间内即合规。
2. File → Place（不是 paste）置入 panel 的 SVG / PDF；保持 Linked 而非 Embedded。
3. Align：横向 panel 顶 / 底对齐；列对齐左 / 右；间距 5–8 mm。
4. Panel letter：左上角对齐 plot area，Helvetica Bold **8pt, lowercase**（a/b/c，不带括号）。
5. 字体一致化：Type → Find Font，所有外来字体替换为 Helvetica
   （matplotlib 默认 SVG 字体可能是 DejaVu Sans——必须替换）。
6. Stroke 检查：选中所有 line，Stroke panel 看是否 0.5–1.0pt。
7. 颜色检查：Window → Swatches 看全图颜色是否一致；重复色合并到同一 swatch。
8. Outline preview（Cmd/Ctrl + Y）：检查 stroke 对齐 / 错位。
9. Save As PDF：preset "High Quality Print" 或 "PDF/X-1a"；字体 "Embed All" 或 outline。
10. Acrobat 400% zoom 复查：raster 糊 / 字体替换 / 颜色偏差。
```

具体投稿尺寸 / bleed 政策以期刊官网为准。

---

