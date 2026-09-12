# -*- coding: utf-8 -*-
"""只读探针: 定位修改方案涉及的锚点 (行号 + 上下文)."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
s = io.open("paper/example.tex", encoding="utf-8").read()

pats = {
    "t_dry 51.085 (三位)": r"51\.085(?!\d)",
    "t_dry 51.09 (摘要)": r"51\.09(?!\d)",
    "t_dry 57.42 (两位)": r"57\.42(?!\d)",
    "57.4223 (表9 基准)": r"57\.4223",
    "唯一…收缩模式": r"唯一.{0,14}收缩模式",
    "独立有限体积": r"独立有限体积",
    "1.71%": r"1\.71",
    "与环境完全平衡": r"与环境完全平衡",
    "label tab:q4": r"label\{tab:q4\}",
    "result2 10800": r"10800",
    "Jacobian 2.2x10^-7": r"2\.2[45]\\times10\^\{-7\}",
    "1.198 / 1.200": r"1\.19[89]|1\.200",
}

for k, p in pats.items():
    ms = list(re.finditer(p, s))
    print(f"{k:22s} 命中 {len(ms)}")
    for m in ms[:5]:
        ln = s[: m.start()].count("\n") + 1
        ctx = s[max(0, m.start() - 65): m.start() + 65].replace("\n", " ")
        print(f"    L{ln}: ...{ctx}...")
    print()
