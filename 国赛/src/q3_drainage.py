# -*- coding: utf-8 -*-
"""问题三: 烘房"排湿工况"情景 —— 恒温平台环境水分浓度 Cbar 抬高的影响.

题面把 4 h 之后定义为 "恒温干燥" 阶段, 本文按附件1 末段均值作平台外推
(Tbar=50 C, Cbar=0.05). 评阅关注: 若不排湿, 烘房水分浓度会升高, 上述外推
是否过于理想? 本脚本用生产口径实测 Cbar = 0.05/0.06/0.075/0.10/0.12/0.15
下的 t_dry, 给出定量回答 (含 Cbar >= C* 时永不达标的极限).

输出: outputs/registry_q3_drainage.csv, outputs/q3_drainage.log
运行: python src/q3_drainage.py
"""
from __future__ import annotations

import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
CBAR0 = 0.0500
CSTAR = 0.15
T_MAX = 518400.0          # 6 天安全网 (高于 3 天, 给高 Cbar 情景留出事件)

SCEN = [("base", 0.0500), ("c060", 0.0600), ("c075", 0.0750),
        ("c100", 0.1000), ("c120", 0.1200), ("c150", 0.1500)]


def _one(cfg):
    from q3_solve import run_case
    tag, cbar = cfg
    t0 = time.time()
    try:
        r = run_case(dict(tag=tag, M=200, rtol=1e-9, atol_T=1e-6, atol_C=1e-9,
                          max_step=3600.0, t_max=T_MAX, Cbar=cbar,
                          sample=False, crossings=False))
        r["Cbar"] = cbar
        r["wall"] = time.time() - t0
        return r
    except Exception as e:                       # 事件未发生 -> 记录而非崩溃
        return dict(tag=tag, Cbar=cbar, t_dry=None, status=f"NO_EVENT: {type(e).__name__}",
                    wall=time.time() - t0, nsteps=-1)


def main():
    REG, LOG = [], []

    def say(s=""):
        print(s, flush=True)
        LOG.append(str(s))

    say("=" * 92)
    say("问题三: 恒温平台水分浓度 Cbar 的情景分析 (排湿/不排湿)")
    say("=" * 92)
    say(f"生产口径: M=200, rtol=1e-9, max_step=3600 s, t_max={T_MAX:.0f} s; "
        f"阈值 C*={CSTAR}; 基准 Cbar={CBAR0}")
    say(f"  {'情景':>8} {'Cbar':>8} {'Cbar/C*':>9} {'t_dry / s':>13} {'t_dry / h':>11} "
        f"{'Δ / h':>9}  {'状态'}")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=len(SCEN)) as ex:
        rows = list(ex.map(_one, SCEN))
    say(f"  [并行 {len(SCEN)} 个算例, 用时 {time.time()-t0:.1f} s]")
    base = next(r for r in rows if r["tag"] == "base")
    tb = base["t_dry"]
    for r in rows:
        cb = r["Cbar"]
        if r["t_dry"] is None:
            say(f"  {r['tag']:>8} {cb:>8.4f} {cb/CSTAR:>9.3f} {'—':>13} {'—':>11} "
                f"{'—':>9}  {r['status']}")
            REG.append([f"DR_{r['tag']}", f"Cbar={cb:.4f} 时 t_dry (无事件)",
                        "nan", "s", "run", "q3_drainage.py",
                        "python src/q3_drainage.py", r["status"]])
            continue
        th = r["t_dry"] / 3600.0
        dh = (r["t_dry"] - tb) / 3600.0
        say(f"  {r['tag']:>8} {cb:>8.4f} {cb/CSTAR:>9.3f} {r['t_dry']:>13.1f} "
            f"{th:>11.4f} {dh:>+9.4f}  {r['status']}")
        REG.append([f"DR_{r['tag']}", f"Cbar={cb:.4f} 时的 t_dry", r["t_dry"], "s",
                    "run", "q3_drainage.py", "python src/q3_drainage.py",
                    f"Cbar/C*={cb/CSTAR:.3f}"])
        REG.append([f"DR_{r['tag']}_h", f"Cbar={cb:.4f} 时的 t_dry (h)", th, "h",
                    "run", "q3_drainage.py", "python src/q3_drainage.py", ""])
        REG.append([f"DR_{r['tag']}_dh", f"Cbar={cb:.4f} 相对基准的 Δt_dry", dh, "h",
                    "run", "q3_drainage.py", "python src/q3_drainage.py", ""])
    say()
    say("注: Cbar -> C* 时过程渐近停滞 (Cbar >= C* 则永不达标); 排湿系统的意义在于"
        "把 Cbar 维持在远低于 C* 的水平。")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "q3_drainage.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    p = os.path.join(OUT, "registry_q3_drainage.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    say(f"注册表: {p}")


if __name__ == "__main__":
    main()
