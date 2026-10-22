# -*- coding: utf-8 -*-
"""Render the project's Markdown deliverables to print-ready A4 PDFs.

The PDF is produced from the same Markdown as the DOCX, through Chromium's
print engine. This keeps tables, headings and lists consistent and avoids
depending on Word for PDF export.
"""

from __future__ import annotations

import html
import os
import re
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright
import pymupdf as fitz


def find_chrome() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    for name in ("chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("Chrome/Edge не найден. Укажите путь в переменной CHROME.")


CHROME = find_chrome()

CSS = """
@page {
  size: A4;
  margin: 18mm 15mm 17mm 19mm;
}
@page wide {
  size: A4 landscape;
  margin: 14mm 15mm 16mm 15mm;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Times New Roman", Times, serif;
  font-size: 10.5pt;
  line-height: 1.35;
  color: #1b1f24;
}
.cover {
  min-height: 235mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}
.cover h1 {
  margin: 0 0 8mm 0;
  font-size: 26pt;
  line-height: 1.15;
  color: #1F3A5F;
  letter-spacing: 0.2pt;
}
.cover h2 {
  margin: 0 0 20mm 0;
  border: none;
  font-size: 17pt;
  line-height: 1.25;
  color: #1F3A5F;
  font-weight: bold;
}
.cover p {
  text-align: center;
  margin: 2mm 0;
  font-size: 10.5pt;
}
.cover table {
  width: 82%;
  margin: 0 auto;
  font-size: 10pt;
}
.cover td, .cover th {
  text-align: left;
}
.cover td:first-child, .cover th:first-child {
  width: 23%;
  white-space: nowrap;
}
h2 {
  margin: 14pt 0 6pt;
  padding-bottom: 2pt;
  border-bottom: 0.6pt solid #B8C2CC;
  font-size: 15pt;
  line-height: 1.2;
  color: #1F3A5F;
  break-after: avoid;
}
h3 {
  margin: 10pt 0 4pt;
  font-size: 12pt;
  line-height: 1.2;
  color: #1F3A5F;
  break-after: avoid;
}
h4 {
  margin: 8pt 0 3pt;
  font-size: 11pt;
  color: #1F3A5F;
  break-after: avoid;
}
p {
  margin: 0 0 5pt;
  text-align: justify;
  orphans: 2;
  widows: 2;
}
ul, ol {
  margin: 3pt 0 6pt;
  padding-left: 16pt;
}
li {
  margin: 0 0 2.5pt;
  text-align: left;
}
table {
  width: 100%;
  margin: 5pt 0 9pt;
  border-collapse: collapse;
  font-size: 8pt;
  line-height: 1.25;
  table-layout: fixed;   /* ширина таблицы фиксирована — Chromium не ужимает страницу */
}
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td {
  border: 0.5pt solid #AAB6C4;
  padding: 2.5pt 3.5pt;
  vertical-align: top;
  word-break: normal;
  overflow-wrap: break-word;
  hyphens: auto;
}
/* Широкие таблицы (10+ столбцов) — на альбомной странице, чтобы не сжимать весь документ */
table.wide {
  page: wide;
  break-before: page;
  font-size: 7.6pt;
}
table.wide th, table.wide td { padding: 2pt 3pt; }
table.wide th:first-child, table.wide td:first-child { min-width: 0; }th {
  background: #E8EEF5;
  color: #1F3A5F;
  font-weight: bold;
  text-align: left;
}
td { text-align: left; }
hr {
  border: none;
  border-top: 0.5pt solid #B8C2CC;
  margin: 10pt 0;
}
.page-break { break-before: page; }
code {
  font-family: Consolas, monospace;
  font-size: 8.8pt;
  background: #F2F4F7;
  padding: 0 2pt;
}
strong { font-weight: bold; }
em { font-style: italic; }
.small { font-size: 8pt; color: #555f6d; }
figure {
  margin: 6pt 0 10pt;
  text-align: center;
  break-inside: avoid;
}
figure img {
  max-width: 100%;
  border: 0.5pt solid #C7D0DA;
}
figcaption {
  margin-top: 3pt;
  font-size: 8pt;
  color: #45505d;
  text-align: center;
}
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    return text


IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


def render_image(alt: str, src: str, base_dir: Path) -> str:
    """Рисунок с подписью (ТЗ § 7.2: номер, название, источник)."""
    path = (base_dir / src).resolve()
    if not path.exists():
        return (f"<p class='small'>[Рисунок не найден: {html.escape(src)}]</p>")
    uri = path.as_uri()
    return (f"<figure><img src='{uri}' alt='{html.escape(alt, quote=True)}'>"
            f"<figcaption>{inline(alt)}</figcaption></figure>")


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|[\s:\-|]+\|\s*$", line))


def column_widths(header: list[str], rows: list[list[str]]) -> list[float]:
    """Пропорциональные ширины столбцов (%), чтобы таблица не выходила за поля страницы.

    Без явных ширин Chromium при неразрывном содержимом растягивает таблицу за пределы
    печатного поля и ужимает всю страницу целиком (кегль основного текста падает).
    """
    n = len(header)
    if n == 0:
        return []
    scores: list[float] = []
    for i in range(n):
        lens = [len(header[i])]
        for r in rows[:80]:
            if i < len(r):
                lens.append(len(r[i]))
        lens.sort()
        p75 = lens[min(len(lens) - 1, int(len(lens) * 0.75))]
        top = min(float(lens[-1]), 70.0)
        scores.append(max(2.0, p75 * 0.7 + top * 0.3))
    total = sum(scores) or 1.0
    pcts = [s / total * 100 for s in scores]
    pcts = [min(max(p, 3.0), 34.0) for p in pcts]
    total = sum(pcts) or 1.0
    return [p / total * 100 for p in pcts]


def render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    data = rows[1:]
    header_empty = all(not cell for cell in header)
    # Широкие таблицы печатаются на альбомной странице (ТЗ § 7.2)
    wide = len(header) >= 10

    out = ["<table class='wide'>" if wide else "<table>"]
    widths = column_widths(header, data)
    if widths:
        out.append("<colgroup>" + "".join(
            f"<col style='width:{w:.3f}%'>" for w in widths) + "</colgroup>")
    if not header_empty:
        out.append("<thead><tr>")
        for cell in header:
            out.append(f"<th>{inline(cell)}</th>")
        out.append("</tr></thead>")
    out.append("<tbody>")
    for row in data:
        out.append("<tr>")
        for cell in row[: len(header)] if header else row:
            out.append(f"<td>{inline(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_list(items: list[tuple[int, str, str]]) -> str:
    """Render a list of (indent, type, text) tuples as nested HTML lists."""
    if not items:
        return ""
    out: list[str] = []
    stack: list[tuple[int, str]] = []
    for indent, kind, text in items:
        if not stack:
            stack.append((indent, kind))
            out.append(f"<{kind}>")
        else:
            while stack and indent < stack[-1][0]:
                out.append(f"</li></{stack[-1][1]}>")
                stack.pop()
            if stack and indent == stack[-1][0] and kind != stack[-1][1]:
                out.append(f"</li></{stack[-1][1]}><{kind}>")
                stack[-1] = (indent, kind)
            elif stack and indent > stack[-1][0]:
                out.append(f"<{kind}>")
                stack.append((indent, kind))
            else:
                out.append("</li>")
        out.append(f"<li>{inline(text)}")
    while stack:
        out.append(f"</li></{stack[-1][1]}>")
        stack.pop()
    return "".join(out)


def markdown_to_html(text: str, title: str, base_dir: Path | None = None) -> str:
    base_dir = base_dir or Path.cwd()
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    first_rule = True
    in_cover = True
    first_h1 = True
    first_h2 = True

    out.append("<!DOCTYPE html><html lang='ru'><head><meta charset='utf-8'>")
    out.append(f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>")
    out.append("<div class='cover'>")

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue

        # Do not include the internal service block in client deliverables.
        if stripped.startswith("### Служебный блок"):
            break

        # Explicit page break
        if stripped == "[[pagebreak]]":
            out.append("<div class='page-break'></div>")
            i += 1
            continue

        # Table
        if stripped.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            rows = [split_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            out.append(render_table(rows))
            continue

        # Horizontal rule / cover break
        if stripped == "---":
            if first_rule:
                out.append("</div>")
                out.append("<div class='page-break'></div>")
                first_rule = False
                in_cover = False
            else:
                out.append("<hr>")
            i += 1
            continue

        # Headings
        if stripped.startswith("#### "):
            out.append(f"<h4>{inline(stripped[5:])}</h4>")
            i += 1
            continue
        if stripped.startswith("### "):
            out.append(f"<h3>{inline(stripped[4:])}</h3>")
            i += 1
            continue
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            if first_h2 and not re.match(r"^\d+\.", heading):
                out.append(f"<h2>{inline(heading)}</h2>")
                first_h2 = False
            else:
                out.append(f"<h2>{inline(heading)}</h2>")
                first_h2 = False
            i += 1
            continue
        if stripped.startswith("# "):
            heading = stripped[2:].strip()
            out.append(f"<h1>{inline(heading)}</h1>" if first_h1 else f"<h2>{inline(heading)}</h2>")
            first_h1 = False
            i += 1
            continue

        # Lists (group consecutive list lines, including nested)
        list_match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", raw)
        if list_match:
            items: list[tuple[int, str, str]] = []
            while i < len(lines):
                m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not m:
                    break
                indent = len(m.group(1))
                kind = "ul" if m.group(2) in ("-", "*") else "ol"
                items.append((indent, kind, m.group(3)))
                i += 1
            out.append(render_list(items))
            continue

        # Рисунок
        if stripped.startswith("!["):
            m = IMG_RE.match(stripped)
            if m:
                out.append(render_image(m.group(1), m.group(2), base_dir))
                i += 1
                continue

        # Paragraph
        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    if in_cover:
        out.append("</div>")
    out.append("</body></html>")
    return "".join(out)


def add_header_footer(pdf_path: Path, header_text: str) -> None:
    doc = fitz.open(pdf_path)
    total = len(doc)
    font_path = r"C:\Windows\Fonts\times.ttf"
    font_size = 7
    for index, page in enumerate(doc):
        if index == 0:
            continue
        # Header: right-aligned in a text box, so long Russian text never
        # runs off the page edge.
        page.insert_textbox(
            fitz.Rect(42, 16, page.rect.width - 42, 32),
            header_text,
            fontname="timesnew",
            fontfile=font_path,
            fontsize=font_size,
            color=(0.33, 0.37, 0.43),
            align=fitz.TEXT_ALIGN_RIGHT,
        )
        # Footer: centered page number.
        footer = f"Стр. {index + 1} из {total}"
        page.insert_textbox(
            fitz.Rect(42, page.rect.height - 32, page.rect.width - 42, page.rect.height - 16),
            footer,
            fontname="timesnew",
            fontfile=font_path,
            fontsize=font_size,
            color=(0.33, 0.37, 0.43),
            align=fitz.TEXT_ALIGN_CENTER,
        )
    doc.saveIncr()
    doc.close()


def convert(md_path: Path, pdf_path: Path, title: str, header_text: str,
            base_dir: Path | None = None) -> None:
    source = md_path.read_text(encoding="utf-8")
    body = markdown_to_html(source, title, base_dir=base_dir or md_path.parent)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(body, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    add_header_footer(pdf_path, header_text)
    html_path.unlink(missing_ok=True)
    print(f"Saved {pdf_path} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    convert(
        base / "TZ_Botkin_2025.md",
        base / "TZ_Botkin_2025.pdf",
        "Техническое задание — анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
        "Техническое задание — анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
    )
    convert(
        base / "KP_Botkin_2025.md",
        base / "KP_Botkin_2025.pdf",
        "Коммерческое предложение — анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
        "Коммерческое предложение — анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
    )
