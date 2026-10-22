"""Этап 0.2: обследование ЕИС по заказчику «Боткина».

Что делает:
  1) берёт первую страницу выдачи реестра контрактов за 2025 год;
  2) разбирает блоки и агрегирует заказчиков (наименование, число контрактов, сумма);
  3) сохраняет первый блок целиком для проверки структуры ссылок;
  4) пишет отчёт в UTF-8, чтобы не зависеть от кодировки консоли.

Запуск: python probe_customers.py [страниц]
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

LPU = cfg.get()
OUT = Path(__file__).resolve().parents[1] / "_probe"
OUT.mkdir(parents=True, exist_ok=True)

SPACES = re.compile(r"[\s\u00a0\u2009]+")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def money(s: str | None) -> float | None:
    if not s:
        return None
    s = norm(s).replace("\u00a0", " ").replace("₽", "").replace("RUB", "")
    m = re.search(r"-?\d[\d\s]*(?:[.,]\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0).replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def serp_url(page: int, search: str) -> str:
    return (
        "https://zakupki.gov.ru/epz/contract/search/results.html"
        f"?searchString={quote(search)}&morphology=on&fz44=on"
        "&contractStageList=0,1,2,3"
        f"&contractDateFrom={cfg.DATE_FROM}&contractDateTo={cfg.DATE_TO}"
        f"&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber={page}"
    )


def main() -> None:
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    warmup()

    all_rows: list[dict] = []
    first_block_html = ""
    first_page_len = 0

    for page in range(1, pages + 1):
        url = serp_url(page, LPU["query"])
        html = fetch(url)
        first_page_len = len(html)
        doc = LH.fromstring(html)
        blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
        if page == 1 and blocks:
            first_block_html = LH.tostring(blocks[0], pretty_print=True, encoding="unicode")
        for b in blocks:
            t = norm(b.text_content())
            hrefs = b.xpath(".//a/@href")
            card = next((h for h in hrefs if "contractCard/common-info" in h), None)
            reestr = re.search(r"reestrNumber=(\d+)", card).group(1) if card else None
            cust_link = next(
                (h for h in hrefs if "organization/view/info" in h or "customer" in h.lower()), None
            )
            org_id = (
                re.search(r"organizationId=(\d+)", cust_link).group(1) if cust_link else None
            )

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

            customer = between("Заказчик", ["Контракт", "Объекты закупки"])
            price = money(between("Цена контракта", ["Заключение контракта"]))
            date = between("Заключение контракта", ["Срок исполнения"])
            all_rows.append({
                "page": page, "reestr": reestr, "customer": customer,
                "price": price, "date": date, "customer_link": cust_link,
                "org_id": org_id,
            })
        print(f"page {page}: блоков {len(blocks)}", flush=True)

    # агрегация по заказчику
    agg: dict[str, dict] = collections.defaultdict(lambda: {"n": 0, "sum": 0.0, "reestr": [], "org_id": None})
    for r in all_rows:
        key = r["customer"] or "—"
        a = agg[key]
        a["n"] += 1
        a["sum"] += r["price"] or 0.0
        a["org_id"] = a["org_id"] or r.get("org_id")
        if r["reestr"]:
            a["reestr"].append(r["reestr"])

    lines = [
        f"Запрос: «{LPU['query']}» · период {cfg.DATE_FROM}–{cfg.DATE_TO}",
        f"Страниц: {pages} · контрактов в выборке: {len(all_rows)}",
        f"Длина первой страницы: {first_page_len} байт",
        "",
        "Заказчики (по убыванию числа контрактов):",
    ]
    for name, a in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
        lines.append(f"  {a['n']:>4}  {a['sum']:>16,.0f} ₽  org={a['org_id']}  {name}")
    lines += ["", "Даты заключения (первые 10):"]
    for r in all_rows[:10]:
        lines.append(f"  {r['date']}  {r['price']}  {r['customer']}  {r['reestr']}")

    (OUT / "customers.txt").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "first_block.html").write_text(first_block_html, encoding="utf-8")
    (OUT / "rows.json").write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"-> {OUT / 'customers.txt'}")


if __name__ == "__main__":
    main()
