# -*- coding: utf-8 -*-
"""只读探针: 核查 R2-m3 关于 1.71% 的断言 —— 论文是否在别处把 1.71% 当作可略依据."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
s = io.open("paper/example.tex", encoding="utf-8").read()

for pat, label in ((r"1\.71", "字面 1.71"),
                   (r"残余项", "残余项"),
                   (r"1\.7073", "1.7073"),
                   (r"基准依赖", "基准依赖"),
                   (r"18\.45", "18.45%")):
    ms = list(re.finditer(pat, s))
    print(f"=== {label} ({pat}) 命中 {len(ms)} ===")
    for m in ms:
        ln = s[: m.start()].count("\n") + 1
        ctx = s[max(0, m.start() - 180): m.start() + 180].replace("\n", " ")
        print(f"  L{ln}: ...{ctx}...")
    print()
