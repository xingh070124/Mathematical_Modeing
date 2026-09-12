# -*- coding: utf-8 -*-
r"""把不能浮动的手工表块改成浮动体, 以消除页底大片留白.

背景: 论文里的表大多写成
    \begin{center}
    \begin{minipage}{0.94\textwidth}
    ...\textbf{表 N ...}\\ tabular ...
    \end{minipage}
    \end{center}
这是**正文流的一部分, 不能浮动**: 一旦当前页剩余高度放不下, LaTeX 只能提前断页,
页底就留下几十到两百 pt 的空白. 改成 table 浮动体后可自动挪到合适位置, 正文把页面填满.
表题是手写的 \textbf{表 N ...}, 不含 \caption, 所以**表号与引用完全不变**.

同时删掉参考文献与附录之间的 \newpage —— 参考文献只有 18 行, 该页原本空出 295 pt.

用法: python src/_floatify_tables.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
DRY = "--dry-run" in sys.argv

lines = open(TEX, encoding="utf-8", newline="").read().split("\n")

out = list(lines)
wrapped = []
i = 0
while i < len(out):
    if out[i].strip() == r"\begin{center}":
        # 向后找第一个非空行, 必须是 minipage 开头
        j = i + 1
        while j < len(out) and out[j].strip() == "":
            j += 1
        if j < len(out) and out[j].lstrip().startswith(r"\begin{minipage}"):
            # 找配对的 \end{center}
            k = j
            while k < len(out) and out[k].strip() != r"\end{center}":
                k += 1
            if k < len(out):
                if any(l.strip() == r"\begin{center}" for l in out[j:k]):
                    i += 1
                    continue                      # 内部还有 center, 跳过
                out[i] = out[i].replace(r"\begin{center}",
                                        r"\begin{table}[htbp]" + "\n" + r"\centering")
                out[k] = out[k].replace(r"\end{center}", r"\end{table}")
                wrapped.append((i + 1, k + 1))
                i = k + 1
                continue
    i += 1

print(f"包成浮动体的表块: {len(wrapped)} 处")
for a, b in wrapped:
    print(f"   L{a:5d} ~ L{b:5d}")

# 删掉附录前的 \newpage
src = "\n".join(out)
NEWPAGE_OLD = "\\newpage\n%附录\n\\begin{appendices}"
NEWPAGE_NEW = "%附录\n\\begin{appendices}"
n_np = src.count(NEWPAGE_OLD)
print(f"\n附录前的 \\newpage: 匹配 {n_np} 处")
if n_np == 1:
    src = src.replace(NEWPAGE_OLD, NEWPAGE_NEW, 1)

if DRY:
    print("--dry-run: 未写文件")
    raise SystemExit(0 if n_np <= 1 else 1)

bak = TEX + time.strftime(".bak_floats_%Y%m%d_%H%M%S")
open(bak, "w", encoding="utf-8", newline="").write("\n".join(lines))
open(TEX, "w", encoding="utf-8", newline="").write(src)
chk = open(TEX, encoding="utf-8", newline="").read()
print(f"备份 {os.path.basename(bak)}")
print(f"table 浮动体: {chk.count(chr(92) + 'begin{table}')} 个; "
      f"center 剩余 {chk.count(chr(92) + 'begin{center}')} 个; "
      f"newpage 剩余 {chk.count(chr(92) + 'newpage')} 个")
