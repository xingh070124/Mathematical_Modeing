"""数据解析模块：解析 .blocks / .nets / .pl 附件文件。

问题一仅用到 .blocks（HardBlock 名称与宽高），但为便于问题二/三复用，
一并解析 .nets（线网）与 .pl（Terminal 固定坐标）。
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

_NUM_RE = re.compile(r"-?\d+")
_XY_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


@dataclass
class Dataset:
    name: str
    names: list[str] = field(default_factory=list)          # 与 widths/heights 同序
    widths: list[int] = field(default_factory=list)
    heights: list[int] = field(default_factory=list)
    terminal_names: list[str] = field(default_factory=list)
    nets: list[list[str]] = field(default_factory=list)     # 每条线网的引脚名列表
    terminal_pos: dict[str, tuple[int, int]] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.names)

    @property
    def total_area(self) -> int:
        return sum(w * h for w, h in zip(self.widths, self.heights))


def parse_blocks(path: str) -> list[tuple[str, str, int, int]]:
    """返回 [(name, kind, w, h), ...]，kind ∈ {'block','terminal'}。

    硬块尺寸由矩形四个角点坐标的包围盒给出；终端无尺寸信息。
    """
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("Num"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name, kind = parts[0], parts[1]
            if kind == "terminal":
                out.append((name, kind, 0, 0))
            elif kind == "block":
                pts = _XY_RE.findall(line)
                xs = [int(a) for a, _ in pts]
                ys = [int(b) for _, b in pts]
                w = max(xs) - min(xs) if xs else 0
                h = max(ys) - min(ys) if ys else 0
                out.append((name, kind, w, h))
    return out


def parse_nets(path: str) -> list[list[str]]:
    nets: list[list[str]] = []
    if not os.path.exists(path):
        return nets
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("Num"):
            i += 1
            continue
        m = re.match(r"NetDegree\s*:\s*(\d+)", ln)
        if m:
            deg = int(m.group(1))
            pins = lines[i + 1 : i + 1 + deg]
            nets.append(pins)
            i += 1 + deg
        else:
            i += 1
    return nets


def parse_pl(path: str) -> dict[str, tuple[int, int]]:
    pos: dict[str, tuple[int, int]] = {}
    if not os.path.exists(path):
        return pos
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    pos[parts[0]] = (int(parts[1]), int(parts[2]))
                except ValueError:
                    continue
    return pos


def load_dataset(data_dir: str, name: str) -> Dataset:
    blocks = parse_blocks(os.path.join(data_dir, f"{name}.blocks"))
    ds = Dataset(name=name)
    for bname, kind, w, h in blocks:
        if kind == "block":
            ds.names.append(bname)
            ds.widths.append(w)
            ds.heights.append(h)
        else:
            ds.terminal_names.append(bname)
    ds.nets = parse_nets(os.path.join(data_dir, f"{name}.nets"))
    ds.terminal_pos = parse_pl(os.path.join(data_dir, f"{name}.pl"))
    return ds


def dataset_stats(ds: Dataset) -> dict:
    return {
        "数据集": ds.name,
        "HardBlock数": ds.n,
        "Terminal数": len(ds.terminal_names),
        "线网数": len(ds.nets),
        "总面积A": ds.total_area,
    }
