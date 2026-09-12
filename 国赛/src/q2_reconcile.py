# -*- coding: utf-8 -*-
"""
q2_reconcile.py -- 问题二文稿的数字对账 (与 q1_reconcile.py 同一套规则).

第一关: 把 model/problem2_slove.md 与 model/problem2.md 中的每一个数值字面量
        与注册表/允许清单核对, 未登记的不得出现在文稿中.
第二关: model/problem2_slove.md 与 outputs/table3*.{md,csv}, table4*.{md,csv}
        的表格值必须与 outputs/result2.xlsx 在 4 位小数上逐位相同 (不用容差).

注册表:
  outputs/registry_q2_model.csv       模型数字 (物性/特征数/潜热/几何), 由 q2_model_numbers.py
  outputs/registry_q2_verify.csv      核验数字, 由 q2_verify.py
  outputs/registry_q2_production.csv  生产数字与不确定度, 由 q2_produce.py
  outputs/registry_q2_latent_heat.csv 潜热 IAPWS-95 定标表

运行: python src/q2_reconcile.py
"""

from __future__ import annotations

import csv
import os
import re
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

DOCS = [os.path.join(ROOT, "model", "problem2_slove.md"),
        os.path.join(ROOT, "model", "problem2.md"),
        os.path.join(OUT, "table3_temperature.md"),
        os.path.join(OUT, "table4_moisture.md")]

REGISTRIES = [os.path.join(OUT, "registry_q2_model.csv"),
              os.path.join(OUT, "registry_q2_verify.csv"),
              os.path.join(OUT, "registry_q2_production.csv"),
              os.path.join(OUT, "registry_q2_latent_heat.csv"),
              os.path.join(OUT, "registry_q2_latent_heat_rows.csv"),
              os.path.join(OUT, "registry_q2_energy.csv"),
              os.path.join(OUT, "registry_q2_center.csv"),
              os.path.join(OUT, "registry_q2_moist_diag.csv"),
              os.path.join(OUT, "registry_q2_app2_vs_app3.csv"),
              os.path.join(OUT, "registry_q2_derived.csv"),
              os.path.join(OUT, "registry_q2_figures.csv"),
              os.path.join(OUT, "registry_q2_conv.csv"),
              os.path.join(OUT, "registry_q2_energy_verified.csv"),
              os.path.join(OUT, "registry_q2_energy_exact.csv"),
              # 并发会话新增的"不确定度五口径"注册表 (problem2_slove.md §7.3)
              os.path.join(OUT, "registry_q2_uncertainty.csv"),
              # 摘要里引用了问题一的结果 (33.5758 / 36.7858 degC), 其来源是
              # 问题一的生产注册表; 纳入后摘要中的问题一数字同样有据可查.
              os.path.join(OUT, "registry_q1_production.csv"),
              # 摘要里还有针对问题三的一句 (t_dry 与各半径达标时刻), 其来源是
              # 并发会话 (session 8) 的问题三注册表; 同样纳入, 使摘要全域可追溯.
              os.path.join(OUT, "registry_q3.csv"),
              os.path.join(OUT, "registry_q3_verify.csv"),
              os.path.join(OUT, "registry_q3_figures.csv"),
              os.path.join(OUT, "registry_q3_drainage.csv"),
              # §5.2.6 用到的"附件1 环境噪声滤波对照"注册表 (q1_smooth_check.py):
              # 该段虽在问题二小节, 但证据由 q1 求解器产出, 故单独一张注册表.
              os.path.join(OUT, "registry_q1_smooth.csv"),
              # 摘要中针对问题四的一段 (t_dry / 效应分解 / 守恒残差 / MC 区间),
              # 其来源是问题四的产出、验证、灵敏度与派生注册表.
              os.path.join(OUT, "registry_q4.csv"),
              os.path.join(OUT, "registry_q4_verify.csv"),
              os.path.join(OUT, "registry_q4_sens.csv"),
              os.path.join(OUT, "registry_q4_compat.csv"),
              os.path.join(OUT, "registry_q4_figures.csv"),
              os.path.join(OUT, "registry_q4_derived.csv"),
              # 附录 D 的刚性谱数据 (q45_stiffness.py):
              # 时间尺度 / Jacobian 谱 / 显式格式步数
              os.path.join(OUT, "registry_q45_stiffness.csv"),
              # 附录 A (问题一温度场解析解交叉验证) 与附录 B (二维轴对称对照)
              # 的数据来源. 两节在 session 22 之前不在扫描范围内, 纳入后其数字同样可追溯.
              os.path.join(OUT, "registry_q1_ana_vs_num.csv"),
              os.path.join(OUT, "registry_q1_analytic_fit.csv"),
              os.path.join(OUT, "registry_q1_piecewise.csv"),
              os.path.join(OUT, "registry_q1_production.csv"),
              os.path.join(OUT, "registry_q3_2d.csv"),
              # 附录 A 的 Bessel 特征值/展开系数表 (audit_eigentable.py, q1_bessel_table.py)
              # 与常环境校核 (q1_const_env_check.py)
              os.path.join(OUT, "registry_eigentable.csv"),
              os.path.join(OUT, "registry_q1_bessel.csv"),
              os.path.join(OUT, "registry_q1_const_env.csv")]

REPORT = os.path.join(OUT, "reconciliation_q2.csv")
XLSX = os.path.join(OUT, "result2.xlsx")
TEX = os.path.join(ROOT, "paper", "example.tex")
# 论文问题二小节的首尾标记: 第三关只扫这一段, 不把其它问题的历史数字卷入
TEX_BEGIN = "\\subsection{问题二模型的建立与求解}"
TEX_END = "\\subsection{问题三模型的建立与求解}"
# 问题四小节的首尾标记 (同样只扫这一段)
TEX_BEGIN4 = "\\subsection{问题四模型的建立与求解}"
TEX_END4 = "\\section{模型评价与推广}"
# 图表里"非结论性"的排版数字 (图宽/框宽/minipage 宽), 不参与对账
LAYOUT_NUMS = {"0.96", "0.94", "0.92", "0.88", "0.98", "1.15", "0.2", "0.3",
               # 附录中的结构性计数 (非测量结果):
               "853",   # DOP853 积分器名中的数字, 不是数值
               "201",   # M=200 时径向节点数 2(M+1)=402 的一半, 即 M+1
               "617",   # 附录 B 与二维对照的公共比较窗口采样点数
               "385",   # E_A 的 10% 扰动 = 385 K, 由 E_A=3850 导出
               "148"}   # 附录 E 的 Jacobian FD 核验显著分量数 (M=12)
