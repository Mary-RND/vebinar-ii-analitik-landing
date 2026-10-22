from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "output" / "dashboard.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    ctx = browser.new_context(viewport={"width": 1500, "height": 1000}, accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.goto(URL)
    page.wait_for_timeout(2000)

    # CSV download
    with page.expect_download() as dl:
        page.click("#csv")
    d = dl.value
    csv_path = ROOT / "_probe" / "dash_export.csv"
    d.save_as(str(csv_path))
    txt = csv_path.read_text(encoding="utf-8-sig")
    print("csv rows:", len(txt.splitlines()), "header:", txt.splitlines()[0][:120])

    # noEst
    before = page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)")
    page.check("#fest")
    page.wait_for_timeout(700)
    after = page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)")
    print("noEst before/after:", before[3], "->", after[3], "| sum:", before[1], "->", after[1])
    page.uncheck("#fest")
    page.wait_for_timeout(500)

    # only80
    page.check("#f80")
    page.wait_for_timeout(700)
    print("only80:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    page.uncheck("#f80")
    page.wait_for_timeout(500)

    # sum range
    page.fill("#fmin", "10000000")
    page.wait_for_timeout(700)
    print("min 10M:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    page.fill("#fmin", "")
    page.wait_for_timeout(500)

    # search
    page.fill("#fq", "катетер")
    page.wait_for_timeout(700)
    print("search:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    page.fill("#fq", "")
    page.wait_for_timeout(500)

    # reset
    page.select_option("#fkind", "lab")
    page.select_option("#forigin", "import")
    page.wait_for_timeout(700)
    page.click("#reset")
    page.wait_for_timeout(700)
    print("reset:", page.eval_on_selector_all(".kpi .value", "els => els.map(e => e.textContent)"))
    print("chips after reset:", page.eval_on_selector_all(".chip", "els => els.length"))

    # sorting categories by name
    page.click("#catTable th[data-k='category']")
    page.wait_for_timeout(500)
    first = page.eval_on_selector("#catTable tbody tr td", "el => el.textContent")
    print("sorted first cat:", first)
    page.click("#catTable th[data-k='sum']")
    page.wait_for_timeout(500)
    print("sorted by sum first:", page.eval_on_selector("#catTable tbody tr td", "el => el.textContent"))

    # registry scroll (virtual)
    page.eval_on_selector("#registry", "el => el.scrollIntoView()")
    page.wait_for_timeout(500)
    page.eval_on_selector(".registry", "el => el.scrollTop = 3000")
    page.wait_for_timeout(600)
    first_idx = page.eval_on_selector("#regBody tr td", "el => el.textContent")
    print("first idx after scroll:", first_idx)

    # theme dark
    page.click("#themeBtn")
    page.wait_for_timeout(800)
    page.screenshot(path=str(ROOT / "_probe" / "dash3_dark_top.png"))
    print("theme:", page.eval_on_selector("html", "el => el.dataset.theme"))
    print("errors:", errors)
    browser.close()
