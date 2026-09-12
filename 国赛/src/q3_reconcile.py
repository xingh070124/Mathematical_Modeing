# -*- coding: utf-8 -*-
"""
q3_reconcile.py -- 问题三数字对账 (三关):
  第一关: model/problem3_slove.md 全文 + 论文 example.tex 的问题三摘要段与 §5.3
          的全部数字 vs 注册表 (registry_q3 / _verify / _figures) + 容许清单;
  第二关: 论文 §5.3 的表 5 (50 个值) vs outputs/result3.xlsx 逐位核对
          (60 s 网格行) 与 registry_q3 的 P05_* 终态行 (t_dry 行);
  第三关: problem3_slove.md 的表 5 vs registry_q3 的 T5_* 行.

匹配规则与 q1_reconcile 相同 (由书写精度推导容差, 绝不做无条件 /100 变体).
容许清单只含**定义性数字**: 题面/附录常数、网格与输出设置、纯数学常数、
引用 problem3.md 的先验、以及显式标注"机器相关"的墙钟耗时.

输出: outputs/reconciliation_q3.csv; 有未对上数字时 exit 2.
运行: python src/q3_reconcile.py
"""

from __future__ import annotations

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_reconcile import NUM_RE, _written_tol, is_structural, latex_to_plain  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
MD_DOC = os.path.join(ROOT, "model", "problem3_slove.md")
TEX = os.path.join(ROOT, "paper", "example.tex")
XLSX = os.path.join(OUT, "result3.xlsx")

REGISTRIES = [os.path.join(OUT, "registry_q3.csv"),
              os.path.join(OUT, "registry_q3_verify.csv"),
              os.path.join(OUT, "registry_q3_figures.csv"),
              os.path.join(OUT, "registry_q3_mc.csv"),
              os.path.join(OUT, "registry_q3_drainage.csv"),
              os.path.join(OUT, "registry_q3_2d.csv")]

