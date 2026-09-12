# -*- coding: utf-8 -*-
"""
q3_mc.py -- 问题三鲁棒性: 附录 3 物性参数的单因素灵敏度 + 蒙特卡洛综合扰动.

    A. 单因素: 9 个附录 3 参数各 +-5% (其余同基准), 共 18 组 -> t_dry 灵敏度
    B. 蒙特卡洛: 9 参数同时均匀扰动 +-5%, N=100 (种子 2026)
       -> t_dry 分布 (均值/标准差/P2.5/P97.5), 供综合误差预算与不确定区间

配置: M=200, rtol=1e-9, atol 同生产, max_step=3600 s;
     t_max=864000 s (10 天): 慢分支 (EA +5% 使 D 乘 exp(-0.596)~0.55) 的
     t_dry 约 1.8 倍, 需放宽安全网; 基准复算应与 registry_q3 一致.

运行: python src/q3_mc.py            (119 组, 4 进程并行, 约 3-5 min)
输出: outputs/registry_q3_mc.csv, outputs/q3_mc.log
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q3_solve import P3, run_parallel, write_registry  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

N_MC = 100
SEED = 2026
REL = 0.05
T_MAX_MC = 864000.0

LOG = []
REG = []


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def radd(id_, q, v, u, unc="", note=""):
    REG.append([id_, q, v, u, unc, "outputs/q3_mc.log",
                "python src/q3_mc.py", note])


def main():
    t0 = time.time()
    say("=" * 96)
    say("问题三鲁棒性: 附录 3 物性参数单因素灵敏度 + 蒙特卡洛 (N=%d, 种子 %d, ±%.0f%%)"
        % (N_MC, SEED, REL * 100))
    say("配置: M=200, rtol=1e-9, max_step=3600 s, t_max=864000 s")
    say("=" * 96)

    keys = list(P3.keys())
    base = dict(tag="base", M=200, rtol=1e-9, t_max=T_MAX_MC)
    cfgs = [base]
    for k in keys:
        for sgn, tag in ((1 - REL, "m"), (1 + REL, "p")):
            p = dict(P3)
            p[k] = P3[k] * sgn
            cfgs.append(dict(tag=f"s_{k}_{tag}", params=p, M=200, rtol=1e-9,
                             t_max=T_MAX_MC))
    rng = np.random.default_rng(SEED)
    fac = 1.0 + rng.uniform(-REL, REL, (N_MC, len(keys)))
    for j in range(N_MC):
        p = {k: P3[k] * fac[j, i] for i, k in enumerate(keys)}
        cfgs.append(dict(tag=f"mc{j:03d}", params=p, M=200, rtol=1e-9,
                         t_max=T_MAX_MC))
    say(f"算例: 1 基准 + {len(keys) * 2} 单因素 + {N_MC} 蒙特卡洛 = {len(cfgs)} 组")

    res = run_parallel(cfgs, workers=4)
    t_base = res["base"]["t_dry"]
    say(f"\n基准 t_dry = {t_base:.3f} s = {t_base / 3600:.4f} h "
        f"(registry P01 = 206720.413 s, 相对差 "
        f"{abs(t_base - 206720.4134563) / 206720.4134563:.1e})")

    say("\n[A] 单因素灵敏度 (±5%, 其余同基准):")
    say(f"  {'参数':>6} {'-5% t_dry (h)':>15} {'+5% t_dry (h)':>15} "
        f"{'Δ/h':>9} {'相对Δ%':>8}")
    sens = {}
    for k in keys:
        tm = res[f"s_{k}_m"]["t_dry"] / 3600.0
        tp = res[f"s_{k}_p"]["t_dry"] / 3600.0
        dv = (tp - tm) / 2.0
        rel = dv / (t_base / 3600.0) * 100.0
        sens[k] = dv
        say(f"  {k:>6} {tm:>15.3f} {tp:>15.3f} {dv:>+9.3f} {rel:>+8.2f}")
        radd(f"MC_s_{k}_m", f"单因素 {k}-5% 的 t_dry", tm, "h")
        radd(f"MC_s_{k}_p", f"单因素 {k}+5% 的 t_dry", tp, "h")
        radd(f"MC_s_{k}_d", f"单因素 {k} ±5% 的半程变化", dv, "h")
    rank = sorted(sens, key=lambda k: -abs(sens[k]))
    say(f"  灵敏度排序: {' > '.join(rank)}")

    td = np.array([res[f"mc{j:03d}"]["t_dry"] for j in range(N_MC)]) / 3600.0
    p_lo, p_hi = np.percentile(td, [2.5, 97.5])
    say("\n[B] 蒙特卡洛 t_dry 分布 (h):")
    say(f"  均值 {td.mean():.4f}  标准差 {td.std(ddof=1):.4f}  "
        f"最小 {td.min():.4f}  最大 {td.max():.4f}")
    say(f"  P2.5 = {p_lo:.4f},  P97.5 = {p_hi:.4f}  "
        f"-> 95% 区间 [{p_lo:.2f}, {p_hi:.2f}] h, 半宽 {0.5 * (p_hi - p_lo):.2f} h")
    lo_s, hi_s = t_base / 3600.0 - td.min(), td.max() - t_base / 3600.0
    say(f"  相对基准的包络: -{lo_s:.2f} / +{hi_s:.2f} h")
    radd("MC_base", "蒙特卡洛基准 t_dry", t_base, "s")
    radd("MC_mean", "蒙特卡洛 t_dry 均值", float(td.mean()), "h")
    radd("MC_std", "蒙特卡洛 t_dry 标准差", float(td.std(ddof=1)), "h")
    radd("MC_min", "蒙特卡洛 t_dry 最小值", float(td.min()), "h")
    radd("MC_max", "蒙特卡洛 t_dry 最大值", float(td.max()), "h")
    radd("MC_p2.5", "蒙特卡洛 t_dry P2.5", float(p_lo), "h")
    radd("MC_p97.5", "蒙特卡洛 t_dry P97.5", float(p_hi), "h")
    radd("MC_env_lo", "蒙特卡洛相对基准下包络", float(lo_s), "h")
    radd("MC_env_hi", "蒙特卡洛相对基准上包络", float(hi_s), "h")

    rp = os.path.join(OUT, "registry_q3_mc.csv")
    write_registry(rp, REG)
    with open(os.path.join(OUT, "q3_mc.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    say(f"\n注册表: {rp} ({len(REG)} 行); 总用时 {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
