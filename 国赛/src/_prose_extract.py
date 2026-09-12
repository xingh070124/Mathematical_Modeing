# -*- coding: utf-8 -*-
r"""从 paper/example.tex 抽出**散文正文**(带原始行号), 供逐句润色使用.

规则:
  * 跳过 algorithm/algorithmic/tabular/tabularx/verbatim/lstlisting/equation/align/
    gather/cases/split/tikzpicture/thebibliography 等环境的**内容**;
  * 保留 figure/table 的 \caption (图注表注也是要润色的散文);
  * 只输出含 >=3 个汉字的行;
  * 去掉 LaTeX 命令, 只留可读文字, 行首标出原始行号 L####.

产物: paper/_prose_dump.txt
用法: python src/_prose_extract.py
"""
from __future__ import annotations

import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
OUT = os.path.join(ROOT, "paper", "_prose_dump.txt")

SKIP_ENVS = ["algorithm", "algorithmic", "tabular", "tabularx", "longtable",
             "verbatim", "lstlisting", "equation", "align", "align*",
             "gather", "gather*", "cases", "split", "tikzpicture",
             "thebibliography", "equation*", "aligned"]
KEEP_ENVS = ["figure", "table", "minipage", "center", "quote", "abstract"]

CN = r"[\u4e00-\u9fff]"
lines = open(TEX, encoding="utf-8").read().splitlines()

depth = {e: 0 for e in SKIP_ENVS}
out = []
for i, raw in enumerate(lines, 1):
    l = raw
    if l.lstrip().startswith("%"):
        continue
    # 进入/退出被跳过的环境
    for e in SKIP_ENVS:
        if re.search(r"\\begin\{" + re.escape(e) + r"\}", l):
            depth[e] += 1
        if re.search(r"\\end\{" + re.escape(e) + r"\}", l):
            depth[e] -= 1
    if any(v > 0 for v in depth.values()):
        continue
    if r"\end{" in l:
        pass
    txt = l
    txt = re.sub(r"\\caption\{?", " ", txt)
    txt = re.sub(r"\\label\{[^}]*\}", " ", txt)
    txt = re.sub(r"\\ref\{([^}]*)\}", r"<\1>", txt)
    txt = re.sub(r"\\upcite\{([^}]*)\}", r"[\1]", txt)
    txt = re.sub(r"\\begin\{[^}]*\}|\\end\{[^}]*\}", " ", txt)
    txt = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", txt)
    txt = re.sub(r"\$[^$]*\$", " ⌁ ", txt)
    txt = re.sub(r"[{}$\\&_^~]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(re.findall(CN, txt)) >= 3:
        out.append(f"L{i:5d} | {txt}")

open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"写出 {OUT}: {len(out)} 行散文, "
      f"{sum(len(re.findall(CN, l)) for l in out)} 汉字")