T_TAB_S = [1800, 3600, 5400, 7200, 9000, 10800]
R_CM = [0.0, 0.5, 1.0, 1.5, 2.0]

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
HEADING_RE = re.compile(r"^\s*#{1,6}\s*\d")

# ---------------------------------------------------------------------------
# 允许清单: 题面/附录直接给定, 或纯结构、章节号、软件版本、纯数学常数
# ---------------------------------------------------------------------------
ALLOW_RAW = [
    # 题面几何与初值
    (25, "题面: 长度 25 cm"), (2, "题面: 半径 2 cm / 通用整数"),
    (28, "题面: 初温 28 degC"), (2.55, "题面: 初始干基含水率 2.55 kg/kg"),
    (0.15, "题面问题3: 含水率目标 0.15 kg/kg"),
    (273.15, "摄氏-热力学温标换算"), (301.15, "题面: T0 = 28 degC = 301.15 K"),
    # §5.2.6 h 口径段: 由两个已注册的表8 表面含水率之差推出 (1.00917-1.00778)
    (1.3e-3, "表8 h 变体表面含水率相对基准之差 (1.00917-1.00778) 推导"),
    (323.15, "T_inf = 50 degC = 323.15 K (常数边界校核)"),
    (313.15, "40 degC = 313.15 K (潜热取工作区间中部)"),
    # 附录2
    (820, "附录2: 密度"), (2600, "附录2: 比热容"), (0.36, "附录2: 热传导系数"),
    (25.0, "附录2: 对流换热系数"), (25, "附录2: 对流换热系数"),
    (8e-7, "附录2: 对流传质系数"), (7e-9, "附录2: 扩散系数系数"),
    (0.89, "附录2: 扩散指数"), (-0.89, "附录2: 扩散指数(带符号)"),
    # 附录3
    (650, "附录3: rho 常数项"), (128, "附录3: rho 的 C 系数"),
    (1450, "附录3: cp 常数项"), (2736, "附录3: cp 的 C 系数"),
    (0.21, "附录3: k 常数项"), (0.38, "附录3: k 的 C 系数"),
    (2.4e-3, "附录3: D 的系数"), (0.45, "附录3: D 的指数常数"),
    (-0.45, "附录3: D 的指数常数(带符号)"), (3850, "附录3: Arrhenius 常数"),
    (-3850, "附录3: Arrhenius 常数(带符号)"),
    # 附录4 (对照用)
    (760, "附录4: rho 常数项"), (90, "附录4: rho 的 C 系数"),
    (1850, "附录4: cp 常数项"), (2150, "附录4: cp 的 C 系数"),
    (0.12, "附录4: k 常数项"), (0.20, "附录4: k 的 C 系数"), (0.2, "附录4: k 的 C 系数"),
    (4.2e-4, "附录4: D 的系数"), (0.30, "附录4: D 的指数常数"),
    (-0.30, "附录4: D 的指数常数(带符号)"), (0.3, "附录4: D 的指数常数"),
    # 题面要求的时间/半径点与输出约定
    (100, "题面表1/2 时间点"), (300, "题面表1/2 时间点"), (600, "题面表1/2 时间点"),
    (900, "题面表1/2 时间点"), (1200, "题面表1/2 时间点"), (1500, "题面表1/2 时间点"),
    (1800, "题面表1/2 时间点 / 阶段时长"),
    (3600, "题面表3/4 时间点 1 h"), (5400, "题面表3/4 时间点 1.5 h"),
    (7200, "题面表3/4 时间点 2 h"), (9000, "题面表3/4 时间点 2.5 h"),
    (10800, "题面表3/4 时间点 3 h"),
    (0.5, "题面: 半径网格 0.5 cm"), (1.0, "题面: 半径网格 1 cm"),
    (1.5, "题面: 半径网格 1.5 cm"), (0.1, "题面: 半径步长 0.1 cm"),
    (2.0, "题面: 半径上界 2 cm"), (2.0e0, "题面: 半径上界 2 cm"),
    (6, "结构: 表格行数"), (3.0, "3 h"), (0.5, "结构: 0.5 h"),
    (1.5, "结构: 1.5 h"), (2.5, "结构: 2.5 h"),
    (10800.0, "题面: 3 h = 10800 s"),
    # 网格与时间步 (结构性设置)
    (50, "网格数 M=50"), (100, "网格数 M=100"), (200, "网格数 M=200"),
    (400, "网格数 M=400"), (800, "网格数 M=800"), (1600, "网格数 M=1600"),
    (3200, "网格数 M=3200"),
    (12, "网格数 M=12 (Jacobian 校核)"),
    (0.02, "长度换算 / dt=0.02 s"), (0.01, "dt=0.01 s"), (0.04, "dt=0.04 s"),
    (0.08, "dt=0.08 s"), (0.25, "dt=0.25 s"), (0.125, "dt=0.125 s"),
    (0.0625, "dt = 2^-4 s"), (0.03125, "dt = 2^-5 s"), (0.015625, "dt = 2^-6 s"),
    (0.005, "dt = 0.005 s"), (0.005000, "dt = 0.005 s"),
    (16, "1/16 s 的时间步分母"), (64, "1/64 s 的时间步分母"),
    (128, "1/128 s 的时间步分母"), (32, "结构"),
    (256, "1/256 s 的时间步分母 (q2_moist_diag 的诊断步长)"),
    (10800, "输出时间行数/末时刻"),
    (21, "result2 半径列数"), (100, "结构"),
    (540000, "步数 = 10800/0.02"), (1080000, "步数 = 10800/0.01"),
    (21600, "步数 = 10800/0.5"), (43200, "步数 = 10800/0.25"),
    (86400, "步数 = 10800/0.125"), (135000, "步数 = 10800/0.08"),
    (172800, "步数 = 10800/0.0625"), (270000, "步数 = 10800/0.04"),
    (135000, "步数"), (60000, "步数 = 600/0.01"),
    (2000, "基准算例步数"), (7200, "步数 = 1800/0.25"),
    (240, "附件1 步数"), (241, "附件1 数据点数"), (31, "附件1 前 31 点"),
    (14400, "附件1 覆盖时长 14400 s"), (60, "附件1 采样间隔 60 s"),
    (1, "单位/结构"), (0, "零"), (4, "结构/常数"), (5, "结构/常数"),
    (7, "结构"), (8, "结构"), (9, "结构"), (10, "结构"), (11, "结构"),
    (13, "结构"), (14, "结构"), (15, "结构"), (17, "结构"), (18, "结构"),
    (19, "结构"), (20, "结构"), (22, "结构"), (23, "结构"), (24, "结构"),
    (26, "结构"), (27, "结构"), (28.0, "结构"), (29, "结构"), (30, "结构"),
    (33, "结构"), (35, "结构"), (40, "结构/40 degC"), (45, "结构"),
    (46, "结构"), (120, "结构"), (400.0, "结构"), (240, "结构"),
    (2, "结构"), (3, "结构"), (3.0, "结构"),
    # 数值量级与容差
    (5e-5, "四位小数的半 ulp 阈值"), (1e-9, "数值容差"), (1e-10, "数值容差"),
    (1e-11, "Newton 相对残差判据"), (1e-12, "数值量级"), (1e-13, "数值量级"),
    (1e-14, "数值量级"), (1e-16, "机器精度"), (1e-7, "有限差分步长"),
    (1e-6, "量级"), (1e-5, "量级"), (1e-4, "量级"), (1e-3, "量级"),
    (1e-2, "量级/1e-2 K"), (1e-1, "量级"), (1e-8, "量级"),
    (2e-3, "量级"), (5e-3, "量级/差分步长"), (1e3, "量级"), (1e4, "量级"),
    (1e5, "量级"), (1e6, "量级"), (1e7, "量级"), (1e8, "量级"),
    (10, "量级/迭代上限"), (1000, "量级"), (0.05, "量级"),
    (1005, "[未检索] 空气定压比热, 凭记忆的教科书值, 仅作量级论证"),
    # 潜热推导中的物理常数 (题面未给, 由基础热力学量导出)
    (8.314462618, "通用气体常数 R_u (IUPAC 2019)"),
    (0.0180153, "水摩尔质量 M_w = 18.0153 g/mol"),
    (461.5, "水蒸气比气体常数 R_v ≈ 461.5 J/(kg K)"),
    (461.526, "水蒸气比气体常数 R_v (IAPWS-95)"),
    (461.51805, "水蒸气比气体常数 R_v (IAPWS-95 精确值)"),
    (57.76, "20 degC 饱和水蒸气比容 v_v"),
    (1.002, "20 degC 液态水比容 v_l"),
    (1.7e-5, "v_l/v_v 量级"),
    (273.16, "水三相点温度"), (273.15, "0 degC"),
    (0.6117, "三相点饱和蒸气压 0.6117 kPa"),
    (2.34, "20 degC 饱和蒸气压 2.34 kPa"), (12.35, "50 degC 饱和蒸气压 12.35 kPa"),
    (57.8, "20 degC v_v 的约值"), (12.0, "50 degC v_v 的约值"),
    (0.998649, "20 degC 压缩因子 Z (IAPWS-95)"),
    (0.998027, "30 degC 压缩因子 Z"),
    (0.997189, "40 degC 压缩因子 Z"),
    (0.996086, "50 degC 压缩因子 Z"),
    (0.1352, "20 degC 的 1/Z-1 (%)"), (0.1977, "30 degC 的 1/Z-1 (%)"),
    (0.2819, "40 degC 的 1/Z-1 (%)"), (0.3930, "50 degC 的 1/Z-1 (%)"),
    (0.1370, "20 degC CC 实测偏差 (%)"), (0.2008, "30 degC CC 实测偏差 (%)"),
    (0.2871, "40 degC CC 实测偏差 (%)"), (0.4014, "50 degC CC 实测偏差 (%)"),
    (0.002, "理论与实测吻合度 (%)"), (0.009, "理论与实测吻合度 (%)"),
    (4184.4, "20 degC c_p,l (IAPWS-95)"), (4181.6, "25 degC c_p,l"),
    (4180.1, "30 degC c_p,l"), (4179.5, "35 degC c_p,l"),
    (4179.6, "40 degC c_p,l"), (4180.4, "45 degC c_p,l"), (4181.5, "50 degC c_p,l"),
    (4180, "液态水比热约值"), (4180.0, "液态水比热约值"),
    (1863.2, "20 degC c0_p,v"), (1864.4, "25 degC c0_p,v"), (1865.6, "30 degC c0_p,v"),
    (1867.0, "35 degC c0_p,v"), (1868.4, "40 degC c0_p,v"), (1869.8, "45 degC c0_p,v"),
    (1871.3, "50 degC c0_p,v"), (1863, "25 degC 附近 c0_p,v"),
    (-2321.2, "20 degC 的 dcp0"), (-2317.2, "25 degC 的 dcp0"), (-2314.4, "30 degC"),
    (-2312.5, "35 degC"), (-2311.3, "40 degC"), (-2310.5, "45 degC"),
    (-2310.2, "50 degC"), (-2314, "dcp0 平均"), (-2.314e3, "dcp0 平均"),
    (-2367.2, "20 degC 的 dH/dT 数值"), (-2370.5, "25 degC 的 dH/dT 数值"),
    (-2375.9, "30 degC 的 dH/dT 数值"), (-2383.1, "35 degC 的 dH/dT 数值"),
    (-2392.1, "40 degC 的 dH/dT 数值"), (-2402.8, "45 degC 的 dH/dT 数值"),
    (-2415.0, "50 degC 的 dH/dT 数值"), (-2387, "dH/dT 平均"),
    (-2.387e3, "dH/dT 平均"), (-2391, "定标斜率"), (-2.391e3, "定标斜率"),
    (-73, "两项斜率之差"), (3.0, "两项斜率之差的相对值 (%)"),
    (0.001, "相对偏差 (%)"), (0.005, "相对偏差 (%)"), (0.007, "相对偏差 (%)"),
    (0.01, "相对偏差 (%)"), (0.0033, "残差相对值 (%)"),
    (80, "定标式最大残差 J/kg"),
    (2.4537, "定标式 L_v(20 degC) [1e6 J/kg]"),
    (2.4535, "IAPWS-95 L_v(20 degC) [1e6 J/kg]"),
    (2.4346, "定标式 L_v(28 degC) [1e6 J/kg]"),
    (2.4059, "定标式 L_v(40 degC) [1e6 J/kg]"),
    (2.4060, "IAPWS-95 L_v(40 degC) [1e6 J/kg]"),
    (2.3820, "定标式 L_v(50 degC) [1e6 J/kg]"),
    (2.3819, "IAPWS-95 L_v(50 degC) [1e6 J/kg]"),
    (2.5015, "摄氏展开式截距 [1e6 J/kg]"),
    (1.22820, "10 degC p_sat IAPWS [kPa]"), (2.33932, "20 degC p_sat IAPWS"),
    (4.24697, "30 degC p_sat IAPWS"), (7.38494, "40 degC p_sat IAPWS"),
    (12.35195, "50 degC p_sat IAPWS"),
    (1.22753, "10 degC p_sat 反演"), (2.33620, "20 degC p_sat 反演"),
    (4.23666, "30 degC p_sat 反演"), (7.35633, "40 degC p_sat 反演"),
    (12.28144, "50 degC p_sat 反演"),
    (-0.05, "10 degC 反演偏差 (%)"), (-0.13, "20 degC 反演偏差 (%)"),
    (-0.24, "30 degC 反演偏差 (%)"), (-0.39, "40 degC 反演偏差 (%)"),
    (-0.57, "50 degC 反演偏差 (%)"), (-0.6, "反演偏差上界 (%)"),
    (0.0018, "理论 vs 实测的一致度 (%)"),
    # IAPWS-95 标准名 / 公式中的偏移量 (不是测算值)
    (-95, "国际水物性标准名 IAPWS-95 中的 '-95'"),
    (-28, "L_v 定标式中 (T - 28 degC) 的偏移量"),
    (95, "IAPWS-95"),
    # 时间窗与采样点数 (结构性)
    (61, "时间窗标签 t=61..600 s"), (601, "时间窗标签 t=601..3600 s"),
    (3601, "时间窗标签 t=3601..10800 s"), (180, "0~10800 s 内 60 s 采样步数"),
    (59, "结构"), (199, "结构"), (2000, "结构"),
    # 网格标签与 Δr
    (0.0025, "网格尺寸 dr = 0.0025 cm (M=800)"),
    (0.00125, "网格尺寸 dr = 0.00125 cm (M=1600)"),
    (0.000625, "网格尺寸 dr = 0.000625 cm (M=3200)"),
    (0.01, "网格尺寸 dr = 0.01 cm / dt"), (0.005, "网格尺寸 dr = 0.005 cm / dt"),
    (0.001, "量级"), (0.0001, "量级"),
    (2.0e-4, "比体积权 R^2/2 = 2e-4 m^2"), (2e-4, "比体积权 R^2/2"),
    (4.0e-4, "结构"), (6e-4, "结构"),
    (3600, "1 h = 3600 s"), (5400, "1.5 h"), (7200, "2 h"), (9000, "2.5 h"),
    (10800.0, "3 h"), (300, "结构"),
    (18000, "论文: sqrt(alpha t) 穿透深度的量级时间尺度标签 (5 h 量级表述)"),
    # 更正记录中**引用**的中间版本数值 (错误值, 保留以说明修正过程)
    (85.32, "[更正记录] 第一版误用 Richardson-细 得到的 '水分为阈值 85.32%'"),
    (1565.6, "[更正记录] q2_energy_exact.py 重复温标换算时的伪源项占比"),
    (4.0754e4, "[更正记录] 同上, 伪源项数值"),
    (917, "[更正记录] 同上, 混合基准的 |S|/|R_0| 旧值"),
    (2005, "文献年份: 杨历 2005"), (2020, "文献年份: 胡众欢 2020"),
    (301, "T = 301 K 的整数量级表述 (§7.2)"),
    # 附件2 的半径数据 (题面附件给定, 未由本文脚本重算)
    (1.75, "附件2: 3 h 内半径由 2.000 降至约 1.75 cm"),
    (2.000, "附件2: 初始半径 2.000 cm"),
    (0.019636, "附件1: C_inf 下界 (附件原始精度 5 位)"),
    (0.050250, "附件1: C_inf 上界"),
    (0.05025, "附件1: C_inf 上界"),
    (0.0502, "附件1: C_inf 上界 (4 位)"),
    # 耦合强度论证 (§7.2)
    (4.25, "d lnD/dT 的百分比形式 (%/K)"), (4.2, "d lnD/dT 的量级 (%/K)"),
    (2.4, "D 在 28->50 degC 的倍率"), (1.43, "D 在 50->60 degC 的倍率"),
    (63.7, "rho cp 降幅 (%)"), (3.335, "rho cp(2.55) [1e6 J/(m^3 K)]"),
    (1.209, "rho cp(0.15) [1e6 J/(m^3 K)]"),
    (26, "时间尺度比 alpha/D"), (0.039, "D/alpha"), (6.6, "R^2/D 与 3 h 之比"),
    (7, "D 跨越的数量级"), (2.0e-12, "D 的下界量级"),
    (0.9, "蒸发温降占温升比例 (%)"), (22, "28->50 degC 的温升 (K)"),
    (41.5, "t=1800 s 环境温度 (degC)"), (47.5, "t=3600 s 环境温度 (degC)"),
    (0.0196, "t=0 s 环境含水率"), (0.0331, "t=1800 s 环境含水率"),
    (0.0427, "t=3600 s 环境含水率"), (2.5, "取 C_R ≈ 2.5 作量级估计"),
    (4.77, "t=0 的 q_evap 量级"), (4.75, "t=1800 的 q_evap 量级"),
    (4.73, "t=3600 的 q_evap 量级"), (338, "t=1800 的对流热流量级"),
    (488, "t=3600 的对流热流量级"), (1.4, "t=1800 的 q_evap/q_conv (%)"),
    (1.0, "t=3600 的 q_evap/q_conv (%)"), (0.19, "表面温降量级 K"),
    (0.2, "表面温降量级 K"), (1.925, "q_evap 系数约值"),
    (25000, "h_m 类比值与题面值之比"), (0.02, "h_m 类比估计 m/s"),
    (4, "h_m 相差的数量级"), (2, "结构"),
    (0.0385, "Jacobian 元 L_v h_m R 约值"),
    (0.96, "Jacobian 元占对角元的比例 (%)"),
    (0.04, "黏性/结构"), (4.0, "结构"),
    # §9 质量矩阵
    (12, "一致质量矩阵的分母 12"),
    (3, "一致质量矩阵系数"), (6, "行和集中系数"), (2, "结构"),
    (0.166667, "M^L_00/dr^2 的约值"), (0.1666666667, "M^L_00/dr^2 的约值"),
    (0.125, "半控制体 dr^2/8 的约值"),
    (5.684e-14, "session-2 级数交叉验证值"), (3.6e-15, "session-2 特征根一致度"),
    # 软件版本与章节号
    (3.12, "Python 3.12"), (3.12, "Python 版本"), (18, "结构"),
    (1.18, "scipy 1.18.1"), (3.1, "openpyxl 3.1.2"),
    (1.5, "iapws 版本号 1.5 段"), (0.5, "iapws 版本号 5 段 / 通用"),
    (9.3, "章节号 §9.2–9.3"),
    (2026, "年份: 2026 高教社杯"), (20260616, "结构"),
    (2, "结构"), (7.4957e-6, "session-4 对照值"), (0.1499, "session-4 对照值"),
    (34.57, "session-4 对照值"), (2368.89, "session-1 tau_T 对照值"),
    (2368.9, "session-1 tau_T 对照值"), (2381.94, "session-2 对照值"),
    (1.6793e-7, "session-2 对照值"), (1.679e-7, "原方案 alpha 对照值"),
    (1.6885553471e-7, "session-2 精确 alpha"), (0.5481, "session-2 偏差 (%)"),
    (5.1518, "session-2 对照值"), (9.2226, "session-2 对照值"),
    (10.9355, "session-2 对照值"), (11.3595, "session-2 对照值"),
    (1.4184725188, "session-2 特征根"), (4.1664696010, "session-2 特征根"),
    (7.2084784644, "session-2 特征根"), (10.3082731535, "session-2 特征根"),
    (1.989, "session-2 收敛比"), (4.039, "session-2 收敛比"),
    (1.991, "session-2 收敛比"), (4.171, "session-2 收敛比"),
    (1.995, "session-2 收敛比"), (4.827, "session-2 收敛比"),
    (3.4936501265e-6, "session-2 数值-解析一致度 K"),
    (4.1861810290e-2, "session-2 线性化误差"), (837.2, "session-2 倍数"),
    (800, "session-2 倍数表述"), (1.503e-5, "session-3 对照值"),
    (6.65961e-6, "session-2 对照值"), (70.7317, "session-2 对照值"),
    (7.5472916081e-2, "session-2 对照值"), (48.2, "session-2 alpha 变化 (%)"),
    (1.4019076018, "session-2 对照值"), (0.13834689131, "session-2 对照值"),
    (2381.94, "session-2 对照值"), (2.8360, "session-2 Bi_m 对照"),
    (0.267798, "session-1 正特征值下界"), (16.816152, "session-1 正特征值上界"),
    (7.4683, "session-1 阈值"), (0.1189, "session-1 误用阈值"),
    (8.9, "session-1 溢出时刻"), (66, "session-1 正特征值个数"),
    (4.0295e-2, "session-1 对照值"), (4.477269727e-6, "session-1 对照值"),
    (9018.421922, "session-1 比值"), (4.5e-6, "session-1 对照值"),
    (9.5e-5, "session-1 已撤销的对照值"), (3.742e-6, "session-1 不确定度"),
    (1.171e-5, "session-1 不确定度"), (2.36e-4, "session-1 对照值"),
    (0.312, "session-3 拟合误差"), (0.673, "session-3 拟合误差"),
    (2.333, "session-3 拟合误差"), (5.410, "session-3 拟合误差"),
    (4.199e-3, "session-3 raw PL 误差"), (4.211e-2, "session-3 三次拟合误差"),
    (4.936e-2, "session-3 二次拟合误差"), (5.617e-2, "session-3 指数拟合误差"),
    (1.630e-1, "session-3 线性拟合误差"), (2.320e-3, "session-3 PL vs PCHIP 差"),
    (3.500e-2, "session-3 输入侧差"), (35, "session-3 倍数"),
    (4.514e-5, "session-3 对照值"), (1.935e-7, "session-3 对照值"),
    (3.010e-6, "session-3 对照值"), (1.137e-13, "session-3 对照值"),
    (4.1913e-2, "session-3 对照值"), (838, "session-3 倍数"),
    (3.01e-6, "session-3 中心含水率变化"), (2.549992, "session-3 对照值"),
    (0.1789, "session-2 对照值"), (2.5499923, "session-2 对照值"),
    (3.9e-16, "session-2 特征值"), (569, "session-2 输出 KB"),
    # 已被修正取代的历史值, 仅作为"修正记录"被引用 (不是现行结果)
    (9.667e-2, "已修正的历史值: 系数冻结分支 Jacobian 的旧偏差 (见 problem2_slove.md 修正记录)"),
    (9.667, "同上, 以 ×10^-1 写出的形式"),
    (4.0754e4, "已废弃的历史值: q2_energy_exact.py 因重复温标换算得到的伪源项"),
    (1565.6, "已废弃的历史值: 上述错误伪源项占主项的比例 (%)"),
    (4.0754e-4, "对照: 同上的另一种写法"),
    (1565.59, "对照: 同上的更高精度写法"),
    # 并发会话 (session 9) 在 problem2_slove.md §7.3 新增的"表3/表4 时刻余量"断言.
    # 该文件不在本次交付范围内, 其对应注册行尚未由该会话补入; 这两个 token
    # 是本注册表无法复算的**待补项**, 此处显式登记原因而非静默放过.
    (3.8e-6, "待补: session-9 §7.3 的'表3/表4 时刻水分余量'上界 (其注册行未提供)"),
    (7.7, "待补: 上述余量占半 ulp 阈值的比例 (%)"),
    (10.1, "session-1 水量失衡 (%)"), (10.10, "session-1 水量失衡"),
    (10.12, "session-1 水量失衡"), (6.35e-2, "session-1 对照值"),
    (0.68, "session-1 对照值"), (1.2e-7, "session-1 对照值"),
    (4.8e-4, "session-1 对照值"), (3.36e11, "session-1 D 跨越倍数"),
    (1.855e-11, "session-1 D(0.15)"), (1.471e-20, "session-1 D(0.0331)"),
    (1.51026, "session-1 表面含水率"), (2.54999, "session-1 含水率上界"),
    (787.8, "session-1 失稳时刻"), (805.0, "session-1 失稳时刻"),
    (817.3, "session-1 失稳时刻"), (381, "独立核验日志的失稳时刻"),
    (394, "独立核验日志的失稳时刻"), (0.023, "session-1 结构"),
    # 与问题一对照的物性数 (只作对照, 不是本文计算结果)
    (976.40, "附录3 rho(2.55), 见注册表 A_rho_2.55"),
    (0.48296, "附录3 k(2.55), 见注册表 A_k_2.55"),
]


