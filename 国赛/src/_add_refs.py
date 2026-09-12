# -*- coding: utf-8 -*-
r"""把 docs/ 下的全部论文补进参考文献, 并在正文相应位置加上引用.

题录来源与核实状态 (重要):
  * 论文正文已核实 (从 PDF 自身读出): yang2005, adrover2019, feyissa2009, purlis2021,
    xu2021, wang2024, zhang2022, du2018, bao2022 —— 共 9 篇;
    purlis2021 另经 Crossref 独立确认 (Foods 2021, 10(4): 778, DOI 10.3390/foods10040778).
  * **未经原始记录核实**: liu2020 —— docs/农产品热风干燥传热传质数值模拟研究进展.pdf 的字体
    没有 ToUnicode 映射, markitdown 与 PyMuPDF 都只能给出乱码, 本机无 OCR; 其题录来自
    项目自有的 docs/文献索引.csv 与 docs/文献综述.md (两份文件一致), **不是**我读原文读出来的.
    该条在下方以注释标明来源, 供人工复核后确认.

用法: python src/_add_refs.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
DRY = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# 1) 正文引用位置 (每条 old 必须全文恰好出现一次)
# ---------------------------------------------------------------------------
CITES = [
    ("是最常见的干燥方式。",
     "是最常见的干燥方式\\upcite{wang2024}。"),
    ("使药材先后经历预热平衡与恒温干燥两个阶段，",
     "使药材先后经历预热平衡与恒温干燥两个阶段\\upcite{zhang2022}，"),
    ("容易导致干燥效率低、能耗高、成品品质不稳定，",
     "容易导致干燥效率低、能耗高、成品品质不稳定\\upcite{du2018}，"),
    ("\\upcite{hu2020}",
     "\\upcite{hu2020,solomon2021}"),
    ("水分迁移由 Fick 扩散描述",
     "水分迁移由 Fick 扩散描述\\upcite{yang2005}"),
    ("采用数值方法求解：",
     "采用数值方法求解\\upcite{liu2020,oliveira2003}："),
    ("把动边界化为固定域有两条路。",
     "把动边界化为固定域有两条路\\upcite{feyissa2009,adrover2019}。"),
    ("内部位移场未知。本文采用\\textbf{均匀收缩}模式：",
     "内部位移场未知\\upcite{adrover2019,purlis2021,xu2021,amankwah2018,marques2023}。"
     "本文采用\\textbf{均匀收缩}模式："),
    ("食品或生物材料的热风干燥",
     "食品或生物材料的热风干燥\\upcite{bao2022}"),
]

# ---------------------------------------------------------------------------
# 2) 新增参考文献条目 (GB/T 7714 风格, 与既有 7 条一致: 正文不印 DOI)
# ---------------------------------------------------------------------------
NEW_ITEMS = r"""
    % ---- 以下 10 条由 docs/ 下的论文补入 (session 24) ----
    % yang2005  题录取自 PDF 第 1 页页眉/题名区与第 31 页自引 (文章编号 1002-6819(2005)01-0027-05)
    \bibitem{yang2005}
    杨历, 陶斌斌.
    \newblock 多孔介质干燥过程传热传质研究\allowbreak[J].
    \newblock 农业工程学报, 2005, 21(1): 27--31.
    % adrover2019  题录取自 PDF 第 1 页刊头与同页脚注 Please cite this article as (CET 74, 1111-1116)
    \bibitem{adrover2019}
    Adrover A, Brasiello A.
    \newblock The role of shrinkage on food isothermal drying: a moving boundary model\allowbreak[J].
    \newblock Chemical Engineering Transactions, 2019, 74: 1111--1116.
    % feyissa2009  题录取自 PDF 第 1 页会议论文集题头 (无 DOI)
    \bibitem{feyissa2009}
    Feyissa A H, Adler-Nissen J, Gernaey K V.
    \newblock Model of heat and mass transfer with moving boundary during roasting of meat in convection-oven\allowbreak[C].
    \newblock Proceedings of the COMSOL Conference 2009 Milan, 2009.
    % purlis2021  题录取自 PDF 第 1 页, 并经 Crossref 独立确认 (Foods 2021, 10(4): 778)
    \bibitem{purlis2021}
    Purlis E, Cevoli C, Fabbri A.
    \newblock Modelling volume change and deformation in food products/processes: an overview\allowbreak[J].
    \newblock Foods, 2021, 10(4): 778.
    % xu2021  题录取自 PDF 第 1 页页眉/题名/DOI 行与自引
    \bibitem{xu2021}
    徐英英, 文怀兴, 谭礼斌, 等.
    \newblock 苹果切片干燥收缩变形的孔道网络模拟及试验\allowbreak[J].
    \newblock 农业工程学报, 2021, 37(12): 289--298.
    % !! liu2020 题录**未经原始记录核实**: 该 PDF 字体无 ToUnicode, 本机无 OCR.
    %    来源是项目自有索引 docs/文献索引.csv 与 docs/文献综述.md (两份一致), 请人工复核.
    \bibitem{liu2020}
    刘格含, 王鹏, 吴小华, 等.
    \newblock 农产品热风干燥传热传质数值模拟研究进展\allowbreak[J].
    \newblock 食品工业科技, 2020, 41(22): 342--350, 357.
    % wang2024  题录取自 PDF 第 1 页页眉/12 位作者/doi 行/文章编号与自引
    \bibitem{wang2024}
    王乐意, 李长河, 刘明政, 等.
    \newblock 中药材干燥技术与装备研究现状\allowbreak[J].
    \newblock 农业工程学报, 2024, 40(2): 1--28.
    % zhang2022  题录取自 PDF 第 1 页刊头/文章编号/DOI 行
    \bibitem{zhang2022}
    张兴亮.
    \newblock 菊花分段式热风烘干工艺研究\allowbreak[J].
    \newblock 中国果菜, 2022, 42(8): 25--29.
    % du2018  题录取自 PDF 第 1 页刊头(全角)与作者行
    \bibitem{du2018}
    杜娟, 廖新福, 热比古丽·哈力克, 等.
    \newblock 热风烘干对桑葚制干效果的影响\allowbreak[J].
    \newblock 黑龙江农业科学, 2018(3): 113--120.
    % bao2022  题录取自 PDF 第 1 页刊头/题名/作者/DOI/文章编号 1673-9868(2022)10-0173-08
    \bibitem{bao2022}
    鲍安红, 豆玉婷, 彭和, 等.
    \newblock 基于 Weibull 分布函数的厨余垃圾干燥过程模拟研究\allowbreak[J].
    \newblock 西南大学学报(自然科学版), 2022, 44(10): 173--180.
