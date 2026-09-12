# -*- coding: utf-8 -*-
r"""
问题一图件 (fig_q1_scheme / fig_q1_results) 的公共导出与渲染前护栏.

包含:
  * save_gated()          —— 对齐门 (nature-figure/audit_panel_alignment.py) + fig_style.save
  * assert_finite()       —— 画布上任何非有限坐标都会让 bbox_inches='tight' 把页面撑爆
                             (本项目曾出现 52437 pt 的页面), 导出前必须拦住
  * assert_data_in_limits() —— 每条数据曲线必须落在其坐标轴范围内 (硬编码 ylim 把曲线
                             裁掉并使曲线冲进标题, 是本项目已发生过的缺陷)
  * few_ticks()           —— 2x3 网格下每轴主刻度限为 4 个, 避免刻度标签互相重叠
  * empty_spot()/place_anno() —— 注释只落在"数据未经过"的空白矩形内 (禁用目测定位)
  * declutter()           —— 一组一维标签的最小间距展开 (曲线右端时刻标签需要)

用法:
    from q1_fig_common import save_gated, place_anno, few_ticks
    save_gated(fig, "fig_q1_results", exclude_axes=EXCLUDE)

运行环境: Windows + python; 对齐门脚本位于 nature-figure skill 的 scripts/ 下, 缺失时
本模块把 HAVE_GATE 置 False 并在 save_gated 中显式报错 (不允许静默跳过).
"""

from __future__ import annotations

import os
import sys

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import FIGDIR, save  # noqa: E402

SKILL_SCRIPTS = r"C:\Users\极光\.dsh\research-skills\nature-figure\scripts"
if os.path.isdir(SKILL_SCRIPTS):
    sys.path.insert(0, SKILL_SCRIPTS)
try:
    from audit_panel_alignment import require_matplotlib_panel_alignment
    HAVE_GATE = True
    GATE_ERR = ""
except Exception as exc:  # noqa: BLE001
    HAVE_GATE = False
    GATE_ERR = str(exc)

CMD = "python src/q1_fig_results.py"


# ---------------------------------------------------------------------------
# 渲染前护栏
# ---------------------------------------------------------------------------
def assert_finite(fig):
    """画布上不得出现 inf/NaN 坐标 (它们是页面被撑爆的根因)."""
    for k, ax in enumerate(fig.axes):
        for j, ln in enumerate(ax.lines):
            for name, arr in (("x", ln.get_xdata()), ("y", ln.get_ydata())):
                a = np.asarray(arr, dtype=float)
                if a.size and not np.all(np.isfinite(a)):
                    raise AssertionError(
                        f"axes[{k}] line[{j}] 的 {name} 含非有限值 "
                        f"(nan={int(np.isnan(a).sum())}, inf={int(np.isinf(a).sum())})")
        for j, im in enumerate(ax.images):
            a = np.asarray(im.get_array(), dtype=float)
            if a.size and not np.all(np.isfinite(a)):
                raise AssertionError(f"axes[{k}] image[{j}] 含非有限值")
        for j, p in enumerate(ax.patches):
            v = p.get_path().vertices if hasattr(p, "get_path") else None
            if v is not None and v.size and not np.all(np.isfinite(v)):
                raise AssertionError(f"axes[{k}] patch[{j}] 顶点含非有限值")


def assert_data_in_limits(fig):
    """不变量: 每条数据曲线都必须落在其坐标轴范围内.

    只按视觉设置 ylim 很容易把曲线尾段裁掉, 使曲线冲出面板并与标题相交; 这里逐一检查.
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


def few_ticks(ax, n=4, which="y"):
    """2x3 网格下每轴主刻度限为 n 个 (六面板曾因刻度过密互相重叠)."""
    axis = ax.yaxis if which == "y" else ax.xaxis
    axis.set_major_locator(matplotlib.ticker.MaxNLocator(n, prune=None))


# ---------------------------------------------------------------------------
# 注释定位
# ---------------------------------------------------------------------------
def empty_spot(ax, pts_xy, box_wh, prefer="upper right"):
    """在轴分数坐标里找一个不含任何数据点的矩形位置.

    返回 (x, y) —— 文本左下角; 调用方必须带 transform=ax.transAxes.
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


