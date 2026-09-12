# -*- coding: utf-8 -*-
import io, csv, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("registry_q2_moist_diag.csv", "registry_q2_conv.csv", "registry_q2_app2_vs_app3.csv",
          "registry_q2_latent_heat.csv"):
    print("=" * 24, p)
    rows = list(csv.DictReader(io.open(os.path.join(ROOT, "outputs", p), encoding="utf-8-sig")))
    for r in rows:
        print(f"  {r['id']:<26} {r['value']:<26} {r['unit'][:14]:<14} {r['quantity'][:64]}")