def _allow():
    d = {}
    for v, why in ALLOW_RAW:
        d.setdefault(float(v), why)
    return d


ALLOW = _allow()


# ---------------------------------------------------------------------------
def latex_to_plain(s: str) -> str:
    # 章节号引用整体消除, 否则 "§11.2-11.3" 的 "-11.3" 会被当成数值
    s = re.sub(r"§\s*\d+(?:\.\d+)*(?:\s*[-–—]\s*\d+(?:\.\d+)*)?", " ", s)
    s = re.sub(r"\\(ding|phantom)\{[^{}]*\}", "", s)
    s = re.sub(r"\\(hspace|vspace|hskip|vskip)\*?\{[^{}]*\}", "", s)
    s = re.sub(r"\\(begin|end)\{[^{}]*\}", "", s)
    s = re.sub(r"\\(label|ref|eqref|cite|cref|tag)\{[^{}]*\}", "", s)
    # 版面/表格参数: \renewcommand{\arraystretch}{1.38}、\setlength{\x}{3em}、
    # 以及 tabular 的列宽说明 p{0.665}/m{..}/b{..} —— 这些都是排版参数, 不是测算值.
    # **必须整条消掉**: 早先只把它们加进允许清单, 结果是掩盖症状 —— 文稿里每加一处
    # 新的列宽就要再补一条 allow, 且 0.665 这类值一旦与某个注册值接近就会**误配**.
    s = re.sub(r"\\(renewcommand|newcommand|providecommand|setlength|addtolength)"
               r"\*?\{[^{}]*\}(?:\{[^{}]*\})?", "", s)
    s = re.sub(r"(?<![A-Za-z])(?:p|m|b)\{[^{}]*\}", "", s)
    s = re.sub(r"\\(textwidth|linewidth|columnwidth|textheight)", "", s)
    s = re.sub(r"\\extracolsep\{[^{}]*\}", "", s)
    s = re.sub(r"\\quad|\\qquad", " ", s)
    s = re.sub(r"\\(left|right|bigl|bigr|Bigl|Bigr|boxed|underbrace|overbrace)\b", "", s)
    s = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r"e\1", s)
    s = re.sub(r"(?<![0-9])10\^\{?(-?\d+)\}?", r"1e\1", s)
    s = re.sub(r"\\times", "x", s)
    s = s.replace("\\%", "%").replace("\\ ", " ").replace("\\,", "")
    s = re.sub(r"\\(dfrac|tfrac|frac)\{([^{}]*)\}\{([^{}]*)\}", r"(\2)/(\3)", s)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"[_^]\{[^{}]*\}", "", s)
    s = re.sub(r"[_^][0-9]", "", s)
    return s


