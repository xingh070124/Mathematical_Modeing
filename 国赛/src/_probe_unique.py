# -*- coding: utf-8 -*-
"""只读探针: 检查论文中"唯一收缩模式"的表述与 eta 族的位置."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
s = io.open("paper/example.tex", encoding="utf-8").read()
for pat in (r"唯一", r"均匀收缩", r"唯一.{0,40}收缩模式", r"\\eta"):
    ms = list(re.finditer(pat, s))
    print(f"--- {pat}  命中 {len(ms)} ---")
    for m in ms[:6]:
        a, b = max(0, m.start() - 130), m.start() + 160
        print("   ...", s[a:b].replace("\n", " ").strip())
    print()
