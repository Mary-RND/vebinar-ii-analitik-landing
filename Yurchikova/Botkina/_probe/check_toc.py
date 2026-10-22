"""Проверка PDF: закладки ведут на страницы с соответствующим заголовком."""
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
doc = fitz.open(ROOT / "output" / "REPORT_Botkin_2025.pdf")
toc = doc.get_toc()
print(f"страниц: {len(doc)}, закладок: {len(toc)}")
bad = 0
for lvl, title, page in toc:
    text = doc[page - 1].get_text()
    key = title.split(".")[0].strip() if title[:1].isdigit() else title[:24]
    ok = key in text or title[:24] in text
    if not ok:
        bad += 1
        print(f"  !! {title!r} -> стр.{page}: заголовок не найден")
print(f"закладок с несовпадением: {bad}")
# оглавление: сверить номера страниц
text0 = doc[1].get_text()
print("\n--- первые строки оглавления (стр. 2) ---")
print("\n".join(text0.splitlines()[:12]))
doc.close()
