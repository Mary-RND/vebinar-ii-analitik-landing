"""Воспроизведение конвертации отчёта и замер размеров шрифта."""
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_tools"))
import md_to_pdf  # noqa: E402

out = ROOT / "_probe" / "scale_probe.pdf"
md_to_pdf.convert(ROOT / "output" / "REPORT_Botkin_2025.md", out,
                  "Анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
                  "Анализ закупок МНКЦ им. С.П. Боткина — 2025")
d = fitz.open(out)
print("страниц:", len(d), "размер стр.1:", d[0].rect)
for p in (4, 8):
    from collections import Counter
    c = Counter()
    for b in d[p - 1].get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                c[round(s["size"], 1)] += len(s["text"])
    print(f"стр.{p}:", c.most_common(4))
d.close()
