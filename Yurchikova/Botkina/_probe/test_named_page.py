"""Проверка поддержки именованных страниц (@page wide) в Chromium."""
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent / "named_page_test.pdf"
html = """<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: A4; margin: 18mm 15mm 17mm 19mm; }
@page wide { size: A4 landscape; margin: 14mm 15mm; }
body { font-family:"Times New Roman",serif; font-size:10.5pt; margin:0; }
table { width:100%; border-collapse:collapse; font-size:8pt; }
td, th { border:0.5pt solid #999; padding:2pt 3pt; }
table.wide { page: wide; break-before: page; break-after: page; }
</style></head><body>
<p>Портретная страница до широкой таблицы.</p>
<table class="wide"><tr><th>Колонка 1</th><th>Колонка 2</th><th>Колонка 3</th><th>Колонка 4</th><th>Колонка 5</th><th>Колонка 6</th><th>Колонка 7</th><th>Колонка 8</th><th>Колонка 9</th><th>Колонка 10</th><th>Колонка 11</th><th>Колонка 12</th></tr>
<tr><td>1</td><td>Текст</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td></tr></table>
<p>Портретная страница после широкой таблицы.</p>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    pg = b.new_page()
    pg.set_content(html, wait_until="load")
    pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True,
           margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    b.close()

d = fitz.open(out)
print("страниц:", len(d))
for i, page in enumerate(d, 1):
    r = page.rect
    print(f"  стр.{i}: {r.width:.0f}x{r.height:.0f} {'альбомная' if r.width > r.height else 'книжная'} | {page.get_text().strip()[:50]!r}")
d.close()
