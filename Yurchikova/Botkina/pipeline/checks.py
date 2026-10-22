"""Быстрые проверки analytics.json (отладка)."""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a = json.loads((ROOT / "data" / "botkina" / "analytics.json").read_text(encoding="utf-8"))

print("страны:")
for c in a["by_country"][:12]:
    print(f"  {c['country'][:40]:<42}{c['n']:>4}{c['sum']:>14,.0f}")

est = [p for p in a["positions"] if p["estimated"]]
print("\nоценочных позиций:", len(est), "из", len(a["positions"]))
names = collections.Counter((p["name"] or "")[:60] for p in est)
for n, c in names.most_common(15):
    print(f"  {c:>3}  {n}")

print("\nконтракты с оценочными позициями (сумма контракта):")
by_c = collections.defaultdict(lambda: [0, 0.0, ""])
for p in est:
    k = p.get("name", "")[:40]
    by_c[k][0] += 1
    by_c[k][1] += p["sum"] or 0
for k, v in sorted(by_c.items(), key=lambda kv: -kv[1][1])[:10]:
    print(f"  {v[0]:>3}  {v[1]:>14,.0f}  {k}")
