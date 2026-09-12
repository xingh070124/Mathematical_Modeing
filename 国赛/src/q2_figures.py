# -*- coding: utf-8 -*-
r"""
问题二的示意图与结果图 (Python/matplotlib; 后端按既有图脚本确定为 Python).

与问题一图件的关系 (逐图说明, 确保不重复):
  问题一已有图: fig_q1_env (环境激励), fig_q1_model (几何+第三类边界),
                fig_q1_fick (Fick 扩散示意), fig_q1_fvm (有限体积网格),
                fig_q1_temp_results / fig_q1_moist_results (30 min 结果),
                fig_q1_sensitivity / fig_q1_robustness (解耦下的灵敏度).
  本脚本产出 5 张, 每张讲一个**问题一不存在**的结论:
    fig_q2_coupling      三条耦合通路 + Jacobian 分块带状结构 + 物性随 C 的漂移
                         (问题一三通路全部断开). 是"耦合"的机理图, 非几何示意.
    fig_q2_energy_form   能量方程两种写法不等价 (17.2745 K) + 伪源项量级 + 收支缺口
                         (问题一 rho cp 为常数, 两式恒等, 无此问题).
    fig_q2_latent        蒸发吸热: 表面热流分解 + 初期表面下穿初温 + 极值原理越界
                         (问题一无相变项).
    fig_q2_temp_results  3 h 温度场: 时空热图 + 表3 剖面 + 径向温差先增后减 (准均匀化)
                         (问题一是"预热分层尚未结束").
    fig_q2_moist_results 3 h 水分场: 时空热图叠加干燥前沿轨迹 + 表4 剖面 + 失水率
                         (问题一是"仅表层干壳").

  问题二的灵敏度/鲁棒性数字以 LaTeX 表格给出 (见论文), 不另出图, 避免与问题一的
  龙卷风图重复.

数据源:
  outputs/result2.xlsx               生产解 (M=1600, dt=1/64 s), 10800x21
  A题/附件/附件1.xlsx                烘房环境 (PCHIP 连续化)
  outputs/registry_q2_{production,verify,center,energy,model}.csv  既有注册表
本脚本自身现算的量写入 outputs/registry_q2_figures.csv。

排版约束 (由 nature-figure 的 QA 契约驱动, 全部为可复算校验):
  1. 所有渲染字形的 PDF 字号 >= 5 pt: 注释/图例基号 7.4 pt, mathtext 上下标
     缩放 0.70 -> 5.18 pt.
  2. 多面板按 SubplotSpec 实测矩形做对齐门 (容差 1.5 pt); 色条/twin 轴无
     subplotspec, 显式排除.
  3. 文字不得与任何描边路径相交、不得相互重叠: 因此禁止 "\n" 多行文本,
     注释位置由 empty_spot() 在数据上检查为空区后才落笔, 并加断言.
  4. 对数轴刻度标签用显式 $10^{e}$: matplotlib 的 LogFormatter 产生
     \mathdefault, 其字体名 'default' 不在 mathtext 字体表中, 会把指数上的
     减号 (U+2212) 替换成占位符.

运行: python src/q2_figures.py           (含两个重算算例, 约 2 min)
      python src/q2_figures.py --no-runs (复用缓存的算例结果)
输出: paper/figures/fig_q2_*.pdf|.png|.svg + *.alignment.json
      outputs/registry_q2_figures.csv, outputs/q2_figures_console.log
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
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C as PAL, GREY, setup  # noqa: E402
from q1_solve import Env, load_attachment1  # noqa: E402
from q2_solve import Par, geometry, march, out_indices, props  # noqa: E402

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
XLSX = os.path.join(OUT, "result2.xlsx")

FS_TITLE, FS_LABEL, FS_TICK, FS_LEG, FS_ANN, FS_CB = 8.5, 8.0, 7.5, 7.4, 7.4, 7.2
HALF_ULP = 5e-5
R_M = 0.02
HM = 8.0e-7
H_CONV = 25.0
HEVAP_28 = 2.4346e6
HEVAP_SLOPE = -2.391e3
HEVAP_TREF = 301.15
T_TAB_S = [1800, 3600, 5400, 7200, 9000, 10800]
T_TAB_H = ["0.5", "1.0", "1.5", "2.0", "2.5", "3.0"]
C_FRONT = 0.9 * 2.55          # 干燥前沿判别含水率 kg/kg (= 2.295)

REG: list[list[str]] = []
EXCLUDE: list = []            # 色条 inset 轴与 twinx 轴 (无 subplotspec)
_LOG: list = [None]
_GLYPH: list = []
CMD = "python src/q2_figures.py"


# ---------------------------------------------------------------------------
# 日志 / 注册表 / 字形监测
# ---------------------------------------------------------------------------
def say(s=""):
    print(s, flush=True)
    if _LOG[0] is not None:
        _LOG[0].write(str(s) + "\n")
        _LOG[0].flush()


class _GlyphWatch(logging.Handler):
    """mathtext 的"缺字形->占位符"告警走 logging, 不经 warnings 模块."""

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


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, "q2_figures.py", CMD, note])
    return v


# ---------------------------------------------------------------------------
# 排版工具
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
    r"""对数轴主刻度换成不触发 \mathdefault 的显式形式 (见模块 docstring)."""
    axis = ax.yaxis if which == "y" else ax.xaxis
    axis.set_major_formatter(FuncFormatter(_decade))
    axis.set_minor_formatter(NullFormatter())


def plain_ticks(ax, ticks, which="y"):
    axis = ax.yaxis if which == "y" else ax.xaxis
    axis.set_major_locator(matplotlib.ticker.FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    axis.set_minor_formatter(NullFormatter())


def colorbar(fig, mappable, ax, label, fs=None):
    cax = ax.inset_axes([1.025, 0.0, 0.04, 1.0])
    cb = fig.colorbar(mappable, cax=cax)
    cb.set_label(label, fontsize=FS_LABEL if fs is None else fs)
    cb.ax.tick_params(labelsize=FS_CB, length=2)
    EXCLUDE.append(cax)
    return cb


def twin(ax):
    ax2 = ax.twinx()
    EXCLUDE.append(ax2)
    return ax2


def empty_spot(ax, pts_xy, box_wh, prefer="upper right"):
    """在轴坐标系里找一个不含任何数据点的矩形位置, 保证注释不被折线穿过.

    pts_xy : (2, N) 数据坐标的数据点集合
    box_wh : (w, h) 注释矩形在**轴分数**下的宽高
    返回轴分数坐标 (x, y) —— 文本左下角; 调用方必须带 transform=ax.transAxes,
    否则会把轴分数误当数据坐标画到轴外 (曾把页面撑到 52437 pt).
    """
    w, h = box_wh
    lo_x, hi_x = ax.get_xlim()
    lo_y, hi_y = ax.get_ylim()
    if lo_x > hi_x:
        lo_x, hi_x = hi_x, lo_x
    if lo_y > hi_y:
        lo_y, hi_y = hi_y, lo_y
    fx = (np.asarray(pts_xy[0], dtype=float) - lo_x) / (hi_x - lo_x)
    fy = (np.asarray(pts_xy[1], dtype=float) - lo_y) / (hi_y - lo_y)
    xs = np.linspace(0.03, max(0.03, 1.0 - w - 0.03), 21)
    ys = np.linspace(0.03, max(0.03, 1.0 - h - 0.03), 21)
    if "right" in prefer:
        xs = xs[::-1]
    if "upper" in prefer:
        ys = ys[::-1]
    for cy in ys:
        for cx in xs:
            if not np.any((fx >= cx) & (fx <= cx + w) & (fy >= cy) & (fy <= cy + h)):
                return float(cx), float(cy)
    raise RuntimeError("未找到空白注释位置, 需要缩小注释或调整坐标范围")


def place_anno(ax, pts_xy, text, prefer="upper right", fs=None):
    """测量真实文字尺寸 -> 在空白处落笔 -> 校验不溢出坐标区.

    只按"估算宽度"扫描会在文字实际溢出时静默失败 (曾溢出到相邻面板的刻度标签上),
    所以这里以渲染后的 bounding box 为准.
    """
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
        raise RuntimeError(f"注释比坐标区还宽/高 ({w:.2f}, {h:.2f}): {text[:34]!r}")
    cx, cy = empty_spot(ax, pts_xy, (w, h), prefer=prefer)
    art = ax.text(cx, cy, text, transform=ax.transAxes, fontsize=fs, va="bottom")
    fig.canvas.draw()
    nb = art.get_window_extent(ren)
    if nb.x0 < ab.x0 - 1.0 or nb.x1 > ab.x1 + 1.0:
        raise RuntimeError(f"注释横向溢出坐标区: {text[:34]!r} "
                           f"(文字 {nb.x0:.0f}..{nb.x1:.0f} vs 坐标区 {ab.x0:.0f}..{ab.x1:.0f})")
    return art


def panel(fig, gs, r, c, gid, title):
    ax = fig.add_subplot(gs[r, c])
    ax.set_gid(gid)
    ax.set_title(title, fontsize=FS_TITLE)
    ax.tick_params(labelsize=FS_TICK)
    return ax


def blank(fig, gs, r, c, gid, title):
    ax = fig.add_subplot(gs[r, c])
    ax.set_gid(gid)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=FS_TITLE)
    return ax


def _diagnose_blowup(fig, w_pt, h_pt):
    """页面尺寸异常时, 逐个 artist 报出超出画布的窗口范围, 直指元凶."""
    say(f"  !! 页面 {w_pt:.1f}x{h_pt:.1f} pt 超出画布, 逐个 artist 排查:")
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    lim = 4.0 * max(fig.bbox.width, fig.bbox.height)
    for k, ax in enumerate(fig.axes):
        tb = ax.get_tightbbox(ren)
        say(f"     axes[{k}] gid={ax.get_gid()} tight="
            f"{None if tb is None else tuple(round(v, 1) for v in tb.bounds)}")
        for j, ln in enumerate(ax.lines):
            bb = ln.get_window_extent(ren)
            if max(abs(bb.x0), abs(bb.x1), abs(bb.y0), abs(bb.y1)) > lim:
                yd = np.asarray(ln.get_ydata(), dtype=float)
                say(f"        line[{j}] ymin={np.nanmin(yd):.4g} ymax={np.nanmax(yd):.4g} "
                    f"win={tuple(round(v, 1) for v in bb.bounds)}")
        for j, tx in enumerate(ax.texts):
            bb = tx.get_window_extent(ren)
            if max(abs(bb.x0), abs(bb.x1), abs(bb.y0), abs(bb.y1)) > lim:
                say(f"        text[{j}] {tx.get_text()[:40]!r} "
                    f"win={tuple(round(v, 1) for v in bb.bounds)}")
    tb = fig.get_tightbbox(ren)
    say(f"     figure tight={tuple(round(v, 1) for v in tb.bounds) if tb else None}")


def assert_data_in_limits(fig):
    """不变量: 每条数据曲线都必须落在其坐标轴范围内.

    只按视觉设置 ylim 很容易把曲线的尾段裁掉 (本图曾把表面温度回升段裁到轴外,
    使曲线冲出面板顶边并与标题相交). 这里对全部数据坐标系的 Line2D 逐一检查.
    """
    for k, ax in enumerate(fig.axes):
        xl, yl = ax.get_xlim(), ax.get_ylim()
        x0, x1 = min(xl), max(xl)
        y0, y1 = min(yl), max(yl)
        dx, dy = x1 - x0, y1 - y0
        for j, ln in enumerate(ax.lines):
            if ln.get_transform() is not ax.transData:
                continue                       # axhline/axvline 等混合坐标系
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
    # 不变量: 导出页面尺寸必须与画布同量级. 任何 inf/NaN 进入画布都会让
    # bbox_inches='tight' 把页面撑到不可用 (曾出现 52437 pt 的页面), 这里拦住.
    import fitz
    doc = fitz.open(f"{base}.pdf")
    w_pt, h_pt = doc[0].rect.width, doc[0].rect.height
    doc.close()
    fw, fh = (v * 72 for v in fig.get_size_inches())
    if not (0.8 * fw <= w_pt <= 1.6 * fw and 0.8 * fh <= h_pt <= 1.6 * fh):
        _diagnose_blowup(fig, w_pt, h_pt)
        raise AssertionError(
            f"{name}: 页面尺寸异常 {w_pt:.1f}x{h_pt:.1f} pt (画布 {fw:.1f}x{fh:.1f} pt); "
            f"检查是否有 inf/NaN 或异常坐标进入了绘图数据")
    say(f"saved: paper/figures/{name}.pdf|.png|.svg  ({w_pt:.0f}x{h_pt:.0f} pt)")


# ---------------------------------------------------------------------------
# 数据读入与派生
# ---------------------------------------------------------------------------
def load_result2():
    from openpyxl import load_workbook

    wb = load_workbook(XLSX, data_only=True, read_only=True)

    def grid(ws):
        rows = list(ws.iter_rows(values_only=True))
        hdr = rows[0][1:]
        t = np.array([r[0] for r in rows[1:]], dtype=float)
        v = np.array([[float(x) for x in r[1:]] for r in rows[1:]], dtype=float)
        return np.array([float(h) for h in hdr]), t, v

    rh, tt, T = grid(wb["温度"])
    _, tc, C = grid(wb["水分浓度"])
    wb.close()
    assert np.array_equal(tt, tc), "温度/水分时间列不一致"
    assert T.shape == C.shape == (10800, 21), f"维度异常 {T.shape} {C.shape}"
    return rh, tt, T, C


def read_registry(path):
    d = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                d[row["id"]] = float(row["value"])
            except (TypeError, ValueError):
                pass
    return d


def hevap_of_Tc(T_c):
    return HEVAP_28 + HEVAP_SLOPE * ((T_c + 273.15) - HEVAP_TREF)


def derive(rh, tt, T, C, env, regp):
    """由生产解与既有注册表派生出图所需的一切量."""
    d = {}
    Tres, Cres = T[:, -1], C[:, -1]
    Tin_C = np.array([env.T(t) - 273.15 for t in tt])
    Cin = np.array([env.C(t) for t in tt])
    d["Tin_C"], d["Cin"] = Tin_C, Cin

    # 表面热流 (向内为正, per 2 pi, 单位轴长)
    d["q_conv"] = H_CONV * R_M * (Tin_C - Tres)
    d["q_evap"] = hevap_of_Tc(Tres) * HM * R_M * (Cres - Cin)
    d["q_cond"] = d["q_conv"] - d["q_evap"]         # 净导入内部的导热热流
    # 蒸发份额 q_evap/q_conv 只在表面对流驱动力远高于附件1 的 1e-3 degC 记录
    # 分辨率的时段才有意义 (T_inf 非单调, 驱动力会过零); 其余置 NaN.
    drive = Tin_C - Tres
    d["q_drive"] = drive
    well = np.abs(drive) >= 0.05
    nz = np.abs(d["q_conv"]) > 1e-9
    d["q_ratio_ok"] = well & nz
    d["q_ratio"] = np.full(len(tt), np.nan)
    d["q_ratio"][d["q_ratio_ok"]] = (d["q_evap"][d["q_ratio_ok"]]
                                     / d["q_conv"][d["q_ratio_ok"]])
    d["n_ratio_ok"] = int(np.count_nonzero(d["q_ratio_ok"]))
    d["n_ratio_bad"] = int(len(tt) - d["n_ratio_ok"])
    # 未加掩码时比值的病态幅度 (记录在案: 该瞬时比值不可用作判据)
    raw = np.full(len(tt), np.nan)
    raw[nz] = d["q_evap"][nz] / d["q_conv"][nz]
    d["q_ratio_raw_max"] = float(np.nanmax(raw))
    d["q_drive_min"] = float(np.min(np.abs(drive)))
    d["q_cond_min"] = float(np.min(d["q_cond"]))
    for t in T_TAB_S:
        d[f"qconv_{t}"] = float(d["q_conv"][t - 1])
        d[f"qevap_{t}"] = float(d["q_evap"][t - 1])
        d[f"qcond_{t}"] = float(d["q_cond"][t - 1])
        d[f"qratio_{t}"] = float(d["q_ratio"][t - 1])
        d[f"drv_{t}"] = float(drive[t - 1])
    d["qconv_decay"] = float(d["q_conv"][1799] / d["q_conv"][10799])

    # 水量: (i) 由态梯形求积 (端点半权, sum = R^2/2); (ii) 由表面通量收支
    wq = np.full(21, 1.0)
    wq[0] = wq[-1] = 0.5
    wq *= (R_M / 20.0) * rh * 1e-2
    d["wq_sum"] = float(np.sum(wq))
    W0 = float(np.full(21, 2.55) @ wq)
    d["W"] = C @ wq
    d["Cbar"] = d["W"] / float(np.sum(wq))
    d["W0"] = W0
    d["W_flux"] = W0 - np.cumsum(HM * R_M * (Cres - Cin))
    d["loss_pct"] = (1.0 - d["W"] / W0) * 100.0
    d["Wbal_rel"] = float(abs(d["W_flux"][-1] - d["W"][-1]) / d["W"][-1])
    for t in T_TAB_S:
        d[f"Cbar_{t}"] = float(d["Cbar"][t - 1])
        d[f"loss_{t}"] = float(d["loss_pct"][t - 1])

    # 干燥前沿: C(r,t) = 0.9 C0 的等值线位置
    # C 沿 r 单调递减, 故 i = 首个使 C <= C_FRONT 的列, 有 ck[i-1] > C_FRONT >= ck[i].
    # 在 [rh[i-1], rh[i]] 上线性反解: w = (C_FRONT - ck[i-1])/(ck[i] - ck[i-1]),
    # r_front = rh[i-1] + w*(rh[i]-rh[i-1]).
    # 曾经写成 wgt = (C_FRONT-ck[i])/(ck[i-1]-ck[i]) 并当作 w 使用 —— 两者互补
    # (w = 1 - wgt), 使前沿位置偏大 2.9~22 %.
    rf = np.full(len(tt), np.nan)
    for k in range(len(tt)):
        ck = C[k]
        if ck[-1] > C_FRONT:
            continue                       # 表面尚未降到判据, 前沿不存在
        if ck[0] <= C_FRONT:
            rf[k] = 0.0                    # 中心也已降到判据, 前沿抵达中心
            continue
        i = int(np.where(ck <= C_FRONT)[0][0])
        w = (C_FRONT - ck[i - 1]) / (ck[i] - ck[i - 1])
        rf[k] = rh[i - 1] + w * (rh[i] - rh[i - 1])
    d["rfront"] = rf
    fin = np.where(np.isfinite(rf))[0]
    d["rfront_first_s"] = int(fin[0]) + 1 if fin.size else -1
    hit = np.where(rf == 0.0)[0]
    d["rfront_center_s"] = int(hit[0]) + 1 if hit.size else -1
    # 自检: 前沿处的 C 必须等于判据 (线性插值的反解应精确复现该值)
    if fin.size:
        chk = []
        for k in fin[:200]:
            cc = np.interp(rf[k], rh, C[k])
            chk.append(abs(cc - C_FRONT))
        d["rfront_selfcheck_max"] = float(max(chk))
    else:
        d["rfront_selfcheck_max"] = 0.0

    # 径向跨距与温差衰减
    d["spanT"] = Tres - T[:, 0]
    d["spanC"] = C[:, 0] - Cres
    for t in T_TAB_S:
        d[f"spanT_{t}"] = float(d["spanT"][t - 1])
        d[f"spanC_{t}"] = float(d["spanC"][t - 1])
    d["spanT_max"], d["spanT_max_t"] = float(d["spanT"].max()), int(d["spanT"].argmax()) + 1
    sl = slice(3599, 10800)
    x, y = tt[sl], np.log(d["spanT"][sl])
    A = np.vstack([x, np.ones_like(x)]).T
    b, a = np.linalg.lstsq(A, y, rcond=None)[0]
    d["tau_dT"] = float(-1.0 / b)
    pred = A @ np.array([b, a])
    d["tau_dT_ss"] = float(1.0 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))

    # 表面初期下穿
    Ts = T[:, -1]
    d["Ts_min"], d["Ts_min_t"] = float(Ts.min()), int(Ts.argmin()) + 1
    d["Ts_dip"] = float(28.0 - Ts.min())
    d["Ts_recross"] = int(np.where(Ts > 28.0)[0][0]) + 1
    # 初期下穿面板的窗口: 下穿幅度只有 0.0095 K, 而表面在 180 s 内已回升到
    # 28.27 degC (相差 28 倍), 同一线性轴无法兼顾, 故窗口取到回升结束的 40 s.
    d["n_dip_window"] = 40
    Ts_win = np.asarray(T[:d["n_dip_window"], -1], dtype=float)
    d["Ts_win_min"] = float(min(Ts_win.min(), 28.0))
    d["Ts_win_max"] = float(max(Ts_win.max(), 28.0))
    d["Ts_180"] = float(T[179, -1])

    # 由既有注册表引入 (避免重复计算)
    d["Tmin"] = regp["V4_Tmin"]
    d["Tmax"] = regp["V4_Tmax"]
    d["Tmin_off"] = regp["V4_Tmin_noevap"]
    d["Tmax_off"] = 49.966643083758      # V8: 无蒸发时 t=10800 s 表面温度
    # 3 h 表面含水率 (与注册表 X_C_10800_2 同一量) 与环境含水率之比
    d["CR_end_m"] = float(C[-1, -1])
    d["drive_end"] = float(drive[-1])
    return d


def run_variants(env, do_runs=True):
    d = {}
    cache = os.path.join(OUT, "q2_fig_energy_form.npz")
    if do_runs:
        t0 = time.time()
        o_nc = march(200, 0.25, 10800.0, env, Par(), out_idx=out_indices(200))
        say(f"  [算例] 非保守形式 M=200 dt=0.25 完成 {time.time()-t0:.1f} s")
        t0 = time.time()
        o_cs = march(200, 0.25, 10800.0, env, Par(energy="conserv"),
                     out_idx=out_indices(200))
        say(f"  [算例] 守恒形式   M=200 dt=0.25 完成 {time.time()-t0:.1f} s")
        np.savez_compressed(
            cache, t=o_nc["t_snap"], T_nc=o_nc["T_snap"], C_nc=o_nc["C_snap"],
            T_cs=o_cs["T_snap"], C_cs=o_cs["C_snap"], E_nc=o_nc["E"], E_cs=o_cs["E"],
            Fh_nc=o_nc["Fh"], Fh_cs=o_cs["Fh"], E0_nc=o_nc["stats"]["E0"],
            E0_cs=o_cs["stats"]["E0"], iters=o_nc["stats"]["iters"])
    else:
        z = np.load(cache)
        o_nc = dict(t_snap=z["t"], T_snap=z["T_nc"], C_snap=z["C_nc"], E=z["E_nc"],
                    Fh=z["Fh_nc"], stats=dict(E0=float(z["E0_nc"])))
        o_cs = dict(t_snap=z["t"], T_snap=z["T_cs"], C_snap=z["C_cs"], E=z["E_cs"],
                    Fh=z["Fh_cs"], stats=dict(E0=float(z["E0_cs"])))
        d["iters"] = z["iters"]
    d["o_nc"], d["o_cs"] = o_nc, o_cs
    d["dT"] = float(np.max(np.abs(o_nc["T_snap"] - o_cs["T_snap"])))
    d["dC"] = float(np.max(np.abs(o_nc["C_snap"] - o_cs["C_snap"])))
    d["T0_nc"] = float(o_nc["T_snap"][-1, 0] - 273.15)
    d["T0_cs"] = float(o_cs["T_snap"][-1, 0] - 273.15)
    d["TR_nc"] = float(o_nc["T_snap"][-1, -1] - 273.15)
    d["TR_cs"] = float(o_cs["T_snap"][-1, -1] - 273.15)
    d["Edef_nc"] = float(abs((o_nc["E"][-1] - o_nc["stats"]["E0"]) + o_nc["Fh"][-1]))
    d["Edef_cs"] = float(abs((o_cs["E"][-1] - o_cs["stats"]["E0"]) + o_cs["Fh"][-1]))
    if do_runs:
        d["iters"] = o_nc["stats"]["iters"]
    return d


def jacobian_pattern():
    """由求解器真实组装的带状 Jacobian 还原密矩阵, 统计分块非零元."""
    from q2_solve import assemble
    M = 30
    g = geometry(M, "lumped")
    x = np.empty(2 * g["n"])
    x[0::2] = 301.15 + 8.0 * g["r"] / R_M
    x[1::2] = 2.55 - 1.2 * g["r"] / R_M
    _, ab, _ = assemble(x, x.copy(), 0.05, g, Par(), 310.0, 0.04)
    n2 = 2 * g["n"]
    J = np.zeros((n2, n2))
    for i in range(n2):
        for j in range(max(0, i - 3), min(n2, i + 4)):
            J[i, j] = ab[3 + i - j, j]
    code = np.zeros((n2, n2))
    for i in range(n2):
        for j in range(n2):
            if J[i, j] != 0.0:
                code[i, j] = {(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}[(i % 2, j % 2)]
    nnz = int(np.count_nonzero(J))
    return dict(M=M, n2=n2, code=code, nnz=nnz, dens=nnz / (n2 * n2),
                bw=int(max(abs(i - j) for i in range(n2) for j in range(n2)
                           if J[i, j] != 0.0)),
                blk={k: int(np.count_nonzero(code == v)) for k, v in
                     (("TT", 1), ("TC", 2), ("CT", 3), ("CC", 4))})


# ---------------------------------------------------------------------------
# 图 1  耦合机理
# ---------------------------------------------------------------------------
def fig_coupling(eig):
    fig = plt.figure(figsize=(7.1, 2.8))
    gs = fig.add_gridspec(1, 4, left=0.030, right=0.985, bottom=0.105,
                          top=0.865, wspace=0.62)
    ax = blank(fig, gs, 0, slice(0, 0 + 2), "a", "(a) 三条耦合通路")
    axb = panel(fig, gs, 0, 2, "b", "(b) Jacobian 分块带状结构")
    axc = panel(fig, gs, 0, 3, "c", "(c) 物性随 $C$ 的漂移")

    # ---- (a) 通路列表 (文字与描边分离, 无多行文本) ----
    bt = FancyBboxPatch((0.035, 0.825), 0.40, 0.135, boxstyle="round,pad=0.010",
                        fc="#dbe7f3", ec=PAL["blue"], lw=1.0)
    bc = FancyBboxPatch((0.035, 0.035), 0.40, 0.135, boxstyle="round,pad=0.010",
                        fc="#fbe3dc", ec=PAL["red"], lw=1.0)
    ax.add_patch(bt); ax.add_patch(bc)
    ax.text(0.235, 0.8925, "温度场 $T(r,t)$", ha="center", va="center", fontsize=FS_ANN)
    ax.text(0.235, 0.1025, "水分场 $C(r,t)$", ha="center", va="center", fontsize=FS_ANN)
    rows = [
        (PAL["blue"], "$T\\to D(C,T)$：$\\partial\\ln D/\\partial T=4.245\\times10^{-2}\\,\\mathrm{K^{-1}}$"),
        (PAL["red"], "$C\\to\\rho c_p,\\,k$：$\\rho c_p$ 降 63.74 %，$k$ 降 46.25 %"),
        (PAL["orange"], "$C(R)\\to q_{\\mathrm{evap}}\\to T(R)$：表面温降 0.19 K"),
    ]
    for k, (col, txt) in enumerate(rows):
        yy = 0.715 - 0.145 * k
        ax.annotate("", xy=(0.100, yy), xytext=(0.116, yy),
                    arrowprops=dict(arrowstyle="-|>", lw=1.2, color=col))
        ax.text(0.132, yy, txt, ha="left", va="center", fontsize=FS_ANN)
    ax.text(0.035, 0.265, "问题一：三通路全部断开；问题二：三条同时打开，双向耦合",
            ha="left", va="center", fontsize=FS_ANN, color=GREY["dark"])

    # ---- (b) Jacobian 稀疏结构 ----
    cmap = mcolors.ListedColormap(["#ffffff", "#2166ac", "#e08214", "#b2182b", "#7f7f7f"])
    axb.imshow(eig["code"], cmap=cmap, vmin=0, vmax=4, interpolation="nearest",
               aspect="auto")
    n2 = eig["n2"]
    axb.axvline(n2 / 2 - 0.5, color=PAL["ink"], lw=0.6, ls=(0, (2, 2)))
    axb.axhline(n2 / 2 - 0.5, color=PAL["ink"], lw=0.6, ls=(0, (2, 2)))
    axb.set_xlabel("列 $j$（交错排序 $T_0,C_0,T_1,C_1,\\dots$）", fontsize=FS_LABEL)
    axb.set_ylabel("行 $i$", fontsize=FS_LABEL)
    hnd = [plt.Line2D([], [], marker="s", ls="", ms=5, mfc=cmap(v), mec="none", label=l)
           for v, l in ((1, "$J_{TT}$"), (2, "$J_{TC}$"), (3, "$J_{CT}$"), (4, "$J_{CC}$"))]
    axb.legend(handles=hnd, loc="upper center", bbox_to_anchor=(0.5, -0.34),
               ncol=4, fontsize=FS_LEG, handletextpad=0.20, columnspacing=0.55,
               borderpad=0.2)

    # ---- (c) 物性漂移 ----
    cc = np.linspace(0.15, 2.55, 200)
    rho, cp, k, *_ = props(cc, "app3")
    rcp = rho * cp
    alpha = k / rcp
    for y, col, lab in ((rcp / rcp[-1], PAL["blue"], "$\\rho c_p$"),
                        (k / k[-1], PAL["red"], "$k$"),
                        (alpha / alpha[-1], PAL["teal"], "$\\alpha$")):
        axc.plot(cc, y, "-", color=col, lw=1.3, label=lab)
    axc.axhline(1.0, color=GREY["mid"], lw=0.6, ls=(0, (3, 2)))
    axc.set_xlim(2.55, 0.15)
    axc.set_ylim(0.30, 1.85)
    axc.legend(loc="upper left", fontsize=FS_LEG, ncol=3, handlelength=1.2,
               columnspacing=0.8)
    axc.set_xlabel("含水率 $C$ (kg/kg)", fontsize=FS_LABEL)
    axc.set_ylabel("物性（以 $C_0$ 归一）", fontsize=FS_LABEL)
    save_gated(fig, "fig_q2_coupling")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 图 2  能量方程形式
# ---------------------------------------------------------------------------
def _shades():
    """6 条剖面曲线的由深至浅配色 (对应 t=0.5..3.0 h)。"""
    return [plt.cm.viridis(0.02 + 0.80 * k / 5) for k in range(6)]


def fig_mechanism(v, en, tt, T, d):
    """图 2: 能量方程形式 (2x2)。合并原 fig_q2_energy_form 与 fig_q2_latent。"""
    fig = plt.figure(figsize=(7.1, 3.7))
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.975, bottom=0.115,
                          top=0.925, hspace=0.62, wspace=0.32)
    ax = panel(fig, gs, 0, 0, "a", "(a) 两种写法的温度演化")
    axb = panel(fig, gs, 0, 1, "b", "(b) 能量源项量级")
    axc = panel(fig, gs, 1, 0, "c", "(c) 表面热流分解")
    axd = panel(fig, gs, 1, 1, "d", "(d) 极值越界量")

    # ---- (a) 两种写法的温度演化 ----
    t = v["o_nc"]["t_snap"] / 3600.0
    Tnc, Tcs = v["o_nc"]["T_snap"] - 273.15, v["o_cs"]["T_snap"] - 273.15
    series = [(Tnc[:, 0], "-", PAL["blue"], 1.5, "非保守：中心"),
              (Tnc[:, -1], "--", PAL["blue"], 1.1, "非保守：表面"),
              (Tcs[:, 0], "-", PAL["red"], 1.5, "守恒：中心"),
              (Tcs[:, -1], "--", PAL["red"], 1.1, "守恒：表面")]
    for y, ls, c, lw, lab in series:
        ax.plot(t, y, ls, color=c, lw=lw, label=lab)
    ax.axhline(50.246, color=GREY["dark"], lw=0.7, ls=(0, (4, 2)))
    ax.set_xlim(0, 3)
    ax.set_ylim(26, 70)
    ax.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    ax.set_ylabel("温度 $T$ ($^\\circ$C)", fontsize=FS_LABEL)
    pts = (np.concatenate([t, t, t, t]),
           np.concatenate([y for y, *_ in series]))
    place_anno(ax, pts, f"$t=10800$ s 差 {v['dT']:.2f} K", prefer="upper left")
    # 图例必须在坐标区**内部**: 画布压到 3.7 in 后, 放在轴外的图例框会与下排
    # 面板的标题相撞 (碰撞门报 5 处 FAIL). 右下角在 t>1.5 h 后是空的
    # (所有曲线都升到 49 degC 以上), 故取 lower right.
    ax.legend(loc="lower right", fontsize=6.0, ncol=2, handlelength=1.2,
              columnspacing=0.8, labelspacing=0.22, borderpad=0.22)

    # ---- (b) 能量源项量级 ----
    items = [("主项", en["main"], PAL["blue"], None),
             ("伪源项", en["Sfalse"], PAL["red"], en["Spct"]),
             ("残差项", en["R0"], PAL["teal"], en["R0pct"]),
             ("对流项", en["cJgradT"], GREY["mid"], None)]
    xs = list(range(len(items)))
    axb.bar(xs, [abs(it[1]) for it in items], color=[it[2] for it in items],
            width=0.55)
    axb.set_yscale("log")
    axb.set_xticks(xs)
    axb.set_xticklabels([it[0] for it in items], fontsize=6.4, rotation=45,
                        ha="right")
    for x, (_nm, vv, _c, pct) in zip(xs, items):
        txt = f"{vv:.3g}" if pct is None else f"{vv:.3g}|{pct:.2f}%"
        axb.text(x, abs(vv) * 1.7, txt, ha="center", fontsize=5.9, va="bottom")
    axb.set_ylim(0.3, 8e6)
    axb.set_xlim(-0.7, 3.7)
    log_ticks(axb, "y")
    axb.set_ylabel("能量源项 (W/m$^3$)", fontsize=FS_LABEL)

    # ---- (c) 表面热流分解 ----
    th = tt / 3600.0
    axc.plot(th, d["q_conv"], "-", color=PAL["blue"], lw=1.4,
             label="对流供热")
    axc.plot(th, d["q_evap"], "-", color=PAL["red"], lw=1.4, label="蒸发吸热")
    axc.plot(th, d["q_cond"], "--", color=PAL["teal"], lw=1.3, label="净导入内部")
    axc.axhline(0.0, color=GREY["mid"], lw=0.7)
    axc.set_xlim(0, 3)
    axc.set_ylim(-0.42, 4.4)
    axc.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    axc.set_ylabel("表面热流 (W/m)", fontsize=FS_LABEL)
    axc.legend(loc="upper right", fontsize=6.4, handlelength=1.4)
    place_anno(axc, (np.concatenate([th, th, th]),
                     np.concatenate([d["q_conv"], d["q_evap"], d["q_cond"]])),
               f"3 h 份额 {d['qratio_10800'] * 100:.1f} %", prefer="lower left")

    # ---- (d) 极值越界量 ----
    env_lo, env_hi = 28.0, 50.246
    over_lo = [0.0, max(0.0, env_lo - d["Tmin"]), max(0.0, env_lo - d["Tmin_off"])]
    over_hi = [0.0, max(0.0, d["Tmax"] - env_hi), max(0.0, d["Tmax_off"] - env_hi)]
    y = np.arange(3)[::-1]
    w = 0.34
    axd.barh(y + w / 2, over_lo, height=w, color=PAL["blue"])
    axd.barh(y - w / 2, over_hi, height=w, color=PAL["orange"])
    axd.set_yticks(y)
    axd.set_yticklabels(["包络", "含蒸发", "无蒸发"], fontsize=FS_TICK)
    axd.set_xlim(0, 0.016)
    axd.set_ylim(-0.85, 2.75)
    axd.set_xlabel("极值越界量 (K)", fontsize=FS_LABEL)
    axd.text(over_lo[1], y[1] + w / 2 + 0.10, f"{over_lo[1]:.4f} K",
             ha="center", fontsize=FS_ANN, color=PAL["blue"])
    axd.text(0.010, y[2] - 0.40, "越界 0.0000 K", ha="center", fontsize=FS_ANN)
    save_gated(fig, "fig_q2_mechanism")
    plt.close(fig)


def fig_results(rh, tt, T, C, d):
    """图 3: 温度场与水分场结果 (2x3)。

    排版要点 (均为碰撞门的要求):
      * 画布 7.4x5.4 in, wspace 0.72 —— 六面板下留给 y 刻度标签与色条的余量;
      * 每条轴的 y 主刻度限为 4 个, 避免刻度标签互相重叠;
      * 色条标签用短式 ($T$/°C, $C$/(kg/kg)) 且字号 7.0, 不与相邻面板的刻度相撞;
      * 面板内的说明一律用不带箭头的短语, 并放在曲线未经过的角落 (或移入图题).
    """
    fig = plt.figure(figsize=(7.4, 4.6))
    gs = fig.add_gridspec(2, 3, left=0.070, right=0.975, bottom=0.105,
                          top=0.930, hspace=0.62, wspace=0.72)
    axT = panel(fig, gs, 0, 0, "a", "(a) 温度场 $T(r,t)$")
    axP = panel(fig, gs, 0, 1, "b", "(b) 温度径向剖面")
    axS = panel(fig, gs, 0, 2, "c", "(c) 径向温差衰减")
    axC = panel(fig, gs, 1, 0, "d", "(d) 水分场与干燥前沿")
    axQ = panel(fig, gs, 1, 1, "e", "(e) 水分径向剖面")
    axE = panel(fig, gs, 1, 2, "f", "(f) 分层演化与失水率")

    th = tt / 3600.0
    idx = [t - 1 for t in T_TAB_S]
    sh = _shades()

    def few(ax, n=4, which="y"):
        axis = ax.yaxis if which == "y" else ax.xaxis
        axis.set_major_locator(matplotlib.ticker.MaxNLocator(n, prune=None))

    # ---- (a) 温度时空热图 ----
    m = axT.pcolormesh(th, rh, T.T, cmap="inferno", shading="auto",
                       vmin=T.min(), vmax=T.max())
    # 色条标签的基号取 7.6 pt: mathtext 上标只有基号的约 0.70 倍, 故 $^\circ$ 为
    # 5.32 pt, 满足 5 pt 的字形下限 (基号 7.0 pt 时上标只有 4.9 pt, 会被判 FAIL).
    colorbar(fig, m, axT, "$T$ / ($^\\circ$C)", fs=7.6)
    axT.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    axT.set_ylabel("到中心距离 $r$ (cm)", fontsize=FS_LABEL)
    few(axT, 4)

    # ---- (b) 温度剖面 ----
    for k, i in enumerate(idx):
        axP.plot(rh, T[i], "-", color=sh[k], lw=1.2)
    axP.set_xlim(0, 2)
    axP.set_ylim(31, 51)
    axP.set_xlabel("$r$ (cm)", fontsize=FS_LABEL)
    axP.set_ylabel("温度 $T$ ($^\\circ$C)", fontsize=FS_LABEL)
    few(axP, 4)
    # 剖面 T(r) 沿 r 单调不减, 左上三角是唯一稳定空白的区域; 但仅按"角落"放仍会
    # 被 0.5 h 那条曲线穿过, 故用 place_anno 按全部 6 条曲线的实际点集避让.
    place_anno(axP, (np.tile(rh, len(idx)), np.concatenate([T[i] for i in idx])),
               "0.5$\\to$3.0 h 由深至浅", prefer="upper left")

    # ---- (c) 径向温差衰减 ----
    axS.plot(th, d["spanT"], "-", color=PAL["blue"], lw=1.4)
    xf = np.linspace(1.0, 3.0, 60)
    axS.plot(xf, d["spanT"][3599] * np.exp(-(xf * 3600 - 3600) / d["tau_dT"]),
             "--", color=PAL["orange"], lw=1.1,
             label=f"$\\tau$={d['tau_dT']:.0f} s")
    axS.axhline(0.0, color=GREY["mid"], lw=0.6)
    axS.set_xlim(0, 3)
    axS.set_ylim(-0.15, 4.3)
    axS.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    axS.set_ylabel("$T(R)-T(0)$ (K)", fontsize=FS_LABEL)
    few(axS, 4)
    axS.legend(loc="upper right", fontsize=6.4)
    # 避让点集必须同时含实测曲线、拟合虚线与 0 线, 否则文字会与后两者相交
    place_anno(axS,
               (np.concatenate([th, xf, th]),
                np.concatenate([d["spanT"],
                                d["spanT"][3599] * np.exp(
                                    -(xf * 3600 - 3600) / d["tau_dT"]),
                                np.zeros_like(th)])),
               f"峰值 {d['spanT_max']:.3f} K", prefer="lower left")

    # ---- (d) 水分时空热图 + 前沿 ----
    m2 = axC.pcolormesh(th, rh, C.T, cmap="viridis", shading="auto",
                        vmin=C.min(), vmax=C.max())
    colorbar(fig, m2, axC, "$C$ / (kg/kg)", fs=7.6)
    rf = d["rfront"]
    ok = np.isfinite(rf)
    axC.plot(th[ok], rf[ok], color="white", lw=1.2, ls=(0, (3, 2)))
    if d["rfront_center_s"] > 0:
        axC.plot([d["rfront_center_s"] / 3600.0], [0.0], "o", ms=3.2,
                 mfc="white", mec=PAL["red"], mew=0.9)
    axC.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    axC.set_ylabel("到中心距离 $r$ (cm)", fontsize=FS_LABEL)
    few(axC, 4)
    # 前沿说明移入图题 (面板内已被色场与虚线占满, 任何文字都会与描边相交)

    # ---- (e) 水分剖面 ----
    for k, i in enumerate(idx):
        axQ.plot(rh, C[i], "-", color=sh[k], lw=1.2)
    axQ.set_xlim(0, 2)
    axQ.set_ylim(0.9, 3.1)
    axQ.set_xlabel("$r$ (cm)", fontsize=FS_LABEL)
    axQ.set_ylabel("水分 $C$ (kg/kg)", fontsize=FS_LABEL)
    few(axQ, 4)
    axQ.text(0.97, 0.955, "0.5$\\to$3.0 h 由深至浅", transform=axQ.transAxes,
             fontsize=6.0, va="top", ha="right")

    # ---- (f) 分层演化与失水率 ----
    axE.plot(th, d["Cbar"], "-", color=PAL["red"], lw=1.4, label="$\\bar C$")
    axE.plot(th, C[:, 0], "-", color=PAL["blue"], lw=1.1, label="中心")
    axE.plot(th, C[:, -1], "-", color=PAL["orange"], lw=1.1, label="表面")
    axE.set_xlim(0, 3)
    axE.set_ylim(0.3, 3.15)
    ax3 = twin(axE)
    ax3.plot(th, d["loss_pct"], ":", color=PAL["teal"], lw=1.2)
    ax3.set_ylabel("失水率 (%)", fontsize=6.6, color=PAL["teal"])
    ax3.tick_params(axis="y", colors=PAL["teal"], labelsize=6.4)
    ax3.set_ylim(0, 74)
    ax3.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
    ax3.spines["right"].set_visible(True)
    ax3.spines["right"].set_color(PAL["teal"])
    axE.set_xlabel("时间 $t$ (h)", fontsize=FS_LABEL)
    axE.set_ylabel("水分 $C$ (kg/kg)", fontsize=FS_LABEL)
    few(axE, 4)
    # 图例移到坐标区外的下部, 三条浓度曲线与失水率点线扫过整个面板
    axE.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), fontsize=6.4,
               ncol=3, handlelength=1.2, columnspacing=0.8, labelspacing=0.25,
               borderpad=0.25)
    save_gated(fig, "fig_q2_results")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-runs", action="store_true", help="跳过重算算例")
    args = ap.parse_args()
    setup()
    matplotlib.rcParams.update({
        "font.size": FS_ANN, "axes.titlesize": FS_TITLE, "axes.labelsize": FS_LABEL,
        "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
        "legend.fontsize": FS_LEG,
    })
    # SimHei 缺 U+2212: 在回退链末尾追加 DejaVu Sans (只影响缺失字形)
    fam = list(matplotlib.rcParams["font.sans-serif"])
    if "DejaVu Sans" not in fam:
        matplotlib.rcParams["font.sans-serif"] = fam + ["DejaVu Sans"]

    os.makedirs(OUT, exist_ok=True)
    open_log(os.path.join(OUT, "q2_figures_console.log"))
    h = _GlyphWatch()
    logging.getLogger("matplotlib.mathtext").addHandler(h)
    _GLYPH.append(h)
    say(f"运行: python src/q2_figures.py{' --no-runs' if args.no_runs else ''}")
    say(f"字体回退链: {matplotlib.rcParams['font.sans-serif']}")
    say(f"字号: 注释/图例 {FS_ANN} pt, 刻度 {FS_TICK} pt, 轴标签 {FS_LABEL} pt, "
        f"标题 {FS_TITLE} pt (mathtext 上下标约 0.70x)")

    rh, tt, T, C = load_result2()
    say(f"result2.xlsx: T/C {T.shape}, 半径 {rh[0]}..{rh[-1]} cm")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    regp = read_registry(os.path.join(OUT, "registry_q2_production.csv"))
    regv = read_registry(os.path.join(OUT, "registry_q2_verify.csv"))
    rege = read_registry(os.path.join(OUT, "registry_q2_energy.csv"))
    reve = read_registry(os.path.join(OUT, "registry_q2_energy_verified.csv"))
    radd = read_registry(os.path.join(OUT, "registry_q2_model.csv"))

    say("\n[A] 派生量")
    d = derive(rh, tt, T, C, env, regv)
    say(f"  W(10800)={d['W'][-1]:.6e}  注册表 P27={regp['P27_W_end']:.6e}"
        f"  相对差={abs(d['W'][-1]-regp['P27_W_end'])/regp['P27_W_end']:.2e}")
    say(f"  通量收支校核相对差={d['Wbal_rel']:.3e}")
    say(f"  Cbar(10800)={d['Cbar_10800']:.7f}  失水={d['loss_10800']:.4f} %")
    say(f"  干燥前沿: 首发 t={d['rfront_first_s']} s, 到中心 t={d['rfront_center_s']} s")
    say(f"  温差峰值 {d['spanT_max']:.4f} K @ {d['spanT_max_t']} s; "
        f"tau={d['tau_dT']:.1f} s (R2={d['tau_dT_ss']:.5f})")
    say(f"  q_evap/q_conv: 0.5h={d['qratio_1800']*100:.2f}%  "
        f"1h={d['qratio_3600']*100:.2f}%  3h={d['qratio_10800']*100:.2f}%")

    say("\n[B] 重算: 能量方程两种形式")
    v = run_variants(env, do_runs=not args.no_runs)
    say(f"  复现 V11 max|dT| = {v['dT']:.6f} K (注册表 {regv['V11_dT']:.6f})")
    say(f"  中心温度 t=10800: 非保守 {v['T0_nc']:.4f} C, 守恒 {v['T0_cs']:.4f} C")
    eig = jacobian_pattern()
    say(f"  Jacobian M={eig['M']}: nnz={eig['nnz']}/{eig['n2']**2} "
        f"({eig['dens']*100:.2f} %), 带宽 {eig['bw']}, 块 {eig['blk']}")
    # 能量源项: 一律取自 q2_energy_verify_sympy.py 的独立复算注册表 (口径显式声明),
    # 不用 registry_q2_energy.csv 的旧值 —— 后者含一处量纲不一致的算式.
    en = dict(main=reve["EV_main"], Sfalse=reve["EV_Sfalse"], R0=reve["EV_R0"],
              Spct=reve["EV_Sfalse_pct"], R0pct=reve["EV_R0_pct"],
              ratio=reve["EV_ratio"], cJgradT=rege["EC_cJgradT"])
    say(f"  能量源项 (EV 注册表): 主项 {en['main']:.4f}, 伪源项 {en['Sfalse']:.4f} "
        f"({en['Spct']:.2f}%), 残差项 {en['R0']:.4f} ({en['R0pct']:.4f}%), "
        f"|S|/|R0| = {en['ratio']:.2f}")

    # ---------------- 注册表 ----------------
    add("FG_V11_dT", "复算: 能量方程两种形式的温度最大差", v["dT"], "K", "复现注册表 V11")
    add("FG_V11_dC", "复算: 能量方程两种形式的水分最大差", v["dC"], "kg/kg", "复现注册表 V11")
    add("FG_T0_nc", "非保守形式 t=10800 s 中心温度", v["T0_nc"], "degC")
    add("FG_T0_cs", "守恒形式 t=10800 s 中心温度", v["T0_cs"], "degC")
    add("FG_TR_nc", "非保守形式 t=10800 s 表面温度", v["TR_nc"], "degC")
    add("FG_TR_cs", "守恒形式 t=10800 s 表面温度", v["TR_cs"], "degC")
    add("FG_Edef_nc", "非保守形式能量收支缺口", v["Edef_nc"], "J/m (per 2pi)")
    add("FG_Edef_cs", "守恒形式能量收支缺口", v["Edef_cs"], "J/m (per 2pi)")
    add("FG_Emain", "能量方程主项量级 (EV 注册表)", en["main"], "W/m^3")
    add("FG_Sfalse", "守恒形式伪源项 (EV 注册表)", en["Sfalse"], "W/m^3")
    add("FG_Sfalse_pct", "伪源项占主项的比例", en["Spct"], "%")
    add("FG_R0", "严格形式残差项 (EV 注册表)", en["R0"], "W/m^3")
    add("FG_R0_pct", "残差项占主项的比例", en["R0pct"], "%")
    add("FG_S_over_R0", "伪源项与残差项之比", en["ratio"], "-")
    add("FG_jac_M", "Jacobian 示例网格数", eig["M"], "-", "结构")
    add("FG_jac_n", "Jacobian 未知量个数 2(M+1)", eig["n2"], "-", "结构")
    add("FG_jac_nnz", "Jacobian 非零元个数", eig["nnz"], "-", "求解器组装还原")
    add("FG_jac_dens", "Jacobian 非零元占比", eig["dens"] * 100.0, "%", "结构")
    add("FG_jac_bw", "Jacobian 带宽", eig["bw"], "-", "结构")
    for kk, vv in eig["blk"].items():
        add(f"FG_jac_n{kk}", f"Jacobian {kk} 块非零元", vv, "-", "结构")
    it = v.get("iters")
    if it is not None:
        add("FG_it_nsteps", "Newton 迭代统计步数", int(it.size), "-", "迭代统计")
        add("FG_it_mean", "Newton 平均迭代次数", float(it.mean()), "-", "迭代统计")
        add("FG_it_max", "Newton 最大迭代次数", int(it.max()), "-", "迭代统计")
    for t in T_TAB_S:
        add(f"FG_qconv_{t}", f"t={t} s 对流供热 (per 2pi)", d[f"qconv_{t}"], "W/m")
        add(f"FG_qevap_{t}", f"t={t} s 蒸发吸热 (per 2pi)", d[f"qevap_{t}"], "W/m")
        add(f"FG_qcond_{t}", f"t={t} s 净导入内部热流 (per 2pi)", d[f"qcond_{t}"], "W/m")
        add(f"FG_qdrive_{t}", f"t={t} s 表面对流驱动力 T_inf-T_R", d[f"drv_{t}"], "K")
        add(f"FG_qratio_{t}", f"t={t} s q_evap/q_conv", d[f"qratio_{t}"], "-")
        add(f"FG_Cbar_{t}", f"t={t} s 体积平均含水率", d[f"Cbar_{t}"], "kg/kg", "梯形求积")
        add(f"FG_loss_{t}", f"t={t} s 累计失水率", d[f"loss_{t}"], "%", "梯形求积")
        add(f"FG_spanT_{t}", f"t={t} s 温度径向跨距", d[f"spanT_{t}"], "K")
        add(f"FG_spanC_{t}", f"t={t} s 水分径向跨距", d[f"spanC_{t}"], "kg/kg")
    add("FG_qconv_decay", "q_conv 由 0.5 h 到 3 h 的衰减倍数", d["qconv_decay"], "-")
    add("FG_qevap_drop", "q_evap 由 0.5 h 到 3 h 的降幅",
        (1.0 - d["q_evap"][-1] / d["q_evap"][1799]) * 100.0, "%")
    add("FG_qratio_pct_1800", "t=1800 s 蒸发占对流供热的比例", d["qratio_1800"] * 100, "%")
    add("FG_qratio_pct_10800", "t=10800 s 蒸发占对流供热的比例", d["qratio_10800"] * 100, "%")
    add("FG_CR_over_Cinf", "3 h 表面含水率与环境含水率之比",
        d["CR_end_m"] / d["Cin"][-1], "-")
    add("FG_Cfront", "干燥前沿判别值 C = 0.9*C0", C_FRONT, "kg/kg", "解析",
        f"C_FRONT = 0.9 * 2.55")
    add("FG_n_ratio_ok", "蒸发份额判据成立的采样点数 (驱动力 >= 0.05 K)", d["n_ratio_ok"],
        "-", "判据")
    add("FG_n_ratio_bad", "蒸发份额判据不成立的采样点数", d["n_ratio_bad"], "-", "判据")
    add("FG_drive_min", "驱动力绝对值的最小值", d["q_drive_min"], "K", "附件1 分辨率说明")
    add("FG_ratio_raw_max", "未加掩码时 q_evap/q_conv 的最大值 (病态放大)",
        d["q_ratio_raw_max"], "-", "判据", "说明瞬时比值不可直接用作判据")
    add("FG_W0", "初始总水量 W(0) (per 2pi)", d["W0"], "kg/kg*m^2", "精确 = R^2 C0/2")
    add("FG_wq_sum", "求积权之和 (应 = R^2/2)", d["wq_sum"], "m^2", "结构性校验")
    add("FG_W_end", "t=10800 s 总水量 (由态求积)", d["W"][-1], "kg/kg*m^2")
    add("FG_W_flux_end", "t=10800 s 总水量 (由通量收支)", d["W_flux"][-1], "kg/kg*m^2",
        "独立校核")
    add("FG_Wbal_rel", "态求积与通量收支的相对差", d["Wbal_rel"], "-", "水量守恒校核")
    add("FG_rfront_first_s", "干燥前沿首次出现时刻", d["rfront_first_s"], "s")
    add("FG_rfront_center_s", "干燥前沿到达中心时刻", d["rfront_center_s"], "s")
    add("FG_spanT_max", "径向温差峰值", d["spanT_max"], "K")
    add("FG_spanT_max_t", "径向温差峰值时刻", d["spanT_max_t"], "s")
    add("FG_tau_dT", "径向温差衰减时间常数 (3600~10800 s 拟合)", d["tau_dT"], "s")
    add("FG_tau_dT_R2", "温差衰减拟合决定系数", d["tau_dT_ss"], "-")
    add("FG_Ts_min", "表面温度全程最小值", d["Ts_min"], "degC")
    add("FG_Ts_min_t", "表面温度最小值时刻", d["Ts_min_t"], "s")
    add("FG_Ts_dip", "表面温度低于初温的幅度", d["Ts_dip"], "K")
    add("FG_Ts_recross", "表面温度回升到初温的时刻", d["Ts_recross"], "s")
    add("FG_Ts_180", "t=180 s 表面温度 (说明为何面板窗口取 40 s)", d["Ts_180"], "degC")
    add("FG_Ts_win_min", "0~40 s 窗口内表面温度最小值", d["Ts_win_min"], "degC")
    add("FG_Ts_win_max", "0~40 s 窗口内表面温度最大值", d["Ts_win_max"], "degC")
    add("FG_alpha_gain", "alpha 由 C=2.55 到 0.15 的升幅",
        (radd["A_alpha_0.15"] / radd["A_alpha_2.55"] - 1) * 100.0, "%", "由附录3")
    add("FG_k_drop", "k 由 C=2.55 到 0.15 的降幅",
        (1 - radd["A_k_0.15"] / radd["A_k_2.55"]) * 100.0, "%", "由附录3")
    add("FG_rho_cp_drop", "rho*cp 由 C=2.55 到 0.15 的降幅", radd["A_rcp_drop"], "%",
        "由附录3")
    add("FG_Tmax_off", "无蒸发对照的温度上界", d["Tmax_off"], "degC", "注册表 V8")
    add("FG_Tmin_off", "无蒸发对照的温度下界", d["Tmin_off"], "degC", "注册表 V4")
    with open(os.path.join(OUT, "registry_q2_figures.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    say(f"\n注册表: outputs/registry_q2_figures.csv ({len(REG)} 行)")

    # ---------------- 出图 ----------------
    say("\n[C] 绘图")
    fig_coupling(eig)
    fig_mechanism(v, en, tt, T, d)
    fig_results(rh, tt, T, C, d)

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
