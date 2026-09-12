# -*- coding: utf-8 -*-
"""打印指定描边索引的路径项, 用于确认审计器报告的是哪条路径."""
from __future__ import annotations

import json
import os
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1] if len(sys.argv) > 1 else "fig_q2_latent"
pdf = os.path.join(root, "paper", "figures", f"{name}.pdf")
aud = pdf.rsplit(".pdf", 1)[0] + ".collision-audit.json"

doc = fitz.open(pdf)
page = doc[0]
drawings = page.get_drawings()
d = json.load(open(aud, encoding="utf-8"))

want = set()
for f in d.get("findings", []):
    if f.get("severity") == "FAIL" and f.get("object_indexes"):
        want.update(int(i) for i in f["object_indexes"])
print(f"{name}: 待查描边索引 {sorted(want)} (共 {len(drawings)} 条)")
for i in sorted(want):
    dr = drawings[i]
    print(f"\n--- stroke[{i}] rect={tuple(round(v,1) for v in dr['rect'])} "
          f"width={dr.get('width')} type={dr.get('type')} items={len(dr['items'])}")
    for op, *rest in dr["items"]:
        shape = []
        for x in rest:
            if isinstance(x, fitz.Point):
                shape.append((round(x.x, 1), round(x.y, 1)))
            elif isinstance(x, fitz.Rect):
                shape.append(tuple(round(v, 1) for v in x))
            else:
                shape.append(x)
        print(f"      {op} {shape}")
