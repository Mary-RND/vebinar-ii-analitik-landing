"""Проверка вёрстки PDF: текст и графика за пределами полей (по горизонтали и вертикали)."""
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv) > 1 else "REPORT_Botkin_2025.pdf"
pdf = ROOT / "output" / name
doc = fitz.open(pdf)
bad = 0
for i, page in enumerate(doc, 1):
    r = page.rect
    blocks = page.get_text("blocks")
    minx, maxx, miny, maxy = 9999, 0, 9999, 0
    over = []
    for b in blocks:
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        minx, maxx = min(minx, x0), max(maxx, x1)
        miny, maxy = min(miny, y0), max(maxy, y1)
        if x1 > r.x1 - 2 or x0 < 2 or y1 > r.y1 - 2 or y0 < 2:
            over.append((round(x0), round(y0), round(x1), round(y1),
                         " ".join(txt.split())[:60]))
    if over:
        bad += 1
        print(f"стр.{i:>3}: выход за поля: {over[:3]}")
    print(f"стр.{i:>3} x:[{minx:.0f}..{maxx:.0f}] y:[{miny:.0f}..{maxy:.0f}] "
          f"из {r.x1:.0f}x{r.y1:.0f}  за полями: {len(over)}")
print(f"\nстраниц с выходом за поля: {bad}")
doc.close()