# ---------------------------------------------------------------------------
# 容许清单 (定义性数字): (值, 理由)
# ---------------------------------------------------------------------------
ALLOW_RAW = [
    # --- 题面与附录常数 ---
    (650, "附录3 rho(C)=650+128C"), (128, "附录3 系数"),
    (1450, "附录3 cp(C) 基项"), (2736, "附录3 cp(C) 系数"),
    (0.21, "附录3 k(C) 基项"), (0.38, "附录3 k(C) 系数"),
    (2.4e-3, "附录3 D 前因子"), (0.45, "附录3 D 的 C 指数"),
    (3850, "附录3 D 的 Arrhenius 温度"),
    (820, "附录2 rho"), (2600, "附录2 cp"), (0.36, "附录2 k"),
    (25.0, "附录2 对流换热系数 h"), (8e-7, "附录2 对流传质系数 h_m"),
    (0.15, "题面阈值 C*"), (2.55, "题面初值 C0"), (28.0, "题面初温 T0 (degC)"),
    (301.15, "T0 (K)"), (273.15, "K <-> degC"), (2.0, "半径 R=2 cm"),
    (0.02, "半径 R (m)"), (50.0, "恒温平台 Tbar (degC)"), (0.05, "恒温平台 Cbar"),
    (323.15, "Tbar (K)"),
    # --- 网格 / 时间 / 输出设置 ---
    (100, "网格 M=100"), (200, "网格 M=200 (生产)"), (400, "网格 M=400"),
    (12, "Jacobian 校核网格 M=12"), (40, "冒烟求解网格 M=40"),
    (0.01, "dr=0.01 cm / 输出间隔"), (0.1, "输出半径间隔 (cm)"),
    (0.5, "表5 半径间隔 (cm)"), (1.0, "单位间隔"), (1.5, "表5 半径"),
    (2.0, "表5 半径"), (21, "输出列数"), (402, "状态维数 2(M+1)"),
    (60.0, "result3 时间间隔 (s)"), (3600.0, "max_step / 小时秒数"),
    (600.0, "线性过渡段 tau (s)"), (1800.0, "tau 敏感性"),
    (14400.0, "附件1 覆盖上界 t_c"), (21600.0, "6 h (s)"),
    (259200.0, "积分上界 3 天 (s)"), (86400.0, "1 天 (s)"),
    (10800.0, "问题二终止时刻"),
    (0.25, "问题二 dt=0.25 s"),
    (0.125, "W4 加密 dt"), (1e-9, "rtol/atol_C"), (1e-6, "atol_T"),
    (1e-7, "W2/W5 对照容限"), (3.0, "天数"),
    (2.4, "t_dry 约 2.4 天 的表述"),
    # --- 汽化潜热定标 (问题二 §4.4c, 本问沿用) ---
    (2.4346e6, "H_evap(28C) 定标截距"), (2.391e3, "H_evap 定标斜率"),
    # --- 纯数学常数 / 结构量 ---
    (1.0, "单位"), (0.0, "零"), (2.0, "倍数"), (3.0, "倍数"), (4.0, "倍数"),
    (6.0, "6 阶 BDF / 每行非零元"), (5.0, "变阶上限 5"), (1.0e5, "10^5 量级"),
    (3600.0, "秒->小时"), (100.0, "百分比"), (1000.0, "千"),
    (0.5, "一半"), (1.5, "倍"), (7.0, "BDF 1~5 阶 / 每行 7 非零"),
    (8.0, "8 倍"), (19.0, "19 倍"), (20.0, "20 倍 / M 的倍数"),
    # --- 量级声明 (指数写法) ---
    (1e-4, "量级声明"), (1e-5, "量级声明"), (1e-6, "量级声明"),
    (1e-7, "量级声明"), (1e-8, "量级声明"), (1e-9, "量级声明"),
    (1e-10, "量级声明"), (1e-11, "量级声明"), (1e-12, "量级声明"),
    (1e-16, "量级声明"),
    # --- 版本号 ---
    (3.12, "python 版本号"), (2.5, "numpy 版本号"), (1.18, "scipy 版本号"),
    (1.17, "problem3.md 原型环境 scipy 版本号"), (3.1, "openpyxl 版本号"),
    # --- 引自 problem3.md 的先验/量级估计 (建模文档 §5.3/§7/§10.4/§12) ---
    (0.046, "problem3.md §7.3 显式格式稳定步长估计"),
    (4.5e6, "problem3.md §7.3 显式格式步数量级估计"),
    (16.8, "problem3.md §5.3 特征时间放大倍数"),
    (2.97e4, "problem3.md §5.3 初期湿分特征时间 R^2/D"),
    (5.0e5, "problem3.md §5.3 末期湿分特征时间 R^2/D"),
    (8.0e-10, "problem3.md §5.3 D(C*, 50C)"),
    (1.9e3, "problem3.md §7.1 末期热特征时间 R^2/alpha (取整)"),
    (8.3e5, "定步长 BE 全程步数推导 206720/0.25"),
    (6341, "problem3.md 原型 BDF 步数 (scipy 1.17.1)"),
    (206726.278, "problem3.md 原型 t_dry (M=200, scipy 1.17.1)"),
    (206403.581, "problem3.md 原型 t_dry (M=100)"),
    (206863.279, "problem3.md 原型 t_dry (M=400)"),
    (206964.4, "problem3.md 原型 Richardson 外推值"),
    (57.4901, "problem3.md 原型 Richardson 外推值 (h)"),
    (1.236, "problem3.md 原型实测收敛阶"),
    (0.0526, "problem3.md 原型表5 末行表面值 (1 ulp 差)"),
    (0.0598, "problem3.md 原型表5 30h 表面值 (1 ulp 差)"),
    (0.0566, "problem3.md 原型表5 36h 表面值 (1 ulp 差)"),
    (47.0, "表5 与原型逐格一致的计数"),
    (4.8, "problem3.md §6.4(d) Cbar 敏感性先验 (h)"),
    (17.27, "问题二 V11 结论: 两种能量形式温度差 (registry_q2_verify)"),
    (0.019636, "附件1 C_inf 全程最小值 (问题一已核)"),
    # --- 表5 行时刻 (6 h 网格定义) ---
    (12.0, "表5 行时刻"), (18.0, "表5 行时刻"), (24.0, "表5 行时刻"),
    (30.0, "表5 行时刻"), (36.0, "表5 行时刻"), (42.0, "表5 行时刻"),
    (48.0, "表5 行时刻"), (54.0, "表5 行时刻"),
    (0.005, "M=400 的 dr (cm) / Cbar 扰动幅度"),
    # --- 推导值 (由注册值四则运算而得, 非独立测量) ---
    (62.7, "平均步长 t_dry/步数 推导"),
    (9.42, "t_dry 的'天+小时'表述推导"),
    (52480.0, "积分上界余量 259200-t_dry 推导"),
    (20.2, "余量百分比推导"),
    (34.0, "条件数 x 1e-5 推导"),
    (0.34, "条件数 x 1e-7 推导"),
    (0.003, "条件数 x 1e-9 推导"),
    (4.8e-5, "0.171 s 换算小时 推导"),
    (0.026, "dC0/dCbar 反推值 (W7 导出)"),
    (2.6, "同上百分比"),
    (2.12, "naive 估计 0.0369x57.42 推导"),
    (3.69e-2, "3850/T^2 @323.15K 推导"),
    (38.0, "先验/实测敏感性之比 推导"),
    # --- 墙钟耗时 (机器相关, 运行间可变, 不对账) ---
    (3.0, "墙钟耗时"), (4.0, "墙钟耗时"), (23.0, "墙钟耗时"),
    (22.7, "墙钟耗时"), (226.0, "墙钟耗时"), (446.0, "墙钟耗时"),
    (75.0, "加速比 (耗时之比, 机器相关)"), (7.6, "加速比 (机器相关)"),
    # --- 运行观测计数 (未入注册表的控制台观测) ---
    (1373, "W5 全稠密差分步数 (运行观测)"),
    (1777, "W6 Radau 步数 (运行观测)"),
    (6358, "W6 LSODA 步数 (运行观测)"),
    (57600.0, "问题二 BE 步数 14400/0.25 (运行观测)"),
    (115200.0, "问题二 BE 步数 14400/0.125 (运行观测)"),
    (2.24e-7, "selftest FD 偏差 (控制台输出)"),
    (2.239e-7, "selftest FD 偏差 (控制台输出)"),
    (6.212e-8, "selftest FD 偏差 (控制台输出)"),
    (0.14, "JTC 符号修正前的 FD 偏差 (修正前观测)"),
    (2.1, "两处 W2 差值的近似书写"),
    # --- W 编号 / 公式与区间写法的结构残留 ---
    (9.0, "W9 编号"), (10.0, "W10 编号"),
    (-1.0, "公式/区间写法结构残留 (direction=-1, 2^p-1)"),
    (-600.0, "区间写法 t_c-600 结构残留"),
    (7200.0, "W4 时间窗边界 (2 h)"),
    (77.0, "registry_q3_verify.csv 行数 (运行观测)"),
    (3324.0, "W1 M=100 步数 (运行观测)"),
    (3276.0, "W1 M=400 步数 (运行观测)"),
    (57.4984, "p=1 保守外推的小时换算 206994.178/3600 推导"),
    (59.2866, "Tbar=49 变体 t_dry(h) = base+dh 推导"),
    (55.6395, "Tbar=51 变体 t_dry(h) = base+dh 推导"),
    (57.3056, "Cbar=0.045 变体 t_dry(h) 推导"),
    (57.5533, "Cbar=0.055 变体 t_dry(h) 推导"),
    (51.0, "Tbar 敏感性变体 51 degC"),
    (0.045, "Cbar 敏感性变体 0.045"),
    # 排湿工况情景分析的 Cbar 设定值 (q3_drainage.py), 属"设置"而非"测量"
    (0.06, "排湿情景 Cbar 设定 0.0600"), (0.075, "排湿情景 Cbar 设定 0.0750"),
    (0.12, "排湿情景 Cbar 设定 0.1200"),
    (-10.0, "百分比标记 -10%"),
    (0.008, "tau=0 变体秒换算 (2.16e-6 h) 推导"),
    (0.070, "tau=1800 变体秒换算 (1.93e-5 h) 推导"),
    (-0.0369, "3850/T^2 @323.15K 推导"),
    (-2.12, "naive 估计 0.0369x57.42 推导"),
    (139.0, "R^2/D 末期特征时间 5.0e5/3600 推导"),
    (5e-5, "四位小数报告阈值 (半 ulp)"),
    (0.04, "W6 三积分器最大差值取整 / 1.82x0.02 推导"),
    (120.0, "result3 A 列时刻 60x2"),
    (-6.0, "原型-生产差值的取整表述 (约 -6 s)"),
    (9.4, "t_dry '天+小时'表述推导"),
    (-3.0, "范围写法 2--3 天 的 en-dash 残留"),
    (-4.0, "\\zihao{-4} 字号命令残留"),
    (0.96, "includegraphics 宽度"),
    (0.94, "minipage 宽度"),
    (57.50, "p=1 保守外推小时值 206994.178/3600 推导"),
    (45.0, "中心 0.46→0.15 历时 57.42-12 推导"),
    (17.0, "D(C0)/D(C*) = 16.8 取整 推导"),
    (56.0, "EA 单因素半程变化百分比 32.12/57.42 推导"),
    (0.55, "exp(-EA·0.05/323.15) 推导"),
    (2026, "蒙特卡洛随机种子 (脚本设置)"),
    # --- W11 二维 (r,z) 对照 (q3_2d_verify.py) 的定义性数字与推导值 ---
    (12.5, "几何定义 半长 L/2 (cm)"),
    (1e4, "W11 端面传质放大倍数 (脚本设置)"),
    (201.0, "W11 二维径向节点数 Nr+1 (设置)"),
    (20502.0, "W11 二维状态维数 2x201x51 推导"),
    (2.5, "W11 二维轴向网格 dz (mm) (设置)"),
    (617.0, "W11 共同比较窗采样点数 (运行观测)"),
    (95.24, "W11 二维全程失水率百分比 1-0.95241 推导"),
    (63.0, "registry_q3_2d.csv 行数 (运行观测)"),
    (14.0, "表 14 编号 (版面, 附录2d 的 t_dry 对照表)"),
]
ALLOW = {}
for item in ALLOW_RAW:
    ALLOW.setdefault(float(item[0]), item[-1])

