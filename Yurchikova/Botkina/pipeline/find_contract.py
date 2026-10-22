"""Найти контракт по фрагменту наименования позиции."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
needle = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
rows = [json.loads(l) for l in (ROOT / "data" / "botkina" / "contracts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in rows:
    for p in r.get("positions") or []:
        if needle in (p.get("name") or "").lower():
            print(r["reestr"], r.get("price"), len(r.get("positions") or []), "|", (p.get("name") or "")[:70])
            break
