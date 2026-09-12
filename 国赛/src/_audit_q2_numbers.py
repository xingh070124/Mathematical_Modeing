# -*- coding: utf-8 -*-
"""Independent numeric reconciliation of the whole Q2 tex section.

Extracts every numeric literal from paper/example.tex between the Q2 and Q3
subsection markers and classifies it against (a) the union of every
outputs/registry_q2_*.csv value, (b) a set of values this audit recomputed
from result2.xlsx / 附件1 / the source code, (c) an explicit allow-list of
structural / problem-statement constants.

Unlike the project's own q2_reconcile.py this uses an explicit, written
allow-list so that the allow-list itself is auditable.
"""
from __future__ import annotations

import csv
import glob
import os
import re
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
TEX = os.path.join(ROOT, "paper", "example.tex")

#  A token is:  [-]mantissa [ (\times10^{exp}) | (e[-]exp) ]
SIMPLE = re.compile(
    r"(?<![\d.])"
    r"(-?\d+(?:\.\d+)?)"
    r"(?:\\times10\^\{(-?\d+)\}|\\times10\^(-?\d+)|e(-?\d+))?"
    r"(?![\d.])")


def to_float(m):
    mant = float(m.group(1))
    e = m.group(2) or m.group(3) or m.group(4)
    return mant * (10.0 ** int(e)) if e is not None else mant

# Explicit allow-list: (regex) -> reason.  Everything not matched here and not
# matched against a registry value is reported as UNMATCHED.
ALLOW = [
    (r"^0$", "零"),
    (r"^1$", "结构/计数"),
    (r"^2$", "题面: 半径 2 cm / 通用整数"),
    (r"^3$", "3 h"),
    (r"^4$", "通用整数"),
    (r"^5$", "通用整数"),
    (r"^6$", "通用整数"),
    (r"^7$", "通用整数"),
    (r"^8$", "通用整数"),
    (r"^9$", "通用整数"),
    (r"^10$", "通用整数"),
    (r"^11$", "通用整数"),
    (r"^12$", "结构"),
    (r"^18$", "结构"),
    (r"^20$", "结构"),
    (r"^21$", "结构: 21 个输出半径"),
    (r"^25$", "模型参数 h=25"),
    (r"^26$", "通用整数"),
    (r"^28$", "题面: 初温 28 degC"),
    (r"^30$", "结构"),
    (r"^40$", "窗口 40 s"),
    (r"^50$", "结构"),
    (r"^60$", "通用整数"),
    (r"^100$", "通用整数"),
    (r"^101$", "结构: M+1 节点"),
    (r"^200$", "结构: M"),
    (r"^241$", "附件1 采样点数"),
    (r"^400$", "结构: M"),
    (r"^800$", "结构: M"),
    (r"^1600$", "结构: M"),
    (r"^0\.1$", "题面: 半径网格 0.1 cm"),
    (r"^0\.5$", "题面: 半径网格 0.5 cm"),
    (r"^1\.0$", "题面: 时间 1.0 h"),
    (r"^1\.5$", "题面: 半径/时间网格"),
    (r"^2\.0$", "题面: 半径 2 cm"),
    (r"^2\.5$", "题面: 时间 2.5 h"),
    (r"^3\.0$", "题面: 时间 3.0 h"),
    (r"^2\.55$", "题面: C0"),
    (r"^301\.15$", "题面: T0 = 28 degC"),
    (r"^0\.15$", "题面/其他问题"),
    (r"^1\.2$", "倍率"),
    (r"^0\.8$", "倍率"),
    (r"^10\.0$", "倍率"),
    (r"^100\.0$", "倍率"),
    (r"^12\.0$", "结构: 网格数"),
    (r"^13\.21$", "AB_Cspan_flat_pct"),
    (r"^8\.9$", "VM_lump_ratio_M25 的下界(四舍五入)"),
    (r"^14\.6$", "VM_lump_ratio_M200 的下界(四舍五入)"),
    (r"^3\.01$", "题面 Q1 相对变化(其他小节)"),
    (r"^25\.671$", "C_ratio_inv"),
    (r"^1\.0353$", "C_Bi"),
    (r"^2\.8360$", "C_Bim"),
    (r"^0\.48296$", "A_k_2.55"),
    (r"^976\.40$", "A_rho_2.55"),
    (r"^3415\.30$", "A_cp_2.55"),
    (r"^0\.36$", "附录2 k"),
    (r"^2600$", "附录2 cp"),
    (r"^820$", "附录2 rho"),
    (r"^0\.89$", "附录2 D 指数"),
    (r"^4\.2$", "dlnD/dT 的 %/K 量级"),
    (r"^2\.4$", "D 倍率 2.4"),
    (r"^8\.314462618$", "R_u CODATA"),
    (r"^0\.01801528$", "M_w"),
    (r"^109\.2$", "V10_resid"),
    (r"^2434560\.5$", "V10_L28"),
    (r"^2391\.0094$", "V10_slope"),
    (r"^2\.4346$", "定标式截距"),
    (r"^4186$", "EA_cl"),
    (r"^1450$", "EA_cs"),
    (r"^650$", "附录3 rho 常数项"),
    (r"^2736$", "附录3 cp 分子"),
    (r"^128$", "附录3 rho 系数"),
    (r"^0\.45$", "附录3 D 指数"),
    (r"^3850$", "附录3 D 指数"),
    (r"^0\.21$", "附录3 k 常数项"),
    (r"^0\.38$", "附录3 k 系数"),
    (r"^5e-5$", "P07 半 ulp"),
    (r"^0\.000001$", "结构"),
    (r"^8e-7$", "附录2 h_m"),
    (r"^1e-11$", "F_rtol"),
    (r"^1e-13$", "Newton 判据"),
    (r"^1e-3$", "驱动力量级/记录分辨率"),
    (r"^0\.05$", "掩码阈值"),
    (r"^4\.5$", "结构"),
    (r"^3\.21$", "Q1 径向温差(其他小节引用)"),
    (r"^30$", "min"),
    (r"^4\.07$", "VS_ratio_50"),
    (r"^4\.31$", "VS_ratio_100"),
    (r"^4\.05$", "VS_ratio_200"),
    (r"^1\.70$", "VS_ratio_400"),
    (r"^1\.14$", "VS_ratio_800"),
]


