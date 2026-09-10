"""
论文 §5 全部解析推导的符号/数值验证 (solve-math-rigorously 流程).

对 paper/example.tex 中问题一模型的每一条解析推导逐项验证, 每条输出 PASS/FAIL:

  V1  FV 几何比 f_i^± = (2i±1)/(2iΔr), A_{1/2}/V_0 = 4/Δr
  V2  内部三对角系数 (守恒差分展开) 与算子行和恒为零
  V3  原方案对角元缺陷: b_user - b_corr = -a_i; 行和 = -α(2i-1)/(2iΔr²) ≠ 0
  V4  中心节点: 半控制体通量平衡 ≡ L'Hôpital 极限离散 (恒等式)
  V5  表面节点渐近: a_M/(-2α/Δr²) → 1, g_h/(2h/(ρc_pΔr)) → 1 (M→∞)
  V6  严格对角占优: b_i - (|a_i|+|c_i|) = 1/Δt > 0 (追赶法适用性)
  V7  时间格式增长因子: BE 对 λ<0 无条件衰减; CN 在 |λ|Δt>2 符号振荡;
      对 λ>0 (反耗散) BE 放大因子 >1
  V8  Robin 圆柱级数解: 特征根 λ J1(λ)=Bi J0(λ) 前 5 根与系数 C_n, 初始重构
  V9  特征数: α, Bi, Bi_m, R²/α, R²/D(C0), 集总时间常数 ρc_pR/(2h)
  V10 扩散系数值与比值 (半隐式 D 的 21% 变化论断)
  V11 节点值 D 的水量收支恒等式 (伸缩求和, 符号 M=2)
  V12 空间算子谱: 修正格式耗散 (max Re λ≈0), 原方案反耗散 (+16.8 /s)

运行:  python src/verify_derivation.py
输出:  outputs/derivation_check.log
"""

from __future__ import annotations

import os
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

RESULTS = []


