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
    page.wait_for_timeout(2500)

    lines = page.eval_on_selector_all("[data-srcline]", "els => els.map(e => e.textContent)")
    print("строк-источников:", len(lines))
    for ln in lines:
        print("   ", ln)
    print("howto блок:", page.eval_on_selector_all(".howto", "e => e.length"),
          "summary:", page.eval_on_selector(".howto summary", "e => e.textContent"))
    print("errors:", errors)
    browser.close()
