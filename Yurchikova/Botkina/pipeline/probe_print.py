"""Проверка печатной формы контракта: есть ли позиции в одном документе.

Если да — можно собирать контракт одним запросом вместо двух.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
RN = sys.argv[1] if len(sys.argv) > 1 else "2771408263625000923"
URL = f"https://zakupki.gov.ru/epz/contract/printForm/view.html?contractReestrNumber={RN}"


def main() -> None:
    warmup()
    html = fetch(URL)
    doc = LH.fromstring(html)
    lines = [f"URL: {URL}", f"Длина: {len(html)}"]
    lines.append("Таблицы:")
    for i, table in enumerate(doc.xpath("//table"), 1):
        head = " | ".join(td.text_content().strip() for td in table.xpath(".//thead//th"))
        rows = table.xpath(".//tbody/tr")
        if rows or head:
            lines.append(f"  [{i}] строк={len(rows)} · {head[:200]}")
    text = re.sub(r"\s+", " ", doc.text_content())
    for marker in ("Цена за единицу", "Наименование товара", "Халат операционный"):
        i = text.find(marker)
        lines.append(f"  маркер «{marker}»: {'найден' if i >= 0 else 'нет'}")
        if i >= 0:
            lines.append("    " + text[max(0, i - 200):i + 500])
    (OUT / f"print_{RN}.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / f'print_{RN}.txt'}")


if __name__ == "__main__":
    main()
