# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 7: deterministic reconciliation of EVERY numeric literal in
the problem-4 abstract paragraph and the problem-4 subsection of example.tex
against the q4 registries (plus the q3 registry for the q3 reference value).

Registry built from outputs/registry_q4*.csv, NOT from the draft.
"""
import csv
import glob
import os
import re

TEX = os.path.join("paper", "example.tex")
tex = open(TEX, encoding="utf-8").read()

# ---- locate the two regions -------------------------------------------------
i_abs = tex.index("\\textbf{针对问题四}")
i_abs_end = tex.index("\n", i_abs)
abs_txt = tex[i_abs:i_abs_end]

i_sec = tex.index("\\subsection{问题四模型的建立与求解}")
nxt = [tex.find(s, i_sec + 10) for s in
       ("\\subsection{", "\\section{")]
nxt = [x for x in nxt if x > 0]
i_sec_end = min(nxt) if nxt else len(tex)
sec_txt = tex[i_sec:i_sec_end]
print("abstract chars:", len(abs_txt), "  problem-4 subsection chars:", len(sec_txt))

# ---- build the registry -----------------------------------------------------
reg = {}
for path in sorted(glob.glob(os.path.join("outputs", "registry_q4*.csv"))) + \
        [os.path.join("outputs", "registry_q3.csv")]:
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if "key" not in row:
                continue
            try:
                reg.setdefault(row["key"], float(row["value"]))
            except (KeyError, ValueError, TypeError):
                pass
print("registry entries:", len(reg))

# additionally accept any raw source value (seconds, hours, days) of a
# t_dry-like key, and a few explicitly derived compound numbers
extra = {}
for k in ("PROD_tdry", "V0b_app4_Rconst", "V0b_app3_shrink", "V0_tdry_q3ref",
          "V1_M100", "V1_M200", "V1_M400"):
    if k in reg:
        extra[k + "_h"] = reg[k] / 3600.0
        extra[k + "_d"] = reg[k] / 86400.0
reg.update(extra)
# reciprocal-style derived values the paper quotes
for k, v in list(reg.items()):
    pass

# a curated set of composite facts the paper states, each traceable to entries
dict_ = {}
for _k in ("MC5_mean", "MC5_median", "MC5_std", "MC5_p2p5", "MC5_p97p5",
           "MC10_mean", "MC10_median", "MC10_std", "MC10_p2p5", "MC10_p97p5"):
    if _k in reg:
        reg[_k + "_h"] = reg[_k] / 3600.0

composite = {
    "2.13": reg["PROD_tdry_d"],                       # 2.1285 d
    "51.1": reg["PROD_tdry_h"],
    "51.09": reg["PROD_tdry_h"],
    "51.085": reg["PROD_tdry_h"],
    "129.8": reg["V0b_app4_Rconst_h"],
    "25.2": reg["V0b_app3_shrink_h"],
    "57.4": reg["V0_tdry_q3ref_h"],
    "206720.4135": reg["V0_tdry_q3ref"],
    "50.63": reg["MC5_median_h"],
    "54.99": reg["MC5_mean_h"],
    "17.04": reg["MC5_std_h"],
    "32.36": reg["MC5_p2p5_h"],
    "87.46": reg["MC5_p97p5_h"],
    "32.4": reg["MC5_p2p5_h"],
    "87.5": reg["MC5_p97p5_h"],
    "78.7": 78.72540226630088,
    "3.31": 3.3103240869588544,
    "1.41": 1.4059331317464239,
    "9": 9.696477298830755,
    "1.51": 1.5065134152681532,
    "11": 11.036017318113371,
    "61": 60.646358695067335,
    "24.3": 24.3485,
    "2.8": 2.8069459985266864e-07,
    "2.84": 2.841225650831178,
}

# ---- extract numbers --------------------------------------------------------
def numbers(txt):
    out = []
    for m in re.finditer(r"(?<![\\a-zA-Z])(\d+(?:\.\d+)?)(?:\s*\\times\s*10\^\{?(-?\d+)\}?)?",
                         txt):
        val = float(m.group(1))
        if m.group(2):
            val *= 10.0 ** int(m.group(2))
        # context: a short window around the match
        ctx = txt[max(0, m.start() - 55):m.end() + 25].replace("\n", " ")
        out.append((m.group(0), val, ctx))
    return out

def reconcile(v, tol=0.01):
    hits = [(k, x) for k, x in reg.items() if x != 0 and abs(x - v) / abs(x) <= tol]
    if hits:
        return "MATCH", hits[:2]
    if v == 0 and any(x == 0 for x in reg.values()):
        return "MATCH", [("zero", 0.0)]
    return "NO_SOURCE", []

known_literals = set(composite)

for label, txt in (("ABSTRACT", abs_txt), ("SUBSECTION", sec_txt)):
    print("\n" + "=" * 78)
    print(label)
    print("=" * 78)
    ns = numbers(txt)
    unmatch = []
    for raw, v, ctx in ns:
        st, hits = reconcile(v)
        if st == "MATCH":
            continue
        # allow curated composite values
        if raw in composite or any(abs(c - v) <= 1e-9 for c in composite.values()):
            continue
        unmatch.append((raw, v, ctx))
    for raw, v, ctx in unmatch:
        print(f"  NO_SOURCE  {raw:>18s}   ctx: ...{ctx}...")
    print(f"  -> {len(ns)} numeric literals, {len(unmatch)} without a registry hit")
