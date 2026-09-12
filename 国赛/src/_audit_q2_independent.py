# -*- coding: utf-8 -*-
"""Independent audit of the Q2 tex section: C5 (tables), C6/C7/C8/C9 (figures),
plus the 附件1-driven checks (Table H, driving force, T_inf peak).

Everything here is recomputed from outputs/result2.xlsx and
A题/附件/附件1.xlsx, NOT from any registry.

Writes outputs/_audit_q2_independent.log and _audit_q2_independent.csv
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np
import openpyxl
from scipy.interpolate import PchipInterpolator

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
ATT = os.path.join(ROOT, "A题", "附件")
ROWS = []
NMATCH = {"MATCH": 0, "ROUNDED": 0, "MISMATCH": 0, "TEXT": 0, "-": 0}


def chk(tag, what, got, tex, unit="", tol_rel=1e-9, tol_round=5e-5):
    if tex is None:
        verdict = "-"
    elif isinstance(tex, str):
        verdict = "TEXT"
    else:
        denom = max(abs(tex), 1e-300)
        rel = abs(got - tex) / denom
        verdict = ("MATCH" if rel <= tol_rel
                   else "ROUNDED" if rel < tol_round else "MISMATCH")
    NMATCH[verdict] = NMATCH.get(verdict, 0) + 1
    flag = "" if verdict in ("MATCH", "ROUNDED", "TEXT", "-") else "   <<<<<<"
    print(f"[{verdict:9s}] {tag:26s} got={got:<24.12g} tex={tex} {unit}  "
          f"{what}{flag}")
    ROWS.append([tag, what, repr(got), repr(tex), unit, verdict])
    return verdict


def read_result2():
    p = os.path.join(OUT, "result2.xlsx")
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    out = {}
    for name in wb.sheetnames:
        ws = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        hdr = rows[0]
        radii_cm = np.array([float(v) for v in hdr[1:]])
        body = np.array([[float(v) for v in r] for r in rows[1:]])
        t = body[:, 0].astype(int)
        out[name] = (t, radii_cm, body[:, 1:])
    wb.close()
    return out


def read_att1():
    p = os.path.join(ATT, "附件1.xlsx")
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    return rows


def main():
    res = read_result2()
    print("=" * 112)
    print("0. result2.xlsx 结构 vs 附件3 模板")
    print("=" * 112)
    tpl = openpyxl.load_workbook(os.path.join(ATT, "附件3", "result2.xlsx"),
                                 data_only=True, read_only=True)
    for nm in tpl.sheetnames:
        ws = tpl[nm]
        rows = list(ws.iter_rows(values_only=True))
        print(f"  template sheet {nm!r}: {len(rows)} rows x {len(rows[0])} cols; "
              f"header={rows[0][:4]}...{rows[0][-2:]}")
    tpl.close()
    for nm, (t, rc, V) in res.items():
        print(f"  produced sheet {nm!r}: {len(t)+1} rows x {V.shape[1]+1} cols; "
              f"r[cm]={rc[0]}..{rc[-1]} n={len(rc)}; t={t[0]}..{t[-1]} n={len(t)}")
    print(f"  >>> 模板只有表头行? 见上; 题面要求 1 s x 0.1 cm 全表: "
          f"n_t={len(list(res.values())[0][0])}, n_r={list(res.values())[0][1].size}")

    names = list(res.keys())
    Tname = [n for n in names if "温" in n][0]
    Cname = [n for n in names if "水" in n][0]
    tT, rcT, TT = res[Tname]
    tC, rcC, CC = res[Cname]
    print(f"  温度 sheet 名 = {Tname!r}, 水分 sheet 名 = {Cname!r}")
    R = 0.02  # m
    assert np.allclose(rcT, rcC)
    rc = rcT * 1e-2            # m
    tt = tT.astype(float)

    print()
    print("=" * 112)
    print("C5. 表 3 (温度 / degC) vs result2.xlsx")
    print("=" * 112)
    texT = {
        0.5: [32.1056, 32.2973, 32.8775, 33.8671, 35.3131],
        1.0: [40.2754, 40.4472, 40.9536, 41.7705, 42.8919],
        1.5: [45.7411, 45.8293, 46.0878, 46.5008, 47.0362],
        2.0: [48.3516, 48.3896, 48.5006, 48.6767, 48.9078],
        2.5: [49.3772, 49.3896, 49.4246, 49.4765, 49.5751],
        3.0: [49.7685, 49.7746, 49.7945, 49.8309, 49.8888],
    }
    texC = {
        0.5: [2.5499, 2.5489, 2.5257, 2.3262, 1.6475],
        1.0: [2.5261, 2.4953, 2.3587, 2.0235, 1.4699],
        1.5: [2.3874, 2.3270, 2.1356, 1.8024, 1.3465],
        2.0: [2.1727, 2.1102, 1.9249, 1.6263, 1.2303],
        2.5: [1.9586, 1.9024, 1.7373, 1.4725, 1.1161],
        3.0: [1.7681, 1.7183, 1.5715, 1.3338, 1.0078],
    }
    cols = [0.0, 0.5, 1.0, 1.5, 2.0]
    icol = [int(round(c / 0.1)) for c in cols]
    nbad_matched = 0
    for h, tv in texT.items():
        ts = int(round(h * 3600))
        row = tT == ts
        got = TT[row][0][icol]
        # the file stores 4-decimal values; compare at 4 decimals
        for j, (g, x) in enumerate(zip(got, tv)):
            if abs(round(g, 4) - x) <= 5e-5:
                nbad_matched += 1
            else:
                print(f"  !! T mismatch t={ts} r={cols[j]} file={g} tex={x}")
    print(f"  表3: {nbad_matched}/30 个数字与 result2.xlsx 在 4 位小数上一致")
    chk("T3_exact", "表3 30 个数字全部一致", float(nbad_matched), 30.0, "个",
        tol_rel=1e-12)
    nbad = 0
    for h, cv in texC.items():
        ts = int(round(h * 3600))
        row = tC == ts
        got = CC[row][0][icol]
        for j, (g, x) in enumerate(zip(got, cv)):
            if abs(round(g, 4) - x) <= 5e-5:
                nbad += 1
            else:
                print(f"  !! C mismatch t={ts} r={cols[j]} file={g} tex={x}")
    print(f"  表4: {nbad}/30 个数字与 result2.xlsx 在 4 位小数上一致")
    chk("T4_exact", "表4 30 个数字全部一致", float(nbad), 30.0, "个",
        tol_rel=1e-12)

    print()
    print("=" * 112)
    print("C8. 体积平均含水率 (3 h) —— 三种求积 + 通量收支参考")
    print("=" * 112)
    C_end = CC[tC == 10800][0]
    C_0 = CC[tC == 1][0]
    print(f"  C(10800) 21 点 = {np.round(C_end, 6)}")
    print(f"  C(1)     21 点 = {np.round(C_0, 6)}")
    h = R / 20
    # (i) trapezoid on f = C*r  (paper / q2_figures)
    f = C_end * rc
    trap = 2.0 / R ** 2 * (h * (0.5 * f[0] + f[1:-1].sum() + 0.5 * f[-1]))
    # (ii) lumped-weight rectangle rule (q2_derive DV_Cbar)
    MLg = np.empty(21)
    MLg[0] = h * h / 6
    MLg[1:20] = h * rc[1:20]
    MLg[20] = h * (rc[19] + 2 * rc[20]) / 6
    lump = (MLg * C_end).sum() / MLg.sum()
    # (iii) Simpson on C*r
    s = C_end * rc
    simp = 2.0 / R ** 2 * (h / 3 * (s[0] + s[-1] + 4 * s[1:-1:2].sum()
                                   + 2 * s[2:-2:2].sum()))
    W_trap = trap * R ** 2 / 2
    W_lump = lump * MLg.sum()
    print(f"  (i)  梯形(21 点)      Cbar = {trap:.9f}   W = {W_trap:.10e}")
    print(f"  (ii) MLg 矩形权       Cbar = {lump:.9f}   W = {W_lump:.10e}")
    print(f"  (iii) Simpson(21 点)  Cbar = {simp:.9f}   W = {simp*R**2/2:.10e}")
    print(f"  W(0) = R^2*C0/2 = {R**2*2.55/2:.10e}  (FG_W0=0.00051)")
    chk("Cbar_trap", "体积平均含水率 (梯形 21 点)", trap, 1.3823, "kg/kg",
        tol_rel=5e-5)
    chk("Cbar_lump", "体积平均含水率 (MLg 矩形权)", lump, 1.3832608022188,
        "kg/kg", tol_rel=5e-5)
    chk("Cbar_simp", "体积平均含水率 (Simpson)", simp, None, "kg/kg")
    loss_trap = 100 * (2.55 - trap) / 2.55
    loss_lump = 100 * (2.55 - lump) / 2.55
    chk("loss_trap", "累计失水率 (梯形)", loss_trap, 45.79, "%", tol_rel=5e-5)
    chk("loss_lump", "累计失水率 (MLg)", loss_lump, 45.7545, "%", tol_rel=5e-5)
    print(f"  两种求积的相对差 = {abs(trap-lump)/trap:.3e} "
          f"(论文宣称的离散不确定度 3.85e-5 的 "
          f"{abs(trap-lump)/3.8467e-5:.1f} 倍)")

    print()
    print("=" * 112)
    print("C8b. 干燥前沿 (C = 0.9*C0 = 2.295 kg/kg)")
    print("=" * 112)
    CF = 0.9 * 2.55
    below_any = np.array([(CC[i] < CF).any() for i in range(CC.shape[0])])
    below_ctr = np.array([CC[i][0] < CF for i in range(CC.shape[0])])
    t_first = tC[below_any][0] if below_any.any() else None
    t_ctr = tC[below_ctr][0] if below_ctr.any() else None
    print(f"  首次出现 C<{CF}: t = {t_first} s   (tex 80 s)   "
          f"C(60,-1)={CC[tC==60][0][-1]:.6f}, C(80,-1)={CC[tC==80][0][-1]:.6f}")
    print(f"  中心首次 C<{CF}: t = {t_ctr} s   (tex 6183 s)  "
          f"C(6182,0)={CC[tC==6182][0][0]:.6f}, C(6183,0)={CC[tC==6183][0][0]:.6f}")
    chk("front_first", "干燥前沿出现时刻", float(t_first), 80.0, "s", 1e-12)
    chk("front_center", "干燥前沿抵达中心时刻", float(t_ctr), 6183.0, "s", 1e-12)
    chk("C_60s_surf", "t=60 s 表面含水率", CC[tC == 60][0][-1], 2.3270, "kg/kg")
    chk("Cpct_center", "3 h 中心含水率占初值", 100 * C_end[0] / 2.55, 69.34, "%",
        5e-5)
    chk("Cpct_surf", "3 h 表面含水率占初值", 100 * C_end[-1] / 2.55, 39.52, "%",
        5e-5)
    chk("CR_Cinf", "C(R)/C_inf at 3 h",
        C_end[-1] / 0.04977, 20.25, "-", 5e-4)

    print()
    print("=" * 112)
    print("C7. 径向温差 span(t) = T(R) - T(0)")
    print("=" * 112)
    span = TT[:, -1] - TT[:, 0]
    imax = int(np.argmax(span))
    print(f"  span 峰值 = {span[imax]:.6f} K @ t = {tT[imax]} s "
          f"(tex 3.2819 K @ 2051 s)")
    chk("span_max", "径向温差峰值", float(span[imax]), 3.2819, "K", 5e-5)
    chk("span_max_t", "径向温差峰值时刻", float(tT[imax]), 2051.0, "s", 1e-12)
    for hh in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        i = int(round(hh * 3600)) - 1
        print(f"  span({hh} h) = {span[i]:.6f} K")
    chk("span_h0p5", "span(0.5 h)", float(span[1800 - 1]), 3.2075, "K", 5e-5)
    chk("span_h3", "span(3 h)", float(span[10800 - 1]), 0.1203, "K", 5e-5)

    # exponential fit variants
    print("  指数拟合 log(span) = a - t/tau:")
    for t0, t1, label in ((3600, 10800, "3600~10800 s (1001 pts)"),
                          (1800, 10800, "1800~10800 s (1501 pts)")):
        m = (tT >= t0) & (tT <= t1)
        x = tT[m].astype(float)
        y = np.log(span[m])
        A = np.vstack([np.ones_like(x), -x]).T
        coef, res_, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ coef
        ss_res = ((y - pred) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum()
        tau = 1.0 / coef[1]
        print(f"    {label}: tau = {tau:.4f} s, R2 = {1-ss_res/ss_tot:.6f}, "
              f"max|resid(log)| = {np.abs(y-pred).max():.4f}")
    # residual structure of the reported fit
    m = (tT >= 3600) & (tT <= 10800)
    x = tT[m].astype(float)
    y = np.log(span[m])
    A = np.vstack([np.ones_like(x), -x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    tau = 1.0 / coef[1]
    pred = A @ coef
    resid = span[m] - np.exp(pred)
    print(f"    >>> tau={tau:.6f}, 相对残差 max = "
          f"{np.abs(resid/span[m]).max():.4f}, 残差符号: 前 5 点 "
          f"{np.sign(resid[:5])}, 后 5 点 {np.sign(resid[-5:])}")
    print(f"    span(3600)={span[3600-1]:.6f}, span(10800)={span[10800-1]:.6f}, "
          f"ratio={span[3600-1]/span[10800-1]:.2f}, "
          f"等效 tau={3600/np.log(span[3600-1]/span[10800-1]):.2f} s")
    chk("tau_dT_365", "指数拟合 tau (3600~10800)", tau, 1942.7, "s", 5e-5)
    chk("tau_R2_365", "拟合 R2", 1 - ((y - pred) ** 2).sum()
        / ((y - y.mean()) ** 2).sum(), 0.9789, "-", 5e-5)

    print()
    print("=" * 112)
    print("C9 / Table H. 附件1 环境 + Hevap 定标式 -> 表面热流分解")
    print("=" * 112)
    rows1 = read_att1()
    print(f"  附件1 sheet={rows1[0][:3]}... 总行数={len(rows1)}")
    hdr = rows1[0]
    print(f"  header = {hdr}")
    dat = np.array([[float(v) if v is not None else np.nan for v in r]
                    for r in rows1[1:]])
    print(f"  shape={dat.shape}")
    t1 = dat[:, 0]
    print(f"  t: {t1[0]} .. {t1[-1]}, n={len(t1)}, "
          f"采样间隔={np.unique(np.diff(t1))}")
    Tin = dat[:, 1]
    Cin = dat[:, 2]
    fT = PchipInterpolator(t1, Tin)
    fC = PchipInterpolator(t1, Cin)
    print(f"  T_inf peak = {Tin.max()} @ t = {t1[np.argmax(Tin)]} "
          f"(tex 50.2460 @ 10620 s)")
    m1080 = t1 <= 10800
    print(f"  T_inf 在 0~10800 内 peak = {Tin[m1080].max()} @ "
          f"{t1[m1080][np.argmax(Tin[m1080])]} (tex 50.2460 @ 10620)")
    print(f"  C_inf(10800) = {fC(10800):.6f} (tex 0.04977); "
          f"C_inf min/max = {Cin.min():.5f}/{Cin.max():.5f}")
    chk("Tinf_peak", "T_inf 峰值 (0~10800)", float(Tin[m1080].max()), 50.2460,
        "degC", 5e-5)
    chk("Tinf_peak_t", "T_inf 峰值时刻", float(t1[m1080][np.argmax(Tin[m1080])]),
        10620.0, "s", 1e-12)
    chk("Cinf_end", "C_inf(10800)", float(fC(10800)), 0.04977, "kg/kg", 5e-5)

    H = lambda TK: 2.4346e6 - 2.391e3 * (TK - 273.15 - 28.0)
    hm = 8e-7
    hh = 25.0
    texH = {0.5: (6.1999, 3.0999, 0.0624, 2.01),
            1.0: (4.5931, 2.2966, 0.0548, 2.39),
            1.5: (2.0798, 1.0399, 0.0497, 4.78),
            2.0: (0.9442, 0.4721, 0.0451, 9.55),
            2.5: (0.5879, 0.2940, 0.0407, 13.83),
            3.0: (0.3062, 0.1531, 0.0365, 23.85)}
    print(f"  {'t/h':>5} {'Tinf-TR':>9} {'qconv':>9} {'qevap':>9} "
          f"{'ratio%':>8}   tex")
    for hh_, (dtex, qctex, qetex, rtex) in texH.items():
        ts = int(round(hh_ * 3600))
        i = ts - 1
        TR = TT[i, -1]
        CR = CC[i, -1]
        dT = float(fT(ts)) - TR
        qc = hh * dT * R
        qe = H(TR + 273.15) * hm * (CR - float(fC(ts))) * R
        ratio = 100 * qe / qc
        ok = (abs(dT - dtex) < 5e-5 and abs(qc - qctex) < 5e-5
              and abs(qe - qetex) < 5e-5 and abs(ratio - rtex) < 5e-3)
        print(f"  {hh_:5.1f} {dT:9.4f} {qc:9.4f} {qe:9.4f} {ratio:8.2f}   "
              f"{dtex}/{qctex}/{qetex}/{rtex}  {'OK' if ok else '<<<< CHECK'}")
        ROWS.append([f"H_{hh_}_drive", "表H 驱动力", f"{dT:.6f}", f"{dtex}",
                     "K", "MATCH" if abs(dT - dtex) < 5e-5 else "MISMATCH"])
        ROWS.append([f"H_{hh_}_qconv", "表H q_conv", f"{qc:.6f}", f"{qctex}",
                     "W/m", "MATCH" if abs(qc - qctex) < 5e-5 else "MISMATCH"])
        ROWS.append([f"H_{hh_}_qevap", "表H q_evap", f"{qe:.6f}", f"{qetex}",
                     "W/m", "MATCH" if abs(qe - qetex) < 5e-5 else "MISMATCH"])
        ROWS.append([f"H_{hh_}_ratio", "表H q_evap/q_conv", f"{ratio:.4f}",
                     f"{rtex}", "%", "MATCH" if abs(ratio - rtex) < 5e-3
                     else "MISMATCH"])
    qc05 = hh * (float(fT(1800)) - TT[1800 - 1, -1]) * R
    qc3 = hh * (float(fT(10800)) - TT[10800 - 1, -1]) * R
    print(f"  q_conv 衰减倍数 (0.5h -> 3h) = {qc05/qc3:.4f} (tex 20.2)")
    print(f"  q_evap 变化倍数 (0.5h -> 3h) = "
          f"{H(TT[1800-1,-1]+273.15)*hm*(CC[1800-1,-1]-float(fC(1800)))*R / (H(TT[10800-1,-1]+273.15)*hm*(CC[10800-1,-1]-float(fC(10800)))*R):.4f}")

    # masked window
    drv = np.array([float(fT(s)) for s in tT]) - TT[:, -1]
    nmask = int((np.abs(drv) >= 0.05).sum())
    print(f"  驱动力 |T_inf-T_R| >= 0.05 K 的采样点数 = {nmask} / {len(tT)}"
          f"   (FG_n_ratio_ok=10704, bad=96)")
    print(f"  min|驱动力| = {np.abs(drv).min():.3e} K  "
          f"(FG_drive_min=8.52e-06)")
    print(f"  未掩码 q_evap/q_conv 最大值 = "
          f"{np.max(np.abs((np.array([H(TT[i,-1]+273.15)*hm*(CC[i,-1]-float(fC(tT[i])))*R for i in range(0,10800,1)]) / (hh*drv*R)))):.4f}"
          f"  (FG_ratio_raw_max=8736.85)")

    print()
    print("=" * 112)
    print("其他: 温度范围 / 最小值时刻 / 单调性")
    print("=" * 112)
    print(f"  T min = {TT.min():.6f} @ t={tT[np.unravel_index(np.argmin(TT), TT.shape)[0]]}, "
          f"r={rc[np.unravel_index(np.argmin(TT), TT.shape)[1]]*100:.2f} cm")
    print(f"  T max = {TT.max():.6f}  (tex 49.8888)")
    surf = TT[:, -1]
    print(f"  表面温度 min = {surf.min():.6f} @ t={tT[np.argmin(surf)]} s  "
          f"(tex 27.9905 @ 10 s)")
    idx = np.where(surf >= 28.0)[0]
    print(f"  表面温度回升到 >=28 的时刻 = {tT[idx[idx>np.argmin(surf)][0]]} s  "
          f"(tex 34 s)")
    d = np.diff(CC, axis=0)
    print(f"  水分非单调上升的采样点数 (全网格) = {int((d > 1e-15).sum())}  "
          f"(tex 0)")

    print()
    print("=" * 112)
    print(f"汇总: {NMATCH}")
    print("=" * 112)
    with open(os.path.join(OUT, "_audit_q2_independent.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["tag", "quantity", "independent", "tex_claim", "unit",
                    "verdict"])
        w.writerows(ROWS)
    print(f"写出 {os.path.join(OUT, '_audit_q2_independent.csv')} ({len(ROWS)} 行)")


if __name__ == "__main__":
    main()
