# -*- coding: utf-8 -*-
"""页面内容画像: 对每页统计 文字行数 / 图片数 / 绘图路径数, 用于找"整页纯文字"或
"整页纯图表"的页面."""
from __future__ import annotations

import os
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf = os.path.join(ROOT, "paper", "example.pdf")
d = fitz.open(pdf)

only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None

print(f"{'页':>3} {'文字块':>6} {'文字行':>6} {'图':>4} {'绘图':>5}  首行文字")
print("-" * 96)
for i, p in enumerate(d, 1):
    if only and i not in only:
        continue
    td = p.get_text("dict")
    nline = nblk = 0
    first = ""
    for blk in td["blocks"]:
        if blk.get("type") != 0:
            continue
        nblk += 1
        for ln in blk.get("lines", []):
            nline += 1
            if not first:
                first = "".join(s["text"] for s in ln["spans"])[:46]
    nimg = len(p.get_images(full=True))
    ndraw = len(p.get_drawings())
    print(f"{i:3d} {nblk:6d} {nline:6d} {nimg:4d} {ndraw:5d}  {first}")
