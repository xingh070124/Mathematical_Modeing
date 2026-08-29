# -*- coding: utf-8 -*-
"""
2024 CUMCM A 题"板凳龙" —— 问题三：最小螺距（二分搜索 + 全程碰撞扫描）

模型（与 model/problem3.md 一致）：
  对给定螺距 p，螺线 r = b·theta，b = p/(2·pi)；龙头前把手初始位于第 16 圈
  （theta0 = 32·pi，r0 = 16p），恒速 1 m/s 顺时针盘入；
  边界约束：龙头前把手盘入到调头空间边界 r = 4.5 m（theta_end = 9·pi/p）。
  可行(p) := 从初始到龙头到达边界全程，任意时刻任意两非相邻板凳矩形不相交。
  最小螺距 p* := 可行的最小 p；由"螺距越大间隙越大"的单调性二分求解。

判定与度量（两层）：
  1) 碰撞判定（二分决策用）：向量 SAT——四分离轴投影全重叠 <=> 相交（间隙记负）。
     注意 SAT 正值只是"最小投影分离量"，是真实间距的下界；符号才是碰撞判据。
  2) 真实间距（报告用）：shapely 精确计算矩形间欧氏距离，用于验证表与图。

数值实现：
  - 把手链：牛顿迭代逆推（上一步角增量 warm start），链残差 ~1e-13 m；
  - 采样：龙头每走 ds 米检一次，终点（龙头恰在边界）必检；
  - 二分：先粗后细（ds = 0.5 m -> 0.1 m），p 精度 1e-4 m。

输出：
  控制台：二分过程、p*、临界碰撞对、验证表
  paper/figures/fig_问题三螺距搜索.png   （全程真实最小间距 vs 螺距，零点即 p*）
  paper/figures/fig_问题三临界形态.png   （p* 时龙头到达边界的整条龙形态）
"""
import math
import time
import os
import numpy as np

# ---------------- 参数 ----------------
HEAD_L, BODY_L = 3.41, 2.20
HOLE_OFF = 0.275
D_HEAD = HEAD_L - 2 * HOLE_OFF   # 2.86
D_BODY = BODY_L - 2 * HOLE_OFF   # 1.65
WIDTH = 0.30
N_HANDLE = 224
N_BENCH = 223
THETA0 = 32 * np.pi              # 第 16 圈
R_BOUND = 4.5                    # 调头空间半径（直径 9 m）


# ---------------- 螺线几何（标量版，math 加速） ----------------
def pos_s(b, th):
    r = b * th
    return r * math.cos(th), r * math.sin(th)


def dpos_s(b, th):
    return b * (math.cos(th) - th * math.sin(th)), b * (math.sin(th) + th * math.cos(th))


def arc_len_s(b, th):
    return 0.5 * b * (th * math.sqrt(th * th + 1.0) + math.asinh(th))


def arc_len_inv(b, S):
    """arc_len 的反函数（θ>0 单调增），牛顿迭代."""
    th = math.sqrt(max(2.0 * S / b, 1e-6))
    for _ in range(50):
        f = arc_len_s(b, th) - S
        fp = b * math.sqrt(th * th + 1.0)
        dth = f / fp
        th -= dth
        if abs(dth) < 1e-13:
            break
    return th


# ---------------- 把手链：牛顿逆推（warm start） ----------------
def chain_thetas(b, th_head, us):
    """由龙头极角逆推全部 224 把手极角；us 为角增量初值（就地更新）."""
    ths = np.empty(N_HANDLE)
    ths[0] = th_head
    th = th_head
    px, py = pos_s(b, th)
    for i in range(N_BENCH):
        d = D_HEAD if i == 0 else D_BODY
        u = us[i] if us[i] > 1e-6 else 0.05
        for _ in range(40):
            qx, qy = pos_s(b, th + u)
            vx, vy = qx - px, qy - py
            n = math.hypot(vx, vy)
            f = n - d
            dpx, dpy = dpos_s(b, th + u)
            fp = (vx * dpx + vy * dpy) / n
            step = f / fp
            u -= step
            if u < 1e-8:
                u = 1e-8
            elif u > math.pi:
                u = math.pi
            if abs(step) < 1e-13:
                break
        us[i] = u
        th += u
        px, py = pos_s(b, th)
        ths[i + 1] = th
    return ths


