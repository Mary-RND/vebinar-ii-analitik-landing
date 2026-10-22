"""Отдельный документ «Методика и паспорт данных» (ТЗ § 3.2, п. 5).

Собирается из готового отчёта: разделы 2 (методика и источники) и приложения
А–В (глоссарий, классификатор, паспорт данных). Выход: PDF и DOCX.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_tools"))

from md_to_docx import convert as convert_docx  # noqa: E402
from md_to_pdf import convert as convert_pdf  # noqa: E402

REPORT_MD = ROOT / "output" / "REPORT_Botkin_2025.md"
OUT_MD = ROOT / "output" / "Методика_и_паспорт_данных.md"


def extract(text: str) -> str:
    """Выборка разделов методики и паспорта из готового отчёта."""
    lines = text.splitlines()
    starts: dict[str, int] = {}
    for i, line in enumerate(lines):
        if line.startswith("## 2. Методика и источники"):
            starts["sec2"] = i
        elif line.startswith("## 3. "):
            starts["sec3"] = i
        elif line.startswith("### Приложение ") and ": " not in line:
            letter = line.split()[2].rstrip(".")
            starts.setdefault(f"app_{letter}", i)

    def take(from_key: str, to_key: str | None) -> list[str]:
        if from_key not in starts:
            return []
        a = starts[from_key]
        b = starts.get(to_key or "", len(lines))
        return lines[a:b]

    parts: list[str] = []
    parts.append("# Методика и паспорт данных")
    parts.append("")
    parts.append("ГБУЗ «ММНКЦ им. С.П. Боткина» ДЗМ — анализ закупок за 2025 год")
    parts.append("")
    parts.append("Приложение к комплекту: отчёт, рабочая книга Excel, дашборд, реестр позиций")
    parts.append("")
    parts.append("Документ содержит методику расчётов, перечень источников и параметров выборки, "
                 "правила исключения, нормализации и дедупликации, методику определения страны "
                 "происхождения и внутренних ценовых бенчмарков, классы достоверности, "
                 "ограничения и глоссарий.")
    parts.append("")
    parts.append("---")
    parts.append("")

    parts.extend(take("sec2", "sec3"))
    parts.append("")

    # приложения А, Б, В — глоссарий, классификатор, паспорт данных
    order = ["А", "Б", "В"]
    for idx, letter in enumerate(order):
        nxt = f"app_{order[idx + 1]}" if idx + 1 < len(order) else "app_Г"
        parts.extend(take(f"app_{letter}", nxt))
        parts.append("")

    return "\n".join(parts)


def main() -> None:
    text = REPORT_MD.read_text(encoding="utf-8")
    md = extract(text)
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"-> {OUT_MD} ({len(md)} символов)")
    header = "Методика и паспорт данных — МНКЦ им. С.П. Боткина, 2025 год"
    convert_pdf(OUT_MD, OUT_MD.with_suffix(".pdf"), header, header)
    convert_docx(OUT_MD, OUT_MD.with_suffix(".docx"), header)


if __name__ == "__main__":
    main()
