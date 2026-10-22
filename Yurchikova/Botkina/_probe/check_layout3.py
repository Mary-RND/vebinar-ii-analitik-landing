"""Проверка вёрстки PDF: текст не выходит за печатную область (поля страницы).

Учитывает, что колонтитулы (шапка/подвал) размещаются PyMuPDF у края листа.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
MM = 72 / 25.4
# поля из CSS @page: книжная 18/15/17/19 мм, альбомная 14/15/16/15 мм (т/п/л/пр)
MARGINS = {
    "portrait": (18 * MM, 15 * MM, 17 * MM, 19 * MM),
    "landscape": (14 * MM, 15 * MM, 16 * MM, 15 * MM),
}

name = sys.argv[1] if len(sys.argv) > 1 else "REPORT_Botkin_2025.pdf"
doc = fitz.open(ROOT / "output" / name)
bad = 0
for i, page in enumerate(doc, 1):
    r = page.rect
    kind = "landscape" if r.width > r.height else "portrait"
    top, right, bottom, left = MARGINS[kind]
    x_lo, x_hi = left - 2, r.width - right + 2
    y_lo, y_hi = top - 2, r.height - bottom + 2
    over = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        if not txt.strip():
            continue
        # колонтитулы у края листа — допускаем
        if y1 < 34 or y0 > r.height - 34:
            continue
        if x0 < x_lo or x1 > x_hi or y0 < y_lo or y1 > y_hi:
            over.append((round(x0), round(y0), round(x1), round(y1),
                         " ".join(txt.split())[:70]))
    if over:
        bad += 1
        print(f"стр.{i:>3} ({kind}): выход за печатную область: {over[:3]}")
print(f"страниц с выходом за печатную область: {bad} из {len(doc)}")
doc.close()
