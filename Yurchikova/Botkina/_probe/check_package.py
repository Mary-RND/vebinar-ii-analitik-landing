"""Проверка пакета передачи: архив открывается, все файлы на месте и читаемы."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "output" / "Анализ_закупок_МНКЦ_им_С.П._Боткина_2025.zip"

REQUIRED = [
    "REPORT_Botkin_2025.pdf",
    "REPORT_Botkin_2025.docx",
    "dashboard.html",
    "ММНКЦ_Боткина_2025_аналитика.xlsx",
    "Реестр_позиций_Боткина_2025.xlsx",
    "Реестр_позиций_Боткина_2025.csv",
    "Методика_и_паспорт_данных.pdf",
    "Методика_и_паспорт_данных.docx",
    "Инструкция_по_работе_с_дашбордом.pdf",
    "Инструкция_по_работе_с_дашбордом.docx",
]

bad = 0
with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    print(f"архив: {ZIP.name} — {ZIP.stat().st_size / 1024 / 1024:.1f} МБ, {len(names)} записей")
    for r in REQUIRED:
        ok = r in names
        bad += 0 if ok else 1
        print(f"  {'OK ' if ok else 'НЕТ'} {r}")
    readme = [n for n in names if n.endswith(".txt")]
    if readme:
        txt = z.read(readme[0]).decode("utf-8")
        print(f"  опись: {readme[0]} ({len(txt)} символов), "
              f"упоминаний файлов: {sum(1 for r in REQUIRED if r in txt)} из {len(REQUIRED)}")
    # целостность архива
    broken = z.testzip()
    print("  целостность архива:", "OK" if broken is None else f"ПОВРЕЖДЁН {broken}")
    bad += 0 if broken is None else 1
print("ИТОГ:", "пакет готов" if bad == 0 else f"проблем: {bad}")
