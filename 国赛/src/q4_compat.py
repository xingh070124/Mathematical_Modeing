# -*- coding: utf-8 -*-
"""
q4_compat.py -- 附件 2 收缩数据与"无孔隙体积可加"假设的相容性检验.

模型: V = V_d + V_w, 干基含水率 C = M_w/M_d, kappa = rho_w/rho_d
      => V/V0 = (kappa + C)/(kappa + C0)  =>  C = (C0+kappa)*(V/V0) - kappa
      径向收缩: V/V0 = (R/R0)^2

输出: outputs/q4_compat.log 与 outputs/registry_q4_compat.csv
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q4_solve import load_attachment2, solve_q4, sample_q4     # noqa: E402
from q2_solve import C0                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
RHO_W = 1000.0
LOG = []


def say(m):
    print(m, flush=True)
    LOG.append(m)


def main():
    t, R = load_attachment2()
    x = (R / R[0]) ** 2                     # V/V0 (径向收缩)
    say("附件2: R(0)=%.3f cm, R(72h)=%.4f cm, (R/R0)^2 由 %.4f 降到 %.4f"
        % (R[0], R[-1], x[0], x[-1]))
    say("无孔隙体积可加假设: C = (C0+kappa)*(V/V0) - kappa,  kappa = rho_w/rho_d, C0=%.2f" % C0)
    say("")

    hrs = [0.5, 1, 2, 4, 6, 12, 18, 24, 36, 48, 60, 72]
    idx = [int(np.argmin(np.abs(t - h * 3600))) for h in hrs]

    # 两个代表 kappa 下的隐含平均含水率
    say("%8s %8s %10s | %14s %14s" % ("t/h", "R/cm", "(R/R0)^2",
                                      "Cbar(kappa=1.111)", "Cbar(kappa=0.667)"))
    say("%8s %8s %10s | %14s %14s" % ("", "", "", "rho_d=900", "rho_d=1500"))
    implied = {}
    for h, i in zip(hrs, idx):
        c1 = (C0 + 1.111) * x[i] - 1.111
        c2 = (C0 + 0.667) * x[i] - 0.667
        implied[h] = (c1, c2)
        say("%8.1f %8.3f %10.4f | %14.4f %14.4f" % (h, R[i], x[i], c1, c2))
    say("")

    # C=0 的临界半径
    for kappa, rhod in ((1.111, 900.0), (0.667, 1500.0), (1.0, 1000.0)):
        r_c = R[0] * np.sqrt(kappa / (C0 + kappa))
        say("kappa=%.4f (rho_d=%4.0f): 隐含 Cbar=0 出现在 R=%.4f cm; 附件2 在 0~72 h 内的"
            "最小半径 %.4f cm -> %s"
            % (kappa, rhod, r_c, R.min(),
               "未达到" if R.min() > r_c else "已达到"))
    say("")

    # 与本文模型 Cbar(t) 逐时刻比对, 反解所需 kappa
    res = solve_q4(M=200)
    s = sample_q4(res["sol"], res["g"], res["rad"], res["t_dry"])
    MLsum = res["g"]["MLg"].sum()
    say("本文模型 (生产解) 的 Cbar(t) 反解出的所需 kappa:")
    say("  由 Cbar = C0*x - kappa*(1-x)  =>  kappa = (C0*x - Cbar)/(1-x)")
    say("%8s %12s %12s %14s %14s" % ("t/h", "Cbar_model", "(R/R0)^2",
                                      "required kappa", "required rho_d"))
    kappas = {}
    for h in [6, 12, 18, 24, 36, 48, 51.1]:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600)))
        iR = int(np.argmin(np.abs(t - s["t60"][i])))
        Cb = s["W60"][i] / MLsum
        xi = (R[iR] / R[0]) ** 2
        k = (C0 * xi - Cb) / (1.0 - xi)
        kappas[h] = k
        say("%8.1f %12.4f %12.4f %14.4f %14.1f" % (h, Cb, xi, k, RHO_W / k))
    ks = np.array(list(kappas.values()))
    say("")
    say("=> 反解 kappa 由 %.3f (6 h) 升到 %.3f (%.1f h), 变化 %.1f 倍;"
        % (ks[0], ks[-1], list(kappas)[-1], ks[-1] / ks[0]))
    say("   对应所需 rho_d 由 %.0f 降到 %.0f kg/m^3." % (RHO_W / ks[0], RHO_W / ks[-1]))
    say("   不存在单一干密度使体积可加关系与扩散模型全程一致.")

    # 单 kappa 要求: 让关系式在 72 h 恰好给出 C* = 0.15
    i72 = int(np.argmin(np.abs(t - 72 * 3600)))
    x72 = x[i72]
    k_star = (C0 * x72 - 0.15) / (1.0 - x72)
    say("")
    say("要让体积可加关系在 72 h 恰好给出阈值 0.15 kg/kg, 需 kappa*=%.4f (rho_d=%.0f kg/m^3);"
        % (k_star, RHO_W / k_star))
    say("   而要让它在 6 h 与扩散模型一致, 需 rho_d=%.0f —— 两者相差 %.1f 倍."
        % (RHO_W / ks[0], (RHO_W / ks[0]) / (RHO_W / k_star)))
    say("   故 R(t) 是独立的实验观测量, 不能由水分收支导出 (假设 D3).")

    # 取中药材常规干密度 rho_d=1300 作为代表值
    rho_d_rep, kappa_rep = 1300.0, RHO_W / 1300.0
    say("")
    say("代表值 rho_d=%.0f (kappa=%.4f, 植物组织常规量级) 下该关系给出的 Cbar:" % (rho_d_rep, kappa_rep))
    for h in [6, 12, 24, 48, 72]:
        i = int(np.argmin(np.abs(t - h * 3600)))
        cb = C0 * x[i] - kappa_rep * (1 - x[i])
        say("   t=%5.0f h: R=%.3f cm -> Cbar=%.4f kg/kg  (阈值的 %.2f 倍)" % (h, R[i], cb, cb / 0.15))

    rows = []
    for h, i in zip(hrs, idx):
        rows.append((f"compat_R_{h:g}h", f"t={h} h 半径 R", float(R[i]), "cm", "compat", "附件2"))
        rows.append((f"compat_x_{h:g}h", f"t={h} h (R/R0)^2", float(x[i]), "1", "compat", "附件2"))
        rows.append((f"compat_Cb_k1p111_{h:g}h", f"kappa=1.111 时反解 Cbar (t={h} h)",
                     float(C0 * x[i] - 1.111 * (1 - x[i])), "kg/kg", "compat", "推导"))
        rows.append((f"compat_Cb_k0p667_{h:g}h", f"kappa=0.667 时反解 Cbar (t={h} h)",
                     float(C0 * x[i] - 0.667 * (1 - x[i])), "kg/kg", "compat", "推导"))
    for kappa, rhod in ((1.111, 900.0), (0.667, 1500.0), (1.0, 1000.0), (0.769, 1300.0)):
        r_c = R[0] * np.sqrt(kappa / (C0 + kappa))
        rows.append((f"compat_rC0_k{kappa:g}", f"kappa={kappa} (rho_d={rhod:g}) 时隐含 C=0 的半径",
                     float(r_c), "cm", "compat", "推导"))
    for h, k in kappas.items():
        rows.append((f"compat_kappa_{h}h", f"使模型与体积可加一致的 kappa (t={h} h)",
                     float(k), "1", "compat", "outputs/q4_compat.log"))
    # 附录 C.4 的表格: 四个代表干密度下的反解 Cbar (逐点, 供论文表格逐位引用)
    say("")
    say("附录 C.4 用表: 四个代表干密度下由附件2 反解的体积平均含水率")
    say("%8s %8s %10s | %10s %10s %10s %10s" % ("t/h", "R/cm", "(R/R0)^2",
                                                 "rho=900", "1000", "1300", "1500"))
    for h in [0.0, 6.0, 12.0, 24.0, 72.0]:
        i = int(np.argmin(np.abs(t - h * 3600)))
        xi = x[i]
        vals = []
        for rhod in (900.0, 1000.0, 1300.0, 1500.0):
            kp = RHO_W / rhod
            vals.append(C0 * xi - kp * (1.0 - xi))
        say("%8.1f %8.3f %10.4f | %10.4f %10.4f %10.4f %10.4f"
            % (h, R[i], xi, *vals))
        rows.append((f"compat_tab_R_{h:g}h", f"附录C.4 表 t={h} h 半径",
                     float(R[i]), "cm", "compat", "附件2"))
        rows.append((f"compat_tab_x_{h:g}h", f"附录C.4 表 t={h} h (R/R0)^2",
                     float(xi), "1", "compat", "推导"))
        for rhod, v in zip((900.0, 1000.0, 1300.0, 1500.0), vals):
            rows.append((f"compat_tab_C_{h:g}h_{int(rhod)}",
                         f"附录C.4 表 t={h} h rho_d={int(rhod)} 的反解 Cbar",
                         float(v), "kg/kg", "compat", "推导"))
            rows.append((f"compat_rhod_{int(rhod)}",
                         f"附录C.4 表所用代表干密度 {int(rhod)}",
                         float(rhod), "kg/m^3", "compat", "设定值"))

    # 反解所需干密度 (附录 C.4 第三条读法)
    for h in [6.0, 51.1]:
        i = int(np.argmin(np.abs(t - h * 3600)))
        Cb = np.interp(t[i], t, (R / R[0]) ** 2)  # 占位, 下面用模型解重算
    res_c = solve_q4(M=200)
    s_c = sample_q4(res_c["sol"], res_c["g"], res_c["rad"], res_c["t_dry"])
    MLsum = res_c["g"]["MLg"].sum()
    for h in [6.0, 12.0, 18.0, 24.0, 36.0, 48.0, 51.1]:
        i = int(np.argmin(np.abs(s_c["t60"] - h * 3600)))
        iR = int(np.argmin(np.abs(t - s_c["t60"][i])))
        Cb = s_c["W60"][i] / MLsum
        xi = x[iR]
        kp = (C0 * xi - Cb) / (1.0 - xi)
        rows.append((f"compat_req_kappa_{h:g}h",
                     f"使模型与体积可加一致的 kappa (t={h} h)", float(kp), "1",
                     "compat", "q4_compat.py"))
        rows.append((f"compat_req_rhod_{h:g}h",
                     f"上式换算的干密度 (t={h} h)", float(RHO_W / kp), "kg/m^3",
                     "compat", "q4_compat.py"))

    # 临界半径: 要求 r_c >= R_min 所需的 kappa 与 rho_d 上界
    k_need = (R.min() / R[0]) ** 2 / (1.0 - (R.min() / R[0]) ** 2) * C0
    say("")
    say("临界半径判据: 要求 r_c >= R_min=%.4f cm, 需 kappa >= %.4f, 等价 rho_d <= %.1f kg/m^3"
        % (R.min(), k_need, RHO_W / k_need))
    rows.append(("compat_kappa_need", "使 r_c >= R_min 所需的最小 kappa",
                 float(k_need), "1", "compat", "推导"))
    rows.append(("compat_rhod_max", "由上一行换算的干密度上界",
                 float(RHO_W / k_need), "kg/m^3", "compat", "推导"))
    rows.append(("compat_Rmin", "附件2 全程最小半径", float(R.min()), "cm",
                 "compat", "附件2"))

    rows.append(("compat_Rmin", "附件2 在 0~72 h 的最小半径", float(R.min()), "cm", "compat", "附件2"))
    rows.append(("compat_kappa_ratio", "反解 kappa 的首末比值",
                 float(ks[-1] / ks[0]), "1", "compat", "推导"))
    rows.append(("compat_kappa_star", "使 72 h 恰为 0.15 的 kappa", float(k_star), "1", "compat", "推导"))
    rows.append(("compat_rhod_star", "上式对应的干密度", float(RHO_W / k_star),
                 "kg/m^3", "compat", "推导"))
    i72 = int(np.argmin(np.abs(t - 72 * 3600)))
    rows.append(("compat_Cb_rho1300_72h",
                 "rho_d=1300 时该关系在 72 h 给出的 Cbar",
                 float(C0 * x[i72] - kappa_rep * (1 - x[i72])), "kg/kg", "compat", "推导"))

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "registry_q4_compat.csv"), "w",
              newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "group", "source"])
        for r in rows:
            w.writerow(r)
    with open(os.path.join(OUTDIR, "q4_compat.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    say("\n写出: outputs/registry_q4_compat.csv (%d 行)" % len(rows))


if __name__ == "__main__":
    main()