def positions(b, ths):
    th = np.asarray(ths)
    r = b * th
    return np.stack([r * np.cos(th), r * np.sin(th)], axis=1)


# ---------------- SAT 碰撞判定（向量，与 problem1/2 同判据） ----------------
def min_gap_pos(Ps):
    """全部非相邻板凳对的 SAT 判定.
    返回 (gap, (i, j), collided_any)：
      gap = -max重叠深度（若存在相交对）或 最小投影分离量（无相交，仅下界非真实间距）；
      (i, j) 为取到该值的板凳对（1 基编号）。gap <= 0 <=> 存在相交。
    """
    p0, p1 = Ps[:-1], Ps[1:]
    L = np.where(np.arange(N_BENCH) == 0, HEAD_L, BODY_L)
    v = p1 - p0
    u = v / np.linalg.norm(v, axis=1, keepdims=True)
    c = 0.5 * (p0 + p1)
    hlen = L / 2.0
    hwid = np.full(N_BENCH, WIDTH / 2.0)

    idx = np.triu_indices(N_BENCH, 1)
    i, j = idx
    mask = (j - i) > 1
    i, j = i[mask], j[mask]
    ci, ui = c[i], u[i]
    cj, uj = c[j], u[j]
    hli, hwi = hlen[i], hwid[i]
    hlj, hwj = hlen[j], hwid[j]
    ni = np.stack([-ui[:, 1], ui[:, 0]], axis=1)
    nj = np.stack([-uj[:, 1], uj[:, 0]], axis=1)

    n_pairs = len(i)
    sep_all = np.empty((4, n_pairs))
    ovl_all = np.empty((4, n_pairs))
    for k, ax in enumerate([ui, ni, uj, nj]):
        rad_i = hli * np.abs((ui * ax).sum(1)) + hwi * np.abs((ni * ax).sum(1))
        rad_j = hlj * np.abs((uj * ax).sum(1)) + hwj * np.abs((nj * ax).sum(1))
        pci = (ci * ax).sum(1)
        pcj = (cj * ax).sum(1)
        lo1, hi1 = pci - rad_i, pci + rad_i
        lo2, hi2 = pcj - rad_j, pcj + rad_j
        sep_all[k] = np.maximum(lo2 - hi1, lo1 - hi2)   # >0: 该轴分离
        ovl_all[k] = np.minimum(hi1, hi2) - np.maximum(lo1, lo2)

    sep_min = np.where(sep_all > 0, sep_all, np.inf).min(axis=0)
    collided = np.isinf(sep_min)                        # 四轴全重叠 => 相交
    ovl_max = ovl_all.max(axis=0)
    pair_gap = np.where(collided, -ovl_max, sep_min)

    k = int(np.argmin(pair_gap))
    return float(pair_gap[k]), (int(i[k]) + 1, int(j[k]) + 1), bool(collided.any())