PCT_RE = re.compile(r"%\s*$")


def load_registry():
    vals = {}
    for path in REGISTRIES:
        if not os.path.exists(path):
            print(f"  [warn] 注册表不存在: {path}")
            continue
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                v = str(r.get("value", ""))
                for tok in NUM_RE.findall(latex_to_plain(v)):
                    try:
                        vals.setdefault(float(tok), (r["id"], os.path.basename(path)))
                    except ValueError:
                        pass
    return vals


def match(x, reg, tok=None):
    """返回 (id, 文件, 偏差) 或 (None, None, None); 容差由书写精度推出.

    容差匹配失败后再尝试 |x| (正文常写"高 1.82 h"而注册表存 -1.8235, 命中时
    在来源上标记 |abs).
    """
    if x in reg:
        return reg[x][0], reg[x][1], 0.0
    tol = _written_tol(tok) if tok else 5e-5
    best, bdev, bsrc = None, None, None
    for rv, (rid, src) in reg.items():
        d = abs(x - rv)
        if d <= tol and (bdev is None or d < bdev):
            best, bdev, bsrc = rid, d, src
    if best is None:
        for rv, (rid, src) in reg.items():
            d = abs(abs(x) - abs(rv))
            if d <= tol and (bdev is None or d < bdev):
                best, bdev, bsrc = rid, d, src + "|abs"
    return (best, bsrc, bdev) if best else (None, None, None)


