# -*- coding: utf-8 -*-
r"""扫描排版层面的"机器味"缺陷 (对象是**编译后的 PDF**, 不是源码).

最典型的一条: 源码里在中文逗号/句号前换行, LaTeX 把换行当一个空格, 于是
渲染出 "定标得到 ，其相对份额" 这种标点前带空格的排版错误 —— 人写稿不会这样.

同时统计: 标点后缺空格(中英之间)、重复标点、破折号出现页.

用法: python src/_typo_scan.py [pdf路径]
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "paper", "build_probe", "_final_check.pdf")
TEX = os.path.join(ROOT, "paper", "example.tex")

doc = fitz.open(PDF)
pages = [p.get_text() for p in doc]
print(f"PDF: {PDF}  ({doc.page_count} 页)")

CHECKS = [
    ("标点前有空格 (，。；：、）", r"[ \u3000][，。；：、）]"),
    ("标点后有空格 (（、 等)", r"[（、][ \u3000]"),
    ("重复标点", r"[，。；]{2,}"),
    ("破折号 ——", r"——"),
    ("半角逗号混排", r"[\u4e00-\u9fff],[\u4e00-\u9fff]"),
    ("半角句号混排", r"[\u4e00-\u9fff]\.[\u4e00-\u9fff]"),
]
tot = Counter()
print()
for name, pat in CHECKS:
    hits = []
    for i, t in enumerate(pages, 1):
        for m in re.finditer(pat, t):
            a = max(0, m.start() - 22)
            hits.append((i, t[a:m.end() + 12].replace("\n", " ")))
    tot[name] = len(hits)
    print(f"  {name:26s} {len(hits):5d}")
    for pg, ctx in hits[:6]:
        print(f"      p{pg:<3d} …{ctx}…")

print()
print("=" * 78)
print("源码层面: 行尾换行紧接标点的位置 (这些渲染出来会多一个空格)")
print("=" * 78)
lines = open(TEX, encoding="utf-8").read().splitlines()
bad = []
for i in range(len(lines) - 1):
    cur, nxt = lines[i].rstrip(), lines[i + 1].lstrip()
    if not cur or not nxt:
        continue
    if cur.lstrip().startswith("%") or nxt.startswith("%"):
        continue
    if re.match(r"^[，。；：、）】》]", nxt):
        bad.append((i + 1, cur[-24:], nxt[:24]))
print(f"  共 {len(bad)} 处")
for ln, a, b in bad:
    print(f"    L{ln:5d} …{a}  ⏎  {b}…")
