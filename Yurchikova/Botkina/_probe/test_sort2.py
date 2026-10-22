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

    def first_rows(sel, n=3):
        return page.eval_on_selector_all(
            f"{sel} tbody tr", f"els => els.slice(0,{n}).map(e => Array.from(e.cells).map(c => c.textContent.trim()).join(' | '))"
        )

    print("категории (по умолчанию):")
    for r in first_rows("#catTable"):
        print("   ", r[:150])
    page.click("#catTable th[data-k='category']")
    page.wait_for_timeout(400)
    print("после сортировки по названию:")
    for r in first_rows("#catTable"):
        print("   ", r[:150])
    page.click("#catTable th[data-k='sum']")
    page.wait_for_timeout(400)
    print("после сортировки по сумме:")
    for r in first_rows("#catTable"):
        print("   ", r[:150])
    page.click("#catTable th[data-k='sum']")
    page.wait_for_timeout(400)
    print("после повторной сортировки по сумме (убывание):")
    for r in first_rows("#catTable"):
        print("   ", r[:150])

    print("номенклатура:")
    for r in first_rows("#itemsTable", 2):
        print("   ", r[:150])
    page.click("#itemsTable th[data-k='name']")
    page.wait_for_timeout(400)
    print("номенклатура по названию:")
    for r in first_rows("#itemsTable", 2):
        print("   ", r[:150])

    print("бенчмарки:")
    for r in first_rows("#benchTable", 2):
        print("   ", r[:200])
    print("итоговые строки:", page.eval_on_selector_all("tfoot tr", "e => e.map(x => x.textContent.trim().slice(0,120))"))
    print("errors:", errors)
    browser.close()
