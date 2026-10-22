"""Этап 0.2: проверка контуров 223-ФЗ и связанных организаций.

1) реестр договоров 223-ФЗ по «Боткина» за 2025;
2) поиск организаций по ИНН 7714082636 (проверка, нет ли отдельных юрлиц/филиалов).

Запуск: python probe_contours.py
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path
from urllib.parse import quote

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
SPACES = re.compile(r"[\s\u00a0\u2009]+")
INN = "7714082636"


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def total_of(html: str) -> str:
    m = re.search(r"search-results__total[^>]*>(.*?)</div>", html, re.S)
    return norm(re.sub(r"<[^>]+>", " ", m.group(1))) if m else "—"


def names(html: str, marker: str = "Заказчик") -> collections.Counter:
    doc = LH.fromstring(html)
    cnt: collections.Counter = collections.Counter()
    for b in doc.xpath("//div[contains(@class,'search-registry-entry-block')]"):
        t = norm(b.text_content())
        i = t.find(marker)
        if i >= 0:
            cnt[norm(t[i + len(marker):i + len(marker) + 140])] += 1
    return cnt


def main() -> None:
    warmup()
    lines: list[str] = []

    # --- 223-ФЗ: реестр договоров
    url223 = (
        "https://zakupki.gov.ru/epz/contract223/search/results.html"
        f"?searchString={quote('Боткина')}&morphology=on"
        f"&contractDateFrom={cfg.DATE_FROM}&contractDateTo={cfg.DATE_TO}"
        "&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber=1"
    )
    html = fetch(url223)
    doc = LH.fromstring(html)
    blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
    lines.append("=== 223-ФЗ, реестр договоров ===")
    lines.append(f"Длина: {len(html)} · Всего: {total_of(html)} · блоков: {len(blocks)}")
    for name, n in names(html).most_common(6):
        lines.append(f"   {n:>3}  {name}")
    lines.append("")

    # --- организации по ИНН
    url_org = (
        "https://zakupki.gov.ru/epz/organization/search/results.html"
        f"?searchString={INN}&morphology=off&recordsPerPage=_50&pageNumber=1"
    )
    html2 = fetch(url_org)
    doc2 = LH.fromstring(html2)
    blocks2 = doc2.xpath("//div[contains(@class,'search-registry-entry-block')]")
    lines.append("=== Организации по ИНН ===")
    lines.append(f"Длина: {len(html2)} · Всего: {total_of(html2)} · блоков: {len(blocks2)}")
    for b in blocks2[:10]:
        t = norm(b.text_content())
        lines.append("   " + t[:220])
    lines.append("")

    # --- 44-ФЗ: сколько организаций-заказчиков с этим ИНН в карточках
    (OUT / "contours.txt").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "search_223.html").write_text(html, encoding="utf-8")
    (OUT / "search_org_inn.html").write_text(html2, encoding="utf-8")
    print(f"-> {OUT / 'contours.txt'}")


if __name__ == "__main__":
    main()
