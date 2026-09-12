# -*- coding: utf-8 -*-
"""一次性补丁: 给 q4_solve 的 make_rhs / make_jac / solve_q4 增加灵敏度旋钮."""
import io
import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "q4_solve.py")
s = io.open(p, encoding="utf-8").read()
orig = s

# --- 1) make_rhs 签名 ---
s = s.replace(
    'def make_rhs(g, env, rad, hevap=True, params=None, form="material", eta=0.0):',
    'def make_rhs(g, env, rad, hevap=True, params=None, form="material", eta=0.0,\n'
    '             hc=None, hm=None, lv_mult=1.0):')
s = s.replace(
    '    p = APP["app4"] if params is None else params\n'
    '    R0m = float(rad.R(0.0))\n'
    '    h, hm = H_CONV, HM\n',
    '    p = APP["app4"] if params is None else params\n'
    '    R0m = float(rad.R(0.0))\n'
    '    h = H_CONV if hc is None else float(hc)\n'
    '    hm = HM if hm is None else float(hm)\n')
s = s.replace(
    '            Lv = HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)\n'
    '            flux_h = h * Rc * (T[M] - Tinf) + Lv * hm * Rc * (C[M] - Cinf)',
    '            Lv = (HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)) * lv_mult\n'
    '            flux_h = h * Rc * (T[M] - Tinf) + Lv * hm * Rc * (C[M] - Cinf)')

# --- 2) make_jac 签名 ---
s = s.replace(
    'def make_jac(g, env, rad, hevap=True, params=None, form="material"):',
    'def make_jac(g, env, rad, hevap=True, params=None, form="material",\n'
    '             hc=None, hm=None, lv_mult=1.0):')
s = s.replace(
    '    p = APP["app4"] if params is None else params\n'
    '    h, hm = H_CONV, HM\n'
    '\n    def jac(t, U):',
    '    p = APP["app4"] if params is None else params\n'
    '    h = H_CONV if hc is None else float(hc)\n'
    '    hm = HM if hm is None else float(hm)\n'
    '\n    def jac(t, U):')
s = s.replace(
    '            Lv = HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)\n'
    '            Lvp = HEVAP_SLOPE\n',
    '            Lv = (HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)) * lv_mult\n'
    '            Lvp = HEVAP_SLOPE * lv_mult\n')

# --- 3) solve_q4 签名与透传 ---
s = s.replace(
    '             form="material", rad=None, rad_mode="data", rad_scale=1.0,\n'
    '             t_span=None, rad_kind="pchip"):',
    '             form="material", rad=None, rad_mode="data", rad_scale=1.0,\n'
    '             t_span=None, rad_kind="pchip", eta=0.0, hc=None, hm=None,\n'
    '             lv_mult=1.0):')
s = s.replace(
    '    rhs = make_rhs(g, env, rad, hevap=hevap, params=params, form=form)\n'
    '    kw = {}\n'
    '    if jac_mode == "analytic":\n'
    '        kw["jac"] = make_jac(g, env, rad, hevap=hevap, params=params, form=form)',
    '    skw = dict(hc=hc, hm=hm, lv_mult=lv_mult)\n'
    '    rhs = make_rhs(g, env, rad, hevap=hevap, params=params, form=form,\n'
    '                   eta=eta, **skw)\n'
    '    kw = {}\n'
    '    if jac_mode == "analytic":\n'
    '        kw["jac"] = make_jac(g, env, rad, hevap=hevap, params=params,\n'
    '                            form=form, **skw)')

assert s != orig, "no replacement made"
io.open(p, "w", encoding="utf-8").write(s)
print("patched q4_solve.py")