def scan_lines(lines, tag, reg, rows, unmatched, counters):
    for ln, raw in enumerate(lines, 1):
        line = latex_to_plain(raw)
        if set(line.strip()) <= set("|-: \n"):
            continue
        for m in NUM_RE.finditer(line):
            tok = m.group(0)
            if is_structural(line, m.span()):
                continue
            x = float(tok)
            if abs(x) >= 1e16:
                continue
            rid, src, _ = match(x, reg, tok)
            if rid:
                counters["reg"] += 1
                kind, key = "MATCH", rid
            elif x in ALLOW:
                counters["allow"] += 1
                kind, key = "ALLOW", "allow: " + ALLOW[x]
            else:
                unmatched.append((tag, ln, tok))
                counters["bad"] += 1
                kind, key = "NO_SOURCE", ""
            rows.append([tag, ln, tok, kind, key, src if rid else ""])


def tex_ranges(lines):
    """论文中问题三相关的扫描区间: 摘要的'针对问题三'段 + §5.3 全节."""
    targets = []
    i0 = next((i for i, l in enumerate(lines) if "针对问题三" in l), None)
    i1 = next((i for i, l in enumerate(lines) if "总结" in l and i0 is not None
               and i > i0), None)
    if i0 is not None and i1 is not None:
        targets.append(("example.tex(摘要问题三段)", lines[i0:i1], i0 + 1))
    j0 = next((i for i, l in enumerate(lines)
               if "问题三模型的建立与求解" in l and "subsection" in l), None)
    j1 = next((i for i, l in enumerate(lines)
               if "问题四模型的建立与求解" in l and "subsection" in l
               and j0 is not None and i > j0), None)
    if j0 is not None and j1 is not None:
        targets.append(("example.tex(§5.3)", lines[j0:j1 + 1], j0 + 1))
    k0 = next((i for i, l in enumerate(lines)
               if "附录：降维合理性" in l and "section" in l), None)
    k1 = next((i for i, l in enumerate(lines)
               if "附录：结果文件与源程序" in l and "section" in l
               and k0 is not None and i > k0), None)
    if k0 is not None and k1 is not None:
        targets.append(("example.tex(附录2d)", lines[k0:k1 + 1], k0 + 1))
    return targets


