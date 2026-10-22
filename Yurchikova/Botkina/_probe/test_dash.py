from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "output" / "dashboard.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.goto(URL)
    page.wait_for_timeout(1800)
    print("title:", page.title())
    print("kpis:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    print("charts:", page.eval_on_selector_all(".chart canvas, .chart svg", "els => els.length"))
    print("reg rows:", page.eval_on_selector_all("#regBody tr:not(.spacer)", "els => els.length"))
    page.screenshot(path=str(ROOT / "_probe" / "dash_top.png"), full_page=False)
    page.eval_on_selector("#registry", "el => el.scrollIntoView()")
    page.wait_for_timeout(500)
    page.screenshot(path=str(ROOT / "_probe" / "dash_reg.png"), full_page=False)
    # фильтр
    page.select_option("#fkind", "lab")
    page.wait_for_timeout(800)
    print("after filter:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    print("errors:", errors)
    browser.close()
