# -*- coding: utf-8 -*-
r"""判定每页是否"整页纯文字"或"整页纯图表".

LaTeX 的表格用 \toprule/\midrule 等**细横线**画成, 面积很小, 用面积阈值会漏判;
故改为: 一页只要有 图片 / 表题(表N、图N) / >=4 条绘图路径, 就算"含图表".
再配合文字占用的垂直高度做判定:

  含图表 but 文字高度很高  -> 正常 (文字为主, 夹杂图表)
  含图表 and 文字高度很低  -> 整页纯图表  (报警)
  不含图表 and 文字高度很高 -> 整页纯文字  (报警)
"""
from __future__ import annotations

import os
import re
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = fitz.open(os.path.join(ROOT, "paper", "example.pdf"))
CAP = re.compile(r"^(表\s*[0-9IVX]+|图\s*[0-9]+)\s*$", re.M)

print(f"{'页':>3} {'文字高%':>7} {'绘图':>5} {'图':>3} {'表题':>4} {'图表格':>6}  判定")
print("-" * 74)
warn = []
for i, p in enumerate(d, 1):
    H = p.rect.height
    ys = []
    for blk in p.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            ys.append((ln["bbox"][1], ln["bbox"][3]))
    th = (max(y[1] for y in ys) - min(y[0] for y in ys)) / H if ys else 0.0
    t = p.get_text()
    nd = len(p.get_drawings())
    ni = len(p.get_images(full=True))
    caps = len(CAP.findall(t))
    has_float = (ni > 0) or (caps > 0) or (nd >= 4)
    tag = ""
    if not has_float and th > 0.75:
        tag = "!! 整页纯文字"
        warn.append((i, tag))
    elif has_float and th < 0.20:
        tag = "!! 整页纯图表"
        warn.append((i, tag))
    print(f"{i:3d} {th*100:6.1f}% {nd:5d} {ni:3d} {caps:4d} "
          f"{'是' if has_float else '否':>6}  {tag}")

print()
print("违规页:", warn if warn else "无")
