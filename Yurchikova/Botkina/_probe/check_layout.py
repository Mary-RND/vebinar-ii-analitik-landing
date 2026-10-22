"""Проверка вёрстки PDF: текст/графика за пределами полей, обрезка таблиц."""
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT / "output" / "REPORT_Botkin_2025.pdf"
doc = fitz.open(pdf)
for i, page in enumerate(doc, 1):
    r = page.rect
    blocks = page.get_text("blocks")
    maxx = 0
    minx = 9999
    over = []
    for b in blocks:
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        maxx = max(maxx, x1)
        minx = min(minx, x0)
        if x1 > r.x1 - 2 or x0 < 2:
            over.append((round(x0), round(y0), round(x1), " ".join(txt.split())[:60]))
    print(f"стр.{i:>3} поля x:[{minx:.0f}..{maxx:.0f}] из {r.x1:.0f}  пересечений: {len(over)}")
    for o in over[:4]:
        print("      ", o)
doc.close()