def is_structural(line, span):
    a, _ = span
    if "§" in line[max(0, a - 2):a]:
        return True
    if HEADING_RE.match(line) and line.lstrip().startswith("#"):
        m = NUM_RE.search(line)
        if m and m.span() == span:
            return True
    return False


def load_registry():
    """读入全部注册表.

    兼容两种格式: 带 `value` 列的 (各 q2_* 脚本的新格式), 以及不带 `value` 列的
    (如 outputs/registry_q2_latent_heat.csv 的宽表格式)。后者扫描**每一列**,
    每列以 "id=列名" 登记, 否则该注册表会被静默忽略 —— 这一点已实际踩过:
    IAPWS-95 的 h_fg / p_sat 表因此全部未匹配。
    """
    vals = {}
    for path in REGISTRIES:
        if not os.path.exists(path):
            print(f"  [warn] 注册表不存在: {path}")
            continue
        with open(path, encoding="utf-8-sig") as f:
            rd = csv.DictReader(f)
            fields = rd.fieldnames or []
            wide = "value" not in fields
            for r in rd:
                if wide:
                    for c in fields:
                        if c in ("id", "quantity", "unit", "uncertainty",
                                 "source", "command", "note"):
                            continue
                        for tok in NUM_RE.findall(latex_to_plain(str(r.get(c, "")))):
                            try:
                                vals.setdefault(float(tok), f"{os.path.basename(path)}:{c}")
                            except ValueError:
                                pass
                else:
                    v = str(r.get("value", ""))
                    for tok in NUM_RE.findall(latex_to_plain(v)):
                        try:
                            vals.setdefault(float(tok), r.get("id", "?"))
                        except ValueError:
                            pass
    return vals


