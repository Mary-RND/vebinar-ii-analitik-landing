"""Формирование рабочего списка контрактов из результатов этапа 0.2.

Читает _probe/botkina_list.json, приводит к формату collect.py
и пишет data/botkina/contracts_list.json.

Запуск: python make_list.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_probe" / "botkina_list.json"
DST = ROOT / "data" / cfg.DEFAULT_LPU / "contracts_list.json"


def main() -> None:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        out.append({
            "reestr": r["reestr"],
            "href": (
                "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html"
                f"?reestrNumber={r['reestr']}"
            ),
            "status": r.get("status"),
            "customer_name": r.get("customer"),
            "price": r.get("price"),
            "signed_date": r.get("date"),
            "subjects_preview": r.get("subjects"),
        })
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {DST}: {len(out)} контрактов")


if __name__ == "__main__":
    main()
