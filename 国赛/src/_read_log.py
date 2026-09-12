# -*- coding: utf-8 -*-
"""打印 xelatex 日志中所有错误的完整上下文 (含 TeX 的 l.NNN 指针)."""
from __future__ import annotations

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "paper", "_pc.log")
L = open(LOG, "rb").read().decode("utf-8", errors="replace").splitlines()
print(f"总行数 {len(L)}")

# 所有以 ! 开头的行 (LaTeX 错误)
errs = [(i, l) for i, l in enumerate(L) if l.startswith("!")]
print(f"错误行 {len(errs)} 个")
for i, l in errs[:4]:
    print("=" * 76)
    print(f"  行 {i}: {l}")
    for j in range(i, min(len(L), i + 12)):
        print(f"   {j:6d}: {L[j]}")

print("\n--- l.NNN 指针 (去重) ---")
seen = []
for l in L:
    if l.startswith("l.") and l not in seen:
        seen.append(l)
for l in seen[:12]:
    print("   ", l)
