# -*- coding: utf-8 -*-
r"""把 paper/_abs_candidate.tex 组装成可单独排版的探测文档 paper/_abs_probe.tex.

为什么这样做: example.tex 可能被并发的 xelatex / 另一个会话占用 (写锁),
而我们只想检验"摘要是否仍落在第 1 页", 不需要整篇 40 页重新排版.
探测文档沿用 example.tex 的**同一份导言区** (\documentclass 到 \maketitle),
其后只放候选摘要, 因此第 1 页的版面与正式稿一致.

用法: python src/_abs_probe_build.py
产物: paper/_abs_probe.tex
"""
from __future__ import annotations

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
CAND = os.path.join(ROOT, "paper", "_abs_candidate.tex")
PROBE = os.path.join(ROOT, "paper", "_abs_probe.tex")

head = open(TEX, encoding="utf-8").read()
marker = " \\maketitle"
i = head.index(marker) + len(marker)
preamble = head[:i]

cand = open(CAND, encoding="utf-8").read()
# 候选文件首两行是说明性注释, 不进探测文档
cand = "\n".join(l for l in cand.splitlines() if not l.startswith("%"))

probe = (preamble + "\n\n" + cand + "\n\n"
         + "\\section{占位}\n占位, 仅用于让第 1 页之后的排版有内容。\n\n"
         + "\\end{document}\n")
open(PROBE, "w", encoding="utf-8").write(probe)
print(f"写出 {PROBE} ({len(probe)} 字符)")
print(f"导言区取自 {TEX} 的前 {i} 字符")
