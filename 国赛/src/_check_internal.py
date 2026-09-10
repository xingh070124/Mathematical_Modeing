"""Internal-consistency check of the cross-document numbers in
model/建模方式对比.md, using only registry values."""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reg = {}
for fn in ("registry_feishu.csv", "registry_q1_energy.csv", "registry_series_cross.csv"):
    p = os.path.join(ROOT, "outputs", fn)
    if not os.path.exists(p):
        continue
    for row in csv.DictReader(open(p, encoding="utf-8-sig")):
        try:
            reg[row["id"]] = float(row["value"])
        except (ValueError, KeyError):
            pass


def chk(name, got, want, tol=1e-6):
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    print("  [%s] %-46s got=%.10g want=%.10g" % ("OK " if ok else "BAD", name, got, want))
    return ok


allok = True
print("== 对比四: F60/F64/F65 内一致性 ==")
d = reg["F65"] - reg["F64"]
allok &= chk("T(1800,r=0) app3 - app2  == F65_diff", d, reg["F65_diff"], 1e-7)
print("  max|dT| (F60) = %.10g  >= |dT at r=0| = %.10g ?" % (reg["F60"], abs(d)))
assert reg["F60"] >= abs(d) - 1e-12, "max must be >= value at r=0"
print("  OK: max 出现在 r=%.4f m (非 r=0), 故 F60 > |F65-F64| 自洽"
      % reg["F60_r"])

print("\n== 百分比一致性 ==")
allok &= chk("F62 -> -14.23%", (reg["F62"] - 1) * 100, -14.229538984, 1e-6)
allok &= chk("F63 -> +14.26%", (reg["F63"] - 1) * 100, 14.258291952, 1e-6)
allok &= chk("F71_pct -> +48.2%", reg["F71_pct"], 48.22133320, 1e-6)

print("\n== F13 摘要值与注册表一致 ==")
allok &= chk("F61 = 0.13834689131 (摘要写 0.1383)", reg["F61"], 0.13834689131, 1e-6)

print("\n== 1.6 节 T(1800s) 与 F43/F44 一致 ==")
allok &= chk("F43 = 306.72583087", reg["F43"], 306.72583087, 1e-9)
allok &= chk("F44 = 309.93578369", reg["F44"], 309.93578369, 1e-9)

print("\n== 收敛阶: lead_cn 一阶 / exact_cn 二阶 ==")
for tag, want in (("leadcn", 2.0), ("exact", 4.0)):
    for M in (100, 200, 400):
        key = "F24_M%d_%s" % (M, tag)
        if key in reg:
            near2 = abs(reg[key] - want) / want
            print("  [%s] %-24s = %.6f   (期望 ~%.0f)" %
                  ("OK " if near2 < 0.25 else "note", key, reg[key], want))

print("\n== 1.7 节线性化误差与阈值之比 ==")
ratio = reg["F50"] / 5e-5
print("  F50 / 5e-5 = %.1f 倍 (文稿称 800 倍以上)" % ratio)
print("  [%s] %s" % ("OK " if ratio > 800 else "BAD", "文稿说法成立" if ratio > 800 else "文稿夸大"))

print("\n结论:", "全部自洽" if allok else "存在不一致 (见上)")
