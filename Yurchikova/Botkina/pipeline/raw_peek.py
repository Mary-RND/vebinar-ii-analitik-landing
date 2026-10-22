"""Сырой фрагмент HTML вокруг маркера (без нормализации)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
url = sys.argv[1]
marker = sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
path = RAW / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".html")
text = path.read_text(encoding="utf-8", errors="replace")
i = text.find(marker)
print(text[max(0, i - width):i + width])
