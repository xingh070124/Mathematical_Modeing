# -*- coding: utf-8 -*-
"""
_q4tbl_note.py -- 给论文表 6 补一条表注, 说明 1.5 cm 列为空的物理原因.

背景: 题面 表 6 的列含 1.5 cm, 而问题四的药材在 3.64 h 时半径已缩到 1.5 cm 以下,
故 6 h 起的每一行该位置都在药材之外, 表中记 "—". 正文已有说明, 但表本身没有注,
读者只看表容易误读为"缺算". 本脚本加一条紧贴表格的表注.

做法(避开并发写入竞态): 读 → 唯一性断言 → 整文件写回 → 回读校验; 并先备份.
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")

ANCHOR = ("$51.0852$ & $\\mathbf{0.1500}$ & $0.1413$ & $0.1080$ & — & $0.0526$ \\\\\n"
          "\\bottomrule\n"
          "\\end{tabular}\n"
          "\\end{minipage}")

NOTE = ("""
\\vspace{3pt}
{\\footnotesize 注：$r=1.5\\,\\mathrm{cm}$ 处的药材在 $t=3.64\\,\\mathrm{h}$ 即被收缩越过，
其后的半径 $R(6\\,\\mathrm{h})=1.374\\,\\mathrm{cm}$ 已小于 $1.5\\,\\mathrm{cm}$，
故 $6\\,\\mathrm{h}$ 起各行该位置均记“—”，并非缺算；末列“药材表面”为 $r=R(t)$ 处的值，
$R(t)$ 由 $2.000\\,\\mathrm{cm}$ 缩至 $1.200\\,\\mathrm{cm}$。若改按材料点口径
（初始位于该半径处的干物质）取值，则该列全程有定义，对应数值见
\\texttt{result4.xlsx} 的“材料坐标”工作表。}
\\end{minipage}""")


def main():
    s = io.open(TEX, encoding="utf-8").read()
    if "处的药材在 $t=3.64" in s and "并非缺算" in s:
        print("表注已存在, 无需重复添加")
        return 0
    n = s.count(ANCHOR)
    print(f"锚点出现次数 = {n}")
    assert n == 1, f"锚点不唯一 ({n}), 中止以免误改"
    bak = TEX + ".bak_tblnote_" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(TEX, bak)
    print("备份:", os.path.basename(bak))
    s2 = s.replace(ANCHOR, ANCHOR.replace("\\end{minipage}", "") + NOTE.lstrip("\n"))
    io.open(TEX, "w", encoding="utf-8", newline="").write(s2)
    # 回读校验
    chk = io.open(TEX, encoding="utf-8").read()
    assert "并非缺算" in chk, "回读未见表注"
    assert chk.count("\\begin{table}") == s.count("\\begin{table}"), "浮动体个数变了"
    print(f"写入成功: {len(s)} -> {len(chk)} 字节; 表注已加")
    return 0


if __name__ == "__main__":
    sys.exit(main())
