from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "output" / "dashboard.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    page = browser.new_page(viewport={"width": 1500, "height": 1000})
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL)
    page.wait_for_timeout(2200)
    for tid in ["#catTable", "#itemsTable", "#countryTable"]:
        print(tid, "tfoot:", page.eval_on_selector(f"{tid} tfoot", "el => el.textContent.trim()") if page.query_selector(f"{tid} tfoot") else "none")
    print("regHint:", page.eval_on_selector("#regHint", "el => el.textContent"))
    print("kindNote:", page.eval_on_selector("#kindNote", "el => el.textContent"))
    print("catHint:", page.eval_on_selector("#catHint", "el => el.textContent"))
    print("itemsHint:", page.eval_on_selector("#itemsHint", "el => el.textContent"))
    # items table total row check
    print("items first 3:", page.eval_on_selector_all("#itemsTable tbody tr", "els => els.slice(0,3).map(e => e.textContent.replace(/\\s+/g,' ').trim())"))
    # category table after filter
    page.select_option("#fkind", "lab")
    page.wait_for_timeout(700)
    print("filtered cat tfoot:", page.eval_on_selector("#catTable tfoot", "el => el.textContent.replace(/\\s+/g,' ').trim()"))
    print("filtered itemsHint:", page.eval_on_selector("#itemsHint", "el => el.textContent"))
    page.screenshot(path=str(ROOT / "_probe" / "dash4_items.png"), full_page=False)
    print("errors:", errors)
    browser.close()