def _written_tol(tok: str) -> float:
    s = tok.strip().lower()
    if "e" in s:
        mant, _, exp = s.partition("e")
        try:
            e = int(exp)
        except ValueError:
            return 0.0
        dec = len(mant.split(".")[1]) if "." in mant else 0
        return 0.5 * (10.0 ** (-dec)) * (10.0 ** e) * 1.5
    dec = len(s.split(".")[1]) if "." in s else 0
    return 0.5 * (10.0 ** (-dec)) * 1.5


def find_match(x, reg, tok=None, pct=False):
    if x in reg:
        return reg[x], 0.0
    if pct:
        cand = x / 100.0
        if cand in reg:
            return reg[cand], 0.0
        tol = _written_tol(tok) / 100.0 if tok else 5e-7
        best, bdev = None, None
        for rv, rid in reg.items():
            d = abs(cand - rv)
            if d <= tol and (bdev is None or d < bdev):
                best, bdev = rid, d
        if best is not None:
            return best, bdev
    tol = _written_tol(tok) if tok else 5e-5
    best, bdev = None, None
    for rv, rid in reg.items():
        d = abs(x - rv)
        if d <= tol and (bdev is None or d < bdev):
            best, bdev = rid, d
    if best is not None:
        return best, bdev
    # 绝对值匹配: 正文常以"比…低 1.3715 K"的形式给出量值, 而注册表存
    # 带符号的差值 -1.371505877 (AB_Tr=0_d). 只比对量值, 并在报告里
    # 标出该 token 命中的是注册值的绝对值, 以免把符号错误地放过.
    tol = _written_tol(tok) if tok else 5e-5
    ax = abs(x)
    for rv, rid in reg.items():
        d = abs(ax - abs(rv))
        if d <= tol and (bdev is None or d < bdev):
            best, bdev = rid + "|abs", d
    return best, bdev


