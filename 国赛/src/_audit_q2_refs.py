# -*- coding: utf-8 -*-
"""Check LaTeX cross-references in paper/example.tex and whether the figure
files referenced actually exist.  Also diff the Q2 section against the
_session-6 backup_ if one is available."""
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
txt = open(TEX, encoding="utf-8").read()
lines = txt.split("\n")

labels = re.findall(r"\\label\{([^}]*)\}", txt)
refs = re.findall(r"\\(?:ref|eqref|autoref)\{([^}]*)\}", txt)
print(f"labels ({len(labels)}): {sorted(labels)}")
print()
missing = sorted(set(refs) - set(labels))
print(f"refs ({len(set(refs))} distinct, {len(refs)} total)")
print(f"DANGLING refs (no matching label): {missing if missing else 'none'}")
for r in missing:
    for i, l in enumerate(lines, 1):
        if f"ref{{{r}}}" in l:
            print(f"   line {i}: {l.strip()[:120]}")
unused = sorted(set(labels) - set(refs))
print(f"labels never referenced: {unused if unused else 'none'}")

print()
print("includegraphics targets:")
for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", txt):
    tgt = m.group(1)
    p = os.path.join(ROOT, "paper", tgt)
    ok = os.path.exists(p)
    ln = txt[:m.start()].count("\n") + 1
    print(f"   line {ln:5d} {tgt:45s} exists={ok}")
    if not ok:
        for ext in (".pdf", ".png"):
            if os.path.exists(p + ext):
                print(f"        (found {tgt}{ext})")

print()
print("Q2 section boundary markers:")
b = txt.find(r"\subsection{问题二模型的建立与求解}")
e = txt.find(r"\subsection{问题三模型的建立与求解}")
print(f"   begin char {b} -> line {txt[:b].count(chr(10))+1}")
print(f"   end   char {e} -> line {txt[:e].count(chr(10))+1}")
print(f"   section length = {txt[b:e].count(chr(10))} lines")
print()
for key in ("sec:q2limit", "局限", "0.05", "驱动力", "无收缩", "111.57",
            "4 个数量级", "外推"):
    hits = [i for i, l in enumerate(lines, 1)
            if key in l and b <= txt.find(l) < e] if False else []
    idx = [i for i, l in enumerate(lines, 1) if key in l]
    inq2 = [i for i in idx if b < sum(len(x) + 1 for x in lines[:i - 1]) < e]
    print(f"  {key!r:16s} total lines {idx}   inside Q2: {inq2}")
