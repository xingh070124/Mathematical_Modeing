# -*- coding: utf-8 -*-
"""Audit C: classify every numeric literal in problem2_slove.md by its reconciliation status."""
from __future__ import annotations
import io, os, re, sys, csv
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

rows = list(csv.DictReader(io.open(os.path.join(OUT, "reconciliation_q2.csv"),
                                   encoding="utf-8-sig")))
slo = [r for r in rows if r["document"] == "problem2_slove.md"]
print("problem2_slove.md literals:", len(slo))
from collections import Counter
print(Counter(r["status"] for r in slo))

# ALLOW tokens that look like physical results: > 3 significant digits, not obvious structure
suspect = []
for r in slo:
    if r["status"] != "ALLOW":
        continue
    tok = r["token"]
    try:
        x = float(tok)
    except ValueError:
        continue
    mant = tok.lstrip("-").split("e")[0].replace(".", "").lstrip("0")
    if len(mant) >= 4 and abs(x) not in (0.0,) :
        suspect.append(r)
print(f"\nALLOW-listed literals with >=4 significant digits: {len(suspect)}")
seen = set()
for r in suspect:
    key = r["token"]
    if key in seen:
        continue
    seen.add(key)
    print(f"  {key:>14}  L{r['line']:>4}  {r['source'][:60]:<60} | {r['context'][:56]}")

# REGISTRY matches with a big relative deviation (loose match)
print("\nREGISTRY matches whose |dev| exceeds a tight 1e-9:")
bad = []
for r in slo:
    if r["status"] != "REGISTRY":
        continue
    try:
        d = abs(float(r["rel_dev"]))
    except ValueError:
        continue
    if d > 1e-9:
        bad.append((d, r))
bad.sort(key=lambda kv: -kv[0])
for d, r in bad[:60]:
    print(f"  dev={d:.3e}  tok={r['token']:>12} -> {r['source'][:28]:<28} L{r['line']:>4} | {r['context'][:60]}")
print(f"  ({len(bad)} such matches)")
