import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a = json.loads((ROOT / "data" / "botkina" / "analytics.json").read_text(encoding="utf-8"))
items = a["items"]
print("позиций номенклатуры всего:", len(items))
print("в 80 %-наборе:", sum(1 for i in items if i.get("in_80")))
print("категорий:", len(a["by_category"]), "в 80 %:", sum(1 for c in a["by_category"] if c.get("in_80")))
t = a["totals"]
print("sum_scope:", t["sum_scope"], "positions_in_scope:", t["positions_in_scope"])
print("coverage:", t.get("country_coverage"), "recon diff:", t.get("reconciliation_diff"))
it80 = [i for i in items if i.get("in_80")]
print("80 %-набор: позиций", len(it80), "сумма", round(sum(i["sum"] for i in it80), 2),
      "доля", round(sum(i["sum"] for i in it80) / t["sum_scope"] * 100, 2), "%")
# проверка ключей позиции
print("ключи items[0]:", sorted(items[0].keys()))