# ---------------- 真实间距（shapely 精确欧氏距离，报告用） ----------------
def true_min_dist(Ps):
    """全部非相邻板凳矩形的最小欧氏距离（相交为 0）. 返回 (dist, (i, j)).

    先用 AABB 外接包围盒向量预筛（间距 < 0.5 m 的候选对），
    再对候选对用 shapely 精确计算，避免全对 24753 对的精确求距开销。
    """
    from shapely.geometry import Polygon
    from shapely import distance as shp_distance

    p0, p1 = Ps[:-1], Ps[1:]
    L = np.where(np.arange(N_BENCH) == 0, HEAD_L, BODY_L)
    v = p1 - p0
    u = v / np.linalg.norm(v, axis=1, keepdims=True)
    c = 0.5 * (p0 + p1)
    hlen = L / 2.0
    hwid = np.full(N_BENCH, WIDTH / 2.0)
    n = np.stack([-u[:, 1], u[:, 0]], axis=1)
    ex = hlen * np.abs(u[:, 0]) + hwid * np.abs(n[:, 0])
    ey = hlen * np.abs(u[:, 1]) + hwid * np.abs(n[:, 1])
    bx0, bx1 = c[:, 0] - ex, c[:, 0] + ex
    by0, by1 = c[:, 1] - ey, c[:, 1] + ey

    idx = np.triu_indices(N_BENCH, 1)
    i, j = idx
    mask = (j - i) > 1
    i, j = i[mask], j[mask]
    dx = np.maximum(np.maximum(bx0[i] - bx1[j], bx0[j] - bx1[i]), 0.0)
    dy = np.maximum(np.maximum(by0[i] - by1[j], by0[j] - by1[i]), 0.0)
    near = dx * dx + dy * dy < 0.25          # AABB 间距 < 0.5 m
    i, j = i[near], j[near]
    if len(i) == 0:
        return float("inf"), None

    polys = np.empty(N_BENCH, dtype=object)
    for k in range(N_BENCH):
        hl, hw = hlen[k], hwid[k]
        ck, uk, nk = c[k], u[k], n[k]
        polys[k] = Polygon([ck + hl * uk + hw * nk, ck + hl * uk - hw * nk,
                            ck - hl * uk - hw * nk, ck - hl * uk + hw * nk])
    ds_ = shp_distance(polys[i], polys[j])
    k = int(np.argmin(ds_))
    return float(ds_[k]), (int(i[k]) + 1, int(j[k]) + 1)


# ---------------- 给定螺距的全程碰撞扫描 ----------------
def scan_pitch(p, ds=0.2, exact_stride=0, verbose=False):
    """龙头从第 16 圈盘入到 r=4.5 边界，逐采样点做 SAT 碰撞判定.

    exact_stride > 0 时，每隔该数个采样点用 shapely 复核真实最小间距。
    返回 dict：
      feasible      全程无相交
      first_coll_s  首次相交时龙头已走过的弧长（不可行时）
      coll_pair     首次相交的板凳对（1 基）
      coll_r_head   首次相交时龙头半径
      total_s       盘入总弧长
      true_d_min    真实最小间距（exact_stride>0 时，含所在位置）
    """
    b = p / (2 * np.pi)
    th_end = R_BOUND / b
    if th_end >= THETA0:
        return dict(feasible=False, reason="第16圈已在调头空间内",
                    total_s=0.0, first_coll_s=0.0)
    S0 = arc_len_s(b, THETA0)
    total = S0 - arc_len_s(b, th_end)
    n_steps = int(math.ceil(total / ds))

    us = np.full(N_BENCH, 0.05)
    first_coll = None
    coll_pair = None
    coll_r = None
    true_best = (math.inf, None, None)      # (dist, s, pair)
    for k in range(n_steps + 1):
        s = min(k * ds, total)
        th_head = th_end if s >= total else arc_len_inv(b, S0 - s)
        ths = chain_thetas(b, th_head, us)
        Ps = positions(b, ths)
        g, pair, coll = min_gap_pos(Ps)
        if coll and first_coll is None:
            first_coll = s
            coll_pair = pair
            coll_r = b * th_head
            if verbose:
                print(f"    p={p:.6f}: 首次相交 s={s:.2f} m (龙头 r={coll_r:.3f} m), "
                      f"对={pair}")
            break
        if exact_stride and k % exact_stride == 0:
            d, dpair = true_min_dist(Ps)
            if d < true_best[0]:
                true_best = (d, s, dpair)
    out = dict(feasible=first_coll is None, total_s=total,
               first_coll_s=first_coll, coll_pair=coll_pair, coll_r_head=coll_r,
               th_end=th_end, n_steps=n_steps)
    if exact_stride:
        out["true_d_min"] = true_best
    return out


