"""Проверка вёрстки сайта дашборда при разных размерах окна.

Логинится на странице входа (output/web), затем проверяет:
  - рабочая область занимает всё окно (без сжатия до ширины шапки);
  - iframe дашборда заполняет высоту под шапкой;
  - внутри дашборда нет горизонтального переполнения страницы;
  - липкая панель фильтров не съедает окно;
  - графики (svg) отрисованы, таблицы видимы при прокрутке.
Снимает скриншоты в _probe/shots/.
"""
from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "output" / "web"
SHOTS = ROOT / "_probe" / "shots"
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
GOOD = (Path(ROOT / "output" / "_password.tmp").read_text(encoding="utf-8").strip()
        if (ROOT / "output" / "_password.tmp").exists() else "Botkina-Dash-2026!")

SIZES = [(1920, 1080), (1440, 900), (1280, 720), (800, 600)]

PROBE = """() => {
  const work = document.getElementById('work');
  const frame = document.getElementById('frame');
  const topbar = document.querySelector('.topbar');
  const d = frame.contentDocument, w = frame.contentWindow;
  const toolbar = d.querySelector('.toolbar');
  const svgs = [...d.querySelectorAll('.chart svg')].map(s => Math.round(s.getBoundingClientRect().width));
  return {
    vw: innerWidth, vh: innerHeight,
    workW: Math.round(work.getBoundingClientRect().width),
    workH: Math.round(work.getBoundingClientRect().height),
    topbarH: Math.round(topbar.getBoundingClientRect().height),
    frameH: Math.round(frame.getBoundingClientRect().height),
    innerScrollW: d.documentElement.scrollWidth,
    innerClientW: d.documentElement.clientWidth,
    toolbarH: Math.round(toolbar.getBoundingClientRect().height),
    toolbarPos: getComputedStyle(toolbar).position,
    chartsSvg: svgs,
    tables: d.querySelectorAll('table').length,
    kpis: d.querySelectorAll('#kpis .kpi').length,
  };
}"""

SCROLL_PROBE = """() => {
  const frame = document.getElementById('frame');
  const d = frame.contentDocument, w = frame.contentWindow;
  const sec = d.getElementById('items');
  sec.scrollIntoView();
  w.scrollBy(0, -60);               // учесть липкую панель
  const r = sec.getBoundingClientRect();
  const tb = sec.querySelector('table');
  const tr = tb ? tb.querySelector('tbody tr') : null;
  const trRect = tr ? tr.getBoundingClientRect() : null;
  const pos = tr ? getComputedStyle(tr).position : null;
  const vis0 = !!trRect && trRect.top < d.documentElement.clientHeight && trRect.bottom > 0;
  // если строка оказалась ниже края — доводим прокруткой и проверяем ещё раз
  if (tr && !vis0) { tr.scrollIntoView({block:'center'}); w.scrollBy(0, -60); }
  const r2 = tr ? tr.getBoundingClientRect() : null;
  const vis1 = !!r2 && r2.top < d.documentElement.clientHeight && r2.bottom > 0;
  return {
    sectionTop: Math.round(r.top),
    sectionVisible: r.top < d.documentElement.clientHeight && r.bottom > 0,
    rowTop: trRect ? Math.round(trRect.top) : null,
    rowPos: pos,
    firstRowVisible: vis0,
    firstRowVisibleAfterScroll: vis1,
    rowText: tr ? tr.innerText.replace(/\\s+/g, ' ').slice(0, 60) : null,
  };
}"""


def serve(port: int = 8733):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}/index.html"


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    httpd, url = serve()
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        for w, h in SIZES:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(url, wait_until="load")
            page.fill("#pw", GOOD)
            page.click("#go")
            page.wait_for_selector("#work", state="visible", timeout=30000)
            page.wait_for_timeout(2500)
            st = page.evaluate(PROBE)

            ok_width = st["workW"] >= st["vw"] - 2
            ok_height = abs(st["frameH"] - (st["vh"] - st["topbarH"])) <= 2
            ok_nohscroll = st["innerScrollW"] <= st["innerClientW"] + 1
            ok_toolbar = st["toolbarH"] <= (0.35 if st["toolbarPos"] == "sticky" else 0.5) * st["vh"]
            ok_charts = len(st["chartsSvg"]) > 0 and min(st["chartsSvg"]) > 50
            ok_tables = st["tables"] >= 6 and st["kpis"] == 9

            page.screenshot(path=str(SHOTS / f"layout_{w}x{h}.png"))

            sc = page.evaluate(SCROLL_PROBE)
            page.wait_for_timeout(400)
            page.screenshot(path=str(SHOTS / f"scroll_{w}x{h}.png"))
            ok_scroll = sc["firstRowVisible"] or sc["firstRowVisibleAfterScroll"]

            print(f"{w}x{h}: окно {st['workW']}x{st['workH']} при {st['vw']}x{st['vh']}, "
                  f"шапка {st['topbarH']}, iframe {st['frameH']}, "
                  f"панель фильтров {st['toolbarH']} ({st['toolbarPos']}), "
                  f"горизонт. переполнение {st['innerScrollW'] - st['innerClientW']} px, "
                  f"графиков svg {len(st['chartsSvg'])} (ширина {min(st['chartsSvg']) if st['chartsSvg'] else 0}"
                  f"-{max(st['chartsSvg']) if st['chartsSvg'] else 0}), таблиц {st['tables']}, KPI {st['kpis']}")
            print(f"        прокрутка: раздел «Номенклатура» виден: {sc['sectionVisible']}, "
                  f"строка №1 (top {sc['rowTop']}, pos {sc['rowPos']}) видна: {sc['firstRowVisible']} "
                  f"/ после доводки: {sc['firstRowVisibleAfterScroll']} — {sc['rowText']!r}")

            for name, ok in (("рабочая область на всю ширину", ok_width),
                             ("iframe по высоте окна", ok_height),
                             ("без горизонтального переполнения", ok_nohscroll),
                             ("панель фильтров не накрывает окно", ok_toolbar),
                             ("графики отрисованы", ok_charts),
                             ("таблицы и KPI на месте", ok_tables),
                             ("строки таблиц видны при прокрутке", ok_scroll)):
                if not ok:
                    problems.append(f"{w}x{h}: {name}")
            page.close()
        browser.close()
    httpd.shutdown()
    print("ИТОГ:", "вёрстка в порядке" if not problems else "ПРОБЛЕМЫ: " + "; ".join(problems))


if __name__ == "__main__":
    main()
