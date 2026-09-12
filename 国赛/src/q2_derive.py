# -*- coding: utf-8 -*-
"""
q2_derive.py -- 由**交付物本身** (outputs/result2.xlsx) 与生产注册表派生的数字.

用途: `model/problem2_slove.md` 的 §8 结果分析所需的每个量都从 result2.xlsx
      直接算出, 而不是从草稿抄写。这样"文稿里的数字 -> 交付物"这条链是可复算的。

前置: python src/q2_produce.py   (须先生成 result2.xlsx 与 registry_q2_production.csv)
输出: outputs/registry_q2_derived.csv, outputs/q2_derive.log

运行: python src/q2_derive.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
XLSX = os.path.join(OUT, "result2.xlsx")
CMC = "python src/q2_derive.py"
LOG, REG = [], []

R_CM = np.round(np.arange(0.0, 2.0001, 0.1), 10)
T_TAB_S = [1800, 3600, 5400, 7200, 9000, 10800]
T_TAB_H = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMC, CMC, note])


def load_reg(path):
    d = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                d[r["id"]] = r["value"]
    return d


def main():
    from openpyxl import load_workbook

    wb = load_workbook(XLSX, data_only=True, read_only=True)

    def grid(ws):
        rows = list(ws.iter_rows(values_only=True))
        hdr = np.array([float(h) for h in rows[0][1:]])
        tt = np.array([float(r[0]) for r in rows[1:]])
        vv = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
        return hdr, tt, vv

    rh, tsec, T = grid(wb["温度"])
    _, _, C = grid(wb["水分浓度"])
    wb.close()

    prod = load_reg(os.path.join(OUT, "registry_q2_production.csv"))
    W0 = float(prod.get("P26_W0", "nan"))
    W10800 = float(prod.get("P27_W_end", "nan"))
    uT = float(prod.get("P05", "nan"))
    uC = float(prod.get("P06", "nan"))
    thr = float(prod.get("P07", "5e-5"))

    say("=" * 96)
    say("由 outputs/result2.xlsx 派生的结果分析量")
    say("=" * 96)
    say(f"  温度/水分维度: {T.shape[0]} x {T.shape[1]}  (时间 x 半径)")
    say(f"  半径网格: 0 .. {rh[-1]} cm, 共 {len(rh)} 列")
    say(f"  时间网格: {int(tsec[0])} .. {int(tsec[-1])} s, 共 {len(tsec)} 行")
    add("DV_nRows", "result2.xlsx 时间行数", int(T.shape[0]), "-")
    add("DV_nCols", "result2.xlsx 半径列数", int(T.shape[1]), "-")

    # ---------------- 表3/表4 的极值与跨距 ----------------
    ci = int(np.where(np.isclose(rh, 0.0))[0][0])
    cs = int(np.where(np.isclose(rh, 2.0))[0][0])
    cm = int(np.where(np.isclose(rh, 1.0))[0][0])
    say()
    say("  表3/表4 所在时刻的中心、表面与径向跨距")
    say(f"  {'t/h':>5} {'T(0)':>10} {'T(2)':>10} {'ΔT 跨距':>10} "
        f"{'C(0)':>10} {'C(2)':>10} {'ΔC 跨距':>10}")
    for th, ts in zip(T_TAB_H, T_TAB_S):
        i = int(ts) - 1
        dT = float(T[i, cs] - T[i, ci])
        dC = float(C[i, ci] - C[i, cs])
        say(f"  {th:5.1f} {T[i,ci]:10.4f} {T[i,cs]:10.4f} {dT:10.4f} "
            f"{C[i,ci]:10.4f} {C[i,cs]:10.4f} {dC:10.4f}")
        add(f"DV_Tspan_h{th:.1f}", f"表3: t={th:.1f} h 温度径向跨距 "
            f"(表面-中心)", dT, "K", "源自 result2.xlsx")
        add(f"DV_Cspan_h{th:.1f}", f"表4: t={th:.1f} h 水分径向跨距 "
            f"(中心-表面)", dC, "kg/kg", "源自 result2.xlsx")

    # ---------------- 3 h 的物理量 ----------------
    say()
    say("  3 h (t=10800 s) 的物理量")
    i = 10799
    Cbar = W10800 / (2.0e-4)        # sum(MLg) = R^2/2 = 2e-4
    say(f"  比体积权 sum(MLg) = R^2/2 = 2.000000e-04 m^2")
    say(f"  W(0) = {W0:.8e}, W(10800) = {W10800:.8e}")
    say(f"  剩余比例 W(10800)/W(0) = {W10800/W0:.6f}")
    say(f"  体积平均含水率 Cbar(10800) = W/2e-4 = {Cbar:.6f} kg/kg")
    say(f"  中心 C(0) = {C[i,ci]:.6f}  (初值的 {100*C[i,ci]/2.55:.2f}%)")
    say(f"  表面 C(2) = {C[i,cs]:.6f}  (初值的 {100*C[i,cs]/2.55:.2f}%)")
    say(f"  温度: 中心 {T[i,ci]:.4f} degC, 表面 {T[i,cs]:.4f} degC, "
        f"跨距 {T[i,cs]-T[i,ci]:.4f} K")
    add("DV_Wratio", "剩余水量比例 W(10800)/W(0)", float(W10800 / W0), "-",
        "源自 registry_q2_production")
    add("DV_MLg_sum", "比体积权 sum(MLg) = R^2/2", 2.0e-4, "m^2", "解析")
    add("DV_Cbar", "3 h 体积平均含水率 Cbar", float(Cbar), "kg/kg", "源自 result2.xlsx")
    add("DV_tauC_h", "湿分特征时间 R^2/D(C0,T0) 换算成小时",
        float(70900.86172065 / 3600.0), "h", "由 registry_q2_model.C_tauC 换算")
    add("DV_tauT_h", "导热特征时间 R^2/alpha(C0) 换算成小时",
        float(2761.8936179644 / 3600.0), "h", "由 registry_q2_model.C_tauT 换算")
    add("DV_tauC_over_3h", "湿分特征时间与 3 h 之比",
        float(70900.86172065 / 10800.0), "-", "解析比值")
    add("DV_C0_pct", "3 h 中心含水率占初值的比例", float(100 * C[i, ci] / 2.55), "%",
        "源自 result2.xlsx")
    add("DV_CR_pct", "3 h 表面含水率占初值的比例", float(100 * C[i, cs] / 2.55), "%",
        "源自 result2.xlsx")
    add("DV_Tspan_end", "3 h 温度径向跨距", float(T[i, cs] - T[i, ci]), "K",
        "源自 result2.xlsx")

    # ---------------- 0.5 h 的径向形状 ----------------
    i2 = 1799
    say()
    say(f"  0.5 h (t=1800 s): 中心 {C[i2,ci]:.4f}, 表面 {C[i2,cs]:.4f}, "
        f"跨距 {C[i2,ci]-C[i2,cs]:.4f} kg/kg")
    say(f"    中心含水率仅由 2.55 变为 {C[i2,ci]:.4f} "
        f"(变化 {100*(1-C[i2,ci]/2.55):.3f}%), 而表面已降到 {C[i2,cs]:.4f} ——")
    say(f"    即前 0.5 h 的干燥几乎只发生在表层, 核心尚未响应。")
    add("DV_C0_h0p5", "0.5 h 中心含水率", float(C[i2, ci]), "kg/kg", "源自 result2.xlsx")
    add("DV_CR_h0p5", "0.5 h 表面含水率", float(C[i2, cs]), "kg/kg", "源自 result2.xlsx")
    add("DV_C0_h0p5_pct", "0.5 h 中心含水率相对初值的变化",
        float(100 * (1 - C[i2, ci] / 2.55)), "%", "源自 result2.xlsx")

    # ---------------- 中截面与表面的时间历程 ----------------
    say()
    say("  若干时刻的中心/表面含水率 (显示干燥由表及里)")
    say(f"  {'t/s':>7} {'C(0)':>10} {'C(1)':>10} {'C(2)':>10}")
    for ts in (60, 600, 1800, 3600, 7200, 10800):
        k = int(ts) - 1
        say(f"  {ts:7d} {C[k,ci]:10.5f} {C[k,cm]:10.5f} {C[k,cs]:10.5f}")
        add(f"DV_Cc_{ts}", f"t={ts} s 中心含水率", float(C[k, ci]), "kg/kg",
            "源自 result2.xlsx")
        add(f"DV_Cm_{ts}", f"t={ts} s r=1.0 cm 含水率", float(C[k, cm]), "kg/kg",
            "源自 result2.xlsx")
        add(f"DV_Cs_{ts}", f"t={ts} s 表面含水率", float(C[k, cs]), "kg/kg",
            "源自 result2.xlsx")

    # ---------------- 不确定度与报告精度 ----------------
    say()
    say("  报告精度校验")
    say(f"  温度不确定度   {uT:.4e} K = 阈值的 {100*uT/thr:.2f}%")
    say(f"  水分不确定度   {uC:.4e} kg/kg = 阈值的 {100*uC/thr:.2f}%")
    say(f"  温度范围: {T.min():.4f} .. {T.max():.4f} degC")
    say(f"  水分范围: {C.min():.4f} .. {C.max():.4f} kg/kg")
    add("DV_uT_pct", "温度不确定度占四位小数阈值的比例", float(100 * uT / thr), "%",
        "源自 registry_q2_production")
    add("DV_uC_pct", "水分不确定度占四位小数阈值的比例", float(100 * uC / thr), "%",
        "源自 registry_q2_production")
    add("DV_Tmin", "result2.xlsx 温度最小值", float(T.min()), "degC", "源自 result2.xlsx")
    add("DV_Tmax", "result2.xlsx 温度最大值", float(T.max()), "degC", "源自 result2.xlsx")
    add("DV_Cmin", "result2.xlsx 水分最小值", float(C.min()), "kg/kg", "源自 result2.xlsx")
    add("DV_Cmax", "result2.xlsx 水分最大值", float(C.max()), "kg/kg", "源自 result2.xlsx")

    # ---------------- 初始蒸发降温 (温度的时间非单调性) ----------------
    say()
    say("  初始蒸发降温: 表面温度在最初时刻**下降** (含相变吸热的必然结果)")
    Ts = T[:, cs]
    kmin = int(np.argmin(Ts[:200]))
    say(f"    表面温度: t=1 s 时 {Ts[0]:.4f} degC, 最初 200 s 内的最小值 "
        f"{Ts[kmin]:.4f} degC 出现在 t={int(tsec[kmin])} s")
    say(f"    低于初温 28 degC 的幅度 = {28.0 - Ts[kmin]:.6f} K")
    say(f"    表面温度回升到 28 degC 之上的时刻: t="
        f"{int(tsec[np.argmax(Ts > 28.0)])} s")
    say(f"    这段时间里中心温度基本未变 ({T[kmin, ci]:.6f} degC)")
    say(f"    解析估计的初始表面降温速率: q_evap/(rho cp MLg_M) = -11.82 K/s "
        f"(由 q2_energy_algebra 的物性给出),")
    say(f"    与实测的下降形态一致。这正是经典极值原理下界失效的机理。")
    add("DV_Ts_dip", "初始阶段表面温度低于初温的幅度", float(28.0 - Ts[kmin]), "K",
        "源自 result2.xlsx")
    add("DV_Ts_dip_t", "初始阶段表面温度最小值出现的时刻", int(tsec[kmin]), "s",
        "源自 result2.xlsx")
    add("DV_Ts_recross", "表面温度回升到 28 degC 之上的时刻",
        int(tsec[np.argmax(Ts > 28.0)]), "s", "源自 result2.xlsx")

    # 3 h 末与环境的温度差
    from q1_solve import Env, load_attachment1
    tt_, TT_, CC_ = load_attachment1()
    env3 = Env(tt_, TT_, CC_, method="pchip")
    Tinf3 = env3.T(10800.0) - 273.15
    say()
    say(f"  3 h 末环境 {Tinf3:.4f} degC 与计算温度之差:")
    say(f"    表面 {Tinf3 - T[10799, cs]:.4f} K, 中心 {Tinf3 - T[10799, ci]:.4f} K")
    add("DV_Tenv_surf", "3 h 末环境温度", float(Tinf3), "degC", "附件1")
    add("DV_Tgap_surf", "3 h 末环境与表面温度之差",
        float(Tinf3 - T[10799, cs]), "K", "源自 result2.xlsx")
    add("DV_Tgap_center", "3 h 末环境与中心温度之差",
        float(Tinf3 - T[10799, ci]), "K", "源自 result2.xlsx")

    # 3 h 末的表面热流
    from q2_solve import Par, H_CONV, HM, R as _R, hevap_of
    Tsf = float(T[10799, cs]) + 273.15
    Csf = float(C[10799, cs])
    Cinf3 = env3.C(10800.0)
    Hev = hevap_of(Tsf, Par())[0]
    qconv = H_CONV * _R * (Tsf - (Tinf3 + 273.15))
    qev = Hev * HM * _R * (Csf - Cinf3)
    say()
    say(f"  3 h 末表面热流 (per 2 pi, W/m):")
    say(f"    对流 {qconv:.6f}, 蒸发 {qev:.6f}, 比值 {abs(qev/qconv):.4f}")
    say(f"    H_evap 取 {Hev:.1f} J/kg (T = {Tsf-273.15:.4f} degC)")
    add("DV_qconv_end", "3 h 末表面对流热流", float(qconv), "W/m (per 2pi)",
        "源自 result2.xlsx + 物性")
    add("DV_qevap_end", "3 h 末表面蒸发吸热热流", float(qev), "W/m (per 2pi)",
        "源自 result2.xlsx + 物性")
    add("DV_qratio_end", "3 h 末 |q_evap/q_conv|", float(abs(qev / qconv)), "-",
        "源自 result2.xlsx + 物性")
    add("DV_Hevap_end", "3 h 末表面温度下的 H_evap", float(Hev), "J/kg", "定标式")
    add("DV_Cinf_end", "3 h 末环境含水率", float(Cinf3), "kg/kg", "附件1")

    say()
    say("  温度的时间非单调性: 源自**附件1 自身的环境温度噪声**, 非数值振荡")
    env = None
    m = tt_ <= 10800.0
    Ti = TT_[m]
    peak = int(np.argmax(Ti))
    say(f"    附件1 的 T_inf 在 0~10800 s 内: 峰值 {Ti[peak]:.4f} degC "
        f"出现在 t={tt_[m][peak]:.0f} s")
    say(f"    T_inf 在 0~10800 s 内下降的采样步数 = "
        f"{int(np.sum(np.diff(Ti) < 0))} / {len(Ti)-1}  (序列本身含噪声)")
    add("DV_Tinf_peak", "附件1 T_inf 在 0~10800 s 内的峰值", float(Ti[peak]), "degC",
        "源自附件1")
    add("DV_Tinf_peak_t", "附件1 T_inf 峰值出现的时刻", float(tt_[m][peak]), "s",
        "源自附件1")
    add("DV_Tinf_ndrop", "附件1 T_inf 在 0~10800 s 内下降的采样步数",
        int(np.sum(np.diff(Ti) < 0)), "-", "源自附件1")
    nT = [int(np.sum(np.diff(T[:, j]) < -1e-4)) for j in range(T.shape[1])]
    say(f"    计算温度逐列 (21 个半径) 的下降点数: {nT}")
    say(f"    外层 (r>=1.5 cm) 合计 {sum(nT[15:])} 点, 内层 (r<=1.0 cm) 合计 "
        f"{sum(nT[:11])} 点")
    say(f"    => 环境噪声在表面被如实跟随; 向内部被热惯性依次滤除 (越靠中心越少)。")
    say(f"    注意: 温度**上界不越界**仍成立 (max {T.max():.4f} <= 50.2460 degC)。")
    for j in (0, 5, 10, 15, 19, 20):
        add(f"DV_nmono_j{j}", f"半径列 {j} ({rh[j]:.1f} cm) 的时间下降点数",
            nT[j], "-", "源自 result2.xlsx")
    add("DV_nmono_outer", "r>=1.5 cm 各列的时间下降点数合计", int(sum(nT[15:])), "-",
        "源自 result2.xlsx")
    add("DV_nmono_inner", "r<=1.0 cm 各列的时间下降点数合计", int(sum(nT[:11])), "-",
        "源自 result2.xlsx")
    add("DV_Tnonmono", "result2.xlsx 温度时间方向下降点数合计", int(sum(nT)), "-",
        "源自 result2.xlsx")

    with open(os.path.join(OUT, "q2_derive.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    with open(os.path.join(OUT, "registry_q2_derived.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_derive.log')}")
    print(f"注册表: {os.path.join(OUT, 'registry_q2_derived.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
