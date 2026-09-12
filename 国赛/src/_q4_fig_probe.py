# -*- coding: utf-8 -*-
"""诊断: 判定 fig_q4_schematic 的 text-stroke 碰撞来自哪个面板."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
src = io.open(os.path.join(ROOT, "src", "q4_figures.py"), encoding="utf-8").read()

probe = src.replace('lab = ["0 h", "3 h", "10 h", "51.1 h"]',
                    'lab = ["AAA", "3 h", "10 h", "51.1 h"]')
probe = probe.replace('        ax.text(0.5, yc + 0.062, lb,',
                      '        ax.text(0.5, yc + 0.062, "BBB" if lb == "AAA" else lb,')
probe = probe.replace('save_gated(fig, "fig_q4_schematic")',
                      'FS.save(fig, "_probe_schematic")')
probe = probe.replace('if __name__ == "__main__":\n    main()\n', '')
g = {"__name__": "__probe__", "__file__": os.path.join(ROOT, "src", "q4_figures.py")}
exec(compile(probe, "probe", "exec"), g)
g["fig_schematic"]()
print("probe saved")
