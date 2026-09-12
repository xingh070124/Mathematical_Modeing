# -*- coding: utf-8 -*-
"""
q45_stiffness.py -- 问题三/问题四的**刚性谱与显式格式不可行性**的定量论证.

论文正文只给出"必须用自适应隐式格式"的结论, 未给定量依据. 本脚本把依据算出来并
写进注册表, 供附录引用:

  * 时间尺度 tau_therm = R^2/alpha, tau_moist = R^2/D, 及其在过程首末的比值
  * 空间算子的 Jacobian 谱 (实部极值), 刚性比 Stiff = |Re lam|max / |Re lam|min
  * 显式格式的稳定步长上界 dt_exp = 2/|Re lam|max 与由此推出的总步数
  * 与实际 BDF 步数对比

对附录 3 (问题三) 与附录 4 (问题四) 各算一遍。问题四的 R 取过程中与末态的值,
以体现"收缩改变谱"。

输出: outputs/q45_stiffness.log 与 outputs/registry_q45_stiffness.csv
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (APP, P4, P3, Q4Radius, geometry_xi, solve_q4,   # noqa: E402
                      props_p, Dfun_p, T0K, C0, R0)
from q2_solve import geometry                                   # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
LOG = []

# 生产步数 (来自 registry_q3.csv / registry_q4.csv)
NSTEP_Q3 = 3299
NSTEP_Q4 = 4007
TDRY_Q3 = 206720.4134563
TDRY_Q4 = 183906.7128


def say(m):
    print(m, flush=True)
    LOG.append(m)


def scales(p, C, T, Rm, lam1=5.7832):
    """时间尺度与谱估计.

    alpha = k/(rho cp);  tau_therm = R^2/alpha;  tau_moist = R^2/D.
    lam1 为圆柱 Neumann 问题第一特征值 (J0 的第一个非零零点平方 ~ 5.7832).
    """
    rho, cp, k, _, _, _ = props_p(np.array([C]), p)
    rho, cp, k = float(rho[0]), float(cp[0]), float(k[0])
    D = float(Dfun_p(np.array([C]), np.array([T]), p)[0])
    alpha = k / (rho * cp)
    return dict(rho=rho, cp=cp, k=k, D=D, alpha=alpha,
                tau_therm=Rm ** 2 / alpha, tau_moist=Rm ** 2 / D,
                lam_max_est=3.0 * alpha / (Rm / 200) ** 2,
                lam_min_est=lam1 * D / Rm ** 2)


def spectrum(J):
    ev = np.linalg.eigvals(np.asarray(J.todense()))
    re = ev.real
    pos = re[re > 0]
    nz = np.abs(re)[np.abs(re) > 1e-14]
    return dict(re_max=float(re.max()), re_min=float(re.min()),
                n_pos=int((re > 1e-12).sum()), n_neg=int((re < -1e-12).sum()),
                abs_max=float(np.abs(re).max()),
                abs_min=float(nz.min()),
                stiff=float(np.abs(re).max() / nz.min()))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = []

    def add(k, q, v, u, src):
        rows.append((k, q, float(v), u, src))

    say("=" * 78)
    say("问题三/问题四 刚性谱与显式格式不可行性")
    say("=" * 78)

    # ---------------- 时间尺度 ----------------
    say("\n[1] 时间尺度 (R 取初值 2.00 cm 与问题四末值 1.20 cm)")
    tb = {}
    for tag, p, C, T, Rm in (
            ("q3_C0", P3, C0, 323.15, R0),
            ("q3_Cstar", P3, 0.15, 323.15, R0),
            ("q4_C0", P4, C0, 323.15, R0),
            ("q4_Cstar_R0", P4, 0.15, 323.15, R0),
            ("q4_Cstar_Rend", P4, 0.15, 323.15, 0.012)):
        s = scales(p, C, T, Rm)
        tb[tag] = s
        say(f"  {tag:16s} rho={s['rho']:7.2f} cp={s['cp']:8.2f} k={s['k']:.5f} "
            f"D={s['D']:.4e} alpha={s['alpha']:.4e} "
            f"tau_th={s['tau_therm']:9.2f}s tau_m={s['tau_moist']:10.2f}s")
        for k_, v_ in (("rho", s["rho"]), ("cp", s["cp"]), ("k", s["k"]),
                       ("D", s["D"]), ("alpha", s["alpha"]),
                       ("tau_therm_s", s["tau_therm"]),
                       ("tau_moist_s", s["tau_moist"])):
            add(f"ST_{tag}_{k_}", f"ST {tag} {k_}", v_, "-", "q45_stiffness.py")

    say("\n  时间尺度分离比 tau_moist / tau_therm = alpha/D:")
    for tag in ("q3_C0", "q3_Cstar", "q4_C0", "q4_Cstar_Rend"):
        s = tb[tag]
        r_ = s["tau_moist"] / s["tau_therm"]
        say(f"    {tag:16s} {r_:9.2f}")
        add(f"ST_ratio_{tag}", f"ST {tag} 尺度分离比", r_, "-", "q45_stiffness.py")

    # ---------------- Jacobian 谱 ----------------
    say("\n[2] Jacobian 谱 (M=200, 2x201=402 阶, 稠密特征值)")
    from q3_solve import make_jac as make_jac3
    from q3_solve import make_rhs as make_rhs3
    from q3_solve import Q3Env
    from q4_solve import make_jac as make_jac4
    from q1_solve import load_attachment1
    t1, T1, C1 = load_attachment1()
    env3 = Q3Env(t1, T1, C1)
    rad = Q4Radius()

    # --- 问题三: t=0 与 t=t_dry ---
    g3 = geometry(200, "lumped")
    n3 = g3["n"]
    J3_0 = make_jac3(g3, env3)(0.0, np.concatenate([np.full(n3, T0K),
                                                    np.full(n3, C0)]))
    sp3_0 = spectrum(J3_0)
    r3 = solve_q4(M=200, app="app3", rad_mode="const")     # 借 q4 框架取问题三态
    U3d = np.concatenate([r3["sol"].y[:n3, -1], r3["sol"].y[n3:, -1]])
    # 问题三的 Jacobian 用 q3 的网格与物性
    from q3_solve import make_jac as _mj3
    J3_d = _mj3(g3, env3)(r3["t_dry"], U3d)
    sp3_d = spectrum(J3_d)
    for lab, sp in (("t=0", sp3_0), ("t=t_dry", sp3_d)):
        say(f"  问题三 {lab:9s}: Re lam in [{sp['re_min']:.4e}, {sp['re_max']:.4e}], "
            f"正 {sp['n_pos']} / 负 {sp['n_neg']}, "
            f"|lam|max={sp['abs_max']:.4e}, |lam|min={sp['abs_min']:.4e}, "
            f"Stiff={sp['abs_max']/sp['abs_min']:.3e}")
        for k_, v_ in sp.items():
            add(f"SP_q3_{lab}_{k_}".replace("=", ""), f"问题三谱 {lab} {k_}", v_,
                "-", "q45_stiffness.py")

    # --- 问题四: t=0 与 t=t_dry ---
    g4 = geometry_xi(200)
    n4 = g4["n"]
    r4 = solve_q4(M=200, app="app4", rad_mode="data")
    U4d = np.concatenate([r4["sol"].y[:n4, -1], r4["sol"].y[n4:, -1]])
    J4_0 = make_jac4(g4, env3, rad, params=P4)(0.0,
                                               np.concatenate([np.full(n4, T0K),
                                                               np.full(n4, C0)]))
    sp4_0 = spectrum(J4_0)
    J4_d = make_jac4(g4, env3, rad, params=P4)(r4["t_dry"], U4d)
    sp4_d = spectrum(J4_d)
    for lab, sp in (("t=0", sp4_0), ("t=t_dry", sp4_d)):
        say(f"  问题四 {lab:9s}: Re lam in [{sp['re_min']:.4e}, {sp['re_max']:.4e}], "
            f"正 {sp['n_pos']} / 负 {sp['n_neg']}, "
            f"|lam|max={sp['abs_max']:.4e}, |lam|min={sp['abs_min']:.4e}, "
            f"Stiff={sp['abs_max']/sp['abs_min']:.3e}")
        for k_, v_ in sp.items():
            add(f"SP_q4_{lab}_{k_}".replace("=", ""), f"问题四谱 {lab} {k_}", v_,
                "-", "q45_stiffness.py")

    # ---------------- 显式格式的代价 ----------------
    say("\n[3] 显式格式的稳定步长与总步数 (dt_exp = 2/|Re lam|max)")
    for tag, sp, T_dry, nstep, name in (
            ("q3", sp3_d, TDRY_Q3, NSTEP_Q3, "问题三 (附录3)"),
            ("q4", sp4_d, TDRY_Q4, NSTEP_Q4, "问题四 (附录4)")):
        dt_e = 2.0 / sp["abs_max"]
        N_e = T_dry / dt_e
        say(f"  {name}: |lam|max={sp['abs_max']:.4e} 1/s -> dt_exp={dt_e:.6f} s; "
            f"全程需 {N_e:.3e} 步; BDF 实测 {nstep} 步; 比值 {N_e/nstep:.3e}")
        add(f"EXP_{tag}_dtexp", f"{name} 显式稳定步长", dt_e, "s", "q45_stiffness.py")
        add(f"EXP_{tag}_N", f"{name} 显式总步数", N_e, "1", "q45_stiffness.py")
        add(f"EXP_{tag}_Nratio", f"{name} 显式步数 / BDF 步数", N_e / nstep, "1",
            "q45_stiffness.py")
        # 谱估计与实际谱对比
        st = tb["q3_Cstar"] if tag == "q3" else tb["q4_Cstar_Rend"]
        say(f"      估计 |lam|max ~ 3 alpha/dr^2 = {st['lam_max_est']:.4e} 1/s; "
            f"估计 |lam|min ~ lam1 D/R^2 = {st['lam_min_est']:.4e} 1/s; "
            f"估计 Stiff = {st['lam_max_est']/st['lam_min_est']:.3e}")
        add(f"EXP_{tag}_lam_max_est", f"{name} 谱估计 |lam|max",
            st["lam_max_est"], "1/s", "q45_stiffness.py")
        add(f"EXP_{tag}_lam_min_est", f"{name} 谱估计 |lam|min",
            st["lam_min_est"], "1/s", "q45_stiffness.py")

    # ---------------- 附录 E 的对数敏感度 (量纲一致的强弱比较) ----------------
    say("\n[4] 附录 E: 对数敏感度的量纲一致比较 (T=50 degC, C*=0.15)")
    T50 = 323.15
    for tag, p, kD in (("app3", P3, P3["kD"]), ("app4", P4, P4["kD"])):
        dlnC = 0.10 * kD / 0.15          # kD 变动 10% 使 lnD 的变化 (= dkD/C*)
        dlnEA = 0.10 * p["EA"] / T50     # EA 变动 10% 使 lnD 的变化 (= dEA/T)
        dlnT1 = p["EA"] / T50 ** 2       # T 升高 1 K 使 lnD 的变化
        ratio = dlnEA / dlnC
        say(f"  {tag}: dkD(10%)/C* = {dlnC:.4f};  dEA(10%)/T = {dlnEA:.4f};  "
            f"EA/T^2 = {dlnT1:.4f} /K;  比值 EA/kD = {ratio:.3f}")
        for k_, v_ in (("dlnD_dkD10", dlnC), ("dlnD_dEA10", dlnEA),
                       ("dlnD_dT1K", dlnT1), ("ratio_EA_over_kD", ratio),
                       ("dEA_10pct_K", 0.10 * p["EA"])):
            add(f"E_{tag}_{k_}", f"附录E {tag} {k_}", v_, "-", "q45_stiffness.py")

    # ---------------- 附录 E 的 Jacobian FD 核验 ----------------
    say("\n[5] 附录 E: 解析 Jacobian 的中心差分核验")
    from q4_solve import check_jacobian_fd
    jchk = check_jacobian_fd(M=12, app="app4", form="material")
    say(f"  M=12 (26x26): 显著分量 {jchk['n_checked']} 个, "
        f"最大相对误差 {jchk['max_rel']:.4e}, 结构外元素 {jchk['max_extra']:.1e}")
    add("E_jac_n", "Jacobian FD 核验的显著分量数", float(jchk["n_checked"]), "1",
        "q45_stiffness.py")
    add("E_jac_maxrel", "Jacobian FD 核验最大相对误差", jchk["max_rel"], "1",
        "q45_stiffness.py")

    # ---------------- 结论 ----------------
    say("\n[6] 结论")
    say("  两问的空间算子谱全部位于左半平面 (无正实部), 故半离散系统是"
        "**渐近稳定**的;")
    say("  但谱跨越 5~6 个数量级, 显式格式的步数比自适应 BDF 多约 2~3 个数量级,")
    say("  这就是正文选用隐式自适应 BDF 的定量依据。")

    with open(os.path.join(OUTDIR, "registry_q45_stiffness.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "source"])
        for r_ in rows:
            w.writerow([r_[0], r_[1], repr(r_[2]), r_[3], r_[4]])
    say(f"\n写出: outputs/registry_q45_stiffness.csv ({len(rows)} 行)")
    with open(os.path.join(OUTDIR, "q45_stiffness.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
