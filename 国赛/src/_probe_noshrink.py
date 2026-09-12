# -*- coding: utf-8 -*-
"""只读探针: 打印论文中对"问题一/二不收缩"假设的表述全文 (供评审核对)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
s = io.open("paper/example.tex", encoding="utf-8").read()
for key in ("预热平衡阶段（$1800", "收缩效应在问题四中显式考虑"):
    i = s.find(key)
    print("=" * 70)
    print(f"key = {key!r}  found at char {i}")
    print("=" * 70)
    if i >= 0:
        print(s[max(0, i - 320):i + 900])
    print()
