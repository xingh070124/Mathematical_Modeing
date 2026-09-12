# -*- coding: utf-8 -*-
"""
_pages_sub.py -- 按标题锚点测量论文各部分的页数占用 (用于定位压缩重点).

要点
----
1. 先判 `\\subsubsection`, 再判 `\\section`: 正则 `\\(sub)*section` 会把
   `\\subsubsection` 也匹配上 (`subsub` + `section`), 故顺序不能反。
2. 锚点**按文件顺序逐个向后扫页**: 标题文字在别处(符号表、交叉引用、摘要)也会出现,
   取"首次出现"会把页号错误地前移。从上一个锚点所在页向后找首个匹配即可。
3. 浮动体(图/表)会浮动到其排版位置, 故页差是**近似**, 但足以比较各节量级。

运行: python src/_pages_sub.py [--sec 问题一]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
PDF = os.path.join(ROOT, "paper", "example.pdf")

RE_H1 = re.compile(r"\\section\{(.+?)\}\s*$")
RE_H2 = re.compile(r"\\subsection\{(.+?)\}\s*$")
RE_H3 = re.compile(r"\\subsubsection\{(.+?)\}\s*$")


def clean(s: str) -> str:
    """标题 -> PDF 文本里出现的形态 (去空白/去 LaTeX 命令与花括号)."""
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("{", "").replace("}", "").replace("~", "")
    s = s.replace("$", "").replace("\\", "")
    return re.sub(r"\s+", "", s)


def anchors():
    out = []
    for i, line in enumerate(open(TEX, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        for rx, lvl in ((RE_H3, "H3"), (RE_H2, "H2"), (RE_H1, "H1")):
            m = rx.match(line.strip())
            if m:
                out.append((i, lvl, m.group(1)))
                break
    return out


def pages_text(doc):
    return [p.get_text().replace("\n", "").replace(" ", "") for p in doc]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sec", default=None, help="只看某个 H2 节, 如 问题一")
    args = ap.parse_args()

    doc = fitz.open(PDF)
    pages = pages_text(doc)
    A = anchors()
    print(f"  PDF {doc.page_count} 页; 锚点 {len(A)} 个\n")

    rows, cur = [], 0
    for ln, lvl, title in A:
        key = clean(title)
        pg = None
        for i in range(cur, len(pages)):
            if key and key in pages[i]:
                pg, cur = i + 1, i
                break
        rows.append((ln, lvl, title, pg))

    for k, (ln, lvl, title, pg) in enumerate(rows):
        nxt = rows[k + 1][3] if k + 1 < len(rows) else doc.page_count
        span = (nxt - pg) if (pg and nxt) else None
        ind = {"H1": "", "H2": "  ", "H3": "    "}[lvl]
        sp = f"{span:3d} 页" if span is not None else "  ?  "
        print(f"  L{ln:5d} {ind}{lvl} p{pg if pg else '?':>3}  {sp}  {title}")


if __name__ == "__main__":
    main()
