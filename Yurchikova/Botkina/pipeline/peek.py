"""Просмотр закэшированной страницы: фрагменты вокруг маркеров.

Запуск: python peek.py <url> <маркер> [ширина]
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SPACES = re.compile(r"[\s\u00a0\u2009]+")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def main() -> None:
    url = sys.argv[1]
    markers = sys.argv[2:] or ["Поставщик"]
    path = RAW / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".html")
    if not path.exists():
        print("нет в кэше:", path)
        return
    text = norm(re.sub(r"<script.*?</script>", " ", path.read_text(encoding="utf-8", errors="replace"), flags=re.S))
    text = norm(re.sub(r"<[^>]+>", " ", text))
    for marker in markers:
        print(f"=== {marker} ===")
        start = 0
        found = 0
        while found < 3:
            i = text.find(marker, start)
            if i < 0:
                break
            print(text[max(0, i - 150):i + 600])
            print("-" * 60)
            start = i + len(marker)
            found += 1


if __name__ == "__main__":
    main()
