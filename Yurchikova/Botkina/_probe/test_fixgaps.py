"""Проверка stage_fixgaps на копии данных (без изменения рабочих файлов)."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import collect as C  # noqa: E402

state = ROOT / "_probe" / "fixgaps_state.json"
if state.exists():
    state.unlink()

tmp_dir = ROOT / "_probe" / "fixtest"
if tmp_dir.exists():
    shutil.rmtree(tmp_dir)
tmp_dir.mkdir(parents=True)

src = ROOT / "data" / "botkina" / "contracts.jsonl"
lines = [l for l in src.read_text(encoding="utf-8").splitlines() if l.strip()][:40]
(tmp_dir / "contracts.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

C.D_DIR = tmp_dir
C.CONTRACTS_JSONL = tmp_dir / "contracts.jsonl"

recs = [json.loads(l) for l in lines]
for r in recs:
    price = r.get("price") or 0
    pos = r.get("positions") or []
    psum = sum((p.get("sum") or 0) for p in pos)
    if price - psum > 1:
        print("кандидат:", r["reestr"], "цена", round(price), "позиций", len(pos),
              "сумма позиций", round(psum))
        try:
            html = C.fetch(C.CARD.format(tab="payment-info-and-target-of-order", rn=r["reestr"]))
            print("   html:", len(html) if html else None)
            new = C.parse_all_positions(html) if html else []
            print("   получено позиций:", len(new), "сумма", round(sum(p.get("sum") or 0 for p in new)))
        except Exception as exc:
            print("   исключение:", type(exc).__name__, exc)

C.stage_fixgaps()
recs2 = [json.loads(l) for l in (tmp_dir / "contracts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
bad = sum(1 for r in recs2
          if (r.get("price") or 0) - sum((p.get("sum") or 0) for p in r.get("positions") or []) > 1)
print("после дозагрузки осталось с разрывом:", bad, "из", len(recs2))
state.unlink(missing_ok=True)
