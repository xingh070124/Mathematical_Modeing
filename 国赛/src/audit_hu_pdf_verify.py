# -*- coding: utf-8 -*-
"""
audit_hu_pdf_verify.py — independent verification of claims (b)-(f) about
胡众欢等 (2020), 西南大学学报(自然科学版) 42(2):118-128, against the PDF text layer.

Read-only w.r.t. the PDF. Prints raw evidence; writes nothing.
Run:  python src/audit_hu_pdf_verify.py
"""
import sys, re, unicodedata
import fitz  # PyMuPDF

PDF = r"docs/基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf"

# PUA code points that this PDF's text layer uses for the math operators
PUA = {0xE065: "<NABLA?>", 0xE785: "<PARTIAL?>"}


def norm(s: str) -> str:
    """NFKC so fullwidth ０１ａｂ and ＋－＝ collapse to ASCII; keep PUA visible."""
    out = []
    for ch in s:
        if ord(ch) in PUA:
            out.append(PUA[ord(ch)])
        else:
            out.append(unicodedata.normalize("NFKC", ch))
    return "".join(out)


def main():
    doc = fitz.open(PDF)
    print(f"PDF pages: {doc.page_count}")
    pages = [norm(p.get_text("text")) for p in doc]
    full = "\n".join(pages)

    print("\n=== per-page image (figure) count and text length ===")
    for i, p in enumerate(doc):
        print(f"  page {i+1}: images={len(p.get_images(full=True))} "
              f"drawings={len(p.get_drawings())} textchars={len(pages[i])}")

    print("\n=== equation numbers present (NFKC) ===")
    for n in range(1, 23):
        pat = f"({n})"
        hits = full.count(pat)
        print(f"  ({n}): {hits} occurrence(s)")

    print("\n=== keyword search over the full text layer ===")
    kws = ["初始条件", "边界条件", "边界", "初始", "渗透率", "渗透系数",
           "水活度", "饱和蒸汽", "相对误差", "绝对误差", "13.3", "0.016",
           "RMSE", "均方根", "MAE", "R2", "R²", "决定系数",
           "弱耦合", "强耦合", "吸热", "吸收热量", "蒸发速率",
           "测量点", "图2", "干燥特性曲线", "表2", "时间轴", "网格", "时间步"]
    for k in kws:
        idx = [m.start() for m in re.finditer(re.escape(k), full)]
        ctx = []
        for i in idx[:4]:
            ctx.append(full[max(0, i - 40):i + 40].replace("\n", " | "))
        print(f"  {k!r}: {len(idx)} hit(s)")
        for c in ctx:
            print(f"        ...{c}...")

    print("\n=== raw text of the pages that carry eq (10) and eq (16)-(22) ===")
    for pno in (3, 4):  # 0-based: printed pp.120, 121
        print(f"\n----- page {pno+1} (printed {118+pno}) -----")
        for line in pages[pno].splitlines():
            if any(t in line for t in ["γ", "R=", "R =", "(20)", "(18)", "(19)",
                                       "(22)", "(21)", "(16)", "(10)", "吸收热量"]):
                print("  |", line)

    print("\n=== raw text of Table 1 region (pages 6-7) ===")
    for pno in (5, 6):
        print(f"\n----- page {pno+1} (printed {118+pno}) -----")
        print(pages[pno])


if __name__ == "__main__":
    main()
