"""第4层（L4）：场景适配接口层（统一模型 + 开关配置）。

问题一抽象为统一配置：
  shape(形状模型) × rotation(旋转群) × outline(轮廓) × objective(目标) × nets(线网)
后续问题二至四通过切换配置复用第1-3层代码，模型主线一致。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Scenario:
    name: str
    shape: str          # 'rect' | 'polyomino'
    rotation: str       # 'C4'（90°/180°/270° 在矩形下等价于 {0°,90°}）
    outline: str        # 'free' | 'fixed' | 'search'
    objective: str      # 'area+aspect' | 'hpwl' | 'min_L' | 'area'
    nets: bool = False
    k0: int = 10        # L1 初解数 K
    kp: int = 5         # 多样性粗筛保留数 K'
    t_ils: float = 30.0  # L2 单条 Skyline+ILS 轨迹时间预算（秒）
    t_bstar: float = 20.0
    t_aspect: float = 12.0
    t_restart: float = 15.0
    nproc: int = 6
    seed: int = 2026
    cp_subset: int = 15
    cp_timeout: int = 60
    out_dir: str = "results"
    verbose: bool = True


SCENARIOS = {
    "Q1": Scenario(name="Q1", shape="rect", rotation="C4", outline="free",
                   objective="area+aspect", nets=False),
    "Q2": Scenario(name="Q2", shape="rect", rotation="C4", outline="fixed",
                   objective="hpwl", nets=True),
    "Q3": Scenario(name="Q3", shape="rect", rotation="C4", outline="search",
                   objective="min_L", nets=False),
    "Q4": Scenario(name="Q4", shape="polyomino", rotation="C4", outline="free",
                   objective="area", nets=False),
}
