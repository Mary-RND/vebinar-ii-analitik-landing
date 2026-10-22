import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
recs = json.loads((ROOT / "data" / "botkina" / "contracts_list.json").read_text(encoding="utf-8"))
print("записей:", len(recs))
print(json.dumps(recs[0], ensure_ascii=False, indent=1)[:1200])
keys = set()
for r in recs:
    keys |= set(r.keys())
print("ключи:", sorted(keys))
have_price = sum(1 for r in recs if r.get("price"))
have_date = sum(1 for r in recs if r.get("signed_date"))
print("с ценой:", have_price, "с датой:", have_date)
