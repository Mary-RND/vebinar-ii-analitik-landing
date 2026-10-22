import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(l) for l in (ROOT / "data" / "botkina" / "contracts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("контрактов:", len(rows))
p0 = rows[0]["positions"][0] if rows[0].get("positions") else {}
print("поля позиции:", sorted(p0.keys()))
print("пример позиции:", json.dumps(p0, ensure_ascii=False)[:400])

gaps = []
for c in rows:
    csum = c.get("price") or 0
    pos = c.get("positions") or []
    psum = sum((p.get("sum") or 0) for p in pos)
    gaps.append((csum - psum, c))
gaps.sort(key=lambda kv: -kv[0])
print("сумма gap:", round(sum(g for g, _ in gaps)))
print("топ-15 разрывов (контракт - позиции):")
for g, c in gaps[:15]:
    print(f"  {g/1e6:12,.2f} млн | цена={(c.get('price') or 0)/1e6:10,.2f} | позиций={len(c.get('positions') or [])} | без сумм={sum(1 for p in (c.get('positions') or []) if not p.get('sum'))}")
print("--- крупнейшие отрицательные (позиции > цены) ---")
for g, c in gaps[-10:]:
    print(f"  {g/1e6:12,.2f} млн | цена={(c.get('price') or 0)/1e6:10,.2f} | позиций={len(c.get('positions') or [])}")