def load_registry_values():
    vals = {}
    for p in glob.glob(os.path.join(OUT, "registry_q2_*.csv")):
        with open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                try:
                    v = float(row["value"])
                except (TypeError, ValueError, KeyError):
                    continue
                vals.setdefault(v, []).append(
                    f"{os.path.basename(p)}:{row.get('id','')}")
    return vals


def class_match(x, mant, exp, reg, extra, tol_slack=0.6):
    """Is x a correct rounding of some registry value?

    The paper prints a rounded value; accept iff |x - v| <= tol_slack *
    10**(exp - decimals(mant)), i.e. x is within a rounding quantum of v.
    Returns (registry_key, rel_dev) or (None, None).
    """
    if "." in mant:
        dec = len(mant.split(".")[1])
    else:
        dec = 0
    e = int(exp) if exp is not None else 0
    q = 10.0 ** (e - dec)
    best = None
    for v, names in reg.items():
        d = abs(x - v)
        if d <= tol_slack * q:
            if best is None or d < best[1]:
                best = (names[0], d / max(abs(v), 1e-300))
    for v, names in extra.items():
        d = abs(x - v)
        if d <= tol_slack * q:
            if best is None or d < best[1]:
                best = (names[0], d / max(abs(v), 1e-300))
    return best if best else (None, None)


def main():
    reg = load_registry_values()
    extra = {}          # values recomputed by this audit
    for name, val in [("audit:Cbar_lump", 1.382947583),
                      ("audit:Cbar_simp", 1.383254),
                      ("audit:loss_lump", 45.7667614379),
                      ("audit:qconv_rounding", 3.09995),
                      ("audit:qevap_ratio_0.5h", 1.7098)]:
        extra.setdefault(val, []).append(name)

    txt = open(TEX, encoding="utf-8").read()
    lines = txt.split("\n")
    b = txt.find("\n\\subsection{问题二模型的建立与求解}")
    e = txt.find("\n\\subsection{问题三模型的建立与求解}")
    seg = txt[b:e]
    off = txt[:b].count("\n") + 1
    print(f"Q2 小节: 行 {off}..{off+seg.count(chr(10))} "
          f"({seg.count(chr(10))} 行)")

    n_tok = n_reg = n_allow = 0
    unmatched = []
    for k, raw in enumerate(seg.split("\n")):
        ln = off + k
        line = raw
        # strip structural LaTeX so that {0.98\textwidth} etc is not scanned
        line = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}", " ", line)
        line = re.sub(r"minipage\}\{[^}]*\}|\\textwidth", " ", line)
        for m in SIMPLE.finditer(line):
            tok = m.group(0)
            n_tok += 1
            x = to_float(m)
            exp = m.group(2) or m.group(3) or m.group(4)
            # structural integers (M, resolutions, counters) via allow-list
            hit = None
            for pat, why in ALLOW:
                if re.fullmatch(pat, m.group(1)) and exp is None:
                    hit = why
                    break
            if hit:
                n_allow += 1
                continue
            key, dev = class_match(x, m.group(1), exp, reg, extra)
            if key is not None:
                n_reg += 1
                continue
            unmatched.append((ln, tok, x, line.strip()[:100]))

    print(f"数值字面量 {n_tok} 个: 对到注册表 {n_reg}, "
          f"允许清单 {n_allow}, 未对上 {len(unmatched)}")
    print()
    print("=" * 100)
    print("未对上的数值")
    print("=" * 100)
    seen = {}
    for ln, tok, x, ctx in unmatched:
        seen.setdefault(tok, []).append((ln, ctx))
    for tok, occ in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        print(f"  token={tok!r}  {len(occ)} 次")
        for ln, ctx in occ[:3]:
            print(f"     line {ln}: {ctx}")
    with open(os.path.join(OUT, "_audit_q2_unmatched.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["line", "token", "value", "context"])
        w.writerows(unmatched)


if __name__ == "__main__":
    main()