def read_by_id(path):
    d = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                d[row["id"]] = float(row["value"])
            except (TypeError, ValueError):
                pass
    return d


def gate2_table5_vs_xlsx(reg, rows, unmatched, counters):
    """第二关: 论文表 5 的 50 个值 vs result3.xlsx (60 s 行) 与 P05_* (t_dry 行)."""
    from openpyxl import load_workbook
    tex = open(TEX, encoding="utf-8").read()
    i = tex.index("tab:q3t5")
    j0 = tex.index("\\begin{tabular*}", i)      # \label 在 tabular* 之前
    j1 = tex.index("\\bottomrule", i)
    body = tex[j0:j1]
    wb = load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["Sheet1"]
    grid = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is not None:
            grid[int(r[0])] = [float(v) for v in r[1:]]
    wb.close()
    p05r = read_by_id(REGISTRIES[0])
    p05 = {"0": p05r["P05_C_center"], "0.5": p05r["P05_C_r0p5"],
           "1": p05r["P05_C_r1"], "1.5": p05r["P05_C_r1p5"],
           "2": p05r["P05_C_surface"]}
    n_ok = 0
    for raw in body.splitlines():
        if "&" not in raw:
            continue
        cells = [latex_to_plain(c) for c in raw.split("&")]
        nums = []
        for c in cells:
            m = NUM_RE.findall(c)
            nums.append(float(m[0]) if m else None)
        if nums[0] is None:
            continue
        th, vals = nums[0], nums[1:6]
        radii = ("0", "0.5", "1", "1.5", "2")
        for rc, v in zip(radii, vals):
            if v is None:
                continue
            if th == 57.42:                      # t_dry 行: 对照 P05_*
                src = f"registry P05_C ({rc} cm)"
                ref = round(p05[rc], 4)
            else:                                # 60 s 网格行: 对照 xlsx
                src = f"result3.xlsx t={int(th * 3600)} s"
                ref = grid[int(th * 3600)][int(round(float(rc) / 0.1))]
            d = abs(v - ref)
            ok = d <= 5e-9
            n_ok += ok
            counters["t5"] += 1
            if not ok:
                unmatched.append((f"表5 {src}", 0, f"{v} vs {ref}"))
                counters["bad"] += 1
            rows.append([f"gate2 表5 {th} h", 0, f"r={rc}: {v}", 
                         "MATCH" if ok else "NO_SOURCE", src, ""])
    print(f"  第二关: 论文表 5 的 {counters['t5']} 个值 vs result3.xlsx/P05 —— "
          f"{n_ok} 个逐位一致, {counters['t5'] - n_ok} 个不符")


def main():
    reg = load_registry()
    print(f"注册表条目: {len(reg)} 个不同数值")
    print(f"容许清单:   {len(ALLOW)} 个数值\n")

    rows, unmatched = [], []
    counters = {"reg": 0, "allow": 0, "bad": 0, "t5": 0}

    # ---- 第一关: md 全文 + tex 问题三相关区间 ----
    with open(MD_DOC, encoding="utf-8") as f:
        scan_lines(f.readlines(), "problem3_slove.md", reg, rows, unmatched,
                   counters)
    tex_lines = open(TEX, encoding="utf-8").read().splitlines()
    for tag, seg, off in tex_ranges(tex_lines):
        scan_lines(seg, tag, reg, rows, unmatched, counters)
        print(f"  第一关扫描: {tag}: {len(seg)} 行")

    # ---- 第二关: 论文表 5 vs result3.xlsx / P05 ----
    gate2_table5_vs_xlsx(reg, rows, unmatched, counters)

    outp = os.path.join(OUT, "reconciliation_q3.csv")
    with open(outp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["doc", "line", "token", "kind", "source", "registry_file"])
        w.writerows(rows)

    print(f"\n第一关扫描数字: {counters['reg'] + counters['allow'] + counters['bad']}"
          f"  注册表命中: {counters['reg']}  容许(定义性): {counters['allow']}  "
          f"未对上: {counters['bad']}")
    for tag, ln, tok in unmatched[:40]:
        print(f"  !! {tag}:{ln}  {tok}")
    print(f"\n明细: {outp}")
    if unmatched:
        print("存在未对上数字 -> exit 2")
        sys.exit(2)
    print("全部数字均有出处, 表 5 逐位一致 -> OK")


if __name__ == "__main__":
    main()
