# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 5: INDEPENDENT reconciliation of paper 表6 against result4.xlsx.

Does not import q4_reconcile.  Reads the xlsx and the tex with its own logic.
"""
import os
import re

import numpy as np
import openpyxl

XLSX = os.path.join("outputs", "result4.xlsx")
TEX = os.path.join("paper", "example.tex")
TDRY = 183906.71282718718

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))
hdr = rows[0]
body = [r for r in rows[1:] if r[0] is not None]
print("=" * 74)
print("AUDIT PROBE 5: independent reconciliation of 表6 vs result4.xlsx")
print("=" * 74)
print("sheet:", ws.title, " header:", hdr[0], "| ncols:", len(hdr),
      "| nrows:", len(body))
print("first radius cols:", hdr[1:5], " last two:", hdr[-2:])
ts = [int(r[0]) for r in body]
print("t range:", ts[0], "..", ts[-1], " step ok:", ts == list(range(60, 60*(len(ts)+1), 60)))

# --- pull table 6 out of the tex ---
tex = open(TEX, encoding="utf-8").read()
i0 = tex.index("\\textbf{表~6\\quad")
i1 = tex.index("\\end{tabular}", i0)
blk = tex[i0:i1]
texrows = []
for line in blk.splitlines():
    if "&" not in line:
        continue
    if any(k in line for k in ("时间", "toprule", "midrule", "bottomrule", "tabular")):
        continue
    cells = [c.strip() for c in line.split("&")]
    cells[-1] = cells[-1].replace("\\\\", "").strip()
    texrows.append(cells)
print("tex 表6 rows parsed:", len(texrows))

colmap = [1, 6, 11, 16, len(hdr) - 1]
names = ["0.0", "0.5", "1.0", "1.5", "surface"]
bad = 0
print("")
print("  t/h      col   tex      xlsx      ok")
for cells in texrows:
    tstr = cells[0].replace("$", "").replace("\\mathbf{", "").replace("}", "")
    try:
        th = float(tstr)
    except ValueError:
        continue
    isdry = abs(th - TDRY / 3600.0) < 0.01
    if isdry:
        k = len(body) - 1
    else:
        k = int(round(th * 3600.0 / 60.0)) - 1
    if k < 0 or k >= len(body):
        print("   ROW OUT OF RANGE", th)
        bad += 1
        continue
    row = body[k]
    if abs(int(row[0]) - 60 * (k + 1)) > 1e-9:
        print("   time mismatch at k", k)
    for jj, c in enumerate(cells[1:5 + 1]):
        cc = c.replace("$", "").replace("\\mathbf{", "").replace("}", "").strip()
        j = colmap[jj]
        if cc in ("—", "-", "--", ""):
            if row[j] is not None:
                print(f"   {th:9.4f} {names[jj]:>7s}  tex='-'  xlsx={row[j]}  MISMATCH")
                bad += 1
            continue
        v_tex = float(cc)
        v_x = row[j]
        ok = v_x is not None and abs(round(float(v_x), 4) - round(v_tex, 4)) < 1e-12
        if not ok:
            bad += 1
        print(f"   {th:9.4f} {names[jj]:>7s}  {v_tex:8.4f}  "
              f"{'None' if v_x is None else format(float(v_x), '.4f'):>8s}  "
              f"{'OK' if ok else 'MISMATCH'}")
print("")
print("  total mismatches:", bad)

# --- structural checks on the xlsx itself ---
print("")
print("--- xlsx structure ---")
nullmask = np.array([[v is None for v in r[1:]] for r in body])
print("  non-null cells:", int((~nullmask).sum()), "of", nullmask.size)
ncols_radius = len([h for h in hdr[1:] if isinstance(h, (int, float))])
print("  numeric radius columns:", ncols_radius)
# per-row first null column index (should be monotone non-increasing count)
firstnull = []
for r in body:
    vals = r[1:-1]
    idx = next((i for i, v in enumerate(vals) if v is None), len(vals))
    firstnull.append(idx)
print("  first-null-index by row: row1 =", firstnull[0], " row3065 =", firstnull[-1])
print("  monotone non-increasing (surface shrinks):",
      all(firstnull[i] >= firstnull[i+1] for i in range(len(firstnull)-1)))
# surface column ordering: is the 'surface' column value equal to the value at
# r = R(t) i.e. should be the LOWEST of the non-nulls in each row?
print("")
print("--- is the surface column consistent with R(t)? ---")
import sys
sys.path.insert(0, "src")
from q4_solve import Q4Radius
rad = Q4Radius()
for k in (0, 1, 2799, 3064):
    Rcm = float(rad.R(float(body[k][0])))
    row = body[k]
    jR = int(round(Rcm / 0.1))
    print(f"  row {k+1} t={row[0]}s  R(t)={Rcm:.6f} cm -> nearest 0.1 col idx "
          f"{jR} value {row[1+jR] if 1+jR < len(row) else 'n/a'}; surface col = "
          f"{row[-1]}")

# --- precision ---
badp = 0
for r in body:
    for v in r[1:]:
        if v is None:
            continue
        if abs(round(float(v), 4) - float(v)) > 1e-12:
            badp += 1
print("  cells exceeding 4 dp:", badp)
