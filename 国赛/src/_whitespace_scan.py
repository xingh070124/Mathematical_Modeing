# -*- coding: utf-8 -*-
r"""逐页测量页底空白, 找出"某一页大片留白"的地方.

对每一页取**全部内容**(文字行 + 图片 + 绘图路径)的上下边界:
    留白 = 版心下界 - 内容下边界
版心上下边距取 cumcmthesis 的 geometry (25 mm).

另外标出: 整页只有图/表、整页只有文字、以及内容低于版心中线的页.

用法: python src/_whitespace_scan.py [pdf路径] [--min-gap 40]
"""
from __future__ import annotations

import os
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "paper", "build_probe", "_final_check.pdf")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if args:
    PDF = args[0] if os.path.isabs(args[0]) else os.path.join(ROOT, args[0])

MIN_GAP = 40.0
if "--min-gap" in sys.argv:
    MIN_GAP = float(sys.argv[sys.argv.index("--min-gap") + 1])

MM = 28.4527  # 1 cm = 28.4527 pt
doc = fitz.open(PDF)
print(f"PDF: {PDF}  ({doc.page_count} 页)")

rows = []
for i, p in enumerate(doc, 1):
    H = p.rect.height
    top_lim = 2.5 * MM          # geometry: top=25mm
    bot_lim = H - 2.5 * MM      # geometry: bottom=25mm
    ys_lo, ys_hi = [], []
    nline = 0
    for b in p.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            nline += 1
            ys_lo.append(ln["bbox"][1])
            ys_hi.append(ln["bbox"][3])
    for b in p.get_text("dict")["blocks"]:
        if b.get("type") == 1:                      # 图片块
            ys_lo.append(b["bbox"][1])
            ys_hi.append(b["bbox"][3])
    for d in p.get_drawings():                      # 表格线/矢量图
        r = d["rect"]
        if r.height < 1 and r.width < 1:
            continue
        ys_lo.append(r.y0)
        ys_hi.append(r.y1)
    # 页脚页码不计入内容: 过滤掉下半部分之外的孤立小字
    body_hi = max([y for y in ys_hi if y < bot_lim + 5] or [0])
    body_lo = min([y for y in ys_lo if y < bot_lim + 5] or [0])
    gap = bot_lim - body_hi
    fill = (body_hi - top_lim) / (bot_lim - top_lim) * 100
    # 本页首行 / 末行文字, 用于定位"为什么这页提前结束"
    lines_all = []
    for b in p.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            if ln["bbox"][3] < bot_lim + 5:
                lines_all.append((ln["bbox"][1],
                                  "".join(sp["text"] for sp in ln["spans"])))
    lines_all.sort()
    first = lines_all[0][1][:34] if lines_all else ""
    last = lines_all[-1][1][:34] if lines_all else ""
    rows.append((i, nline, body_lo, body_hi, gap, fill, len(p.get_images(full=True)),
                 len(p.get_drawings()), first, last))

print(f"\n{'页':>3} {'行':>4} {'页底留白':>8} {'填充%':>6} {'图':>3} {'绘图':>6}  判定 / 首行 → 末行")
print("-" * 108)
bad = []
for (i, nline, lo, hi, gap, fill, nimg, ndraw, first, last) in rows:
    tag = ""
    if gap > MIN_GAP:
        tag = "!! 大片留白"
        bad.append((i, gap, nline))
    elif gap > MIN_GAP * 0.6:
        tag = "~  略空"
    if nline <= 3 and (nimg or ndraw >= 20):
        tag = (tag + " /整页图表").strip(" /")
    print(f"{i:3d} {nline:4d} {gap:8.1f} {fill:6.1f} {nimg:3d} {ndraw:6d}  {tag}")
    if tag:
        print(f"      首行: {first}")
        print(f"      末行: {last}")

print()
if bad:
    print(f"页底留白 > {MIN_GAP:.0f} pt 的页: ", ", ".join(f"p{i}({g:.0f}pt)" for i, g, _ in bad))
    tot = sum(g for _, g, _ in bad)
    print(f"共 {len(bad)} 页, 合计可回收约 {tot:.0f} pt ≈ {tot / 17:.1f} 行")
else:
    print(f"没有页底留白 > {MIN_GAP:.0f} pt 的页")