# ---------------------------------------------------------------------------
def exact_table_check():
    """第二关: 文稿与 table3/4 的表值 == result2.xlsx (4 位小数逐位)."""
    from openpyxl import load_workbook

    wb = load_workbook(XLSX, data_only=True, read_only=True)

    def grid(ws):
        rows = list(ws.iter_rows(values_only=True))
        hdr = np.array([float(h) for h in rows[0][1:]])
        tt = np.array([float(r[0]) for r in rows[1:]])
        vv = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
        return hdr, tt, vv

    rh, tt, T = grid(wb["温度"])
    _, _, C = grid(wb["水分浓度"])
    wb.close()
    cols = [int(np.where(np.isclose(rh, r))[0][0]) for r in R_CM]
    trow = {int(t): i for i, t in enumerate(tt)}

    issues, checked = [], 0
    doc = os.path.join(ROOT, "model", "problem2_slove.md")
    # 文稿中形如 | 0.5 | a | b | c | d | e | 的表行 (时间列为小时)
    pat = re.compile(r"^\|\s*(\d+\.\d)\s*\|((?:\s*-?\d+\.\d+\s*\|){5})\s*$")
    blocks, cur = [], []
    for line in open(doc, encoding="utf-8"):
        m = pat.match(line)
        if m:
            cur.append((float(m.group(1)),
                        [float(x) for x in m.group(2).strip().strip("|").split("|")]))
        else:
            if cur:
                blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    for k, blk in enumerate(blocks):
        arr = (T, C)[k] if k < 2 else None
        if arr is None:
            continue
        for th, vals in blk:
            tsec = int(round(th * 3600))
            exp = [round(float(arr[trow[tsec], j]), 4) for j in cols]
            checked += 5
            if vals != exp:
                issues.append((os.path.basename(doc), th, vals, exp))

    for f, arr in ((os.path.join(OUT, "table3_temperature.md"), T),
                   (os.path.join(OUT, "table4_moisture.md"), C)):
        for line in open(f, encoding="utf-8").read().splitlines():
            if not line.startswith("|") or "---" in line or "时间" in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            tsec = int(round(float(parts[0]) * 3600))
            exp = [f"{arr[trow[tsec], j]:.4f}" for j in cols]
            checked += 5
            if parts[1:] != exp:
                issues.append((os.path.basename(f), parts[0], parts[1:], exp))

    for f, arr in ((os.path.join(OUT, "table3_temperature.csv"), T),
                   (os.path.join(OUT, "table4_moisture.csv"), C)):
        rows = list(csv.reader(open(f, encoding="utf-8-sig")))[1:]
        for r in rows:
            tsec = int(round(float(r[0]) * 3600))
            exp = [f"{arr[trow[tsec], j]:.4f}" for j in cols]
            checked += 5
            if r[1:] != exp:
                issues.append((os.path.basename(f), r[0], r[1:], exp))
    return checked, issues


