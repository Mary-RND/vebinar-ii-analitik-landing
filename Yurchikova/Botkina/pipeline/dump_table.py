"""Дамп таблицы позиций контракта из кэша (отладка парсинга).

Запуск: python dump_table.py <reestr> [число строк]
"""
from __future__ import annotations

import sys
from pathlib import Path

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import fetch  # noqa: E402

RN = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 5
URL = f"https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber={RN}"


def main() -> None:
    html = fetch(URL)
    doc = LH.fromstring(html)
    for ti, table in enumerate(doc.xpath("//table"), 1):
        head = [th.text_content().strip() for th in table.xpath(".//thead//th")]
        trs = table.xpath(".//tbody/tr")
        if "Цена за единицу" not in " | ".join(head):
            continue
        print("TABLE", ti, "rows", len(trs), "head", head)
        for tr in trs[:N]:
            cells = [td.text_content().strip().replace("\n", " ")[:60] for td in tr.xpath("./td")]
            print(len(cells), cells)
            print("-" * 40)


if __name__ == "__main__":
    main()
