"""Этап 0.2: проверка вариантов поиска контрактов заказчика.

Сравнивает выдачу по:
  * searchString=Боткина (широкий, с ложными совпадениями);
  * searchString=7714082636 (ИНН);
  * customerInn=7714082636 (параметр фильтра).

Пишет: сколько всего найдено, сколько блоков на первой странице, какие заказчики.
Запуск: python probe_search.py
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
    if not m:
        return "—"
    return norm(re.sub(r"<[^>]+>", " ", m.group(1)))


def customers(html: str) -> collections.Counter:
    doc = LH.fromstring(html)
    cnt: collections.Counter = collections.Counter()
    for b in doc.xpath("//div[contains(@class,'search-registry-entry-block')]"):
        t = norm(b.text_content())
        i = t.find("Заказчик")
        j = t.find("Контракт", i)
        if i >= 0:
            cnt[norm(t[i + 8:j if j > 0 else i + 200])[:120]] += 1
    return cnt


def url_variant(kind: str, page: int = 1) -> str:
    base = "https://zakupki.gov.ru/epz/contract/search/results.html?"
    tail = (
        "&morphology=on&fz44=on&contractStageList=0,1,2,3"
        f"&contractDateFrom={cfg.DATE_FROM}&contractDateTo={cfg.DATE_TO}"
        f"&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber={page}"
    )
    if kind == "query":
        return base + f"searchString={quote('Боткина')}" + tail
    if kind == "inn":
        return base + f"searchString={INN}" + tail
    return base + f"searchString=&customerInn={INN}" + tail


def main() -> None:
    warmup()
    lines: list[str] = []
    for kind, title in (("query", "searchString=Боткина"),
                        ("inn", "searchString=7714082636"),
                        ("innparam", "customerInn=7714082636")):
        url = url_variant(kind)
        html = fetch(url)
        doc = LH.fromstring(html)
        blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
        cnt = customers(html)
        lines.append(f"=== {title} ===")
        lines.append(f"Всего: {total_of(html)} · блоков на стр.1: {len(blocks)}")
        for name, n in cnt.most_common(5):
            lines.append(f"   {n:>3}  {name}")
        lines.append("")
        (OUT / f"search_{kind}.html").write_text(html, encoding="utf-8")
    (OUT / "search_variants.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / 'search_variants.txt'}")


if __name__ == "__main__":
    main()
