"""Этап 0.2: подбор рабочего URL реестра договоров 223-ФЗ.

Проверяет несколько вариантов адреса и печатает код/размер/заголовок.
Запуск: python probe_223_urls.py
"""
from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eis_client import HEADERS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_probe"
Q = quote("Боткина")

CANDIDATES = [
    f"https://zakupki.gov.ru/223/contract/search/results.html?searchString={Q}&morphology=on&pageNumber=1&recordsPerPage=_50",
    f"https://zakupki.gov.ru/epz/contract/search/results.html?searchString={Q}&morphology=on&fz223=on&pageNumber=1&recordsPerPage=_50",
    f"https://zakupki.gov.ru/epz/order/notice/223/search/results.html?searchString={Q}&morphology=on&pageNumber=1&recordsPerPage=_50",
    f"https://zakupki.gov.ru/223/purchase/public/purchase/search/results.html?searchString={Q}&morphology=on&pageNumber=1&recordsPerPage=_50",
]


def main() -> None:
    lines: list[str] = []
    for url in CANDIDATES:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = resp.read()
            text = data.decode("utf-8", errors="replace")
            title = ""
            i = text.find("<title>")
            if i >= 0:
                title = text[i + 7:text.find("</title>", i)][:120]
            lines.append(f"{resp.status}  {len(text):>8}  {url}")
            lines.append(f"      title: {title}")
        except urllib.error.HTTPError as exc:
            lines.append(f"{exc.code}  {'':>8}  {url}")
        except Exception as exc:  # noqa: BLE001
            lines.append(f"ERR {type(exc).__name__}  {url}")
        time.sleep(2)
    (OUT / "urls_223.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT / 'urls_223.txt'}")


if __name__ == "__main__":
    main()