# ---------------- 二分求最小螺距 ----------------
def solve_pitch(lo=0.30, hi=1.70, tol=1e-4, verbose=True):
    flo = scan_pitch(lo, ds=0.5, verbose=verbose)
    fhi = scan_pitch(hi, ds=0.5, verbose=verbose)
    if verbose:
        print(f"端点检验: p={lo:.2f} 可行={flo['feasible']}; p={hi:.2f} 可行={fhi['feasible']}")
    assert (not flo["feasible"]) and fhi["feasible"], "端点可行性不满足单调假设"
    hist = []
    it = 0
    while hi - lo > tol:
        it += 1
        mid = 0.5 * (lo + hi)
        ds = 0.5 if hi - lo > 0.02 else 0.1      # 先粗后细
        r = scan_pitch(mid, ds=ds, verbose=verbose)
        hist.append((mid, r["feasible"], r.get("first_coll_s"), r.get("coll_pair")))
        if verbose:
            msg = f"可行" if r["feasible"] else f"不可行(首碰 s={r['first_coll_s']:.1f} m, 对={r['coll_pair']})"
            print(f"  [{it:02d}] p={mid:.6f}  {msg}  (ds={ds} m)")
        if r["feasible"]:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi), lo, hi, hist


# ---------------- 主流程 ----------------
def main():
    t0 = time.time()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    figdir = os.path.join(root, "paper", "figures")

    print("=" * 64)
    print("问题三：最小螺距（龙头前把手盘入调头空间边界 r = 4.5 m）")
    print("=" * 64)

    p_star, lo, hi, hist = solve_pitch()
    b_star = p_star / (2 * np.pi)
    th_end_star = R_BOUND / b_star
    total_star = arc_len_s(b_star, THETA0) - arc_len_s(b_star, th_end_star)
    print("\n" + "=" * 64)
    print(f"最小螺距 p* ∈ ({lo:.6f}, {hi:.6f})，取 p* ≈ {p_star:.6f} m")
    print(f"  龙头到边界时极角 theta_end = {th_end_star:.4f} rad "
          f"（第 {th_end_star / (2 * np.pi):.4f} 圈）")
    print(f"  盘入总弧长 ≈ {total_star:.2f} m，经历圈数 16 - 4.5/p = {16 - 4.5 / p_star:.4f}")
    bs2 = b_star ** 2
    rho = (R_BOUND ** 2 + bs2) ** 1.5 / (R_BOUND ** 2 + 2 * bs2)
    print(f"  入口曲率半径 rho = {rho:.6f} m（与 4.5 m 偏差 {4.5 - rho:.2e} m）")
    print("=" * 64)

    # ---- 验证表：p* 两侧若干螺距 ----
    probes = [p_star - 0.02, p_star - 0.005, p_star - 0.001,
              p_star + 0.001, p_star + 0.005, p_star + 0.02]
    print("\n=== 螺距验证表（可行域边界两侧） ===")
    rows = []
    for pv in probes:
        r = scan_pitch(pv, ds=0.1, exact_stride=10, verbose=False)
        rows.append((pv, r))
        if r["feasible"]:
            tb = r.get("true_d_min", (float("nan"), None, None))
            print(f"  p={pv:.6f}: 可行,   全程真实最小间距={tb[0]:.6f} m "
                  f"(对={tb[2]}, 位置 s≈{tb[1]:.1f} m)")
        else:
            print(f"  p={pv:.6f}: 不可行, 首碰 s={r['first_coll_s']:.2f}/{r['total_s']:.2f} m "
                  f"(龙头 r={r['coll_r_head']:.3f} m), 对={r['coll_pair']}")

    # ---- 图 ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
            if os.path.exists(fp):
                fm.fontManager.addfont(fp)
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
        plt.rcParams["axes.unicode_minus"] = False

        # 图 1：全程真实最小间距 vs 螺距（加密采样 p* 附近）
        grid = list(np.arange(p_star - 0.03, p_star + 0.031, 0.005))
        grid += [0.35, 0.40, 0.60, 1.70]
        grid = sorted(set(round(x, 6) for x in grid))
        xs, ys = [], []
        print("\n=== 间距-螺距曲线采样 ===")
        for pv in grid:
            r = scan_pitch(pv, ds=0.2, exact_stride=10, verbose=False)
            tb = r.get("true_d_min", (float("nan"), None, None))
            xs.append(pv); ys.append(tb[0])
            print(f"  p={pv:.4f}: true_min_dist={tb[0]:.6f} m")
        xs, ys = np.array(xs), np.array(ys)

        fig, ax = plt.subplots(figsize=(9, 4.6))
        ax.plot(xs, ys, "o-", color="#1f6fb2", lw=1.6, ms=4.5, label="全程真实最小间距")
        ax.axhline(0, color="red", ls="--", lw=1.2, label="碰撞阈值 (0)")
        ax.axvline(p_star, color="green", ls=":", lw=1.5,
                   label=f"$p^*\\approx{p_star:.4f}$ m")
        ax.set_xlabel("螺距 p (m)")
        ax.set_ylabel("全程板凳最小间距 (m)")
        ax.set_title("问题三：全程板凳真实最小间距随螺距变化（曲线过零处即最小螺距）")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        f1 = os.path.join(figdir, "fig_问题三螺距搜索.png")
        plt.savefig(f1, dpi=200)
        plt.close()
        print(f"\n[输出] {f1}")

        # 图 2：p* 时龙头到达边界的临界形态
        ths = chain_thetas(b_star, th_end_star, np.full(N_BENCH, 0.05))
        Ps = positions(b_star, ths)
        dmin, dpair = true_min_dist(Ps)
        g, gpair, _ = min_gap_pos(Ps)
        print(f"终点配置：SAT 判定无碰撞={g > 0}, 终点真实最小间距={dmin:.6f} m (对={dpair})")

        from matplotlib.patches import Polygon, Circle
        fig, ax = plt.subplots(figsize=(7.8, 7.8))
        th_grid = np.linspace(th_end_star - 0.5, ths[-1] + 3.0, 4000)
        rr = b_star * th_grid
        ax.plot(rr * np.cos(th_grid), rr * np.sin(th_grid), color="#9dc3e6",
                lw=0.8, zorder=1)
        ax.add_patch(Circle((0, 0), R_BOUND, fc="#fff2ae", ec="k", ls="--",
                            lw=1.2, zorder=0))
        ax.text(0, 0, "调头空间\n$\\oslash\\,9$ m", ha="center", va="center", fontsize=11)
        for bi in range(N_BENCH):
            p0, p1 = Ps[bi], Ps[bi + 1]
            Lv = HEAD_L if bi == 0 else BODY_L
            u = (p1 - p0) / np.linalg.norm(p1 - p0)
            n = np.array([-u[1], u[0]])
            ctr = 0.5 * (p0 + p1)
            hl, hw = Lv / 2.0, WIDTH / 2.0
            corners = [ctr + hl * u + hw * n, ctr + hl * u - hw * n,
                       ctr - hl * u - hw * n, ctr - hl * u + hw * n]
            is_near = dpair and (bi + 1) in dpair
            col = "#e06666" if is_near else ("#f6b26b" if bi == 0 else "#b6d7a8")
            ax.add_patch(Polygon(corners, closed=True, fc=col, ec="#666666",
                                 lw=0.3, zorder=2))
        hx, hy = Ps[0]
        ax.plot(hx, hy, "k*", ms=13, zorder=3)
        ax.annotate("龙头前把手（r = 4.5 m）", (hx, hy), textcoords="offset points",
                    xytext=(16, 12), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8))
        ax.set_aspect("equal")
        ax.set_xlim(-9.5, 9.5)
        ax.set_ylim(-9.5, 9.5)
        ax.set_title(f"问题三：$p^*\\approx{p_star:.4f}$ m 龙头到达调头空间边界\n"
                     f"（红色为间距最小的板凳对 {dpair}，间距 {dmin:.3f} m）")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        f2 = os.path.join(figdir, "fig_问题三临界形态.png")
        plt.savefig(f2, dpi=200)
        plt.close()
        print(f"[输出] {f2}")
    except Exception as e:
        print(f"[警告] 绘图失败: {e}")

    print(f"\n耗时 {time.time() - t0:.1f} s")
    print(f"\n【结论】最小螺距 p* ≈ {p_star:.6f} m（区间 ({lo:.6f}, {hi:.6f})，精度 1e-4 m）")


if __name__ == "__main__":
    main()
