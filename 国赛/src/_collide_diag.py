# -*- coding: utf-8 -*-
"""诊断: 对某张 PDF, 打印每个 FAIL 的文字框与相交描边框, 并列出描边清单."""
from __future__ import annotations

import json
import os
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dump(pdf, max_items=14):
    doc = fitz.open(pdf)
    page = doc[0]
    print(f"=== {os.path.basename(pdf)}  page rect {page.rect} ===")
    aud = pdf.rsplit(".pdf", 1)[0] + ".collision-audit.json"
    if not os.path.exists(aud):
        print("  [no audit json]")
        return
    d = json.load(open(aud, encoding="utf-8"))
    strokes = []
    for dr in page.get_drawings():
        b = dr["rect"]
        strokes.append((round(b.x0, 1), round(b.y0, 1), round(b.x1, 1), round(b.y1, 1),
                        round(dr.get("width") or 0, 2), dr.get("type")))
    for f in d.get("findings", []):
        if f.get("severity") != "FAIL":
            continue
        tb = f.get("text_bbox")
        ob = f.get("other_bbox")
        print(f"\n[{f['kind']}] {str(f.get('text'))[:44]!r}")
        print(f"   text bbox {[round(v,1) for v in tb] if tb else None}")
        if f.get("other_text"):
            print(f"   other text {str(f['other_text'])[:44]!r}")
        if ob:
            print(f"   other bbox {[round(v,1) for v in ob]}")
        idx = f.get("object_indexes")
        if idx:
            print(f"   stroke idx {list(idx)[:6]}")
            for i in list(idx)[:3]:
                if 0 <= i < len(strokes):
                    print(f"      stroke[{i}] = {strokes[i]}")
    print(f"\n--- 描边总数 {len(strokes)} (前 {max_items} 条) ---")
    for i, s in enumerate(strokes[:max_items]):
        print(f"   {i:3d} {s}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "fig_q2_latent"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dump(os.path.join(root, "paper", "figures", f"{name}.pdf"))