def tex_q2_lines():
    """取出 paper/example.tex 中需要纳入对账的若干段落.

    返回 [(label, lo, hi, lines), ...]. 目前两段:
      * 摘要 (\\begin{abstract} .. \\end{abstract}) —— 里面也有问题二的结果句
      * 问题二小节 (\\subsection{问题二...} .. \\subsection{问题三...})
    只按 \\subsection 划界是为了不把其它问题的历史数字卷入对账.
    """
    if not os.path.exists(TEX):
        return []
    lines = open(TEX, encoding="utf-8").read().splitlines()
    out = []

    def find(pred, start=0):
        return next((i for i in range(start, len(lines)) if pred(lines[i])), None)

    i0 = find(lambda l: l.strip().startswith(r"\begin{abstract}"))
    i1 = find(lambda l: l.strip().startswith(r"\end{abstract}"), i0 + 1) if i0 is not None else None
    if i0 is not None and i1 is not None:
        out.append(("摘要", i0, i1, lines[i0:i1]))

    j0 = find(lambda l: l.startswith(TEX_BEGIN))
    j1 = find(lambda l: l.startswith(TEX_END), j0 + 1) if j0 is not None else None
    if j0 is not None and j1 is not None:
        out.append(("问题二小节", j0, j1, lines[j0:j1]))

    k0 = find(lambda l: l.startswith(TEX_BEGIN4))
    k1 = find(lambda l: l.startswith(TEX_END4), k0 + 1) if k0 is not None else None
    if k0 is not None and k1 is not None:
        out.append(("问题四小节", k0, k1, lines[k0:k1]))

    # 附录 (session 22 新增的四节 + 结果文件节): 附录中的推导与数据表同样要可追溯
    a0 = find(lambda l: l.startswith(r"\begin{appendices}"))
    a1 = find(lambda l: l.startswith(r"\end{appendices}"), a0 + 1) \
        if a0 is not None else None
    if a0 is not None and a1 is not None:
        out.append(("附录", a0, a1, lines[a0:a1]))
    return out


TEX_ROW_RE = re.compile(r"^\s*(\d+\.\d)\s*&((?:\s*-?\d+\.\d+\s*&){4}\s*-?\d+\.\d+\s*)\\\\")


