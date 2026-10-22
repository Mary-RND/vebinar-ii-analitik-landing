"""Проверка новых полей реестра после обогащения analyze.py."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a = json.loads((ROOT / "data" / "botkina" / "analytics.json").read_text(encoding="utf-8"))

t = a["totals"]
print("поставщиков (известных):", t["suppliers"], "| всего записей:", t["suppliers_total"])
print("позиций без поставщика:", t["positions_supplier_unknown"],
      "сумма:", t["sum_supplier_unknown"], "доля:", t["share_supplier_unknown"], "%")

pos = a["positions"]
print("\nпозиций:", len(pos))
print("поля позиции:", sorted(pos[0].keys()))

prof = [p for p in pos if p["scope"] in ("main", "borderline")]
for field in ("href", "supplier_inn", "trademark", "unit_norm", "country_src",
              "mixed", "comment", "supplier", "ru_number", "nkmi"):
    filled = sum(1 for p in prof if p.get(field))
    print(f"  {field:<16} заполнено у {filled:>5} из {len(prof)} ({filled / len(prof) * 100:5.1f} %)")

print("\nпример позиции:")
for k, v in sorted(prof[0].items()):
    print(f"   {k}: {str(v)[:90]}")
