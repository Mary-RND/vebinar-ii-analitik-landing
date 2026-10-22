"""Проверка геометрии рисунков: обрезка текста и наложения подписей.

Загружает SVG в Chromium и для каждого <text> проверяет:
  * элемент не выходит за границы холста;
  * подписи не накладываются друг на друга (пересечение bbox).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from playwright.sync_api import sync_playwright  # noqa: E402

import build_charts  # noqa: E402

CHROME = Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")

JS = r"""
() => {
  const svg = document.querySelector('svg');
  const sr = svg.getBoundingClientRect();
  const items = [...svg.querySelectorAll('text')].map(t => {
    const r = t.getBoundingClientRect();
    return {
      txt: t.textContent.slice(0, 28),
      x0: r.left - sr.left, y0: r.top - sr.top,
      x1: r.right - sr.left, y1: r.bottom - sr.top,
    };
  });
  return {w: sr.width, h: sr.height, items};
}
"""

JS_OVERLAP = r"""
() => {
  const svg = document.querySelector('svg');
  const sr = svg.getBoundingClientRect();
  const t = [...svg.querySelectorAll('text')].map(e => {
    const r = e.getBoundingClientRect();
    return {txt: e.textContent.slice(0, 26),
            x0: r.left - sr.left, y0: r.top - sr.top,
            x1: r.right - sr.left, y1: r.bottom - sr.top};
  });
  const hits = [];
  for (let i = 0; i < t.length; i++) {
    for (let j = i + 1; j < t.length; j++) {
      const a = t[i], b = t[j];
      const ow = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0);
      const oh = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (ow > 1.5 && oh > 1.5) {
        const area = ow * oh;
        const small = Math.min((a.x1-a.x0)*(a.y1-a.y0), (b.x1-b.x0)*(b.y1-b.y0));
        hits.push({a: a.txt, b: b.txt, area: Math.round(area),
                   pct: small ? Math.round(area/small*100) : 0,
                   ov: `${ow.toFixed(1)}x${oh.toFixed(1)}`});
      }
    }
  }
  return hits;
}
"""


def main() -> None:
    a = json.loads((ROOT / "data" / "botkina" / "analytics.json").read_text(encoding="utf-8"))
    svgs = build_charts.build_svgs(a)
    tmp = ROOT / "_probe" / "_chart_check.html"
    problems = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=str(CHROME))
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        for name, svg, meta in svgs:
            tmp.write_text(
                f"<html><body style='margin:0'>{svg}</body></html>", encoding="utf-8")
            page.goto(tmp.resolve().as_uri(), wait_until="load")
            info = page.evaluate(JS)
            hits = page.evaluate(JS_OVERLAP)
            out = []
            for it in info["items"]:
                if it["x0"] < -1 or it["y0"] < -1 or it["x1"] > info["w"] + 1 or it["y1"] > info["h"] + 1:
                    out.append(f"    ЗА ГРАНИЦЕЙ: '{it['txt']}' "
                               f"({it['x0']:.0f},{it['y0']:.0f})-({it['x1']:.0f},{it['y1']:.0f}) "
                               f"при холсте {info['w']:.0f}x{info['h']:.0f}")
            for h in sorted(hits, key=lambda x: -x["pct"]):
                if h["pct"] >= 12:
                    out.append(f"    НАЛОЖЕНИЕ {h['pct']}% ({h['ov']}): '{h['a']}' / '{h['b']}'")
            problems += len(out)
            print(f"{name}: текстов {len(info['items'])}, закладок {len(hits)}, "
                  f"проблем {len(out)}")
            for line in out[:12]:
                print(line)
        browser.close()
    tmp.unlink(missing_ok=True)
    print("\nИТОГО проблем:", problems)


if __name__ == "__main__":
    main()
