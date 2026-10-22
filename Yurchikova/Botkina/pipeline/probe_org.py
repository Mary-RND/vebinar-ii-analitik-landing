"""Этап 0.2: карточка заказчика в ЕИС — ИНН/КПП/ОГРН/наименование.

Запуск: python probe_org.py <organizationId> [...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
OUT.mkdir(parents=True, exist_ok=True)
SPACES = re.compile(r"[\s\u00a0\u2009]+")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def main() -> None:
    warmup()
    ids = sys.argv[1:] or ["656294"]
    lines: list[str] = []

    for oid in ids:
        url = f"https://zakupki.gov.ru/epz/organization/view/info.html?organizationId={oid}"
        html = fetch(url)
        doc = LH.fromstring(html)
        lines.append(f"=== organizationId={oid} ===")
        lines.append(f"URL: {url}")

        title = doc.xpath("//h1//text()")
        if title:
            lines.append("H1: " + norm(" ".join(title)))

        seen: set[str] = set()
        for sec in doc.xpath("//section[contains(@class,'blockInfo__section')]"):
            t = doc.xpath(".//span[contains(@class,'section__title')]//text()", smart_strings=False)
            t = doc.xpath("//section[contains(@class,'blockInfo__section')]")
            break
        for sec in doc.xpath("//section[contains(@class,'blockInfo__section')]"):
            ttl = norm(" ".join(sec.xpath(".//span[contains(@class,'section__title')]//text()")))
            val = norm(" ".join(sec.xpath(".//span[contains(@class,'section__info')]//text()")))
            if ttl and ttl not in seen:
                seen.add(ttl)
                lines.append(f"{ttl}: {val[:250]}")

        # блок реквизитов в шапке карточки
        for block in doc.xpath("//div[contains(@class,'registry-entry__body-block')]"):
            ttl = norm(" ".join(block.xpath(".//div[contains(@class,'registry-entry__body-title')]//text()")))
            val = norm(" ".join(block.xpath(".//div[contains(@class,'registry-entry__body-value')]//text()")))
            if ttl and ttl not in seen:
                seen.add(ttl)
                lines.append(f"{ttl}: {val[:250]}")

        lines.append("")
        (OUT / f"org_{oid}.html").write_text(html, encoding="utf-8")

    (OUT / "org.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / 'org.txt'}")


if __name__ == "__main__":
    main()
