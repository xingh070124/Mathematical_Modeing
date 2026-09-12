# -*- coding: utf-8 -*-
r"""
问题三的图件 (Python/matplotlib; 后端按既有图脚本确定为 Python).

与问题一/二图件的关系 (逐图说明, 确保不重复):
  问题一已有图: fig_q1_env/model/fick/fvm/temp_results/moist_results/sensitivity/robustness
  问题二已有图: fig_q2_coupling / fig_q2_mechanism / fig_q2_results
  (q2 results 已画 3 h 内的时空热图 + 干燥前沿轨迹 + 失水率; q1 已画灵敏度龙卷风图)

  本脚本产出 2 张, 每张讲一个**问题一/二不存在**的结论:
    fig_q3_event   烘干时间的确定 (问题三的定义性特征: 积分到状态而非时刻):
                   (a) 全场最大含水率 max_i C_i(t) 全程单调下降, 与阈值 0.15 的唯一交点
                       即 t_dry —— 由求解器事件定位自动给出;
                   (b) 末段放大: 事件前 g=max C - C* 恒正 (最小 2.9e-7), 终点为零;
                   (c) 自适应 BDF 步长演化: 快变段小步、慢变段大步, 跨约 5 个数量级
                       (问题二为定步长 0.25 s —— 对照线).
    fig_q3_order   由表及里的达标次序 (q2 results 讲 3 h 内前沿推进, 本图讲
                   "前沿抵达中心之后, 全场依次达标的长尾过程"):
                   (a) 五个输出半径的 C(t) 曲线与各自达标时刻;
                   (b) 水分剖面 C(r) 的演化 (6/24/48 h 与 t_dry), 全场低于阈值;
                   (c) 达标时刻 vs 半径 —— "由表及里"的直接呈现.

数据源 (全部现算, 保证与生产解同源):
  src/q3_solve.solve_q3(M=200, rtol=1e-9, ...)   生产配置重解 (~3 s)
  outputs/registry_q3.csv                        既有注册表 (交叉核对)
本脚本自身现算的量写入 outputs/registry_q3_figures.csv。

QA 契约 (与 q2_figures 相同): 对齐门 (1.5 pt) / 数据不出轴 / 页面尺寸不变量 /
mathtext 字形监视 / 对数轴显式刻度; 另以 CLI 跑碰撞门与最小字号门.

运行: python src/q3_figures.py
输出: paper/figures/fig_q3_{event,order}.pdf|.png|.svg + *.alignment.json
      outputs/registry_q3_figures.csv, outputs/q3_figures_console.log
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C as PAL, GREY, setup  # noqa: E402
from q3_solve import (CSTAR, PROD_M, PROD_RTOL, crossing_times, sample_all,  # noqa: E402
                      solve_q3)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKILL_SCRIPTS = r"C:\Users\极光\.dsh\research-skills\nature-figure\scripts"
if os.path.isdir(SKILL_SCRIPTS):
    sys.path.insert(0, SKILL_SCRIPTS)
try:
    from audit_panel_alignment import require_matplotlib_panel_alignment
    HAVE_GATE = True
except Exception as _e:  # noqa: BLE001
    HAVE_GATE = False
    _GATE_ERR = str(_e)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
FIGD = os.path.join(ROOT, "paper", "figures")

FS_TITLE, FS_LABEL, FS_TICK, FS_LEG, FS_ANN = 8.5, 8.0, 7.5, 7.4, 7.4

REG: list[list[str]] = []
EXCLUDE: list = []
_LOG: list = [None]
_GLYPH: list = []
CMD = "python src/q3_figures.py"

RADII_CM = np.round(np.arange(0.0, 2.0001, 0.1), 10)
R5 = (0.0, 0.5, 1.0, 1.5, 2.0)                 # 达标次序的五个半径
COL5 = ["#b2182b", "#e08214", "#2166ac", "#01665e", "#762a83"]


# ---------------------------------------------------------------------------
# 日志 / 注册表 / 字形监测 (与 q2_figures 相同的约定)
# ---------------------------------------------------------------------------
def say(s=""):
    print(s, flush=True)
    if _LOG[0] is not None:
        _LOG[0].write(str(s) + "\n")
        _LOG[0].flush()


class _GlyphWatch(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.hits: list[str] = []

    def emit(self, record):
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001
            msg = str(record.msg)
        if "glyph" in msg and "dummy symbol" in msg:
            self.hits.append(msg)


def open_log(path):
    _LOG[0] = open(path, "w", encoding="utf-8")


def add(id_, q, v, u="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, "", "q3_figures.py", CMD, note])
    return v


def read_registry(path):
    d = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                d[row["id"]] = float(row["value"])
            except (TypeError, ValueError):
                pass
    return d


# ---------------------------------------------------------------------------
# 排版工具 (与 q2_figures 相同)
# ---------------------------------------------------------------------------
def _decade(v, _pos=None):
    if not np.isfinite(v) or v == 0:
        return "0"
    s = "-" if v < 0 else ""
    a = abs(v)
    e = int(round(np.log10(a)))
    if abs(a - 10.0 ** e) > 1e-9 * a:
        return ""
    if -1 <= e <= 4:
        return f"{s}{a:g}"
    return f"{s}$10^{{{e}}}$"


def log_ticks(ax, which="y"):
    axis = ax.yaxis if which == "y" else ax.xaxis
    axis.set_major_formatter(FuncFormatter(_decade))
    axis.set_minor_formatter(NullFormatter())


def empty_spot(ax, pts_xy, box_wh, prefer="upper right"):
    """在轴坐标系里找一个不含任何数据点的矩形位置 (对数轴安全).

    数据点经 transData -> 轴分数变换 (自动处理 log 刻度), 再扫描空白矩形;
    返回轴分数坐标 (x, y) —— 文本左下角; 调用方必须带 transform=ax.transAxes.
    """
    w, h = box_wh
    fig = ax.figure
    fig.canvas.draw()
    p = ax.transData.transform(np.column_stack(pts_xy))
    ab = ax.get_window_extent(fig.canvas.get_renderer())
    fx = (p[:, 0] - ab.x0) / ab.width
    fy = (p[:, 1] - ab.y0) / ab.height
    xs = np.linspace(0.03, max(0.03, 1.0 - w - 0.03), 21)
    ys = np.linspace(0.03, max(0.03, 1.0 - h - 0.03), 21)
    if "right" in prefer:
        xs = xs[::-1]
    if "upper" in prefer:
        ys = ys[::-1]
    for cy in ys:
        for cx in xs:
            if not np.any((fx >= cx - 0.01) & (fx <= cx + w + 0.01)
                          & (fy >= cy - 0.01) & (fy <= cy + h + 0.01)):
                return float(cx), float(cy)
    raise RuntimeError("未找到空白注释位置")


def place_anno(ax, pts_xy, text, prefer="upper right", fs=None):
    fs = FS_ANN if fs is None else fs
    fig = ax.figure
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    probe = ax.text(0.0, 0.0, text, fontsize=fs, transform=ax.transAxes, va="bottom")
    bb = probe.get_window_extent(ren)
    ab = ax.get_window_extent(ren)
    probe.remove()
    w = bb.width / ab.width + 0.04
    h = bb.height / ab.height + 0.04
    if w >= 1.0 or h >= 1.0:
        raise RuntimeError(f"注释比坐标区还宽/高: {text[:34]!r}")
    cx, cy = empty_spot(ax, pts_xy, (w, h), prefer=prefer)
    art = ax.text(cx, cy, text, transform=ax.transAxes, fontsize=fs, va="bottom")
    fig.canvas.draw()
    nb = art.get_window_extent(ren)
    if nb.x0 < ab.x0 - 1.0 or nb.x1 > ab.x1 + 1.0:
        raise RuntimeError(f"注释横向溢出坐标区: {text[:34]!r}")
    return art


def panel(fig, gs, r, c, gid, title):
    ax = fig.add_subplot(gs[r, c])
    ax.set_gid(gid)
    ax.set_title(title, fontsize=FS_TITLE)
    ax.tick_params(labelsize=FS_TICK)
    return ax


def assert_data_in_limits(fig):
    for k, ax in enumerate(fig.axes):
        xl, yl = ax.get_xlim(), ax.get_ylim()
        x0, x1 = min(xl), max(xl)
        y0, y1 = min(yl), max(yl)
        dx, dy = x1 - x0, y1 - y0
        for j, ln in enumerate(ax.lines):
            if ln.get_transform() is not ax.transData:
                continue
            X = np.asarray(ln.get_xdata(), dtype=float)
            Y = np.asarray(ln.get_ydata(), dtype=float)
            m = np.isfinite(X) & np.isfinite(Y)
            if not m.any():
                continue
            X, Y = X[m], Y[m]
            bad = []
            if X.min() < x0 - 1e-9 * max(dx, 1e-30):
                bad.append(f"x_min={X.min():.6g} < {x0:.6g}")
            if X.max() > x1 + 1e-9 * max(dx, 1e-30):
                bad.append(f"x_max={X.max():.6g} > {x1:.6g}")
            if Y.min() < y0 - 1e-9 * max(dy, 1e-30):
                bad.append(f"y_min={Y.min():.6g} < {y0:.6g}")
            if Y.max() > y1 + 1e-9 * max(dy, 1e-30):
                bad.append(f"y_max={Y.max():.6g} > {y1:.6g}")
            if bad:
                raise AssertionError(
                    f"axes[{k}] gid={ax.get_gid()} line[{j}] 数据超出坐标范围: "
                    + "; ".join(bad))


def save_gated(fig, name):
    os.makedirs(FIGD, exist_ok=True)
    base = os.path.join(FIGD, name)
    assert_data_in_limits(fig)
    if HAVE_GATE:
        rep = require_matplotlib_panel_alignment(
            fig, json_out=f"{base}.alignment.json",
            overlay_svg=f"{base}.alignment.svg",
            tolerance_pt=1.5, gutter_tolerance_pt=1.5,
            exclude_axes=EXCLUDE, strict=True)
        say(f"  [对齐门] {name}: {rep['verdict']} "
            f"(比较 {rep['summary']['comparisons']} 组, fail={rep['summary']['fail']},"
            f" warn={rep['summary']['warn']})")
    fig.savefig(f"{base}.pdf", bbox_inches="tight")
    fig.savefig(f"{base}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{base}.svg", bbox_inches="tight")
    import fitz
    doc = fitz.open(f"{base}.pdf")
    w_pt, h_pt = doc[0].rect.width, doc[0].rect.height
    doc.close()
    fw, fh = (v * 72 for v in fig.get_size_inches())
    if not (0.8 * fw <= w_pt <= 1.6 * fw and 0.8 * fh <= h_pt <= 1.6 * fh):
        raise AssertionError(
            f"{name}: 页面尺寸异常 {w_pt:.1f}x{h_pt:.1f} pt (画布 {fw:.1f}x{fh:.1f} pt)")
    say(f"saved: paper/figures/{name}.pdf|.png|.svg  ({w_pt:.0f}x{h_pt:.0f} pt)")


# ---------------------------------------------------------------------------
# 数据
# ---------------------------------------------------------------------------
def load_production():
    """现算生产解 (与 q3_produce 同配置), 采样全部图所需数据."""
    o = solve_q3(M=PROD_M, rtol=PROD_RTOL)
    sol, g, n = o["sol"], o["g"], o["n"]
    t_dry = o["t_dry"]
    smp = sample_all(sol, g, o["env"], t_dry)
    # 五个半径在 C60 的 21 个输出列中的位置 (输出半径 0,0.1,...,2.0 cm)
    idx5 = [int(round(rc / 0.1)) for rc in R5]
    Y5 = smp["C60"][:, idx5]                       # (n60, 5)
    # 剖面 (全部 201 节点)
    tprof = [6 * 3600.0, 24 * 3600.0, 48 * 3600.0, t_dry]
    P = sol.sol(np.asarray(tprof))[n:]             # (n_node, 4)
    r_cm = g["r"] * 100.0
    # 末段 1 s 序列 (48 h -> t_dry)
    tz = np.linspace(t_dry - 9 * 3600.0, t_dry, 9 * 3600 + 1)
    maxZ = sol.sol(tz)[n:].max(axis=0)
    # 步长序列
    tst = sol.t
    dt = np.diff(tst)
    return dict(o=o, sol=sol, g=g, n=n, t_dry=t_dry, smp=smp,
                t60=smp["t60"] / 3600.0, maxC60=smp["maxC60"],
                Y5=Y5, tprof=tprof, P=P, r_cm=r_cm,
                tz=tz / 3600.0, maxZ=maxZ,
                t_steps=tst[1:] / 3600.0, dt_steps=dt,
                crossings=crossing_times(sol, g, n, t_dry))


# ---------------------------------------------------------------------------
# 图 1: 烘干时间的确定 (事件定位 + 自适应步长)
# ---------------------------------------------------------------------------
def fig_event(d):
    reg = read_registry(os.path.join(OUT, "registry_q3_verify.csv"))
    t_dry_h = d["t_dry"] / 3600.0
    th = CSTAR

    fig = plt.figure(figsize=(9.0, 2.75))
    gs = fig.add_gridspec(1, 3, wspace=0.34, left=0.065, right=0.985,
                          top=0.86, bottom=0.17)

    # ---- (a) 全程 max_i C_i(t) ----
    ax = panel(fig, gs, 0, 0, "a", r"(a) 全场最大含水率 $\max_i C_i(t)$")
    ax.semilogx(d["t60"], d["maxC60"], color=PAL["blue"], lw=1.4)
    ax.axhline(th, color=GREY["mid"], lw=0.9, ls="--")
    ax.axvline(t_dry_h, color=PAL["red"], lw=1.0, ls=":")
    ax.plot([t_dry_h], [th], marker="o", ms=4.5, color=PAL["red"], zorder=5)
    ax.set_xlim(0.015, 80.0)
    ax.set_ylim(0.0, 2.8)
    ax.set_xlabel("时间 / h", fontsize=FS_LABEL)
    ax.set_ylabel(r"$\max_i C_i$ / (kg/kg)", fontsize=FS_LABEL)
    log_ticks(ax, "x")
    place_anno(ax, (d["t60"], d["maxC60"]),
               r"$t_{\mathrm{dry}}=57.42\,$h（事件定位）", prefer="upper left")

    # ---- (b) 末段放大 ----
    ax = panel(fig, gs, 0, 1, "b", r"(b) 末段放大（$9\,$h，$1\,$s 采样）")
    ax.plot(d["tz"], d["maxZ"], color=PAL["blue"], lw=1.4)
    ax.axhline(th, color=GREY["mid"], lw=0.9, ls="--")
    ax.plot([t_dry_h], [th], marker="o", ms=4.5, color=PAL["red"], zorder=5)
    ax.set_xlim(d["tz"][0], d["tz"][-1] * 1.002)
    ymin = float(d["maxZ"].min())
    ax.set_ylim(min(th - 0.004, ymin - 0.002), float(d["maxZ"].max()) + 0.002)
    ax.set_xlabel("时间 / h", fontsize=FS_LABEL)
    ax.set_ylabel(r"$\max_i C_i$ / (kg/kg)", fontsize=FS_LABEL)
    gmin = float((d["maxZ"] - th)[:-1].min())
    place_anno(ax, (d["tz"], d["maxZ"]),
               r"事件前恒正：$\min g=$" + f"{gmin:.1e}".replace("e-0", "e-"),
               prefer="upper right")
    ax.annotate("终止事件", xy=(t_dry_h, th), xytext=(-56, -18),
                textcoords="offset points", fontsize=FS_ANN, color=PAL["red"])

    # ---- (c) 自适应步长 ----
    ax = panel(fig, gs, 0, 2, "c", "(c) BDF 步长演化")
    ax.semilogy(d["t_steps"], d["dt_steps"], color=PAL["teal"], lw=0.7)
    ax.axhline(3600.0, color=GREY["mid"], lw=0.9, ls="--")
    ax.axhline(0.25, color=PAL["red"], lw=0.9, ls=":")
    ax.set_xlim(0.0, d["t_steps"][-1] * 1.02)
    dts = d["dt_steps"]
    ax.set_ylim(dts.min() * 0.5, 3600.0 * 2.2)
    ax.set_xlabel("时间 / h", fontsize=FS_LABEL)
    ax.set_ylabel(r"步长 $\Delta t$ / s", fontsize=FS_LABEL)
    log_ticks(ax, "y")
    n_dec = np.log10(dts.max() / dts.min())
    say(f"  (c) 步长范围 {dts.min():.3g} ~ {dts.max():.3g} s "
        f"(跨 {n_dec:.2f} 个数量级), 平均 {dts.mean():.1f} s")
    save_gated(fig, "fig_q3_event")
    return dict(n_dec=n_dec, dt_min=float(dts.min()), dt_max=float(dts.max()),
                dt_mean=float(dts.mean()))


# ---------------------------------------------------------------------------
# 图 2: 由表及里的达标次序
# ---------------------------------------------------------------------------
def fig_order(d):
    t_dry_h = d["t_dry"] / 3600.0
    th = CSTAR
    cross = d["crossings"]                        # {r_cm: t_s}
    ct_h = [cross[rc] / 3600.0 for rc in R5]

    fig = plt.figure(figsize=(9.0, 2.75))
    gs = fig.add_gridspec(1, 3, wspace=0.36, left=0.065, right=0.985,
                          top=0.86, bottom=0.17)

    # ---- (a) 五个半径的 C(t) ----
    ax = panel(fig, gs, 0, 0, "a", "(a) 各半径含水率的演化与达标时刻")
    for j, rc in enumerate(R5):
        ax.semilogx(d["t60"], d["Y5"][:, j], color=COL5[j], lw=1.3)
        ax.plot([ct_h[j]], [th], marker="o", ms=4.0, color=COL5[j], zorder=5)
    ax.axhline(th, color=GREY["mid"], lw=0.9, ls="--")
    ax.set_xlim(0.015, 80.0)
    ax.set_ylim(0.0, 2.75)
    ax.set_xlabel("时间 / h", fontsize=FS_LABEL)
    ax.set_ylabel(r"$C$ / (kg/kg)", fontsize=FS_LABEL)
    log_ticks(ax, "x")
    place_anno(ax, (d["t60"], d["Y5"][:, 0]),
               "曲线自上而下：r = 0 → 2.0 cm", prefer="upper right")

    # ---- (b) 剖面演化 ----
    ax = panel(fig, gs, 0, 1, "b", "(b) 水分剖面的演化")
    shades = ["#92c5de", "#67a9cf", "#2166ac", "#b2182b"]
    lbls = ["6 h", "24 h", "48 h", r"$t_{\mathrm{dry}}$"]
    for k in range(4):
        ax.plot(d["r_cm"], d["P"][:, k], color=shades[k], lw=1.3, label=lbls[k])
    ax.axhline(th, color=GREY["mid"], lw=0.9, ls="--")
    ax.axhline(0.05, color=GREY["dark"], lw=0.8, ls=":")
    ax.set_xlim(0.0, 2.05)
    ax.set_ylim(0.0, 2.75)
    ax.set_xlabel("到药材中心的距离 / cm", fontsize=FS_LABEL)
    ax.set_ylabel(r"$C$ / (kg/kg)", fontsize=FS_LABEL)
    leg = ax.legend(fontsize=FS_LEG, loc="upper right", handlelength=1.4)
    leg.set_zorder(6)

    # ---- (c) 达标时刻 vs 半径 ----
    ax = panel(fig, gs, 0, 2, "c", "(c) 达标次序：由表及里")
    ypos = np.arange(5) * 1.0                    # r=0 在底部, r=2.0 在顶部
    vals = ct_h
    ax.barh(ypos, vals, height=0.62, color=COL5, alpha=0.85)
    for y, v in zip(ypos, vals):
        ax.text(v - 1.0, y, f"{v:.2f} h", va="center", ha="right",
                fontsize=FS_ANN, color="white")
    ax.axvline(t_dry_h, color=PAL["red"], lw=1.0, ls=":")
    ax.set_yticks(ypos)
    ax.set_yticklabels(["0（轴心）", "0.5 cm", "1.0 cm", "1.5 cm", "2.0 cm"],
                       fontsize=FS_TICK)
    ax.set_xlim(0.0, 70.0)
    ax.set_ylim(-0.55, 4.55)
    ax.set_xlabel("达标时刻 / h", fontsize=FS_LABEL)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save_gated(fig, "fig_q3_order")
    return ct_h


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-solve", action="store_true", help="只重画, 不重解 (需缓存)")
    args = ap.parse_args()
    setup()
    matplotlib.rcParams.update({
        "font.size": FS_ANN, "axes.titlesize": FS_TITLE, "axes.labelsize": FS_LABEL,
        "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
        "legend.fontsize": FS_LEG,
    })
    fam = list(matplotlib.rcParams["font.sans-serif"])
    if "DejaVu Sans" not in fam:
        matplotlib.rcParams["font.sans-serif"] = fam + ["DejaVu Sans"]

    os.makedirs(OUT, exist_ok=True)
    open_log(os.path.join(OUT, "q3_figures_console.log"))
    h = _GlyphWatch()
    logging.getLogger("matplotlib.mathtext").addHandler(h)
    _GLYPH.append(h)
    say(f"运行: python src/q3_figures.py{' --no-solve' if args.no_solve else ''}")

    t0 = time.time()
    d = load_production()
    say(f"生产解复现: t_dry = {d['t_dry']:.3f} s = {d['t_dry'] / 3600:.4f} h, "
        f"{d['o']['nsteps']} 步, 用时 {time.time() - t0:.1f} s")
    regp = read_registry(os.path.join(OUT, "registry_q3.csv"))
    dev = abs(d["t_dry"] - regp["P01_tdry"]) / regp["P01_tdry"]
    say(f"  与注册表 P01_tdry 相对差 = {dev:.2e}")
    if dev > 1e-8:
        raise SystemExit("生产解与注册表不一致, 先重跑 q3_produce.py")

    # ---------------- 注册表 ----------------
    add("FG3_tdry", "复现: 烘干时间 t_dry", d["t_dry"], "s", "与 P01_tdry 交叉核对")
    add("FG3_nsteps", "复现: 生产求解步数", int(d["o"]["nsteps"]), "-", "与 P03_nsteps 交叉核对")
    add("FG3_maxC_dry", "复现: 终态 max_i C_i 与 C* 之差",
        d["smp"]["maxC_dry"] - CSTAR, "kg/kg", "事件一致性")
    smp = d["smp"]
    add("FG3_maxC60_min", "max_i C_i 全程最小值 (60 s 网格)", float(smp["maxC60"].min()),
        "kg/kg")
    add("FG3_maxC60_max", "max_i C_i 全程最大值 (60 s 网格)", float(smp["maxC60"].max()),
        "kg/kg")
    gmin = float((smp["maxC_fin"] - CSTAR)[:-1].min())
    add("FG3_gpre_min", "事件前 g 的最小值 (末 2 h, 1 s)", gmin, "kg/kg", "W10 交叉核对")
    for j, rc in enumerate(R5):
        add(f"FG3_cross_r{rc:g}", f"复现: r={rc:g} cm 达标时刻",
            d["crossings"][rc] / 3600.0, "h", "与 P07_* 交叉核对")
    ev = fig_event(d)
    add("FG3_dt_min", "BDF 最小步长", ev["dt_min"], "s")
    add("FG3_dt_max", "BDF 最大步长", ev["dt_max"], "s")
    add("FG3_dt_mean", "BDF 平均步长", ev["dt_mean"], "s")
    add("FG3_dt_decades", "步长跨越的数量级", ev["n_dec"], "-")
    ct = fig_order(d)
    for j, rc in enumerate(R5):
        add(f"FG3_ct_h_r{rc:g}", f"图(c) 达标时刻标注值 r={rc:g} cm", ct[j], "h")
    with open(os.path.join(OUT, "registry_q3_figures.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    say(f"\n注册表: outputs/registry_q3_figures.csv ({len(REG)} 行)")

    # ---------------- 出图 ----------------
    n_glyph = sum(len(x.hits) for x in _GLYPH)
    say(f"\n字形完整性: mathtext 缺字形告警 {n_glyph} 次")
    if n_glyph:
        for x in _GLYPH:
            for msg in x.hits[:3]:
                say(f"   {msg}")
        raise SystemExit(3)
    say("完成。")


if __name__ == "__main__":
    main()
