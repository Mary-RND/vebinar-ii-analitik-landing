"""Проверка парсера списка 223-ФЗ на закэшированной первой странице."""
from __future__ import annotations

import sys
from pathlib import Path

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect223 as c  # noqa: E402
from eis_client import fetch  # noqa: E402

html = fetch(c.serp_url(1))
doc = LH.fromstring(html)
blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
print("блоков:", len(blocks))
rows = [r for r in (c.parse_block(b) for b in blocks) if r]
target = [r for r in rows if r.get("customer_inn") == c.TARGET_INN]
print("распознано:", len(rows), "целевых:", len(target))
for r in target[:5]:
    print(r["reestr"], r["contract_no"], r["price"], r["signed_date"], r["placed_date"], "|", (r["customer_name"] or "")[:40])
