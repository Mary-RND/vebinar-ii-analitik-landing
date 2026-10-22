"""Проверка легенды «факт/оценка» на каждом экране дашборда (ТЗ § 5.9)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "dashboard.html"
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

JS = r"""
() => {
  const out = [];
  document.querySelectorAll('section.block').forEach(sec => {
    const leg = sec.querySelector('.factlegend');
    out.push({
      id: sec.id,
      title: (sec.querySelector('h2') || {}).textContent || '',
      legend: leg ? leg.innerText.replace(/\s+/g, ' ').trim() : null,
    });
  });
  return out;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.goto(HTML.resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(1200)
    secs = page.evaluate(JS)
    print(f"экранов (section.block): {len(secs)}")
    bad = 0
    for s in secs:
        ok = s["legend"] and "факт" in s["legend"] and "оценка" in s["legend"]
        print(f"  {'OK ' if ok else 'НЕТ'} {s['id']:<14} {s['title'][:40]}")
        if not ok:
            bad += 1
            print(f"       -> {s['legend']}")
    print("\nэкранов без легенды:", bad)
    print("ошибки консоли:", errs)
    browser.close()
