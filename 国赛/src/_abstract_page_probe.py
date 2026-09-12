# -*- coding: utf-8 -*-
"""测量摘要页(第 1 页)的版面余量, 用于判断摘要可以加长多少字.

输出: 页高 / 文本框上下边界 / 正文末行的下边界 / 剩余可用高度(pt 与 行数估计).
用法: python src/_abstract_page_probe.py [pdf 路径]
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
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "paper", "example.pdf")

d = fitz.open(PDF)
p = d[0]
H = p.rect.height
lines = []
for b in p.get_text("dict")["blocks"]:
    if b.get("type") != 0:
        continue
    for ln in b.get("lines", []):
        txt = "".join(s["text"] for s in ln["spans"])
        lines.append((ln["bbox"][1], ln["bbox"][3], txt))
lines.sort()
print(f"PDF      : {PDF}")
print(f"总页数   : {d.page_count}")
print(f"页高     : {H:.1f} pt  页宽 {p.rect.width:.1f} pt")
if not lines:
    print("第 1 页无文字")
    raise SystemExit(0)
top = min(x[0] for x in lines)
bot = max(x[1] for x in lines)
print(f"文字顶   : {top:.1f} pt")
print(f"文字底   : {bot:.1f} pt")
# 正文版心的下边界: 取页高减去下边距(类文件 cumcmthesis 默认 2.5cm 上下边距)
for margin_cm in (2.5, 2.54, 3.0):
    lim = H - margin_cm * 28.4527
    print(f"  若下边距 {margin_cm} cm -> 版心下界 {lim:.1f} pt, 余量 {lim - bot:.1f} pt"
          f" (~{(lim - bot) / 17.0:.1f} 行)")
print()
print("末 3 行:")
for a, b_, t in lines[-3:]:
    print(f"  y={a:7.1f}~{b_:7.1f}  {t[:60]}")

if "--all" in sys.argv[1:]:
    print()
    print("第 1 页全部文字行 (y 顶 / 字号 / 文本):")
    for a, b_, t in lines:
        print(f"  {a:7.1f}  {t[:70]}")
