# -*- coding: utf-8 -*-
"""定位未对上的数值在 example.tex 中的位置与上下文 (供人工判断)."""
import csv
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import q2_reconcile as R  # noqa: E402

rep = os.path.join(ROOT, "outputs", "reconciliation_q2.csv")
unmatched = []
with open(rep, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        if row.get("verdict") == "UNMATCHED":
            unmatched.append((row["token"], row.get("line", ""), row.get("scope", "")))

lines = io.open(os.path.join(ROOT, "paper", "example.tex"),
                encoding="utf-8").read().splitlines()
seen = set()
for tok, ln, scope in unmatched:
    if tok in seen:
        continue
    seen.add(tok)
    hits = [i + 1 for i, l in enumerate(lines) if tok.replace("e-", "\\times10^{-")
            .replace("e", "\\times10^{")[:4] in l or tok in l]
    ctx = ""
    for h in hits[:1]:
        ctx = lines[h - 1].strip()[:150]
    print(f"{tok:16s} scope={scope:10s} line={ln:>6s}  ctx={ctx}")
