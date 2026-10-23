"""Проверка страницы входа под паролем: неверный пароль не открывает, верный открывает дашборд."""
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
GOOD = (os.environ.get("BOTKINA_WEB_PASSWORD")
        or ((ROOT / "output" / "_password.tmp").read_text(encoding="utf-8").strip()
            if (ROOT / "output" / "_password.tmp").exists() else None)
        or "Botkina-Dash-2026!")
BAD = GOOD[:-1] + ("X" if GOOD[-1] != "X" else "Y")   # тот же пароль с изменённым последним символом


def serve(port: int = 8731):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}/index.html"


def main() -> None:
    if not (SITE / "payload.bin").exists():
        raise SystemExit("нет output/web — запустите pipeline/build_web.py")
    httpd, url = serve()
    ok_all = True
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.goto(url, wait_until="load")
        page.wait_for_timeout(600)

        # 1. пустой пароль
        page.click("#go")
        page.wait_for_timeout(200)
        e1 = page.inner_text("#err").strip()
        print(f"пустой пароль        -> {e1!r}")
        ok_all &= bool(e1)

        # 2. неверный пароль
        page.fill("#pw", BAD)
        page.click("#go")
        page.wait_for_timeout(3000)
        e2 = page.inner_text("#err").strip()
        lock_visible = page.is_visible("#lock")
        print(f"неверный пароль      -> ошибка: {e2!r}; форма видна: {lock_visible}")
        ok_all &= ("Неверный" in e2) and lock_visible

        # 3. верный пароль
        page.fill("#pw", GOOD)
        page.click("#go")
        page.wait_for_timeout(6000)
        state = page.evaluate("""() => ({
          lock: getComputedStyle(document.getElementById('lock')).display,
          work: getComputedStyle(document.getElementById('work')).display,
          kpis: document.getElementById('frame').contentDocument
                ? document.getElementById('frame').contentDocument.querySelectorAll('#kpis .kpi').length
                : -1,
          title: document.title,
        })""")
        print(f"верный пароль        -> форма {state['lock']}, рабочая область {state['work']}, "
              f"KPI во фрейме: {state['kpis']}, заголовок: {state['title']!r}")
        ok_all &= (state["lock"] == "none") and (state["kpis"] > 0)

        # 4. фильтр внутри раскрытого дашборда работает
        frame = page.frame_locator("#frame")
        try:
            frame.locator("#fkind").select_option(index=1, timeout=4000)
            page.wait_for_timeout(700)
            chips = frame.locator("#chips .chip").count()
            print(f"фильтр во фрейме     -> чипсов активных: {chips}")
            ok_all &= chips > 0
        except Exception as ex:      # noqa: BLE001
            print("фильтр во фрейме     -> НЕ РАБОТАЕТ:", ex)
            ok_all = False

        print("ошибки консоли:", errs)
        browser.close()
    httpd.shutdown()

    # 5. отдельный сервер, где payload.bin не опубликован — должна быть понятная ошибка, а не «неверный пароль»
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="webgate_"))
    shutil.copy2(SITE / "index.html", tmp / "index.html")
    handler2 = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp))
    httpd2 = http.server.ThreadingHTTPServer(("127.0.0.1", 8732), handler2)
    threading.Thread(target=httpd2.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=CHROME)
            page = browser.new_page()
            page.goto("http://127.0.0.1:8732/index.html", wait_until="load")
            page.fill("#pw", GOOD)
            page.click("#go")
            page.wait_for_timeout(1500)
            msg = page.inner_text("#err").strip()
            print("нет payload.bin      ->", repr(msg))
            ok_all &= "payload.bin" in msg
            browser.close()
    finally:
        httpd2.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    print("ИТОГ:", "страница входа работает" if ok_all else "ЕСТЬ ПРОБЛЕМЫ")


if __name__ == "__main__":
    main()
