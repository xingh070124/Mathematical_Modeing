# -*- coding: utf-8 -*-
"""汇总/复跑 Q2 图件的 PDF 审计结果 (文本字号 + 碰撞)."""

from __future__ import annotations

import glob
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGD = os.path.join(ROOT, "paper", "figures")

names = ["fig_q2_coupling", "fig_q2_energy_form", "fig_q2_latent",
         "fig_q2_temp_results", "fig_q2_moist_results", "fig_q2_sensrob"]
for n in names:
    p = os.path.join(FIGD, f"{n}.collision-audit.json")
    if not os.path.exists(p):
        print(f"{n:22s} [no audit json]")
        continue
    d = json.load(open(p, encoding="utf-8"))
    s = d.get("summary", {})
    print(f"{n:22s} verdict={d.get('verdict'):20s} fail={s.get('fail')} warn={s.get('warn')}")
    for f in d.get("findings", []):
        if f.get("severity") != "FAIL":
            continue
        txt = f.get("text") or f.get("text_a") or ""
        other = f.get("other_text") or ""
        print(f"    - {f.get('kind'):22s} {str(txt)[:46]!r} vs {str(other)[:30]!r}")
