# -*- coding: utf-8 -*-
r"""把 paper/_abs_candidate.tex 的摘要块写回 paper/example.tex.

为什么不直接用编辑器: 本工作区可能有并发会话在写 example.tex, 手工按行替换
会因"文件已变化"而失败或撞车. 这里做一次**定界替换**:
  读入 example.tex -> 定位 \begin{abstract} .. \end{abstract} -> 整块换成候选块
  -> 先备份 -> 写回 -> 重新读入校验.

候选块是经 paper/_abs_probe.tex 单独排版验证过"关键词仍在第 1 页"的那一份,
因此替换本身不改变版面结论.

用法: python src/_abs_apply.py [--candidate paper/_abs_candidate.tex]
"""
from __future__ import annotations

import os
import shutil
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")

cand = os.path.join(ROOT, "paper", "_abs_candidate.tex")
if "--candidate" in sys.argv:
    cand = os.path.join(ROOT, sys.argv[sys.argv.index("--candidate") + 1])
cand = os.path.abspath(cand)

src = open(TEX, encoding="utf-8").read()
block = open(cand, encoding="utf-8").read()
# 候选文件首部的说明性注释不进正文
block = "\n".join(l for l in block.splitlines() if not l.startswith("%"))
block = block.strip("\n")

B0, B1 = r"\begin{abstract}", r"\end{abstract}"
i0 = src.index(B0)
i1 = src.index(B1, i0) + len(B1)
old = src[i0:i1]

backup = TEX + time.strftime(".bak_abs_%Y%m%d_%H%M%S")
shutil.copy2(TEX, backup)

new = src[:i0] + block + src[i1:]
if new == src:
    print("候选块与现稿相同, 无需写回")
    raise SystemExit(0)
if "\\maketitle" not in src[:i0]:
    print("!! 摘要块不在 \\maketitle 之后, 拒绝写回")
    raise SystemExit(1)

open(TEX, "w", encoding="utf-8", newline="").write(new)

# 回读校验
chk = open(TEX, encoding="utf-8").read()
ok = "\n".join(l for l in block.splitlines()) in chk
print(f"备份      : {os.path.basename(backup)}")
print(f"原摘要块  : {len(old)} 字符")
print(f"新摘要块  : {len(block)} 字符")
print(f"写回校验  : {'OK 新块已在文件中' if ok else '!! 写回不一致'}")
print(f"文件长度  : {len(src)} -> {len(chk)} 字符")
assert ok, "写回校验失败"
