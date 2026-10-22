"""Проверка PDF: страницы, переполнение по ширине, наличие колонтитулов."""
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "output" / (sys.argv[1] if len(sys.argv) > 1 else "Инструкция_по_работе_с_дашбордом.pdf")
doc = fitz.open(path)
print(f"{path.name}: страниц {doc.page_count}, закладок {len(doc.get_toc())}")
for i, page in enumerate(doc):
    w = page.rect.width
    over = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1 = b[:4]
        if x1 > w - 30 or x0 < 20:
            over.append((round(x0), round(x1), " ".join(b[4].split())[:60]))
    if over:
        print(f"  стр.{i + 1}: выход за поля: {over[:3]}")
print("--- текст первой страницы ---")
print(doc[0].get_text()[:700])
print("--- текст второй страницы (начало) ---")
if doc.page_count > 1:
    print(doc[1].get_text()[:400])
