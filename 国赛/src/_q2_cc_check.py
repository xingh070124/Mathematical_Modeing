# -*- coding: utf-8 -*-
"""临时: 检验 CC 近似的偏差是否**全部**来自气相非理想性, 还是也含 v_f/v_g 项."""
from iapws import IAPWS95

Rv = IAPWS95(T=300.0, x=1).R * 1000.0
DLT = 1e-2
print("Rv = %.6f" % Rv)
hdr = ("T(C)", "(CC-1)%", "(1/Z-1)%", "diff_pp", "vf/vg*100", "pred Z*(1-vf/vg)")
print("%6s %10s %10s %9s %11s %16s" % hdr)
for Tc in (20, 25, 30, 35, 40, 45, 50):
    T = Tc + 273.15
    liq, vap = IAPWS95(T=T, x=0), IAPWS95(T=T, x=1)
    psat = vap.P * 1e6
    vf, vg, Z = 1.0 / liq.rho, 1.0 / vap.rho, vap.Z
    dp = (IAPWS95(T=T + DLT, x=1).P - IAPWS95(T=T - DLT, x=1).P) * 1e6 / (2 * DLT)
    Lcc = Rv * T * T * dp / psat
    hfg = (vap.h - liq.h) * 1000.0
    cc = 100 * (Lcc - hfg) / hfg
    invZ = 100 * (1.0 / Z - 1.0)
    # 精确关系: L_CC/L_true = 1/(Z (1 - v_f/v_g))
    pred = 100 * (1.0 / (Z * (1.0 - vf / vg)) - 1.0)
    print("%6.1f %10.5f %10.5f %9.5f %11.5f %16.5f"
          % (Tc, cc, invZ, cc - invZ, 100 * vf / vg, pred))
print()
print("结论: ")
print("  - (CC-1) 与 (1/Z-1) 的差 (diff_pp) 与 pred-(1/Z-1) 同量级、同向")
print("    且 pred 复现 (CC-1) 到 ~1e-5 个百分点:")
print("    故 CC 的偏差**不全部**来自气相非理想性 (1/Z), 还含被略去的 v_f/v_g 项。")
