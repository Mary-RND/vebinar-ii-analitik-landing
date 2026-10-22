"""Проверка пустого среза: вместо нулей показывается «Нет данных» (ТЗ § 8.6)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "dashboard.html"
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(HTML.resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(1200)

    # строка источников на каждом экране
    n_srcline = page.evaluate(
        "() => [...document.querySelectorAll('section.block')].map(s => "
        "({id: s.id, srcline: !!s.querySelector('[data-srcline]'), "
        " legend: !!s.querySelector('.factlegend')}))")
    print("экранов:", len(n_srcline))
    for s in n_srcline:
        print(f"   {s['id']:<12} строка источников: {s['srcline']}  легенда: {s['legend']}")

    # пустой срез: страна + поставщик, которые не встречаются вместе
    page.evaluate("""() => {
      const sups = [...document.querySelector('#fsup').options].map(o=>o.value).filter(Boolean);
      const ctry = [...document.querySelector('#fcountry').options].map(o=>o.value).filter(Boolean);
      window.__probe = {sups: sups.slice(0,40), ctry: ctry.slice(0,40)};
    }""")
    probe = page.evaluate("() => window.__probe")
    found = False
    for s in probe["sups"]:
        for c in probe["ctry"]:
            page.select_option("#fsup", s)
            page.select_option("#fcountry", c)
            page.wait_for_timeout(120)
            n = page.evaluate("() => document.querySelectorAll('#regBody tr').length")
            total = page.evaluate("() => document.querySelector('#kpis')?.innerText || ''")
            if "нет данных" in total.lower() or n == 0:
                found = True
                break
        if found:
            break
    page.wait_for_timeout(500)
    state = page.evaluate("""() => {
      const txt = document.body.innerText;
      return {
        empties: [...document.querySelectorAll('.empty')].map(e=>e.innerText.trim()).slice(0,8),
        chartempty: [...document.querySelectorAll('.chartempty')].length,
        zeros: /(^|[^\\d])0([^\\d%]|$)/.test(txt),
      };
    }""")
    print("пустой срез найден:", found)
    print("сообщения «Нет данных»:", state["empties"])
    print("графиков с заглушкой:", state["chartempty"])
    print("ошибки консоли:", errs)
    browser.close()
