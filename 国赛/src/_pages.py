# -*- coding: utf-8 -*-
"""测量论文各部分占用的页数.

用法:  python src/_pages.py [pdf路径]
       (默认 paper/example.pdf; 并发编译时可用 -jobname 产出的私有 PDF)
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
pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "paper", "example.pdf")
d = fitz.open(pdf)

ANCHORS = ["问题分析", "问题一模型的建立与求解", "问题二模型的建立与求解",
           "问题三模型的建立与求解", "问题四模型的建立与求解",
           "模型评价与推广", "附录：结果文件与源程序"]
pos = {}
for i, p in enumerate(d):
    t = p.get_text().replace("\n", "")
    for k in ANCHORS:
        if k in t and k not in pos:
            pos[k] = i + 1
for k in ANCHORS:
    if k in pos:
        print(f"  p{pos[k]:3d}  {k}")
print(f"  总页数 {d.page_count}")

for a, b in zip(ANCHORS, ANCHORS[1:]):
    if a in pos and b in pos:
        print(f"  {a} -> {b}: {pos[b] - pos[a]} 页")
