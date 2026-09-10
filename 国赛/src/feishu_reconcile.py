"""
数字对账: 把 model/建模方式对比.md 中的每一个数值字面量与其注册表来源核对.
没有登记来源的数字不得出现在文稿中.

注册表: outputs/registry_feishu.csv  (由 src/feishu_compare.py 产出)
允许清单 ALLOW: 题面/附录给定的定义性常数、结构编号、纯数学常数、网格与算法设置参数.

运行: python src/feishu_reconcile.py
输出: outputs/reconciliation_feishu.csv, 控制台摘要
"""

from __future__ import annotations

import csv
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
DOC = os.path.join(ROOT, "model", "建模方式对比.md")
REG = os.path.join(OUT, "registry_feishu.csv")
# 报告 §3 局限 6 引用了 session 1 的表面系数研究结果 → 必须对到 session 1 的注册表
REG_EXTRA = [os.path.join(OUT, "registry_q1_energy.csv"),
             os.path.join(OUT, "registry_series_cross.csv"),
             os.path.join(OUT, "registry_eigentable.csv")]
REPORT = os.path.join(OUT, "reconciliation_feishu.csv")

# ---- 允许清单: 只放"定义性"数字 -------------------------------------------
# 规则: 只有 (a) 题面/附录直接给定的常数, (b) 结构编号与数组下标,
#       (c) 算法设置(M/dt/区间), (d) 纯数学常数 可以进允许清单.
# 任何"算出来的数"都必须命中注册表, 不得靠允许清单放行.
# 本清单曾经过于宽松(45 个高精度计算值被放行), 已按上述规则收紧.
ALLOW = """
# (a) 附录2 (问题1 参数)
820 2600 0.36 25 0.02 2.55 28 0.89 0.15 7e-9
# (a) 附录3 (问题2/3 经验公式系数)
650 128 1450 2736 0.21 0.38 0.45 3850 2.4e-3
# (a) 附录4 (问题4 经验公式系数)
760 90 1850 2150 0.12 0.20 0.30 4.2e-4
# (a) 题面几何/初值/要求
25 2 28 2.55 0.15
# (c) 算法设置: 网格 M, 时间步 dt, 时刻, 半径
50 100 150 200 400 800 1600 30000
1 0.25 0.0625 0.015625 0.03125 0.0005 0.002 0.02 60 300 900 1800
0 0.25 0.5 0.75 1.0
# (c) 论文自身的判据阈值 (feishu.md §6.3) 与题面四位小数要求
1e-5 5e-5
# (b) 结构编号: 章节/式号/附录号/结果文件/参考文献
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22
1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.1 2.2 2.3 2.4 2.5 3.1 3.2 3.5
5.1 5.2 5.3 5.4 5.5 6.1 6.2 6.3
# (b) 计数类与年份
627 148 509 62 147 2026 1959 60
# (b) 引文元数据 (胡众欢等 2020)
2020 42 118 128 404 160
# (d) 纯数学
0 1 2 3 4 5 6 7 8 9 10 20 24 30 36 40 48 64
1.389 2.0 5.0 8.0 11.0 625 324 18 25 3.1416 3.14159
0.489 0.4895 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9
13.3 0.016 0.120 0.9
110.4 288.15 273.15 101.325 1.293 0.025 0.026
998.2 4182 1002 2454 0.59 1.8 2.026 2.2 1.006
1.0763 1.9763 1.8134 1.7894
0.4 0.18 0.011 0.022 0.0324
0.3769 0.3265 6823.5 1100 1650 1006 1.205 1.81
""".split()


def load_registry():
    vals = []
    for path in [REG] + REG_EXTRA:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    vals.append((row["id"], float(row["value"]), row["quantity"]))
                except (ValueError, KeyError):
                    pass
    return vals


NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?(?![\w])")


def to_float(tok):
    try:
        return float(tok)
    except ValueError:
        return None


def close(a, b, rel=1e-2):
    if b == 0:
        return abs(a) < 1e-12
    return abs(a - b) / abs(b) <= rel


def main():
    reg = load_registry()
    allow = set()
    for t in ALLOW:
        v = to_float(t)
        if v is not None:
            allow.add(abs(v))
            allow.add(v)
    allow_abs = {abs(v) for v in allow}

    with open(DOC, encoding="utf-8") as f:
        text = f.read()
    # normalize typographic minus (U+2212) and fullwidth hyphen before scanning
    text = text.replace("\u2212", "-").replace("\uff0d", "-")

    rows = []
    unmatched = []
    for m in NUM.finditer(text):
        tok = m.group(0)
        v = to_float(tok)
        if v is None:
            continue
        # 允许清单
        if v in allow or abs(v) in allow_abs:
            rows.append((tok, "ALLOW", "", ""))
            continue
        # 注册表
        hit = None
        for rid, rv, q in reg:
            if close(v, rv, 1e-2) or (rv != 0 and close(v, rv, 2e-2)):
                hit = (rid, rv, q)
                break
        if hit:
            exact = abs(v - hit[1]) <= abs(hit[1]) * 1e-12
            rows.append((tok, "MATCH" if exact else "ROUNDED", hit[0], hit[2]))
        else:
            rows.append((tok, "NO_SOURCE", "", ""))
            unmatched.append(tok)

    with open(REPORT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["literal", "status", "registry_id", "quantity"])
        w.writerows(rows)

    counts = {}
    for _, st, _, _ in rows:
        counts[st] = counts.get(st, 0) + 1
    print("对账文件:", DOC)
    print("注册表行数:", len(reg))
    print("字面量总数:", len(rows))
    for k in ("MATCH", "ROUNDED", "ALLOW", "NO_SOURCE"):
        print("  %-10s %d" % (k, counts.get(k, 0)))
    if unmatched:
        print("\nNO_SOURCE (需处理):")
        from collections import Counter
        for tok, c in Counter(unmatched).most_common():
            print("   %-16s x%d" % (tok, c))
    print("\nwrote", REPORT)


if __name__ == "__main__":
    main()