def place_anno(ax, pts_xy, text, prefer="upper right", fs=None, linespacing=1.5):
    """量出真实文字尺寸 -> 在空白处落笔 -> 校验不溢出坐标区.

    只按"估算宽度"扫描会在文字实际溢出时静默失败 (会溢到相邻面板的刻度标签上),
    所以这里以渲染后的 bounding box 为准.

    linespacing 默认 1.5: 多行文字在 1.2 行距下, 中日韩字形的 em 框会互相重叠
    (实测两行文本框重叠 10.6%), 被碰撞门判 text-text FAIL.
    """
    fs = 7.4 if fs is None else fs
    fig = ax.figure
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    probe = ax.text(0.0, 0.0, text, fontsize=fs, transform=ax.transAxes, va="bottom",
                    linespacing=linespacing)
    bb = probe.get_window_extent(ren)
    ab = ax.get_window_extent(ren)
    probe.remove()
    w = bb.width / ab.width + 0.04
    h = bb.height / ab.height + 0.04
    if w >= 1.0 or h >= 1.0:
        raise RuntimeError(f"注释比坐标区还宽/高 ({w:.2f}, {h:.2f}): {text[:34]!r}")
    cx, cy = empty_spot(ax, pts_xy, (w, h), prefer=prefer)
    art = ax.text(cx, cy, text, transform=ax.transAxes, fontsize=fs, va="bottom",
                  linespacing=linespacing)
    fig.canvas.draw()
    nb = art.get_window_extent(ren)
    if nb.x0 < ab.x0 - 1.0 or nb.x1 > ab.x1 + 1.0:
        raise RuntimeError(f"注释横向溢出坐标区: {text[:34]!r} "
                           f"(文字 {nb.x0:.0f}..{nb.x1:.0f} vs 坐标区 {ab.x0:.0f}..{ab.x1:.0f})")
    return art


def declutter(values, min_gap):
    """一维标签的最小间距展开, 且**位移最小** (保序 L2 投影 = PAVA).

    曲线右端的时刻标签在压缩后的坐标轴上会互相重叠 (本项目 6 面板图的已知缺陷).
    朴素写法"逐对把过近的两端各推开一半"会沿链式传播一路累积: 实测把最上方标签
    推离其曲线端点 0.71 data 单位 (轴高的 48%), 标签与曲线失去对应关系.
    这里改为求解 min Σ(y_i - v_i)^2  s.t. y_{i+1} - y_i >= min_gap 的保序回归,
    用 PAVA (pool adjacent violators) 精确求解, 得到位移最小的合法排布.

    参数 values 不必有序; 内部按值升序处理后再还原原顺序.
    """
    v = np.asarray(values, dtype=float)
    n = v.size
    if n < 2:
        return v.copy()
    order = np.argsort(v, kind="stable")
    s = v[order]
    z = s - min_gap * np.arange(n)          # 约束化为 z 非降
    lvl: list[float] = []
    wt: list[int] = []
    for x in z:
        lvl.append(float(x)); wt.append(1)
        while len(lvl) > 1 and lvl[-2] > lvl[-1]:
            x2, w2 = lvl.pop(), wt.pop()
            x1, w1 = lvl.pop(), wt.pop()
            lvl.append((x1 * w1 + x2 * w2) / (w1 + w2)); wt.append(w1 + w2)
    fit = np.concatenate([np.full(w, x) for x, w in zip(lvl, wt)])
    y = fit + min_gap * np.arange(n)
    out = np.empty(n, dtype=float)
    out[order] = y
    return out


# ---------------------------------------------------------------------------
# 导出
# ---------------------------------------------------------------------------
def save_gated(fig, name, *, exclude_axes=(), exemptions=None,
               row_groups=None, column_groups=None,
               tolerance_pt=1.5, gutter_tolerance_pt=1.5):
    """对齐门 -> fig_style.save -> 页面尺寸校验.

    拒绝: 对齐门 fail (exit 1) 与 NOT AUDITABLE (exit 2). WARN 在 strict 下同样阻断.
    """
    assert_finite(fig)
    assert_data_in_limits(fig)
    os.makedirs(FIGDIR, exist_ok=True)
    base = os.path.join(FIGDIR, name)
    if not HAVE_GATE:
        raise RuntimeError(f"对齐门脚本不可用, 拒绝导出 ({GATE_ERR})")
    rep = require_matplotlib_panel_alignment(
        fig, json_out=f"{base}.alignment.json",
        overlay_svg=f"{base}.alignment.svg",
        tolerance_pt=tolerance_pt, gutter_tolerance_pt=gutter_tolerance_pt,
        exclude_axes=list(exclude_axes), strict=True,
        exemptions=list(exemptions or ()),
        row_groups=row_groups, column_groups=column_groups)
    s = rep["summary"]
    print(f"  [对齐门] {name}: {rep['verdict']} (比较 {s['comparisons']} 组, "
          f"fail={s['fail']}, warn={s['warn']}, 豁免={s['exemptions']})")
    save(fig, name)
    # 不变量: 导出页面尺寸必须与画布同量级 (inf/NaN 曾把页面撑到 52437 pt)
    import fitz
    doc = fitz.open(f"{base}.pdf")
    w_pt, h_pt = doc[0].rect.width, doc[0].rect.height
    doc.close()
    fw, fh = (v * 72 for v in fig.get_size_inches())
    if not (0.8 * fw <= w_pt <= 1.6 * fw and 0.8 * fh <= h_pt <= 1.6 * fh):
        raise AssertionError(
            f"{name}: 页面尺寸异常 {w_pt:.1f}x{h_pt:.1f} pt (画布 {fw:.1f}x{fh:.1f} pt)")
    print(f"  [页面] {name}: {w_pt:.1f} x {h_pt:.1f} pt "
          f"({w_pt/72:.3f} x {h_pt/72:.3f} in); 画布 {fw/72:.2f} x {fh/72:.2f} in")
    return rep
