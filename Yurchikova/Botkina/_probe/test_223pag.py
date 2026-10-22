"""Проверка пагинации позиций 223-ФЗ."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import collect223 as C  # noqa: E402

rn = sys.argv[1] if len(sys.argv) > 1 else "87714082636250003690000"
html = C.fetch(C.CARD.format(tab="contract-subject", rn=rn))
rows1 = C.parse_positions(html)
rows = C.parse_all_positions(html, rn)
print("без пагинации:", len(rows1), "с пагинацией:", len(rows))
tot = sum((p.get("qty") or 0) * (p.get("unit_price") or 0) for p in rows)
print("сумма qty×price:", f"{tot:,.2f}")
print("n-ы:", [p.get("n") for p in rows])
