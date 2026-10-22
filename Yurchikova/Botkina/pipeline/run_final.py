"""Финальная сборка комплекта: данные → аналитика → отчёт → дашборд → Excel.

Запускается после завершения сбора ЕИС:
    python pipeline/run_final.py            # только сборка документов
    python pipeline/run_final.py --reload   # сначала дозагрузка обрезанных позиций
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline"
PY = sys.executable


def run(title: str, args: list[str]) -> None:
    print(f"\n=== {title} ===", flush=True)
    t0 = time.time()
    res = subprocess.run([PY, *args], cwd=PIPE, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    out = (res.stdout or "").rstrip()
    err = (res.stderr or "").rstrip()
    if out:
        print(out[-4000:])
    if err:
        print("--- stderr ---")
        print(err[-2000:])
    print(f"[{title}: код {res.returncode}, {time.time() - t0:.0f} с]", flush=True)
    if res.returncode != 0:
        raise SystemExit(f"шаг «{title}» завершился с ошибкой")


def main() -> None:
    reload = "--reload" in sys.argv

    if reload:
        # сброс состояния предыдущих прогонов дозагрузки
        for name in ("fixgaps_state.json", "fixgaps223_state.json"):
            p = ROOT / "_probe" / name
            if p.exists():
                p.unlink()
                print(f"удалён {p.name}")
        run("слив реестра 44-ФЗ", ["collect.py", "merge", "contracts_rev.jsonl"])
        run("слив реестра 223-ФЗ", ["collect223.py", "merge"])
        run("дозагрузка позиций 44-ФЗ", ["collect.py", "fixgaps"])
        run("дозагрузка позиций 223-ФЗ", ["collect223.py", "fixgaps"])
        run("сверка сумм позиций и контрактов", ["collect.py", "verify"])

    run("аналитика", ["analyze.py", "build"])
    run("рисунки отчёта", ["build_charts.py"])
    run("отчёт: Markdown", ["build_report_md.py"])
    run("отчёт: DOCX и PDF", ["render_report.py"])
    run("дашборд", ["build_dashboard.py"])
    run("рабочая книга Excel", ["export_xlsx.py"])
    run("инструкция по дашборду", ["build_dashboard_guide.py"])
    run("методика и паспорт данных", ["build_methodology.py"])
    run("пакет передачи (ZIP)", ["package_delivery.py"])
    print("\nготово")


if __name__ == "__main__":
    main()