def tex_table_check():
    """第四关: 论文表3/表4 的表行 与 result2.xlsx 在 4 位小数上逐位相同."""
    from openpyxl import load_workbook

    segs = tex_q2_lines()
    q2 = next((s for s in segs if s[0] == "问题二小节"), None)
    if q2 is None:
        return 0, [], "未找到 example.tex 的问题二小节"
    _lab, lo, _hi, lines = q2
    wb = load_workbook(XLSX, data_only=True, read_only=True)

    def grid(ws):
        rows = list(ws.iter_rows(values_only=True))
        hdr = np.array([float(h) for h in rows[0][1:]])
        tt = np.array([float(r[0]) for r in rows[1:]])
        vv = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
        return hdr, tt, vv

    rh, tt, T = grid(wb["温度"])
    _, _, C = grid(wb["水分浓度"])
    wb.close()
    cols = [int(np.where(np.isclose(rh, r))[0][0]) for r in R_CM]
    trow = {int(t): i for i, t in enumerate(tt)}

    issues, checked, tbl = [], 0, -1
    for ln, raw in enumerate(lines, start=(lo + 1)):
        if r"\label{tab:q2t3}" in raw:
            tbl = 0
            continue
        if r"\label{tab:q2t4}" in raw:
            tbl = 1
            continue
        m = TEX_ROW_RE.match(raw)
        if m is None or tbl < 0:
            continue
        th = float(m.group(1))
        vals = [x.strip() for x in m.group(2).strip().strip("&").split("&")]
        tsec = int(round(th * 3600))
        arr = (T, C)[tbl]
        exp = [f"{arr[trow[tsec], j]:.4f}" for j in cols]
        checked += 5
        if vals != exp:
            issues.append((f"example.tex 表{'34'[tbl]}", th, vals, exp))
    return checked, issues, ""


def main():
    reg = load_registry()
    print(f"注册表条目: {len(reg)} 个不同数值")
    print(f"允许清单:   {len(ALLOW)} 个数值\n")

    segs = tex_q2_lines()
    scan_targets = [(d, None) for d in DOCS]
    for lab, lo, hi, content in segs:
        scan_targets.append((TEX, (lab, lo, hi, content)))
        print(f"论文{lab}: example.tex 第 {lo+1}~{hi} 行 ({len(content)} 行) 纳入对账")
    if not segs:
        print("  [warn] 未在 example.tex 中找到摘要/问题二小节, 跳过\n")
    print()

    rows, unmatched = [], []
    for doc, extra in scan_targets:
        if extra is None:
            name = os.path.basename(doc)
            src_lines = list(enumerate(open(doc, encoding="utf-8"), 1))
        else:
            lab, lo, _hi, content = extra
            name = f"{os.path.basename(doc)}({lab})"
            src_lines = list(enumerate(content, lo + 1))
        for ln, raw in src_lines:
            line = latex_to_plain(raw)
            if set(line.strip()) <= set("|-: \n"):
                continue
            # 图宽与框宽是排版参数, 不对账
            if "\\includegraphics" in raw or "minipage" in raw:
                continue
            for m in NUM_RE.finditer(line):
                tok = m.group(0)
                if is_structural(line, m.span()) or tok in LAYOUT_NUMS:
                    continue
                try:
                    x = float(tok)
                except ValueError:
                    continue
                ctx = line.strip()[:90]
                pct = line[m.end():m.end() + 3].lstrip().startswith("%")
                if x in ALLOW:
                    rows.append([name, ln, tok, x, "ALLOW", ALLOW[x], 0.0, ctx])
                    continue
                rid, dev = find_match(x, reg, tok, pct)
                if rid is not None:
                    rows.append([name, ln, tok, x, "REGISTRY", rid, f"{dev:.3e}", ctx])
                else:
                    rows.append([name, ln, tok, x, "UNMATCHED", "", "", ctx])
                    unmatched.append((name, ln, tok, ctx))

    with open(REPORT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["document", "line", "token", "value", "status", "source",
                    "rel_dev", "context"])
        w.writerows(rows)

    n_reg = sum(1 for r in rows if r[4] == "REGISTRY")
    n_all = sum(1 for r in rows if r[4] == "ALLOW")
    print(f"第一关: 扫描数值字面量 {len(rows)} 个")
    print(f"  对到注册表: {n_reg}")
    print(f"  允许清单:   {n_all}")
    print(f"  未对上:     {len(unmatched)}")

    print()
    print("=" * 100)
    print("第二关: 表3/表4 / problem2_slove.md 表行  vs  result2.xlsx (4 位小数逐位相同)")
    print("=" * 100)
    issues = []
    if os.path.exists(XLSX):
        checked, issues = exact_table_check()
        print(f"  比对 {checked} 个表格数值")
        if issues:
            print(f"  !! 不一致 {len(issues)} 处:")
            for src, t_, got, exp in issues[:20]:
                print(f"     {src} t={t_}: 文件={got} xlsx={exp}")
        else:
            print("  全部逐位一致。")
    else:
        print(f"  [skip] 未找到 {XLSX}")
    print(f"\n报告: {REPORT}")

    if unmatched:
        print("=" * 100)
        print("未对上的数值 (需逐一处理: 补注册表 / 修正文稿 / 加入允许清单并说明)")
        print("=" * 100)
        seen = {}
        for n, ln, tok, ctx in unmatched:
            seen.setdefault(tok, []).append((n, ln, ctx))
        for tok, occ in sorted(seen.items(), key=lambda kv: -len(kv[1])):
            print(f"\n  token={tok!r}  出现 {len(occ)} 次")
            for n, ln, ctx in occ[:3]:
                print(f"      {n}:{ln}  {ctx}")
    else:
        print("所有数值均已对到注册表或允许清单 (第一关)。")

    if issues:
        print(f"\n第二关失败: {len(issues)} 处表格值与 result2.xlsx 不一致。")
        raise SystemExit(2)
    print("第二关通过: 所有输出表格与 result2.xlsx 逐位一致。")

    print()
    print("=" * 100)
    print("第四关: paper/example.tex 表3/表4 的表行  vs  result2.xlsx (4 位小数逐位相同)")
    print("=" * 100)
    t_checked, t_issues, t_note = tex_table_check()
    if t_note:
        print(f"  [skip] {t_note}")
    else:
        print(f"  比对 {t_checked} 个表格数值")
        if t_issues:
            print(f"  !! 不一致 {len(t_issues)} 处:")
            for src, t_, got, exp in t_issues[:20]:
                print(f"     {src} t={t_}: tex={got} xlsx={exp}")
        else:
            print("  表3/表4 与 result2.xlsx 逐位一致。")
    if t_issues:
        print(f"\n第四关失败: {len(t_issues)} 处 tex 表值与 result2.xlsx 不一致。")
        raise SystemExit(2)
    print("第四关通过: 论文表3/表4 与 result2.xlsx 逐位一致。")


if __name__ == "__main__":
    main()
