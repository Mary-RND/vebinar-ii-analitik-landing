"""Рендер отчёта: Markdown -> DOCX и PDF с оглавлением и закладками.

1. Собирает Markdown без номеров страниц и делает DOCX.
2. Рендерит PDF, определяет страницы разделов.
3. Пересобирает PDF с номерами страниц в оглавлении.
4. Добавляет интерактивные закладки (PyMuPDF set_toc).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "_tools"))

import build_report_md  # noqa: E402
import md_to_docx  # noqa: E402
import md_to_pdf  # noqa: E402

MD_PATH = ROOT / "output" / "REPORT_Botkin_2025.md"
DOCX_PATH = ROOT / "output" / "REPORT_Botkin_2025.docx"
PDF_PATH = ROOT / "output" / "REPORT_Botkin_2025.pdf"
TMP_MD = ROOT / "_probe" / "report_pdf.md"
TMP_PDF = ROOT / "_probe" / "report_pdf.pdf"
TOC_JSON = ROOT / "_probe" / "toc_pages.json"

TITLE = "Анализ закупок МНКЦ им. С.П. Боткина за 2025 год"
HEADER = "Анализ закупок МНКЦ им. С.П. Боткина — 2025"


def headings(md: str) -> list[tuple[int, str]]:
    out = []
    for line in md.splitlines():
        if line.startswith("## ") and "Содержание" not in line:
            out.append((1, line[3:].strip()))
        elif line.startswith("### "):
            out.append((2, line[4:].strip()))
    return out


def find_pages(pdf: Path, items: list[tuple[int, str]]) -> dict[str, int]:
    doc = fitz.open(pdf)
    result: dict[str, int] = {}
    for _, title in items:
        needle = " ".join(title.split())[:45]
        for i in range(2, len(doc)):
            text = " ".join(doc[i].get_text("text").split())
            if needle in text:
                result[title] = i + 1
                break
    doc.close()
    return result


def add_bookmarks(pdf: Path, items: list[tuple[int, str]], pages: dict[str, int]) -> None:
    doc = fitz.open(pdf)
    toc = [[1, "Обложка", 1], [1, "Содержание", 2]]
    for level, title in items:
        page = pages.get(title)
        if page:
            toc.append([level, title, page])
    doc.set_toc(toc)
    doc.saveIncr()
    doc.close()


def main() -> None:
    # 1. Markdown без номеров страниц + DOCX
    base_md = build_report_md.build(None)
    MD_PATH.write_text(base_md, encoding="utf-8")
    items = headings(base_md)
    md_to_docx.convert(MD_PATH, DOCX_PATH, TITLE, base_dir=ROOT / "output")
    print(f"-> {DOCX_PATH}")

    # 2. Первый проход PDF
    md_to_pdf.convert(MD_PATH, PDF_PATH, TITLE, HEADER, base_dir=ROOT / "output")
    pages = find_pages(PDF_PATH, items)
    TOC_JSON.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3. Второй проход с номерами страниц
    for attempt in range(2):
        TMP_MD.write_text(build_report_md.build(pages), encoding="utf-8")
        md_to_pdf.convert(TMP_MD, TMP_PDF, TITLE, HEADER, base_dir=ROOT / "output")
        new_pages = find_pages(TMP_PDF, items)
        if new_pages == pages:
            break
        pages = new_pages
    shutil.copyfile(TMP_PDF, PDF_PATH)

    # 4. Закладки
    add_bookmarks(PDF_PATH, items, pages)
    doc = fitz.open(PDF_PATH)
    print(f"-> {PDF_PATH} ({len(doc)} стр., закладок: {len(doc.get_toc())})")
    doc.close()


if __name__ == "__main__":
    main()
