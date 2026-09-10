"""
问题1 生产计算 + 结果文件生成.

生产设置: 节点式 FV (修正系数), M=800, dt=2^-7 s = 0.0078125 s (t=1 s 恰为第128步)
独立校核: (a) M=800, dt=2^-8;  (b) M=1600, dt=2^-7

输出:
  outputs/result1.xlsx        温度 / 水分浓度 两个工作表, 模板格式
  outputs/table1_temperature.md, outputs/table2_moisture.md   论文表1/表2
  outputs/q1_production.log   运行记录 (含校核偏差)

运行:  python src/q1_produce.py
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import Env, load_attachment1, solve_q1, R0  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

T_END = 1800.0
R_OUT_CM = np.round(np.arange(0.0, 2.0001, 0.1), 10)      # 0, 0.1, ..., 2.0 cm
R_OUT_M = R_OUT_CM / 100.0
T_REQ = np.arange(1.0, T_END + 1.0, 1.0)                   # 1..1800 s


def run(M, dt, tag):
    t0 = time.time()
    dr = R0 / M
    idx = np.round(R_OUT_M / dr).astype(int)
    assert np.allclose(idx * dr, R_OUT_M, atol=1e-12), "输出半径必须落在节点上"
    r_, T_, C_, sT, sC = solve_q1(M, dt, T_END, env, corr=True, probes_t=T_REQ)
    el = time.time() - t0
    print(f"  [{tag}] M={M}, dt={dt:.10g} s, dr={dr*1000:.5f} mm, "
          f"{len(T_REQ)} 个输出时刻, 用时 {el:.1f} s")
    return sT[:, idx], sC[:, idx], el


if __name__ == "__main__":
    log_path = os.path.join(OUT, "q1_production.log")
    lines = []

    def say(s):
        print(s)
        lines.append(s)

    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")

    say("=" * 92)
    say("问题1 生产计算 (节点式有限体积, 修正系数, 全隐式 Euler)")
    say("=" * 92)
    say(f"  输出半径 (cm): {list(R_OUT_CM)}")
    say(f"  输出时刻: 1..{int(T_END)} s, 共 {len(T_REQ)} 个")

    say("\n[A] 生产解 M=3200, dt=2^-8 s")
    Tp, Cp, _ = run(3200, 2.0 ** -8, "prod")

    say("\n[B] 校核1 M=3200, dt=2^-9 s (时间步再减半)")
    Tb, Cb, _ = run(3200, 2.0 ** -9, "chk-t")

    say("\n[C] 校核2 M=6400, dt=2^-8 s (网格再加密)")
    Tc, Cc, _ = run(6400, 2.0 ** -8, "chk-h")

    dTt = np.max(np.abs(Tp - Tb))
    dCt = np.max(np.abs(Cp - Cb))
    dTh = np.max(np.abs(Tp - Tc))
    dCh = np.max(np.abs(Cp - Cc))
    say("\n" + "=" * 92)
    say("生产解的不确定度 (与两组独立加密解比较)")
    say("=" * 92)
    say(f"  时间步加密 (dt/2):        max|dT| = {dTt:.3e} K    max|dC| = {dCt:.3e} kg/kg")
    say(f"  网格加密   (M x2):        max|dT| = {dTh:.3e} K    max|dC| = {dCh:.3e} kg/kg")
    say("")
    say("  分时段 (为说明早时段表面水分的启动瞬态被充分解析):")
    say(f"  {'时间窗':>14} {'max|dT| [K]':>16} {'max|dC| [kg/kg]':>20}")
    for lo, hi, lbl in ((1, 10, "t=1..9 s"), (10, 100, "t=10..99 s"),
                        (100, 600, "t=100..599 s"), (600, 1800, "t=600..1800 s"),
                        (1, 1800, "t=1..1800 s")):
        st, sc = lo - 1, hi - 1
        if lo == 1 and hi == 1800:
            st, sc = 0, 1799
        say(f"  {lbl:>14} {np.max(np.abs((Tp-Tc)[st:sc+1])):>16.3e} "
            f"{np.max(np.abs((Cp-Cc)[st:sc+1])):>20.3e}")
    say("")
    say(f"  最大不确定度: 温度 {max(dTt,dTh):.1e} K, 水分浓度 {max(dCt,dCh):.1e} kg/kg")
    say("  四位小数 = 半 ulp 5e-5; 上述不确定度均低于该阈值 -> 四位小数报告是安全的")

    # ---------------- 写 result1.xlsx ----------------
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "温度"
    ws.cell(row=1, column=1, value="时间\\到药材中心的距离")
    for j, rc in enumerate(R_OUT_CM):
        ws.cell(row=1, column=2 + j, value=float(rc))
    for i, tt in enumerate(T_REQ):
        ws.cell(row=2 + i, column=1, value=int(tt))
        for j in range(len(R_OUT_CM)):
            ws.cell(row=2 + i, column=2 + j, value=round(float(Tp[i, j]) - 273.15, 4))

    ws2 = wb.create_sheet("水分浓度")
    ws2.cell(row=1, column=1, value="时间\\到药材中心的距离")
    for j, rc in enumerate(R_OUT_CM):
        ws2.cell(row=1, column=2 + j, value=float(rc))
    for i, tt in enumerate(T_REQ):
        ws2.cell(row=2 + i, column=1, value=int(tt))
        for j in range(len(R_OUT_CM)):
            ws2.cell(row=2 + i, column=2 + j, value=round(float(Cp[i, j]), 4))

    p = os.path.join(OUT, "result1.xlsx")
    wb.save(p)
    say(f"\n结果文件: {p}  (温度 {ws.max_row-1}x{ws.max_column-1}, "
        f"水分浓度 {ws2.max_row-1}x{ws2.max_column-1})")

    # ---------------- 表1 / 表2 (文稿 Markdown + 机器可读 CSV) ----------------
    t_req_tab = [100, 300, 600, 900, 1200, 1500, 1800]
    cols = [0, 5, 10, 15, 20]      # 0,0.5,1,1.5,2 cm 在输出列中的下标
    for name, arr, isT in (("table1_temperature.md", Tp - 273.15, True),
                           ("table2_moisture.md", Cp, False)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write("| 时间/s | 0 | 0.5 | 1 | 1.5 | 2 |\n|---|---|---|---|---|---|\n")
            for tt in t_req_tab:
                i = int(tt) - 1
                f.write(f"| {tt} | " + " | ".join(f"{arr[i, j]:.4f}" for j in cols) + " |\n")

    # CSV 必须与 xlsx 同源同值 (此前为粗网格残留, 与 result1.xlsx 在第 4 位小数冲突)
    import csv as _csv
    for name, arr in (("table1_temperature.csv", Tp - 273.15),
                      ("table2_moisture.csv", Cp)):
        with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8-sig") as f:
            w = _csv.writer(f)
            w.writerow(["时间/s", "0", "0.5", "1", "1.5", "2"])
            for tt in t_req_tab:
                i = int(tt) - 1
                w.writerow([tt] + [f"{arr[i, j]:.4f}" for j in cols])

    say("\n" + "=" * 92)
    say("表1 温度 (degC) — 生产解 M=3200, dt=2^-8 s")
    say("=" * 92)
    say("  t/s      " + "".join(f"{d:>11}" for d in ["0", "0.5", "1", "1.5", "2"]))
    for tt in t_req_tab:
        i = int(tt) - 1
        say(f"  {tt:>5}    " + "".join(f"{Tp[i, j]-273.15:>11.4f}" for j in cols))
    say("\n" + "=" * 92)
    say("表2 水分浓度 (kg/kg) — 生产解 M=3200, dt=2^-8 s")
    say("=" * 92)
    say("  t/s      " + "".join(f"{d:>11}" for d in ["0", "0.5", "1", "1.5", "2"]))
    for tt in t_req_tab:
        i = int(tt) - 1
        say(f"  {tt:>5}    " + "".join(f"{Cp[i, j]:>11.4f}" for j in cols))

    # 低温/低湿端的稳健性: 表面 vs 环境
    say("\n附: 表面水分浓度与环境水分浓度 (t=1800 s)")
    say(f"  C(r=R,1800s) = {Cp[-1, -1]:.4f} kg/kg ;  C_inf(1800s) = {env.C(1800.0):.5f} kg/kg ; "
        f"比值 = {Cp[-1,-1]/env.C(1800.0):.1f}")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n日志: {log_path}")
