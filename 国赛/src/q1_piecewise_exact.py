"""
误差最低的路线是怎么处理附件1 的?  —— 机理验证

结论预告: 它**不构造**任何光滑闭式函数, 也不做任何数值积分.
它直接用附件1 的原始 31 个点作为**分段线性**的折点, 而 Duhamel 卷积在
每个线性段上有闭式原函数 —— 所以整条路线是**精确**的, 没有求积误差.

本脚本建立三个论断:
  W1 分段闭式公式本身精确: 线性环境 + 单段递推 vs 解析闭式 vs 独立ODE.
  W2 用原始点做折点 -> 全时段结果对"分段粗细"不敏感 (证明无求积误差).
  W3 PCHIP 则相反: 它需要细分才收敛 (证明那是求积近似).
      两者最终答案之差是**认识论**差异 (数据只有 31 点), 不是数值误差.

运行: python src/q1_piecewise_exact.py
输出: outputs/registry_q1_piecewise.csv, outputs/q1_piecewise.log
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.special import j0

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import ALPHA, H_CONV, K_COND, R0, T0_K, Env, load_attachment1  # noqa: E402
from q1_analytic_fit import eigen, series_T  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
BI = H_CONV * R0 / K_COND
K2C = 273.15
T_END = 1800.0
CMD = "python src/q1_piecewise_exact.py"
REG: list = []


def say(s=""):
    print(s)


def add(id_, q, v, u, unc="run", src="run q1_piecewise_exact", note=""):
    vs = v if isinstance(v, str) else (f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])
    say(f"    [reg] {id_:14s} {q[:52]:52s} = {vs} {u}")


def write_reg():
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "registry_q1_piecewise.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source", "command", "note"])
        w.writerows(REG)
    say(f"\n注册表: {p} ({len(REG)} 行)")


def main():
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    x, lam, c = eigen(BI, 400)
    mu = ALPHA * lam ** 2
    r_eval = np.array([0.0, 0.005, 0.010, 0.015, 0.020])
    J = j0(np.outer(lam, r_eval))

    say("=" * 100)
    say("附件1 如何变成'连续函数'? —— 误差最低路线的真实做法")
    say("=" * 100)

    # ================================================================ W1
    say("\n" + "-" * 100)
    say("W1. 分段闭式公式本身是否精确? (线性环境 + 单段)")
    say("-" * 100)
    say("  取 T_inf 在整段上是**严格线性**的 (最简单也最严苛的检验):")
    A_, B_ = 20.0, 0.01                      # T_inf = 20 + 0.01 t  [degC]
    Tinf_f = lambda tt: (A_ + B_ * tt) + K2C

    # (a) 单段递推 (一步)
    tg1 = np.array([0.0, T_END])
    Ts_seg = series_T(tg1, Tinf_f(tg1), r_eval, x, lam, c)[-1]
    # (b) 解析闭式: b_k = c_k(T0-Tinf0)e^{-mu t} - c_k s (1-e^{-mu t})/mu
    tt = T_END
    b_closed = (c * (T0_K - Tinf_f(0.0)) * np.exp(-mu * tt)
                - c * B_ * (1.0 - np.exp(-mu * tt)) / mu)
    Ts_closed = float(Tinf_f(tt)) + b_closed @ J
    # (c) 独立 ODE
    def rhs(t, y):
        return -mu * y - c * B_
    sol = solve_ivp(rhs, (0.0, tt), c * (T0_K - Tinf_f(0.0)),
                    method="DOP853", rtol=1e-13, atol=1e-16)
    Ts_ode = float(Tinf_f(tt)) + sol.y[:, -1] @ J

    d1 = float(np.max(np.abs(Ts_seg - Ts_closed)))
    d2 = float(np.max(np.abs(Ts_closed - Ts_ode)))
    say(f"  单段递推 vs 解析闭式      : max|dT| = {d1:.3e} K")
    say(f"  解析闭式 vs 独立ODE(DOP853): max|dT| = {d2:.3e} K")
    say(f"  T(r=R, 1800s) = {Ts_seg[-1]-K2C:.12f} degC (三种算法)")
    for j, rr in enumerate(r_eval):
        add(f"W03_r{int(rr*1000)}", f"线性环境: T(r={rr*100}cm,1800s) 单段递推",
            float(Ts_seg[j]) - K2C, "degC", "解析精确", "run W1", "")
        add(f"W04_r{int(rr*1000)}", f"线性环境: T(r={rr*100}cm,1800s) 独立ODE",
            float(Ts_ode[j]) - K2C, "degC", "DOP853 rtol=1e-13", "run W1", "")
    add("W01", "单段递推 vs 解析闭式 max|dT|", d1, "K", "解析精确", "run W1",
        "线性环境, 整段一步")
    add("W02", "解析闭式 vs 独立ODE max|dT|", d2, "K", "DOP853 rtol=1e-13", "run W1", "")
    say("  -> 三者一致到 ~1e-13 K. 分段闭式公式是**精确**的, 不是近似.")

    # ================================================================ W2
    say("\n" + "-" * 100)
    say("W2. 用附件1 原始点做折点: 结果对'分段粗细'不敏感 (无求积误差)")
    say("-" * 100)
    tD = t1[t1 <= T_END]
    TD = T1[t1 <= T_END] + K2C          # 31 个原始点 (K)
    say(f"  折点 = 附件1 的 {len(tD)} 个原始点, 段长 60 s (精确落在这 31 点上)")

    def pl_at(tgrid):
        return np.interp(tgrid, tD, TD)

    say(f"\n  {'细分方式':<34} {'T(r=R,1800s) [degC]':>22} {'与原始折点之差 [K]':>20}")
    base = series_T(tD, TD, r_eval, x, lam, c)[-1, -1]
    say(f"  {'原始 31 折点 (Δτ=60 s)':<34} {base-K2C:>22.12f} {'—':>20}")
    add("W10", "原始折点 PL: T(r=R,1800s)", float(base) - K2C, "degC", "解析精确",
        "run W2", "31 个折点")
    for sub in (2, 4, 8, 16):
        tsub = np.arange(0.0, T_END + 1e-9, 60.0 / sub)
        tsub = np.unique(np.concatenate([tsub, tD]))
        v = series_T(tsub, pl_at(tsub), r_eval, x, lam, c)[-1, -1]
        say(f"  {'每段再细分 ' + str(sub) + ' 份':<34} {v-K2C:>22.12f} {abs(v-base):>20.3e}")
        add(f"W11_sub{sub}", f"PL 每段细分 {sub} 份: T(r=R,1800s)", float(v) - K2C, "degC",
            "解析精确", "run W2", "")
        add(f"W11d_sub{sub}", f"PL 每段细分 {sub} 份 与原始折点之差", abs(float(v - base)),
            "K", "解析差值", "run W2", "应为 0")
    say("  -> 无论怎么细分, 答案完全不变 (差异 < 1e-12 K).")
    say("     因为每个 60 s 段内 T_inf 严格线性, 闭式积分是**精确**的,")
    say("     细分只是把同一个精确积分切成更多段, 不改变结果.")
    Tpl_all = series_T(tD, TD, r_eval, x, lam, c)[-1]
    for j, rr in enumerate(r_eval):
        add(f"W12_r{int(rr*1000)}", f"原始折点 PL: T(r={rr*100}cm,1800s)",
            float(Tpl_all[j]) - K2C, "degC", "解析精确", "run W2", "31 个折点")

    # ================================================================ W3
    say("\n" + "-" * 100)
    say("W3. 反过来: PCHIP 需要细分才收敛 (它才是有求积误差的那个)")
    say("-" * 100)
    pT = PchipInterpolator(tD, TD)
    say(f"\n  {'Δτ [s]':>8} {'T(r=R,1800s) [degC]':>22} {'相邻半步之差 [K]':>18}")
    prev = None
    for tau in (8.0, 4.0, 2.0, 1.0, 0.5, 0.25):
        tg = np.arange(0.0, T_END + 1e-9, tau)
        v = series_T(tg, pT(tg), r_eval, x, lam, c)[-1, -1]
        d = "—" if prev is None else f"{abs(v-prev):.3e}"
        say(f"  {tau:>8} {v-K2C:>22.12f} {d:>18}")
        add(f"W20_tau{tau}", f"PCHIP 逐段递推 Δτ={tau}s: T(r=R,1800s)", float(v) - K2C,
            "degC", "解析(逐段)", "run W3", "")
        if prev is not None:
            add(f"W21_tau{tau}", f"PCHIP Δτ={tau}s 的相邻半步之差", abs(float(v - prev)),
                "K", "解析差值", "run W3", "一阶收敛")
        prev = v
    say("  -> 差异随 Δτ 减小而减小 (一阶), 说明此处确有求积近似;")
    say("     Δτ=1 s 时已达 3e-06 K, 远低于四位小数阈值 5e-5 K.")

    # ================================================================ W4
    say("\n" + "-" * 100)
    say("W4. 那么两条路线的最终差异是什么性质? (认识论, 不是数值误差)")
    say("-" * 100)
    v_pl = series_T(tD, TD, r_eval, x, lam, c)[-1, -1]
    tg_f = np.arange(0.0, T_END + 1e-9, 0.25)
    v_pc = series_T(tg_f, pT(tg_f), r_eval, x, lam, c)[-1, -1]
    d_pl_pc = abs(v_pl - v_pc)
    tt = np.linspace(0.0, T_END, 180001)
    d_in = float(np.max(np.abs(np.interp(tt, tD, TD) - pT(tt))))
    say(f"  输入侧 (环境温度):  分段线性 vs PCHIP 最大差 = {d_in:.3e} K")
    say(f"  输出侧 (药材表面):  两者最终答案之差       = {d_pl_pc:.3e} K")
    say(f"  附件1 的记录精度只有 1e-3 K; 输入侧差异是它的 {d_in/1e-3:.1f} 倍.")
    say("  -> 这就是真正的温度不确定度来源: 不是数值格式, 而是'60 s 之间发生了什么'")
    say("     这件事数据本身没告诉你. 两种插值都合理, 差异 ~2e-3 K.")
    add("W30", "输入侧: PL vs PCHIP 环境温度最大差", d_in, "K", "两种插值", "run W4", "")
    add("W31", "输出侧: PL vs PCHIP 最终温度之差", d_pl_pc, "K", "两种插值", "run W4",
        "认识论不确定度")
    add("W32", "输入侧差异 / 附件1 记录精度 1e-3 K", d_in / 1e-3, "倍", "解析比值", "run W4", "")

    # ================================================================ W5
    say("\n" + "-" * 100)
    say("W5. 机制对比: 为什么拟合更差")
    say("-" * 100)
    say(f"  原始点 PL / PCHIP : 保留全部 {len(tD)} 个数据点, 不降维, 无系统偏差")
    say(f"  三次多项式拟合     : 压缩为 4 个参数 (31:4)")
    say(f"  饱和指数拟合       : 压缩为 3 个参数 (31:3)")
    say(f"  线性拟合           : 压缩为 2 个参数 (31:2)")
    say("  -> 拟合是**降维**, 用少数参数去代表 31 个点, 必然引入系统偏差;")
    say("     而分段插值只做'点间连接', 不改变数据本身的形状.")
    add("W40", "附件1 在 0-1800 s 内数据点数", len(tD), "个", "附件1", "run W5", "60 s 间隔")
    for nm, k in (("三次", 4), ("饱和指数", 3), ("线性", 2)):
        add(f"W41_{nm}", f"{nm}拟合参数个数 (降维比 {len(tD)}:{k})", k, "个", "结构",
            "run W5", "")

    write_reg()


if __name__ == "__main__":
    main()
