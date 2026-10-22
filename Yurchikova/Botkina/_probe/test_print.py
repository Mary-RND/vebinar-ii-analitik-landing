from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "output" / "dashboard.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    ctx = browser.new_context(viewport={"width": 1500, "height": 1000})
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.goto(URL)
    page.wait_for_timeout(2000)

    print("rows before:", page.eval_on_selector_all("#regBody tr", "e => e.length"))
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    page.wait_for_timeout(500)
    print("rows in print mode:", page.eval_on_selector_all("#regBody tr", "e => e.length"))
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    page.wait_for_timeout(500)
    print("rows after:", page.eval_on_selector_all("#regBody tr", "e => e.length"))

    # печать в PDF: проверяем, что разрывы страниц и таблицы не ломаются
    page.emulate_media(media="print")
    page.wait_for_timeout(500)
    page.pdf(path=str(ROOT / "_probe" / "dashboard_print.pdf"), format="A4", landscape=True,
             print_background=True, margin={"top": "10mm", "bottom": "10mm", "left": "8mm", "right": "8mm"})
    page.emulate_media(media="screen")
    print("pdf written")
    print("errors:", errors)
    browser.close()