\end{thebibliography}"""

src = open(TEX, encoding="utf-8", newline="").read()

bad = [(o, src.count(o)) for o, _ in CITES if src.count(o) != 1]
if bad:
    print("!! 以下引用锚点匹配数不为 1, 中止:")
    for o, n in bad:
        print(f"   {n} 次  {o!r}")
    raise SystemExit(1)
n_bib = src.count("\\end{thebibliography}")
print(f"引用锚点 {len(CITES)} 条均唯一; \\end{{thebibliography}} 出现 {n_bib} 次")
if n_bib != 1 or "\\bibitem{liu2020}" in src:
    print("!! 结构不符, 中止")
    raise SystemExit(1)

out = src
for o, n in CITES:
    out = out.replace(o, n, 1)
out = out.replace("\\end{thebibliography}", NEW_ITEMS, 1)
out = out.replace("\\begin{thebibliography}{9}", "\\begin{thebibliography}{99}", 1)

n_items = out.count("\\bibitem")
print(f"参考文献条目: {src.count(chr(92) + 'bibitem')} -> {n_items}")
if DRY:
    print("--dry-run: 未写文件")
    raise SystemExit(0)

bak = TEX + time.strftime(".bak_refs_%Y%m%d_%H%M%S")
open(bak, "w", encoding="utf-8", newline="").write(src)
open(TEX, "w", encoding="utf-8", newline="").write(out)
chk = open(TEX, encoding="utf-8", newline="").read()
keys = ["yang2005", "adrover2019", "feyissa2009", "purlis2021", "xu2021",
        "liu2020", "wang2024", "zhang2022", "du2018", "bao2022"]
missing = [k for k in keys if f"\\bibitem{{{k}}}" not in chk]
uncited = [k for k in keys if f"\\upcite" not in chk or (k not in chk.split("\\begin{thebibliography}")[0])]
print(f"备份 {os.path.basename(bak)}")
print(f"新增条目缺失: {missing or '无'}")
print(f"正文未引用的新条目: {uncited or '无'}")
