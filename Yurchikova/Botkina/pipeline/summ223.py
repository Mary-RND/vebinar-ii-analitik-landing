"""Сводка по списку 223-ФЗ: годы, суммы, размеры договоров."""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "data" / "botkina" / "contracts223_list.json").read_text(encoding="utf-8"))


def year(s: str | None) -> str:
    return (s or "")[-4:]


years = collections.Counter(year(r["signed_date"]) for r in rows)
y25 = [r for r in rows if year(r["signed_date"]) == "2025"]
prices = sorted(r["price"] or 0 for r in y25)
print("всего", len(rows), "по годам", sorted(years.items()))
print("2025:", len(y25), "сумма", f"{sum(prices):,.0f}".replace(",", " "))
print("без даты", sum(1 for r in rows if not r["signed_date"]))
if prices:
    print("max", f"{prices[-1]:,.0f}", "median", f"{prices[len(prices) // 2]:,.0f}")
    print("до 600 тыс.", sum(1 for x in prices if x <= 600_000))
    print("свыше 10 млн", sum(1 for x in prices if x > 10_000_000))
print("статусы", collections.Counter((r.get("status") or "")[:30] for r in y25).most_common(5))
