# -*- coding: utf-8 -*-
"""
q4_produce.py -- 问题四生产求解与结果产出.

产出:
  outputs/result4.xlsx        按模板 (Sheet1): A列时间(60 s), 第1行半径 0..2.0 cm + 药材表面
  outputs/table6_moisture.csv 表6: 每 6 h x {0,0.5,1.0,1.5, 药材表面}
  outputs/registry_q4.csv     数字注册表 (供对账)
  outputs/q4_production.log   运行日志

生产配置: M=200, rtol=1e-9, atol=(1e-6 K, 1e-9 kg/kg), max_step=3600 s,
          解析稀疏 Jacobian, 附录4 物性, R(t) 取附件2 PCHIP.
"""

from __future__ import annotations

import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (solve_q4, sample_q4, crossing_times_q4, Q4Radius,   # noqa: E402
                      load_attachment2, P4, PROD_M, PROD_RTOL, PROD_ATOL_T,
                      PROD_ATOL_C, PROD_MAX_STEP, T_MAX, CSTAR)
from q3_solve import TBAR_C, CBAR, TAU                                   # noqa: E402
from q2_solve import C0, R as R0, HM                                     # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
LOG = []


def say(m):
    print(m, flush=True)
    LOG.append(m)


def fmt4(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v), 4)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    say("=" * 78)
    say("问题四生产求解 (q4_produce.py)")
    say("=" * 78)
    say(f"配置: M={PROD_M}, rtol={PROD_RTOL:g}, atol=({PROD_ATOL_T:g} K, "
        f"{PROD_ATOL_C:g} kg/kg), max_step={PROD_MAX_STEP:g} s, 解析稀疏 Jacobian")
    say(f"      物性=附录4, R(t)=附件2 PCHIP, 环境: 附件1 + 平台 "
        f"({TBAR_C:.2f} degC, {CBAR:.4f}) + {TAU:g} s 过渡")
    say("")

    t0 = time.time()
    res = solve_q4(M=PROD_M)
    say(f"求解完成: t_dry = {res['t_dry']:.4f} s = {res['t_dry']/3600:.4f} h "
        f"= {res['t_dry']/86400:.4f} 天")
    say(f"          nsteps={res['nsteps']}, nfev={res['nfev']}, njev={res['njev']}, "
        f"wall={time.time()-t0:.1f} s")

    g, rad, sol = res["g"], res["rad"], res["sol"]
    t_dry = res["t_dry"]
    # 材料坐标口径取全部 21 个初始半径 (0.0~2.0, 步长 0.1) —— 初始位于 r0 处的
    # 物质点在整个过程中位于 r0*R(t)/R0, 恒在域内, 故该口径全程有定义。
    R_MAT = tuple(np.round(np.arange(0.0, 2.0 + 1e-9, 0.1), 1))
    s = sample_q4(sol, g, rad, t_dry, r_out_cm=R_MAT)
    n, M = g["n"], g["M"]
    MLsum = g["MLg"].sum()
    # t_dry 时刻的状态 (60 s 网格不含 t_dry, 末点为 60*floor(t_dry/60))
    U_dry = sol.sol(t_dry)
    C_dry = U_dry[n:]
    T_dry = U_dry[:n]
    R_dry = float(rad.R(t_dry))

    def C_at_phys(rcm):
        """t_dry 时刻、物理半径 rcm [cm] 处的含水率; 超出 R(t_dry) 记 NaN."""
        if rcm * 1e-2 > R_dry * (1.0 + 1e-12):
            return float("nan")
        return float(np.interp((rcm * 1e-2) / R_dry, g["xi"], C_dry))

    # ---------------- 表 6 ----------------
    cols5 = [0.0, 0.5, 1.0, 1.5]
    j5 = [int(np.argmin(np.abs(s["grid_cm"] - c))) for c in cols5]
    hours = np.arange(6.0, np.floor(t_dry / 3600.0 / 6.0) * 6.0 + 1e-9, 6.0)
    say("")
    say("表6  药材烘干过程的(收缩)水分浓度  [kg/kg]")
    hdr = ["时间/h"] + [f"{c:.1f}cm" for c in cols5] + ["药材表面"]
    say("  " + "".join(f"{x:>10s}" for x in hdr))
    t6 = []
    for h in hours:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        row = [h] + [s["Cg"][i, j] for j in j5] + [s["Cs"][i]]
        t6.append(row)
        say("  " + f"{h:>10.1f}" + "".join(
            f"{(('%.4f' % v) if v is not None and not np.isnan(v) else '--'):>10s}"
            for v in row[1:]))
    # 末行必须取 t = t_dry 处的状态。此前误用 60 s 网格末点 Cg[-1]
    # (= 60*n60 = 183900 s = 51.0833 h), 而标签写 t_dry, 两者相差 6.71 s;
    # 该时刻 max C = 0.15000345 > 0.15, 尚未达标。见修订 A2。
    row_dry = ([t_dry / 3600.0]
               + [C_at_phys(c) for c in cols5]
               + [float(C_dry[-1])])
    t6.append(row_dry)
    say("  " + f"{t_dry/3600.0:>10.4f}" + "".join(
        f"{(('%.4f' % v) if v is not None and not np.isnan(v) else '--'):>10s}"
        for v in row_dry[1:]) + "   <- t_dry")
    say(f"  注: 末行 t_dry = {t_dry:.4f} s = {t_dry/3600.0:.4f} h; "
        f"此时药材半径 R = {s['Rs'][-1]:.4f} cm")
    say(f"      表面列为 r = R(t) 处 (物理半径随 t 收缩), 非固定 2.0 cm")

    with open(os.path.join(OUTDIR, "table6_moisture.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["时间/h"] + [f"r={c:.1f}cm" for c in cols5] + ["药材表面"])
        for r_ in t6:
            w.writerow([f"{r_[0]:.4f}"] + [("" if (v is None or np.isnan(v)) else f"{v:.4f}")
                                           for v in r_[1:]])
    say("  写出: outputs/table6_moisture.csv")

    # ---------------- result4.xlsx ----------------
    import openpyxl
    grid = np.arange(0.0, 2.0 + 1e-9, 0.1)
    Cg = s["Cg"]                      # (n60, 21)
    Cs = s["Cs"]
    n60 = s["n60"]
    # 每行的表面值精确对应 R(t); 用 R(t) 对 0.1 cm 网格重采样
    Rt = s["Rs"] / 100.0              # m
    Cgrid = np.array(Cg)              # 已是物理半径网格
    # 表面列: 把 R(t) 处的值填到最接近的 0.1 cm 列? 否 —— 单独一列
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.cell(row=1, column=1, value="时间\\到药材中心的距离")
    for j, c in enumerate(grid):
        ws.cell(row=1, column=2 + j, value=float(round(c, 1)))
    ws.cell(row=1, column=2 + grid.size, value="药材表面")
    for i in range(n60):
        ws.cell(row=2 + i, column=1, value=int(round(s["t60"][i])))
        for j in range(grid.size):
            v = Cgrid[i, j]
            if not np.isnan(v):
                ws.cell(row=2 + i, column=2 + j, value=round(float(v), 4))
        ws.cell(row=2 + i, column=2 + grid.size, value=round(float(Cs[i]), 4))
    path_x = os.path.join(OUTDIR, "result4.xlsx")

    # ---- 补充工作表: 材料坐标口径 ----
    # 题面"到药材中心距离"随药材收缩有两种读法: (i) 当刻的物理距离 (Sheet1,
    # 超出当前表面 R(t) 的位置无定义); (ii) 物质点标签, 即该团干物质在 t=0 时
    # 的半径 (本题)。初始位于 r0 处的物质点全程位于 r0*R(t)/R0, 故该口径在
    # 21 列 0~2.0 cm 上**全程有定义、无空格**; 末列即药材表面 (初始 2.0 cm 处
    # 的物质点就是当前表面)。两表并存, 任一读法下都不缺数据。
    ws2 = wb.create_sheet("材料坐标")
    ws2.cell(row=1, column=1, value="时间\\材料点初始半径")
    for j in range(len(R_MAT)):
        hdr_j = "药材表面" if j == len(R_MAT) - 1 else float(R_MAT[j])
        ws2.cell(row=1, column=2 + j, value=hdr_j)
    matC = s["matC"]                       # (n60, 21) @ 初始半径 0.0,0.1,...,2.0
    assert matC.shape[1] == len(R_MAT), (matC.shape, len(R_MAT))
    for i in range(n60):
        ws2.cell(row=2 + i, column=1, value=int(round(s["t60"][i])))
        for j in range(len(R_MAT)):
            ws2.cell(row=2 + i, column=2 + j, value=round(float(matC[i, j]), 4))
    wb.save(path_x)
    say(f"  写出: outputs/result4.xlsx  Sheet1 物理口径 {n60} 行 x {grid.size} 列 + 表面列; "
        f"「材料坐标」表 {n60} 行 x {len(R_MAT)} 列 (0.0~2.0 cm 步长 0.1, 全程有定义; "
        f"末列=药材表面)")

    # ---------------- 关键读数 ----------------
    r_out = res["rad"].R(t_dry)
    say("")
    say("[关键读数]")
    say(f"  烘干时长 t_dry        = {t_dry:.4f} s = {t_dry/3600.0:.4f} h "
        f"= {t_dry/86400.0:.4f} 天")
    say(f"  结束半径 R(t_dry)     = {R_dry*100:.4f} cm  (R0 = {R0*100:.4f} cm, "
        f"收缩比 {R_dry*100/(R0*100):.4f})")
    say(f"  表面含水率 @ t_dry    = {C_dry[-1]:.6f} kg/kg  (C* = {CSTAR}, "
        f"高于环境平台 {CBAR} 的 {C_dry[-1]-CBAR:.4f})")
    say(f"  中心含水率 @ t_dry    = {C_dry[0]:.6f} kg/kg")
    say(f"  全场最大含水率 @ t_dry= {C_dry.max():.8f} kg/kg  (= C*, 事件定义)")
    say(f"  表面温度 @ t_dry      = {T_dry[-1]-273.15:.4f} degC")
    say(f"  全场最高温度 @ t_dry  = {T_dry.max()-273.15:.4f} degC")
    say(f"  体积平均含水率 @ t_dry= {(g['MLg']*C_dry).sum()/MLsum:.6f} kg/kg")
    say("  注: 以上均为 t = t_dry 处的状态; 60 s 网格末点 (60*floor(t_dry/60))")
    say(f"      为 {60*int(np.floor(t_dry/60))} s = {60*int(np.floor(t_dry/60))/3600:.4f} h, "
        f"该时刻 max C = {s['Cg'][-1].max() if not np.isnan(s['Cg'][-1].max()) else float('nan'):.8f}")

    # 跨 t_dry 的细网格, 使 r=0 也能定位
    t_grid = np.unique(np.concatenate([np.arange(60.0, t_dry, 60.0), [t_dry]]))
    xt, xflag = crossing_times_q4(sol, g, rad, t_dry, CSTAR,
                                  r_out_cm=(0.0, 0.5, 1.0, 1.5, 2.0), t_grid=t_grid)
    say("")
    say("[各物理半径首次达标的时刻]")
    for k, v in xt.items():
        if v is not None:
            say(f"  r = {k:.1f} cm : {v:12.1f} s = {v/3600.0:8.4f} h")
        elif xflag[k] == "out":
            t_out = min(x for x in t_grid
                        if (k * 1e-2) / float(res["rad"].R(x)) > 1.0) if k > 0 else None
            say(f"  r = {k:.1f} cm : -- 该位置在 t ≈ "
                f"{(t_out/3600.0 if t_out else float('nan')):.3f} h 收缩出域")
        else:
            say(f"  r = {k:.1f} cm : -- 全程在域内, 但 [0,t_dry] 内未降到阈值以下")

    # 材料坐标口径 (初始半径 r0 处那团物质)
    say("")
    say("[材料坐标口径] 初始半径 2.0 cm 处那团物质的物理位置与含水率")
    for h in [0.5, 1, 2, 4, 6, 12, 24, 36, 48, t_dry / 3600.0]:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        rr = s["Rs"][i] / 2.0                      # 归一化物理位置
        say(f"  t={h:8.4f} h: R={s['Rs'][i]:.4f} cm, 该物质点位于 "
            f"r={s['Rs'][i]:.4f} cm (表面), C={s['matC'][i, -1]:.4f} kg/kg")

    # ---------------- 注册表 ----------------
    reg = []
    A = reg.append
    A(("Q4_tdry_s", "烘干所需时间 t_dry", t_dry, "s", "生产解", "q4_production.log"))
    A(("Q4_tdry_h", "烘干所需时间 t_dry", t_dry / 3600.0, "h", "生产解", "q4_production.log"))
    A(("Q4_tdry_d", "烘干所需时间 t_dry", t_dry / 86400.0, "d", "生产解", "q4_production.log"))
    A(("Q4_Rend_cm", "t_dry 时药材半径", R_dry * 100.0, "cm", "生产解", "q4_production.log"))
    A(("Q4_Rend_ratio", "t_dry 时半径与初始半径之比", R_dry * 100.0 / (R0 * 100),
       "1", "生产解", "q4_production.log"))
    A(("Q4_Csurf", "t_dry 时表面含水率", C_dry[-1], "kg/kg", "生产解", "q4_production.log"))
    A(("Q4_Ccenter", "t_dry 时中心含水率", C_dry[0], "kg/kg", "生产解", "q4_production.log"))
    A(("Q4_Cmax_dry", "t_dry 时全场最大含水率 (= C*)", C_dry.max(), "kg/kg",
       "生产解", "q4_production.log"))
    A(("Q4_Cbar_dry", "t_dry 时体积平均含水率", (g["MLg"] * C_dry).sum() / MLsum,
       "kg/kg", "生产解", "q4_production.log"))
    A(("Q4_Tsurf", "t_dry 时表面温度", T_dry[-1] - 273.15, "degC", "生产解",
       "q4_production.log"))
    A(("Q4_Tmax", "t_dry 时全场最高温度", T_dry.max() - 273.15, "degC", "生产解",
       "q4_production.log"))
    # 60 s 网格末点的状态 (与 t_dry 不同, 保留以供追溯; 表 6 末行不用它)
    _i60 = -1
    A(("Q4_Ccenter_60s", "60 s 网格末点的中心含水率", s["Cg"][_i60, 0], "kg/kg",
       "诊断", "q4_production.log"))
    A(("Q4_t60_last", "60 s 网格末点时刻", s["t60"][_i60], "s", "诊断",
       "q4_production.log"))
    A(("Q4_nsteps", "BDF 步数", float(res["nsteps"]), "1", "生产解", "q4_production.log"))
    A(("Q4_wall", "求解耗时", res["wall"], "s", "生产解", "q4_production.log"))
    A(("Q4_n60", "result4.xlsx 数据行数", float(n60), "1", "生产解", "q4_production.log"))
    A(("Q4_M", "空间节点数", float(PROD_M), "1", "设置", "q4_production.log"))
    A(("Q4_rtol", "相对容限", PROD_RTOL, "-", "设置", "q4_production.log"))
    A(("Q4_max_step", "步长上界", PROD_MAX_STEP, "s", "设置", "q4_production.log"))
    A(("Q4_Tbar", "恒温平台环境温度", TBAR_C, "degC", "环境", "q3_solve.TBAR_C"))
    A(("Q4_Cbar", "恒温平台环境水分浓度", CBAR, "kg/kg", "环境", "q3_solve.CBAR"))
    A(("Q4_tau", "环境过渡段长度", TAU, "s", "环境", "q3_solve.TAU"))
    A(("Q4_Cstar", "烘干达标阈值", CSTAR, "kg/kg", "题面", "docs/A题.md"))
    for c in cols5:
        i = len(hours) - 1
        j = int(np.argmin(np.abs(s["grid_cm"] - c)))
        A((f"Q4_T6_last_r{c:g}", f"表6 末行(24h前最后一整6h) r={c} cm 含水率",
           s["Cg"][i, j], "kg/kg", "表6", "q4_production.log"))
    for h in hours:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        A((f"Q4_T6_Csurf_{h:g}h", f"表6 t={h:g} h 表面含水率", Cs[i], "kg/kg",
           "表6", "q4_production.log"))
        for c in cols5:
            j = int(np.argmin(np.abs(s["grid_cm"] - c)))
            A((f"Q4_T6_{h:g}h_r{c:g}", f"表6 t={h:g} h r={c} cm 含水率",
               s["Cg"][i, j], "kg/kg", "表6", "q4_production.log"))
    A((f"Q4_T6_dry", "表6 末行 t_dry 时刻", t_dry / 3600.0, "h", "表6", "q4_production.log"))
    for jj, c in enumerate(cols5):
        A((f"Q4_T6_dry_r{c:g}", f"表6 末行 r={c} cm 含水率", row_dry[1 + jj],
           "kg/kg", "表6", "q4_production.log"))
    A(("Q4_T6_dry_surf", "表6 末行 表面含水率", row_dry[-1], "kg/kg", "表6",
       "q4_production.log"))
    for k, v in xt.items():
        if v is not None:
            A((f"Q4_tcross_r{k:g}", f"r={k} cm 首次达标时刻", v, "s", "诊断",
               "q4_production.log"))
    # 附录4 物性 (设置值)
    for k, v in P4.items():
        A((f"Q4_P4_{k}", f"附录4 物性系数 {k}", v, "-", "设置", "docs/A题.md 附录4"))
    # 网格 (供核对)
    for c in [0.0, 0.5, 1.0, 1.5, 2.0]:
        A((f"Q4_grid_{c:g}", f"物理半径网格点 {c} cm 是否落在 [0,R(t_dry)] 内",
           1.0 if c <= s["Rs"][-1] + 1e-9 else 0.0, "1", "诊断", "推导"))

    reg_path = os.path.join(OUTDIR, "registry_q4.csv")
    with open(reg_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "group", "source"])
        for r_ in reg:
            w.writerow([r_[0], r_[1], repr(float(r_[2])), r_[3], r_[4], r_[5]])
    say(f"\n写出: outputs/registry_q4.csv ({len(reg)} 行)")

    with open(os.path.join(OUTDIR, "q4_production.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
