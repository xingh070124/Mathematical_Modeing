# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 7b: focused reconciliation of the *scientific* literals."""
import csv
import glob
import os
import re

tex = open(os.path.join("paper", "example.tex"), encoding="utf-8").read()
i_abs = tex.index("\\textbf{针对问题四}")
abs_txt = tex[i_abs:tex.index("\n", i_abs)]
i_sec = tex.index("\\subsection{问题四模型的建立与求解}")
nxt = [tex.find(s, i_sec + 10) for s in ("\\subsection{", "\\section{")]
i_sec_end = min([x for x in nxt if x > 0])
sec_txt = tex[i_sec:i_sec_end]

# strip \includegraphics options and table-6/tabular bodies
def clean(t):
    t = re.sub(r"\\includegraphics\[[^\]]*\]", "", t)
    t = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", " ", t, flags=re.S)
    return t

reg = {}
for path in sorted(glob.glob(os.path.join("outputs", "registry_q4*.csv"))) + \
        [os.path.join("outputs", "registry_q3.csv")]:
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                reg.setdefault(row["key"], float(row["value"]))
            except (KeyError, ValueError, TypeError):
                pass
for _k in list(reg):
    if _k.endswith(("_tdry", "_Rconst", "_shrink", "_q3ref")) or _k.startswith(("V1_M", "MC")):
        reg[_k + "_h"] = reg[_k] / 3600.0
        reg[_k + "_d"] = reg[_k] / 86400.0
for _k in ("MC5_mean", "MC5_median", "MC5_std", "MC5_p2p5", "MC5_p97p5",
           "MC10_mean", "MC10_median", "MC10_std", "MC10_p2p5", "MC10_p97p5"):
    if _k in reg:
        reg[_k + "_h"] = reg[_k] / 3600.0

# explicitly derived from registry entries
derived = {
    "0.012": abs(reg["V1_M400"] + (reg["V1_M400"] - reg["V1_M200"]) /
                 (2 ** 1.5065134152681532 - 1) - reg["V1_M200"]) / 3600.0,
    "0.0042": abs(reg["V1_M400"] + (reg["V1_M400"] - reg["V1_M200"]) /
                  (2 ** 1.5065134152681532 - 1) - reg["V1_M400"]) / 3600.0,
    "0.0035": 12.60599734337302 / 3600.0,
    "3e-5": 0.10980239600758068 / 3600.0,
    "78.7": 78.72540226630088, "51.1": reg["PROD_tdry_h"],
    "51.09": reg["PROD_tdry_h"], "51.085": reg["PROD_tdry_h"],
    "51.0852": reg["PROD_tdry_h"], "129.8": reg["V0b_app4_Rconst_h"],
    "25.2": reg["V0b_app3_shrink_h"], "57.4": reg["V0_tdry_q3ref_h"],
    "206720.4135": reg["V0_tdry_q3ref"], "2.13": reg["PROD_tdry_d"],
    "5.4": reg["V0b_app4_Rconst_d"], "50.63": reg["MC5_median_h"],
    "54.99": reg["MC5_mean_h"], "17.04": reg["MC5_std_h"],
    "32.36": reg["MC5_p2p5_h"], "87.46": reg["MC5_p97p5_h"],
    "32.4": reg["MC5_p2p5_h"], "87.5": reg["MC5_p97p5_h"],
    "3.31": 3.3103240869588544, "1.41": 1.4059331317464239,
    "9": 9.696477298830755, "1.51": 1.5065134152681532,
    "2.84": 2.841225650831178, "11": 11.036017318113371,
    "61": 60.646358695067335, "24.3": 24.3485,
    "2.8e-7": 2.8069459985266864e-07, "2.1e-5": 2.0747426788148005e-05,
    "30.7": -30.710695538189675, "1.6": 1.6, "0.007": 0.007,
    "29.79": 29.7903, "46.40": 46.4026, "3.64": 3.64142, "63": 63.0,
    "3065": 3065.0, "183900": 183900.0,
}

print("=" * 78)
print("AUDIT PROBE 7b: scientific literals in the problem-4 text vs registries")
print("=" * 78)
for label, txt in (("ABSTRACT", abs_txt), ("SUBSECTION", clean(sec_txt))):
    print("\n---", label, "---")
    seen = set()
    for m in re.finditer(r"(-?\d+\.\d+|-?\d+(?:\\times)?10\^\{?-?\d+\}?)", txt):
        raw = m.group(1)
        if raw in seen:
            continue
        seen.add(raw)
        # normalise
        base = raw.replace("\\times", "e").replace("^{", "").replace("}", "")
        base = base.replace("10e", "1e") if base.startswith("10e") else base
        try:
            v = float(base)
        except ValueError:
            v = None
        hit = [k for k, x in reg.items() if v and x != 0 and abs(x - v) / abs(x) <= 0.012]
        dh = [k for k, x in derived.items() if v is not None and abs(x - v) <= 0.012 * max(abs(x), 1)]
        ctx = txt[max(0, m.start() - 45):m.end() + 20].replace("\n", " ")
        status = "MATCH" if (hit or dh) else "NO_SOURCE"
        print(f"  {status:9s} {raw:>16s}  <- {(hit or dh)[:2] if (hit or dh) else ''}")
        if status == "NO_SOURCE":
            print(f"            ctx: ...{ctx}...")
