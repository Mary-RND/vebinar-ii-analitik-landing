"""Проверка учёта в дашборде (ТЗ § 8.6): срез + отсечено фильтрами + исключено = общий объём."""
from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "dashboard.html"
CHROME = r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"


def to_rubles(txt: str) -> float:
    """'5 436,7 млн ₽' -> 5436700000.0"""
    t = txt.replace("\xa0", " ").replace("₽", "").strip()
    mult = 1.0
    if "млрд" in t:
        mult = 1e9
    elif "млн" in t:
        mult = 1e6
    t = re.sub(r"(млрд|млн|тыс\.|₽)", "", t).strip()
    t = t.replace(" ", "").replace(",", ".")
    try:
        return float(t) * mult
    except ValueError:
        return float("nan")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME)
    page = browser.new_page(viewport={"width": 1500, "height": 950})
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(HTML.resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(1200)

    def kpis():
        return page.evaluate(
            "() => [...document.querySelectorAll('#kpis .kpi')].map(c => ({"
            "l: c.querySelector('.label').innerText.trim(),"
            "v: c.querySelector('.value').innerText.trim(),"
            "h: c.querySelector('.hint').innerText.trim()}))")

    def check(tag):
        k = {c["l"].lower(): c["v"] for c in kpis()}
        total = to_rubles(k["общий объём 2025"])
        prof = to_rubles(k["профильный объём"])
        cut = to_rubles(k["отсечено фильтрами"])
        excl = to_rubles(k["исключено"])
        got = prof + cut + excl
        ok = abs(got - total) / total < 0.005
        print(f"{tag:<22} срез {prof/1e6:>12,.1f} млн + отсечено {cut/1e6:>9,.1f} млн "
              f"+ исключено {excl/1e6:>12,.1f} млн = {got/1e6:>12,.1f} млн "
              f"(общий {total/1e6:,.1f} млн) -> {'OK' if ok else 'РАСХОЖДЕНИЕ'}")
        return ok

    ok = check("без фильтров")
    page.select_option("#fkind", index=1)
    page.wait_for_timeout(400)
    ok &= check("фильтр: вид закупки")
    page.select_option("#fkind", "")
    page.fill("#fq", "катетер")
    page.wait_for_timeout(500)
    ok &= check("фильтр: поиск")
    page.click("#reset")
    page.wait_for_timeout(500)
    ok &= check("после сброса")
    print("ошибки консоли:", errs)
    browser.close()
    print("ИТОГ:", "учёт сходится" if ok else "есть расхождение")
