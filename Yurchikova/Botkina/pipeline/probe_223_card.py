"""Этап 0.2: структура карточки договора 223-ФЗ.

Проверяем, есть ли перечень товаров с ОКПД2, количеством, ценой и страной
происхождения, и на какой вкладке он находится.

Запуск: python probe_223_card.py [reestrNumber]
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
BASE = "https://zakupki.gov.ru"


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def main() -> None:
    warmup()
    url = f"{BASE}/epz/contractfz223/card/contract-info.html?reestrNumber={RN}"
    html = fetch(url)
    doc = LH.fromstring(html)

    lines = [f"URL: {url}", f"Длина: {len(html)}", "", "Ссылки карточки:"]
    for h in sorted(set(doc.xpath("//a/@href"))):
        if "contractfz223" in h or "tab" in h.lower():
            lines.append("   " + h[:200])

    lines += ["", "Заголовки:"]
    for h in doc.xpath("//h1//text() | //h2//text() | //div[contains(@class,'title')]//text()"):
        t = norm(h)
        if t and len(t) > 3:
            lines.append("   " + t[:150])

    lines += ["", "Таблицы:"]
    for i, table in enumerate(doc.xpath("//table"), 1):
        head = " | ".join(norm(th.text_content()) for th in table.xpath(".//thead//th"))
        rows = table.xpath(".//tbody/tr")
        lines.append(f"  [{i}] строк={len(rows)} · {head[:220]}")

    lines += ["", "Текст (первые 4000):", norm(doc.text_content())[:4000]]

    (OUT / f"card223_{RN}.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / f'card223_{RN}.txt'}")


if __name__ == "__main__":
    main()
