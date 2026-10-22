from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "output" / "dashboard.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    page = browser.new_page(viewport={"width": 1500, "height": 1000})
    errors = []
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.goto(URL)
    page.wait_for_timeout(2200)
    print("title:", page.title())
    print("kpis:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    print("charts:", page.eval_on_selector_all(".chart svg", "els => els.length"))
    print("reg rows:", page.eval_on_selector_all("#regBody tr:not(.spacer)", "els => els.length"))
    print("key cards:", page.eval_on_selector_all(".pcard", "els => els.length"))
    page.screenshot(path=str(ROOT / "_probe" / "dash2_top.png"), full_page=False)

    page.eval_on_selector("#categories", "el => el.scrollIntoView()")
    page.wait_for_timeout(600)
    page.screenshot(path=str(ROOT / "_probe" / "dash2_cat.png"), full_page=False)

    page.eval_on_selector("#country", "el => el.scrollIntoView()")
    page.wait_for_timeout(600)
    page.screenshot(path=str(ROOT / "_probe" / "dash2_country.png"), full_page=False)

    page.eval_on_selector("#bench", "el => el.scrollIntoView()")
    page.wait_for_timeout(600)
    page.screenshot(path=str(ROOT / "_probe" / "dash2_bench.png"), full_page=False)

    page.eval_on_selector("#registry", "el => el.scrollIntoView()")
    page.wait_for_timeout(600)
    page.screenshot(path=str(ROOT / "_probe" / "dash2_reg.png"), full_page=False)

    # фильтры
    page.select_option("#fkind", "lab")
    page.wait_for_timeout(900)
    print("after kind:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    page.select_option("#forigin", "import")
    page.wait_for_timeout(900)
    print("after origin:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    print("chips:", page.eval_on_selector_all(".chip", "els => els.map(e => e.textContent.trim())"))
    # тема
    page.click("#themeBtn")
    page.wait_for_timeout(700)
    print("theme:", page.eval_on_selector("html", "el => el.dataset.theme"))
    page.screenshot(path=str(ROOT / "_probe" / "dash2_dark.png"), full_page=False)
    print("errors:", errors)
    browser.close()
