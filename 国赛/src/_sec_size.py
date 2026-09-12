# -*- coding: utf-8 -*-
"""统计问题一小节的规模 (行数 / 子节 / 浮动体), 用于篇幅压缩的进度检查."""
from __future__ import annotations

import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "paper", "example.tex")
lines = io.open(P, encoding="utf-8").read().splitlines()

A = r"\subsection{问题一模型的建立与求解}"
B = r"\subsection{问题二模型的建立与求解}"
b = next(i for i, l in enumerate(lines) if l.startswith(A))
e = next(i for i, l in enumerate(lines) if l.startswith(B))
blk = lines[b:e]
print(f"问题一 subsection: 行 {b+1} .. {e}   共 {e-b} 行")
print("  子节:")
for i in range(b, e):
    if lines[i].startswith(r"\subsubsection{"):
        print(f"    L{i+1}: {lines[i][len(chr(92)+'subsubsection{'):-1]}")
nfig = sum(1 for l in blk if "includegraphics" in l)
ntab = sum(1 for l in blk if re.search(r"\\begin\{table\}", l))
nmin = sum(1 for l in blk if re.search(r"\\begin\{minipage\}", l))
neq = sum(1 for l in blk if re.search(r"\\begin\{(equation|align)\}", l))
print(f"  浮动体: 图 {nfig} 个, table 环境 {ntab} 个, minipage 块 {nmin} 个")
print(f"  公式环境: {neq} 个")
