# figure-references/ — figure 设计 SKILL 的细节文件库

总索引在 `../FIGURE-SKILL.md`（瘦索引：arXiv↔Nature 对照表 + routing table + quick card + 已核实硬约束 + caveat）。本目录是按主题拆分的 12 个细节文件，**按需 Read**。

## 加载规则

| 你在做什么 | Read |
|---|---|
| 设计 Fig. 1 | `01-fig1-schematic.md` + `12-bridge-to-writing.md` |
| 选颜色 | `02-color.md` |
| 数据图选型 | `04-chart-selection.md` + `05-stats-in-figure.md` |
| matplotlib → Illustrator pipeline | `06-workflow-and-files.md` + `10-templates.md` |
| 自查反模式 | `08-antipatterns.md` |
| 写 caption | `09-caption.md` + `../references/05-results.md` §5.5 |
| 投不同刊调整风格 | `07-voice-by-subgenre.md` + `../references/14-journals.md` |

详细映射见 `../FIGURE-SKILL.md` §1.1。

## 目录

| 文件 | 主题 |
|---|---|
| `01-fig1-schematic.md` | Fig. 1 六种主导构图（数据流 / 模块组装 / 漏斗 / 任务地图 / 双轴对比 / 时间线）+ corpus 实例 |
| `02-color.md` | 三类 colormap、Wong/Okabe-Ito 8 色板（hex 值已 verify）、分组高亮、不要做的事 |
| `03-typography-layout.md` | Helvetica/Arial、**panel letter 8pt bold lowercase + 其他 5–7pt**（Nature 官方）、不放 figure 内 title、Panel 布局规则 |
| `04-chart-selection.md` | 数据图选型决策树、错误图型组合 |
| `05-stats-in-figure.md` | error bar / 显著性 / N / boxplot 约定 |
| `06-workflow-and-files.md` | matplotlib→Illustrator pipeline、PNG 反模式、字体 embed Type 42、DPI 300/450、RGB vs CMYK 政策、主图格式白名单（不接受 PNG/JPG/TIFF 作主图本体）、文件大小 ≤50MB |
| `07-voice-by-subgenre.md` | Nature 旗舰 / NMI / NC / NCS / 临床 5 种视觉口音 |
| `08-antipatterns.md` | 19 条 arXiv→Nature 症状 + 修法 |
| `09-caption.md` | Caption title 风格（declarative vs noun phrase）、panel 必写字段、不该写的 |
| `10-templates.md` | matplotlib rcParams（Wong palette + Type 42 + 8pt panel letter）+ ggplot2 theme_nature + Illustrator 拼版 10 步 checklist |
| `11-taste-development.md` | 看图练习 / 临摹 / 工具熟练度 / 反馈来源 |
| `12-bridge-to-writing.md` | story shape × Fig. 1 构图对应表 + caption-Results 对偶 |

## 与其他目录的关系

- `../FIGURE-SKILL.md`：figure skill 瘦索引（必读）
- `../SKILL.md` + `../references/`：写作姊妹 skill
- `../extracts/`：36 篇 OA 论文 verbatim 抽取，含 figure caption / call-out 引文
