"""Этап 0.2: вкладка «Предмет договора» 223-ФЗ — есть ли позиционная детализация.

Запуск: python probe_223_subject.py [reestrNumber]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
SPACES = re.compile(r"[\s\u00a0\u2009]+")
RN = sys.argv[1] if len(sys.argv) > 1 else "87714082636250005830000"
URL = f"https://zakupki.gov.ru/epz/contractfz223/card/contract-subject.html?reestrNumber={RN}"


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def main() -> None:
    warmup()
    html = fetch(URL)
    doc = LH.fromstring(html)

    lines = [f"URL: {URL}", f"Длина: {len(html)}", "", "Таблицы:"]
    for i, table in enumerate(doc.xpath("//table"), 1):
        head = " | ".join(norm(th.text_content()) for th in table.xpath(".//thead//th"))
        rows = table.xpath(".//tbody/tr")
        lines.append(f"  [{i}] строк={len(rows)} · {head[:300]}")
        for tr in rows[:5]:
            cells = [norm(td.text_content()) for td in tr.xpath("./td")]
            lines.append("      " + " || ".join(c[:120] for c in cells))

    body = norm(doc.text_content())
    for marker in ("Предмет договора", "Информация о товарах", "Товары", "Наименование товара"):
        i = body.find(marker)
        if i >= 0:
            lines += ["", f"Фрагмент от «{marker}»:", body[i:i + 2500]]
            break

    (OUT / f"subject223_{RN}.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / f'subject223_{RN}.txt'}")


if __name__ == "__main__":
    main()
