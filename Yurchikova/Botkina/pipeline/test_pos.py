"""Проверка парсинга количества/единиц после правки."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect  # noqa: E402
import collect223  # noqa: E402
from eis_client import fetch  # noqa: E402

print("223 · предмет договора:")
page = fetch("https://zakupki.gov.ru/epz/contractfz223/card/contract-subject.html?reestrNumber=87714082636250002130000")
for p in collect223.parse_positions(page)[:6]:
    print(f"  {p['n']} {p['name'][:50]:<52} qty={p['qty']} unit={p['unit']!r} price={p['unit_price']}")

print("44 · позиции:")
page = fetch("https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=2771408263625001547")
for p in collect.parse_positions(page)[:4]:
    print(f"  {p['n']} {p['name'][:50]:<52} qty={p['qty']} unit={p['unit']!r} price={p['unit_price']} sum={p['sum']}")
