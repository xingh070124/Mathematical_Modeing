# -*- coding: utf-8 -*-
r"""核对"表 N"的位置: 每张表出现在第几页, 与引用它的正文差几页.

把表改成浮动体后最大的风险是**表漂移**: 正文写"如下表", 表却跑到几页之外.
本脚本列出每张表所在页, 以及首次引用该表号的页, 给出漂移页数.

用法: python src/_table_map.py [pdf路径]
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
PDF = os.path.join(ROOT, "paper", "build_probe", "_final_check.pdf")
if len(sys.argv) > 1:
    PDF = sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(ROOT, sys.argv[1])

doc = fitz.open(PDF)
pages = [p.get_text().replace("\n", "") for p in doc]

CAP = re.compile(r"表\s?(\d+)\s")          # 表题(或引用)
cap_page, ref_page = {}, {}
for i, t in enumerate(pages, 1):
    for m in CAP.finditer(t):
        n = int(m.group(1))
        # 表题: 该表号出现在一段较长的标题性文字里; 简化处理——首次出现记为引用,
        # 若该页的行首就是 "表 N " 则记为表题所在页
        if n not in ref_page:
            ref_page[n] = i
    for ln in pages[i - 1].split("\u3000"):
        pass

# 更可靠: 用行的 bbox 判断"表 N ..."独占一段(表题行)
for i, p in enumerate(doc, 1):
    for b in p.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        txt = "".join(sp["text"] for ln in b.get("lines", []) for sp in ln["spans"])
        m = re.match(r"^表\s?(\d+)\s", txt.strip())
        if m:
            n = int(m.group(1))
            if n not in cap_page:
                cap_page[n] = i

print(f"PDF {PDF}  {doc.page_count} 页")
print(f"检出的表题: {len(cap_page)} 张\n")
print(f"{'表号':>4} {'表题页':>7} {'正文首次提及页':>14} {'漂移':>5}")
print("-" * 40)
worst = 0
for n in sorted(cap_page):
    c = cap_page[n]
    r = ref_page.get(n, 0)
    d = c - r if r else 0
    worst = max(worst, d)
    flag = "  <<<" if d > 2 else ""
    print(f"{n:>4} {c:>7} {r:>14} {d:>5}{flag}")
print(f"\n最大漂移: {worst} 页")
