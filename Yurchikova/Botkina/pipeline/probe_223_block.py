"""Этап 0.2: структура блока реестра договоров 223-ФЗ.

Нужно понять, как выглядят поля и ссылки, чтобы написать отдельный сборщик:
у 223-ФЗ другая разметка, парсер 44-ФЗ не подходит.

Запуск: python probe_223_block.py
"""
from __future__ import annotations

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
    "&publishDateFrom=01.11.2024&publishDateTo=31.03.2026"
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

    lines = [f"Всего: {total} · блоков: {len(blocks)}", ""]
    for i, b in enumerate(blocks[:3], 1):
        lines.append(f"--- блок {i} ---")
        lines.append(norm(b.text_content())[:700])
        lines.append("ссылки:")
        for h in b.xpath(".//a/@href"):
            lines.append("   " + h[:180])
        lines.append("")

    (OUT / "block223.txt").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "block223.html").write_text(
        LH.tostring(blocks[0], pretty_print=True, encoding="unicode") if blocks else "",
        encoding="utf-8",
    )
    print(f"-> {OUT / 'block223.txt'} ({total})")


if __name__ == "__main__":
    main()
