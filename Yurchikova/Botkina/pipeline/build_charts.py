"""Генерация рисунков отчёта (ТЗ § 7.2: номер, название, источник).

SVG собирается вручную (в среде нет matplotlib), затем рендерится в PNG
через Chromium (Playwright). Результат: output/img/*.png + output/img/figures.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "botkina" / "analytics.json"
OUT_DIR = ROOT / "output" / "img"

NAVY = "#1F3A5F"
BLUE = "#2E6DA4"
TEAL = "#2E8B8B"
GOLD = "#C08A2E"
GRAY = "#6B7A8C"
LIGHT = "#E4EAF1"
RED = "#A94442"
FONT = "Segoe UI, Arial, sans-serif"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def short(s: str | None, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def money(v: float) -> str:
    """1234567 -> '1,23 млн ₽'."""
    if abs(v) >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f} млрд ₽"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f} млн ₽"
    if abs(v) >= 1_000:
        return f"{v / 1_000:.0f} тыс ₽"
    return f"{v:.0f} ₽"


def pctf(v: float, d: int = 1) -> str:
    return f"{v:.{d}f} %".replace(".", ",")


def svg_text(x, y, s, size=10, fill=NAVY, anchor="start", weight="normal",
             rotate=None, opacity=None) -> str:
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{tr}{op}>'
            f'{esc(s)}</text>')


def render(name: str, svg: str) -> None:
    """Рендер SVG -> PNG через Chromium."""
    from playwright.sync_api import sync_playwright

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = (f"<html><head><meta charset='utf-8'><style>"
            f"html,body{{margin:0;padding:0;background:#fff}}"
            f"svg{{display:block}}</style></head><body>{svg}</body></html>")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome",
                                     args=["--force-device-scale-factor=2"])
        page = browser.new_page(viewport={"width": 1200, "height": 900},
                                device_scale_factor=2)
        page.set_content(html, wait_until="load")
        el = page.query_selector("svg")
        el.screenshot(path=str(OUT_DIR / name))
        browser.close()


# --------------------------------------------------------------------- графики

def hbar_chart(rows: list[tuple[str, float, str]], title: str, sub: str = "",
                w: int = 1000, row_h: int = 42, bar_color: str = BLUE,
                value_fmt=money) -> str:
    """Горизонтальные полосы: [(подпись, значение, доп. подпись)]."""
    h = 96 + row_h * len(rows) + 30
    left, right = 440, 260
    plot_w = w - left - right
    mx = max((v for _, v, _ in rows), default=1) or 1
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}">']
    p.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>')
    p.append(svg_text(26, 32, title, 20, NAVY, weight="600"))
    if sub:
        p.append(svg_text(26, 56, sub, 13, GRAY))
    y0 = 88
    for i, (label, val, extra) in enumerate(rows):
        y = y0 + i * row_h
        bw = plot_w * (val / mx)
        p.append(svg_text(left - 10, y + 17, short(label, 42), 13, NAVY, "end"))
        p.append(f'<rect x="{left}" y="{y + 3}" width="{plot_w}" height="19" fill="{LIGHT}" rx="2"/>')
        p.append(f'<rect x="{left}" y="{y + 3}" width="{max(bw, 1):.1f}" height="19" '
                 f'fill="{bar_color}" rx="2"/>')
        p.append(svg_text(left + bw + 8, y + 17, value_fmt(val), 13, NAVY, weight="600"))
        if extra:
            p.append(svg_text(left + bw + 14 + len(value_fmt(val)) * 7.2, y + 17, extra,
                              12, GRAY))
    p.append("</svg>")
    return "".join(p)


def pareto_chart(labels: list[str], values: list[float], cum: list[float],
                 title: str, sub: str = "", w: int = 1000, h: int = 540,
                 n_labels: int = 14, val_labels: int = 10) -> str:
    """Столбцы + накопленная доля с линией 80 %."""
    left, right, top, bottom = 80, 70, 140, 116
    plot_w = w - left - right
    plot_h = h - top - bottom
    mx = max(values) if values else 1
    n = len(values)
    step = plot_w / max(n, 1)
    bw = min(step * 0.68, 30)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}">']
    p.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>')
    p.append(svg_text(26, 32, title, 22, NAVY, weight="600"))
    if sub:
        p.append(svg_text(26, 56, sub, 14, GRAY))

    # сетка и ось Y (млн ₽)
    for i in range(5):
        val = mx * i / 4
        y = top + plot_h - plot_h * i / 4
        p.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
                 f'stroke="{LIGHT}" stroke-width="1"/>')
        p.append(svg_text(left - 8, y + 4.5, f"{val / 1e6:.0f}", 13, GRAY, "end"))
    p.append(svg_text(left - 8, top - 16, "млн ₽", 13, GRAY, "end"))

    # линия 80 %
    y80 = top + plot_h * 0.2
    p.append(f'<line x1="{left}" y1="{y80:.1f}" x2="{left + plot_w}" y2="{y80:.1f}" '
             f'stroke="{RED}" stroke-width="1.6" stroke-dasharray="7 5"/>')
    p.append(svg_text(left + plot_w - 4, y80 - 6, "80 % накопленной доли", 13, RED, "end"))

    # столбцы
    pts = []
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = left + step * i + (step - bw) / 2
        bh = plot_h * (v / mx) if mx else 0
        y = top + plot_h - bh
        col = TEAL if cum[i] <= 80.0 else "#9FB6CC"
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                 f'fill="{col}" rx="1.5"/>')
        # сумма столбца — вертикально над столбцом, чтобы подписи не накладывались
        p.append(svg_text(x + bw / 2 + 4, y - 6, f"{v / 1e6:.1f}", 12, NAVY,
                          "start", rotate=-90))
        pts.append((x + bw / 2, top + plot_h - plot_h * (cum[i] / 100.0)))
        # порядковый номер под столбцом (соответствует номеру строки в таблице раздела)
        p.append(svg_text(x + bw / 2, top + plot_h + 18, str(i + 1), 11, GRAY, "middle"))
    # ось X
    p.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" '
             f'y2="{top + plot_h}" stroke="{GRAY}" stroke-width="1"/>')
    # накопленная линия
    path = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    p.append(f'<path d="{path}" fill="none" stroke="{GOLD}" stroke-width="2.2"/>')
    for i, (x, y) in enumerate(pts):
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{GOLD}"/>')
    p.append(svg_text(left + plot_w, h - 14,
                      "номера под столбцами соответствуют порядку строк в таблице раздела",
                      13, GRAY, "end"))
    p.append("</svg>")
    return "".join(p)


def line_chart(labels: list[str], values: list[float], title: str, sub: str = "",
               w: int = 1000, h: int = 400) -> str:
    left, right, top, bottom = 88, 50, 104, 96
    plot_w = w - left - right
    plot_h = h - top - bottom
    mx = max(values) if values else 1
    n = len(values)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}">']
    p.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>')
    p.append(svg_text(26, 32, title, 20, NAVY, weight="600"))
    if sub:
        p.append(svg_text(26, 56, sub, 13, GRAY))
    for i in range(5):
        val = mx * i / 4
        y = top + plot_h - plot_h * i / 4
        p.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
                 f'stroke="{LIGHT}" stroke-width="1"/>')
        p.append(svg_text(left - 8, y + 4.5, f"{val / 1e6:.1f}", 12, GRAY, "end"))
    step = plot_w / max(n - 1, 1)
    pts = [(left + step * i, top + plot_h - plot_h * (v / mx)) for i, v in enumerate(values)]
    p.append(f'<path d="{" ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))}" '
             f'fill="none" stroke="{BLUE}" stroke-width="2.6"/>')
    for i, (x, y) in enumerate(pts):
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.8" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2.2"/>')
        p.append(svg_text(x, y - 12, f"{values[i] / 1e6:.1f}", 12, NAVY, "middle"))
        p.append(svg_text(x, top + plot_h + 22, labels[i], 12, NAVY, "middle"))
    p.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" '
             f'stroke="{GRAY}" stroke-width="1"/>')
    p.append("</svg>")
    return "".join(p)


def spread_chart(rows: list[dict], title: str, sub: str = "", w: int = 1000,
                 h: int = 540) -> str:
    """Ценовой разброс: минимум—максимум, медиана, средневзвешенная (лог. шкала)."""
    import math

    left, right, top, bottom = 430, 70, 104, 56
    plot_w = w - left - right
    plot_h = h - top - bottom
    vals = [r["pmin"] for r in rows if r.get("pmin")] + [r["pmax"] for r in rows if r.get("pmax")]
    lo, hi = min(vals), max(vals)
    lo = max(lo * 0.7, 1.0)
    hi = hi * 1.3
    llo, lhi = math.log10(lo), math.log10(hi)

    def X(v: float) -> float:
        return left + plot_w * (math.log10(max(v, lo)) - llo) / (lhi - llo)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}">']
    p.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>')
    p.append(svg_text(26, 32, title, 20, NAVY, weight="600"))
    if sub:
        p.append(svg_text(26, 56, sub, 13, GRAY))
    # сетка
    for k in range(6):
        v = 10 ** (llo + (lhi - llo) * k / 5)
        x = X(v)
        p.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{top + plot_h}" '
                 f'stroke="{LIGHT}" stroke-width="1"/>')
        p.append(svg_text(x, top + plot_h + 20, f"{v:,.0f}".replace(",", " "), 12, GRAY, "middle"))
    p.append(svg_text(left + plot_w, h - 12, "цена за единицу, ₽ (логарифмическая шкала)",
                      12, GRAY, "end"))
    step = plot_h / max(len(rows), 1)
    for i, r in enumerate(rows):
        y = top + step * i + step / 2
        x1, x2 = X(r["pmin"]), X(r["pmax"])
        p.append(svg_text(left - 10, y + 4.5, short(r["name"], 44), 12, NAVY, "end"))
        p.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" '
                 f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round" opacity="0.55"/>')
        if r.get("pmed"):
            xm = X(r["pmed"])
            p.append(f'<line x1="{xm:.1f}" y1="{y - 7:.1f}" x2="{xm:.1f}" y2="{y + 7:.1f}" '
                     f'stroke="{NAVY}" stroke-width="2.2"/>')
        if r.get("pw"):
            xw = X(r["pw"])
            p.append(f'<circle cx="{xw:.1f}" cy="{y:.1f}" r="4" fill="{GOLD}"/>')
    # легенда
    p.append(svg_text(left, top - 16, "— минимум/максимум", 12, BLUE))
    p.append(svg_text(left + 150, top - 16, "│ медиана", 12, NAVY))
    p.append(svg_text(left + 250, top - 16, "● средневзвешенная", 12, GOLD))
    p.append("</svg>")
    return "".join(p)


def build_svgs(a: dict) -> list[tuple[str, str, dict]]:
    """Список (имя файла, SVG, описание рисунка) в порядке нумерации отчёта."""
    t = a["totals"]
    out: list[tuple[str, str, dict]] = []

    # 1. динамика по кварталам (первый рисунок в тексте отчёта — раздел 3.2)
    qs = [q["quarter"].replace("2025-", "Q") for q in a["by_quarter"]]
    svg = line_chart(qs, [q["sum"] for q in a["by_quarter"]],
                     "Рисунок 1 — Динамика объёма профиля по кварталам 2025 года",
                     "Сумма позиций профиля по дате заключения контракта, млн ₽")
    out.append(("fig_quarterly.png", svg,
                {"file": "img/fig_quarterly.png", "num": 1,
                 "title": "Динамика объёма профиля по кварталам 2025 года",
                 "source": "ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ"}))

    # 2. структура по видам
    kinds = [(k["title"], k["sum"], f'{k["share"]:.1f} % · {k["n"]} поз.')
             for k in a["by_kind"]]
    svg = hbar_chart(kinds, "Рисунок 2 — Структура закупок по укрупнённым видам",
                     "Профиль закупок 2025 года, % от объёма профиля")
    out.append(("fig_kinds.png", svg,
                {"file": "img/fig_kinds.png", "num": 2,
                 "title": "Структура закупок по укрупнённым видам",
                 "source": "ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ; "
                           "расчёт по позициям профиля"}))

    # 3. Парето категорий
    cats = a["by_category"]
    cum = [c["cum_share"] for c in cats]
    svg = pareto_chart([c["category"] for c in cats], [c["sum"] for c in cats], cum,
                       "Рисунок 3 — Парето товарных групп: вклад в 80 % объёма",
                       f"Профиль закупок 2025 года, {t['sum_scope'] / 1e9:.2f} млрд ₽; "
                       f"{t['categories_in_80']} из {t['categories_total']} групп")
    out.append(("fig_pareto_cat.png", svg,
                {"file": "img/fig_pareto_cat.png", "num": 3,
                 "title": "Парето товарных групп: вклад в 80 % объёма",
                 "source": "ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ; "
                           "расчёт по позициям профиля"}))

    # 4. Парето номенклатуры
    items = sorted(a["items"], key=lambda i: -(i["sum"] or 0))
    top = items[:40]
    svg = pareto_chart([i["name"] for i in top], [i["sum"] or 0 for i in top],
                       [i["cum_share"] for i in top],
                       "Рисунок 4 — Парето номенклатурных позиций",
                       f"Топ-40 позиций из {t['items_total']}; "
                       f"пунктир — накопленная доля 80 %", n_labels=12, h=540,
                       val_labels=12)
    out.append(("fig_pareto_items.png", svg,
                {"file": "img/fig_pareto_items.png", "num": 4,
                 "title": "Парето номенклатурных позиций",
                 "source": "ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ; "
                           "расчёт по позициям профиля"}))

    # 5. страны
    countries = [(c["country"], c["sum"], f'{c["share"]:.1f} %')
                 for c in a["by_country"][:12]]
    svg = hbar_chart(countries, "Рисунок 5 — Структура закупок по стране происхождения",
                     f"Атрибуция по {t['country_coverage']:.1f} % объёма профиля; "
                     "без указания страны — отдельно в таблице раздела 7", bar_color=TEAL)
    out.append(("fig_countries.png", svg,
                {"file": "img/fig_countries.png", "num": 5,
                 "title": "Структура закупок по стране происхождения",
                 "source": "ЕИС: поле «Страна происхождения» в спецификации контракта"}))

    # 6. ценовой разброс
    rows = []
    for i in items:
        if not i.get("price_min"):
            continue
        rows.append({"name": i["name"], "pmin": i["price_min"], "pmax": i["price_max"],
                     "pmed": i.get("price_median"), "pw": i.get("price_weighted"),
                     "sum": i["sum"]})
        if len(rows) >= 12:
            break
    svg = spread_chart(rows, "Рисунок 6 — Внутренний ценовой разброс по ключевым позициям",
                       "Минимум—максимум за 2025 год по позициям с известным количеством")
    out.append(("fig_price_spread.png", svg,
                {"file": "img/fig_price_spread.png", "num": 6,
                 "title": "Внутренний ценовой разброс по ключевым позициям",
                 "source": "Расчёт по данным ЕИС: цены позиций профиля за 2025 год"}))
    return out


def main() -> None:
    a = json.loads(DATA.read_text(encoding="utf-8"))
    figs: list[dict] = []
    for name, svg, meta in build_svgs(a):
        render(name, svg)
        figs.append(meta)
    figs.sort(key=lambda f: f["num"])
    (OUT_DIR / "figures.json").write_text(
        json.dumps(figs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"рисунков построено: {len(figs)} -> {OUT_DIR}")


if __name__ == "__main__":
    main()
