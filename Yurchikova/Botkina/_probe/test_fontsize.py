"""Проверка масштаба шрифта при печати PDF через Playwright."""
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "_probe" / "font_test.pdf"
html = """<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: A4; margin: 18mm 15mm 17mm 19mm; }
body { margin:0; font-family:"Times New Roman",serif; font-size:10.5pt; line-height:1.35; }
table { width:100%; border-collapse:collapse; font-size:8pt; }
td { border:0.5pt solid #999; padding:3pt 4pt; }
</style></head><body>
<p>Проверка размера основного текста. Ожидается 10,5 pt.</p>
<table><tr><td>Ячейка таблицы — ожидается 8 pt</td><td>Ещё ячейка</td></tr></table>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    pg = b.new_page()
    pg.set_content(html, wait_until="load")
    pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True,
           margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    b.close()

d = fitz.open(out)
print("страниц:", len(d), "размер:", d[0].rect)
for blk in d[0].get_text("dict")["blocks"]:
    for line in blk.get("lines", []):
        for s in line["spans"]:
            print(f"  {s['size']:.2f} pt  {s['text'][:60]!r}")
d.close()
