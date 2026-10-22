"""Снимок страницы входа в веб-дашборд (для проверки вёрстки и показа пользователю)."""
from __future__ import annotations

import functools
import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "output" / "web"
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
OUT = ROOT / "output" / "web_вход.png"

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8741), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=CHROME)
    pg = b.new_page(viewport={"width": 1280, "height": 860})
    pg.goto("http://127.0.0.1:8741/index.html", wait_until="load")
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT), full_page=True)
    # и состояние ошибки неверного пароля — тоже часто проверяют
    pg.fill("#pw", "nevernyj-parol")
    pg.click("#go")
    pg.wait_for_timeout(3000)
    pg.screenshot(path=str(ROOT / "output" / "web_вход_ошибка.png"), full_page=True)
    b.close()
httpd.shutdown()
print("снимки:", OUT, "и", ROOT / "output" / "web_вход_ошибка.png")
