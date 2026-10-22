"""Этап 0.2: полный список контрактов заказчика за 2025 год.

Стратегия: обходим широкую выдачу по «Боткина» (все заказчики-тёзки),
фильтруем по organizationId заказчика ММНКЦ (656294) и по названию.
Карточки контрактов не загружаем — только список, чтобы оценить масштаб.

Запуск: python probe_list.py [макс.страниц]
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from eis_client import fetch, warmup  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
TARGET_ORG = "656294"
TARGET_NAME = "МНОГОПРОФИЛЬНЫЙ НАУЧНО-КЛИНИЧЕСКИЙ ЦЕНТР ИМЕНИ С.П. БОТКИНА"
SPACES = re.compile(r"[\s\u00a0\u2009]+")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def money(s: str | None) -> float | None:
    if not s:
        return None
    m = re.search(r"-?\d[\d\s\u00a0]*(?:[.,]\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0).replace("\u00a0", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def serp_url(page: int) -> str:
    return (
        "https://zakupki.gov.ru/epz/contract/search/results.html"
        f"?searchString={quote('Боткина')}&morphology=on&fz44=on"
        "&contractStageList=0,1,2,3"
        f"&contractDateFrom={cfg.DATE_FROM}&contractDateTo={cfg.DATE_TO}"
        f"&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber={page}"
    )


def main() -> None:
    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    warmup()

    rows: dict[str, dict] = {}
    stats = collections.Counter()

    for page in range(1, max_pages + 1):
        html = fetch(serp_url(page))
        doc = LH.fromstring(html)
        blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
        if not blocks:
            print(f"page {page}: пусто -> стоп", flush=True)
            break
        added = 0
        for b in blocks:
            t = norm(b.text_content())
            hrefs = b.xpath(".//a/@href")
            card = next((h for h in hrefs if "contractCard/common-info" in h), None)
            reestr = re.search(r"reestrNumber=(\d+)", card).group(1) if card else None
            org = next((h for h in hrefs if "organization/view/info" in h), None)
            org_id = re.search(r"organizationId=(\d+)", org).group(1) if org else None

            def between(start: str, end: list[str]) -> str | None:
                i = t.find(start)
                if i < 0:
                    return None
                i += len(start)
                j = len(t)
                for e in end:
                    k = t.find(e, i)
                    if k >= 0:
                        j = min(j, k)
                return norm(t[i:j])

            customer = between("Заказчик", ["Контракт", "Объекты закупки"]) or ""
            is_target = org_id == TARGET_ORG or TARGET_NAME in customer.upper()
            stats["seen"] += 1
            if org_id:
                stats[f"org_{org_id}"] += 1
            if not is_target or not reestr:
                continue
            rows[reestr] = {
                "reestr": reestr,
                "customer": customer,
                "org_id": org_id,
                "price": money(between("Цена контракта", ["Заключение контракта"])),
                "date": between("Заключение контракта", ["Срок исполнения"]),
                "status": between("№ " + reestr, ["Заказчик"]),
                "subjects": between("Объекты закупки", ["Цена контракта", "Объект закупки"]),
            }
            added += 1
        print(f"page {page}: блоков {len(blocks)}, целевых +{added}, всего {len(rows)}", flush=True)
        if len(blocks) < 50:
            break

    data = sorted(rows.values(), key=lambda r: r.get("date") or "", reverse=True)
    (OUT / "botkina_list.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    total = sum(r.get("price") or 0 for r in data)
    dates = [r["date"] for r in data if r.get("date")]
    lines = [
        f"Заказчик: {TARGET_NAME} (organizationId {TARGET_ORG})",
        f"Период: {cfg.DATE_FROM} – {cfg.DATE_TO}",
        f"Контрактов найдено: {len(data)}",
        f"Сумма по цене контрактов: {total:,.2f} ₽".replace(",", " "),
        f"Даты: от {min(dates) if dates else '—'} до {max(dates) if dates else '—'}",
        f"Просмотрено блоков: {stats['seen']}",
        "",
        "Разбивка по заказчикам в широкой выдаче:",
    ]
    for k, v in stats.most_common():
        if k.startswith("org_"):
            lines.append(f"  org {k[4:]}: {v}")
    (OUT / "list_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / 'list_report.txt'} ({len(data)} контрактов)")


if __name__ == "__main__":
    main()
