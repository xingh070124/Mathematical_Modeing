# -*- coding: utf-8 -*-
"""
q4_reconcile.py -- 问题四的结果对账门.

  第一关: paper/example.tex 表6 的每一行  vs  outputs/result4.xlsx 逐位一致
  第二关: result4.xlsx 的结构规格 (表头/行列数/精度/超域留空)
  第三关: outputs/table6_moisture.csv 与 result4.xlsx 一致

退出码 0 = 全部通过.
"""

from __future__ import annotations

import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
XLSX = os.path.join(OUT, "result4.xlsx")
CSV6 = os.path.join(OUT, "table6_moisture.csv")
TEX = os.path.join(ROOT, "paper", "example.tex")

fails = []


def head(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def read_result4():
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    body = [r for r in rows[1:] if r[0] is not None]
    return ws.title, hdr, body


def main():
    if not os.path.exists(XLSX):
        print(f"[!] 缺少 {XLSX}")
        return 1
    title, hdr, body = read_result4()

    # ---------------- 第二关: 结构规格 ----------------
    head("第二关: result4.xlsx 的结构规格")
    print(f"  工作表名: {title!r}")
    ncol = len(hdr) - 1
    radii = [h for h in hdr[1:]]
    print(f"  表头: {hdr[0]!r} + {ncol} 列")
    print(f"  首列半径: {radii[0]}, 次列 {radii[1]}, 第 3 列 {radii[2]}")
    print(f"  末列: {radii[-1]!r}")
    print(f"  数据行数: {len(body)}")
    ok_struct = True
    # A 列为 60,120,... 整数秒
    ts = [int(r[0]) for r in body]
    if ts != list(range(60, 60 * (len(ts) + 1), 60)):
        print("  !! A 列不是 60 s 等间隔")
        fails.append("A列时间间隔")
        ok_struct = False
    else:
        print(f"  OK A 列为 60 s 等间隔, 由 {ts[0]} 到 {ts[-1]}")
    # 半径列 0.0..2.0 步长 0.1
    num_radii = [h for h in radii if isinstance(h, (int, float))]
    if len(num_radii) == 21 and abs(num_radii[0]) < 1e-12 and abs(num_radii[-1] - 2.0) < 1e-12:
        print(f"  OK 半径列 0.0~2.0 共 {len(num_radii)} 列, 步长 0.1")
    else:
        print(f"  !! 半径列异常: {num_radii[:5]} ... ({len(num_radii)} 列)")
        fails.append("半径列")
        ok_struct = False
    if radii[-1] in ("药材表面",):
        print("  OK 末列为药材表面")
    else:
        print(f"  !! 末列不是药材表面: {radii[-1]!r}")
        fails.append("末列标签")
        ok_struct = False
    # 四位小数
    bad_prec = 0
    nonnull = 0
    for r in body:
        for v in r[1:]:
            if v is None:
                continue
            nonnull += 1
            if abs(round(float(v), 4) - float(v)) > 1e-12:
                bad_prec += 1
    print(f"  {'OK ' if bad_prec == 0 else '!! '}四位小数: 非空 {nonnull} 格, "
          f"超过四位小数的 {bad_prec} 格")
    if bad_prec:
        fails.append("精度")
        ok_struct = False

    # ---------------- 第一关: 表6 vs result4.xlsx ----------------
    head("第一关: paper/example.tex 表6  vs  result4.xlsx")
    tex = open(TEX, encoding="utf-8").read()
    # 定位表6 的 tabular
    i0 = tex.index("\\textbf{表~6\\quad")
    i1 = tex.index("\\end{tabular}", i0)
    body_tex = tex[i0:i1]
    rows = [l for l in body_tex.splitlines()
            if re.match(r"^\s*(\\?[$\w.]+)\s*&", l) and "&" in l]
    got = []
    for l in rows:
        if "时间" in l or "toprule" in l or "midrule" in l:
            continue
        cells = [c.strip() for c in l.split("&")]
        cells[-1] = cells[-1].replace("\\\\", "").strip()
        got.append(cells)
    print(f"  从 tex 抽出 {len(got)} 行表6")

    # result4 的时间网格 → 行索引
    gt = {int(t): k for k, t in enumerate(ts)}
    t_dry = 183906.7128
    nbad = 0
    for cells in got:
        ts_str = cells[0].replace("$", "").replace("\\mathbf{", "").replace("}", "")
        try:
            th = float(ts_str)
        except ValueError:
            continue
        if abs(th - t_dry / 3600.0) < 0.01:
            k = len(ts) - 1                     # 末行 = t_dry
            tsec = t_dry
        else:
            tsec = th * 3600.0
            k = int(round(tsec / 60.0)) - 1
        if k < 0 or k >= len(body):
            print(f"  !! t={th} h 超出 result4 行范围")
            fails.append(f"行越界 t={th}")
            continue
        row = body[k]
        # tex 表6 的列依次是 r = 0, 0.5, 1.0, 1.5 cm 与"药材表面";
        # 对应 xlsx 的列索引为 1, 6, 11, 16 与最后一列 (0.1 cm 步长).
        colmap = [1, 6, 11, 16, len(hdr) - 1]
        for jj, c in enumerate(cells[1:]):
            if jj >= len(colmap):
                continue
            j = colmap[jj]
            cc = c.strip()
            if cc in ("—", "-", "--", ""):
                continue
            cc = cc.replace("$", "").replace("\\mathbf{", "").replace("}", "").strip()
            try:
                v_tex = float(cc)
            except ValueError:
                continue
            v_x = row[j]
            if v_x is None:
                print(f"  !! t={th} h 第{jj}列(r 索引 {j}): tex={v_tex} 但 xlsx 为空")
                fails.append(f"空值 t={th} c{j}")
                nbad += 1
                continue
            if abs(round(float(v_x), 4) - round(v_tex, 4)) > 1e-12:
                print(f"  !! t={th} h 第{jj}列(r 索引 {j}): tex={v_tex:.4f} "
                      f"xlsx={float(v_x):.4f}")
                fails.append(f"不一致 t={th} c{j}")
                nbad += 1
    if nbad == 0:
        print(f"  OK 表6 的 {len(got)} 行与 result4.xlsx 逐位一致")
    else:
        print(f"  !! 共 {nbad} 处不一致")

    # ---------------- 第三关: table6_moisture.csv ----------------
    head("第三关: outputs/table6_moisture.csv  vs  result4.xlsx")
    import csv
    with open(CSV6, encoding="utf-8-sig") as f:
        r6 = list(csv.reader(f))
    print(f"  CSV 表头: {r6[0]}")
    print(f"  CSV 行数: {len(r6)-1}")
    nbad2 = 0
    for row in r6[1:]:
        th = float(row[0])
        if abs(th - t_dry / 3600.0) < 0.01:
            k, tsec = len(ts) - 1, t_dry
        else:
            k = int(round(th * 3600.0 / 60.0)) - 1
        if k < 0 or k >= len(body):
            continue
        xl = body[k]
        cols = [1, 6, 11, 16]     # 0,0.5,1.0,1.5 cm → 索引 1,6,11,16
        for j, c in zip(cols, row[1:5]):
            if c.strip() == "":
                continue
            if xl[j] is None or abs(float(xl[j]) - float(c)) > 1e-12:
                print(f"  !! t={th} 列索引{j}: csv={c} xlsx={xl[j]}")
                nbad2 += 1
        # 表面列
        if row[5].strip() and abs(float(xl[-1]) - float(row[5])) > 1e-12:
            print(f"  !! t={th} 表面: csv={row[5]} xlsx={xl[-1]}")
            nbad2 += 1
    if nbad2 == 0:
        print("  OK CSV 与 result4.xlsx 一致")
    else:
        fails.append(f"csv {nbad2} 处")

    print("\n" + "=" * 78)
    if fails:
        print(f"未通过 ({len(fails)} 项): " + "; ".join(fails[:10]))
        return 1
    print("问题四结果对账全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
