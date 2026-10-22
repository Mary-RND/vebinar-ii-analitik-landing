"""Этап 0.2: разбор выдачи с флагом fz223=on.

Проверяет, действительно ли флаг переключает реестр на 223-ФЗ:
смотрит общее число, заказчиков и поля блока.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path
from urllib.parse import quote

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
SPACES = re.compile(r"[\s\u00a0\u2009]+")
URL = (
    "https://zakupki.gov.ru/epz/contractfz223/search/results.html"
    f"?searchString={quote('Боткина')}&morphology=on"
    "&publishDateFrom=01.01.2025&publishDateTo=31.12.2025"
    "&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber=1"
)


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def main() -> None:
    warmup()
    html = fetch(URL)
    doc = LH.fromstring(html)
    m = re.search(r"search-results__total[^>]*>(.*?)</div>", html, re.S)
    total = norm(re.sub(r"<[^>]+>", " ", m.group(1))) if m else "—"
    blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")

    cnt: collections.Counter = collections.Counter()
    for b in blocks:
        t = norm(b.text_content())
        i = t.find("Заказчик")
        if i >= 0:
            cnt[norm(t[i + 8:i + 150])] += 1

    lines = [f"URL: {URL}", f"Всего: {total} · блоков: {len(blocks)}", ""]
    for name, n in cnt.most_common(6):
        lines.append(f"{n:>3}  {name}")
    if blocks:
        lines += ["", "Первый блок (текст, 900 символов):", norm(blocks[0].text_content())[:900]]
    (OUT / "parse_223.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / 'parse_223.txt'}")


if __name__ == "__main__":
    main()