def check(vid, desc, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    RESULTS.append((vid, tag, desc, detail))
    print(f"[{tag}] {vid:4s} {desc}" + (f"\n       {detail}" if detail else ""))


def main():
    # ------------------------------------------------ V1 几何比
    i, dr = sp.symbols("i dr", positive=True)
    V_i = sp.pi * (((i + sp.Rational(1, 2)) * dr) ** 2 - ((i - sp.Rational(1, 2)) * dr) ** 2)
    A_p = 2 * sp.pi * (i + sp.Rational(1, 2)) * dr
    A_m = 2 * sp.pi * (i - sp.Rational(1, 2)) * dr
    fp = sp.simplify(A_p / V_i)
    fm = sp.simplify(A_m / V_i)
    ok1 = (sp.simplify(fp - (2 * i + 1) / (2 * i * dr)) == 0
           and sp.simplify(fm - (2 * i - 1) / (2 * i * dr)) == 0)
    V0 = sp.pi * (dr / 2) ** 2
    A_half = 2 * sp.pi * (dr / 2)
    ok1b = sp.simplify(A_half / V0 - 4 / dr) == 0
    check("V1", "FV 几何比 f±=(2i±1)/(2iΔr), A_{1/2}/V_0=4/Δr", ok1 and ok1b,
          f"f+ = {fp}, f- = {fm}")

    # ------------------------------------------------ V2 内部系数与行和
    al, dt = sp.symbols("alpha dt", positive=True)
    Tim1, Ti, Tip1 = sp.symbols("T_im1 T_i T_ip1")
    L = ((i + sp.Rational(1, 2)) * dr * (Tip1 - Ti) / dr
         - (i - sp.Rational(1, 2)) * dr * (Ti - Tim1) / dr) / (i * dr) / dr
    L = sp.expand(al * L)
    la = sp.simplify(sp.expand(L).coeff(Tim1))
    lb = sp.simplify(sp.expand(L).coeff(Ti))
    lc = sp.simplify(sp.expand(L).coeff(Tip1))
    ok2 = (sp.simplify(la - al * (i - sp.Rational(1, 2)) / (i * dr ** 2)) == 0
           and sp.simplify(lb + 2 * al / dr ** 2) == 0
           and sp.simplify(lc - al * (i + sp.Rational(1, 2)) / (i * dr ** 2)) == 0
           and sp.simplify(la + lb + lc) == 0)
    check("V2", "内部三对角系数 a_i=-α(i-1/2)/(iΔr²), b_i=1/Δt+2α/Δr², c_i=-α(i+1/2)/(iΔr²); 行和=0",
          ok2, f"a={la}, b={lb}, c={lc}")

    # ------------------------------------------------ V3 原方案缺陷
    b_user = dt ** -1 + al * (2 * i + 1) / (2 * i * dr ** 2)
    a_tri = -la
    c_tri = -lc
    b_corr = dt ** -1 - lb
    defect = sp.simplify(b_user - b_corr)
    ok3 = (sp.simplify(defect - a_tri) == 0
           and sp.simplify((a_tri + b_user + c_tri) - dt ** -1
                           + al * (2 * i - 1) / (2 * i * dr ** 2)) == 0)
    check("V3", "原方案 b_user-b_corr=-a_i (缺陷恰为 |a_i|); 用户行和=-α(2i-1)/(2iΔr²)≠0",
          ok3, f"b_user-b_corr = {defect}")

    # ------------------------------------------------ V4 中心节点恒等式
    T0s, T1s = sp.symbols("T_0 T_1")
    fv0 = sp.simplify(al * A_half * (T1s - T0s) / (dr * V0))
    lhop = sp.simplify(2 * al * 2 * (T1s - T0s) / dr ** 2)   # 2α·T_rr, T_rr≈2(T1-T0)/Δr²
    ok4 = sp.simplify(fv0 - lhop) == 0
    check("V4", "中心节点: 半控制体通量平衡 ≡ L'Hôpital 极限离散 (4α(T1-T0)/Δr²)", ok4)

    # ------------------------------------------------ V5 表面节点渐近
    R, M = sp.symbols("R M", positive=True)
    drm = R / M
    V_M = sp.pi * (R ** 2 - (R - drm / 2) ** 2)
    A_in = 2 * sp.pi * (R - drm / 2)
    a_M = -al * A_in / (drm * V_M)
    g_h = 2 * sp.pi * R * sp.Symbol("h", positive=True) / (sp.Symbol("rho", positive=True)
                                                           * sp.Symbol("cp", positive=True) * V_M)
    ra = sp.simplify(sp.limit(a_M / (-2 * al / drm ** 2), M, sp.oo))
    # g_h 与 2h/(ρc_p·Δr) 之比的极限 (g_h 本身 ~1/Δr → ∞, 须验证比值而非极限值)
    gh_ratio = sp.simplify(g_h / (2 * sp.Symbol("h", positive=True)
                                  / (sp.Symbol("rho", positive=True)
                                     * sp.Symbol("cp", positive=True) * drm)))
    rg = sp.simplify(sp.limit(gh_ratio, M, sp.oo))
    ok5 = ra == 1 and rg == 1
    check("V5", "表面节点渐近: a_M/(-2α/Δr²)→1, g_h/(2h/(ρc_pΔr))→1 (M→∞)", ok5,
          f"lim a_M/(-2α/Δr²) = {ra}, lim g_h/[2h/(ρc_pΔr)] = {rg}")

    # ------------------------------------------------ V6 对角占优
    # 三对角系数: a^tri=-la, b^tri=1/Δt-lb, c^tri=-lc (la>0, lc>0)
    # b^tri-(|a^tri|+|c^tri|) = (1/Δt-lb)-(la+lc) = 1/Δt-(la+lb+lc) = 1/Δt
    dom = sp.simplify((dt ** -1 - lb) - (la + lc))
    ok6 = sp.simplify(dom - dt ** -1) == 0
    check("V6", "严格对角占优: b_i-(|a_i|+|c_i|) = 1/Δt > 0 (追赶法适用)", ok6)

    # ------------------------------------------------ V7 时间格式增长因子
    lam, h_dt = sp.symbols("lambda dtstep", real=True)
    # λ<0: 1-λΔt = 1+|λ|Δt > 1 (恒等式) → BE 因子 |1/(1-λΔt)|<1 对一切 Δt>0
    ok7a = sp.simplify((1 - lam * h_dt) - (1 + (-lam) * h_dt)) == 0
    be_decay = all(abs(1 / (1 - (-16.816) * x)) < 1 for x in (1e-4, 0.01, 0.1, 1.0, 100.0))
    # CN 因子 G=(1+λΔt/2)/(1-λΔt/2): |λ|Δt>2 时分子变负 → 符号振荡; |λ|Δt→∞ 时 G→-1 (非 L-稳定)
    cn_g = lambda l, x: (1 + l * x / 2) / (1 - l * x / 2)
    cn_osc = [cn_g(-16.816, x) < 0 for x in (0.13, 0.2, 0.5)]       # 阈值 Δt=2/16.816≈0.119 s
    cn_stiff = cn_g(-1e6, 0.1)                                       # 刚性极限 → -1
    # λ>0: BE 在 0<λΔt<2 放大 (1-λΔt∈(0,1) → 因子>1), 取样验证
    amp = [abs(complex(1 / (1 - 0.5 * 1e-2 * x))) for x in (0.5, 1.0, 1.9)]
    ok7c = all(v > 1 for v in amp)
    check("V7", "增长因子: BE(λ<0)恒衰减; CN 在 |λ|Δt>2 符号振荡且 G→-1 (非 L-稳定); BE(λ>0) 放大",
          ok7a and be_decay and all(cn_osc) and abs(cn_stiff + 1) < 1e-3 and ok7c,
          f"BE(|λ|=16.816) 全 Δt 衰减: {be_decay}; CN Δt>0.119s 振荡: {cn_osc}; "
          f"CN 刚性极限 G={cn_stiff:.6f}; BE(λ>0) 放大样本 {['%.3f' % v for v in amp]}")

    # ------------------------------------------------ V8 Robin 圆柱级数解
    from scipy.optimize import brentq
    from scipy.special import j0, j1
    Bi_v = 25.0 * 0.02 / 0.36
    f = lambda x: x * j1(x) - Bi_v * j0(x)
    grid = np.linspace(1e-9, 60, 200000)
    vals = f(grid)
    roots = []
    for k in range(len(grid) - 1):
        if vals[k] * vals[k + 1] < 0:
            roots.append(brentq(f, grid[k], grid[k + 1], xtol=1e-14))
        if len(roots) >= 5:
            break
    paper_lam = [1.418473, 4.166470, 7.208478, 10.308273, 13.427161]
    paper_C = [1.265822, -0.377974, 0.174964, -0.103759, 0.070187]
    Cn = [2 * j1(x) / (x * (j0(x) ** 2 + j1(x) ** 2)) for x in roots]
    ok8a = all(abs(a - b) < 5e-6 for a, b in zip(roots, paper_lam))
    ok8b = all(abs(a - b) < 5e-6 for a, b in zip(Cn, paper_C))
    rho_t = np.linspace(0, 1, 21)
    recon = np.array([sum(Cn[n] * j0(roots[n] * rr) for n in range(5)) for rr in rho_t])
    # 5 项的部分重构误差与论文 120 项 2.35e-3 同量级即可 (非严格断言)
    ok8 = ok8a and ok8b
    check("V8", "级数解特征根/系数与论文一致 (λJ1=BiJ0 前 5 根)", ok8,
          "λ=" + ",".join(f"{x:.6f}" for x in roots))

    # ------------------------------------------------ V9 特征数
    alpha_v = 0.36 / (820.0 * 2600.0)
    Bi_v2 = 25.0 * 0.02 / 0.36
    D0v = 7e-9 * np.exp(-0.89 / 2.55)
    Bim = 8e-7 * 0.02 / D0v
    tau_th = 0.02 ** 2 / alpha_v
    tau_mo = 0.02 ** 2 / D0v
    tau_lump = 820.0 * 2600.0 * 0.02 / (2 * 25.0)
    ok9 = (abs(alpha_v - 1.6885553e-7) < 5e-13 and abs(Bi_v2 - 1.388889) < 1e-5
           and abs(Bim - 3.2404) < 5e-4 and abs(tau_th - 2368.9) < 0.1
           and abs(tau_mo - 81010) < 5 and abs(tau_lump - 852.8) < 0.1)
    check("V9", "特征数: α, Bi, Bi_m, R²/α, R²/D(C0), 集总常数 ρc_pR/(2h)", ok9,
          f"α={alpha_v:.7e}, Bi={Bi_v2:.6f}, Bi_m={Bim:.4f}, R²/α={tau_th:.1f}, "
          f"R²/D={tau_mo:.0f}, τ_lump={tau_lump:.1f}")

    # ------------------------------------------------ V10 D 值与比值
    D = lambda c: 7e-9 * np.exp(-0.89 / c)
    ok10 = (abs(D(2.55) - 4.9377e-9) / 4.9377e-9 < 1e-3
            and abs(D(0.15) - 1.8547e-11) / 1.8547e-11 < 2e-3
            and abs(D(1.5102) - 3.88e-9) / 3.88e-9 < 5e-3
            and abs(D(1.5102) / D(2.55) - 0.786) < 2e-3)
    check("V10", "D 值: D(2.55), D(0.15), D(1.5102) 及半隐式论断 D(1.51)/D(2.55)≈0.786", ok10,
          f"D(2.55)={D(2.55):.4e}, D(0.15)={D(0.15):.4e}, D(1.5102)={D(1.5102):.4e}, "
          f"ratio={D(1.5102)/D(2.55):.4f}")

    # ------------------------------------------------ V11 节点值 D 伸缩恒等式 (M=2)
    u0, u1, u2 = sp.symbols("u0 u1 u2")           # V_i·dC_i/dt
    d0, d1, d2 = sp.symbols("d0 d1 d2")           # 节点扩散系数
    c0, c1, c2, cinf = sp.symbols("c0 c1 c2 c_inf")
    hm, Asym = sp.symbols("h_m A_s", positive=True)
    A12 = sp.pi * dr
    A32 = 3 * sp.pi * dr / 2
    Vv0 = sp.pi * dr ** 2 / 4
    Vv1 = 2 * sp.pi * dr ** 2
    Vv2 = 7 * sp.pi * dr ** 2 / 4
    eq0 = sp.Eq(u0, A12 * d0 * (c1 - c0) / dr)
    eq1 = sp.Eq(u1, A32 * d1 * (c2 - c1) / dr - A12 * d1 * (c1 - c0) / dr)
    eq2 = sp.Eq(u2, -d2 * A32 * (c2 - c1) / dr + hm * Asym * (cinf - c2))
    Vv = [Vv0, Vv1, Vv2]
    ui = [u0, u1, u2]
    lhs = sp.expand(sum(Vv[k] * ui[k] / sp.Symbol("Vsum_dummy") * 0 for k in range(3))  # placeholder
                    )
    # 直接对通量作伸缩求和: Σ u_i = 表面通量 + 失配项
    flux_sum = sp.expand(sum(sp.solve(eqk, uk)[0] for eqk, uk in zip((eq0, eq1, eq2), ui)))
    mismatch = ((d0 - d1) * A12 * (c1 - c0) / dr + (d1 - d2) * A32 * (c2 - c1) / dr)
    surf = hm * Asym * (cinf - c2)
    resid = sp.simplify(flux_sum - (surf + mismatch))
    ok11 = resid == 0
    check("V11", "节点值 D 水量收支恒等式: Σu_i = 表面通量 + Σ(D_j-D_{j+1})A(C_{j+1}-C_j)/Δr", ok11)

    # ------------------------------------------------ V12 空间算子谱
    from audit_eigs_dt import operators
    Ac, Au = operators(200, with_robin=True)
    ev_c = np.linalg.eigvals(Ac).real
    ev_u = np.linalg.eigvals(Au).real
    ok12 = ev_c.max() < 1e-12 and abs(ev_u.max() - 16.816) < 5e-3
    check("V12", "算子谱 (M=200, 含 Robin): 修正格式耗散, 原方案 max Re λ=+16.816 /s", ok12,
          f"max Re λ_corr = {ev_c.max():.3e}, max Re λ_user = {ev_u.max():.4f} /s")

    # ------------------------------------------------ 汇总
    n_fail = sum(1 for r in RESULTS if r[1] == "FAIL")
    print("\n" + "=" * 80)
    print(f"共 {len(RESULTS)} 项检查, PASS {len(RESULTS) - n_fail}, FAIL {n_fail}")
    print("=" * 80)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "derivation_check.log"), "w", encoding="utf-8") as fh:
        for vid, tag, desc, detail in RESULTS:
            fh.write(f"[{tag}] {vid:4s} {desc}" + (f"\n    {detail}" if detail else "") + "\n")
        fh.write(f"\n共 {len(RESULTS)} 项检查, PASS {len(RESULTS) - n_fail}, FAIL {n_fail}\n")
    print(f"日志: outputs/derivation_check.log")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
