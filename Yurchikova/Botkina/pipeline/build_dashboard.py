"""Интерактивный дашборд по закупкам: analytics.json -> standalone HTML.

Вход:  data/<slug>/analytics.json
Выход: output/dashboard.html (ECharts встроен, файл открывается без сервера)

Покрывает § 8 ТЗ: KPI, структура, Pareto 80 %, страны, бенчмарки,
ключевая номенклатура, реестр с виртуальной прокруткой, методика,
светлая/тёмная/системная темы, печать, фильтры, поиск в таблицах и экспорт в Excel и CSV.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = cfg.DEFAULT_LPU
ANALYTICS = ROOT / "data" / SLUG / "analytics.json"
OUT = ROOT / "output" / "dashboard.html"
ECHARTS = ROOT.parent / "Hospitals" / "dashboard" / "vendor" / "echarts.min.js"


def build() -> None:
    a = json.loads(ANALYTICS.read_text(encoding="utf-8"))
    scope = [p for p in a["positions"] if p["scope"] in ("main", "borderline")]

    def ikey(p: dict) -> str:
        ktru = (p.get("ktru") or "").split("-")[0]
        nm = re.sub(r"[^а-яa-z0-9 ]", "", (p.get("name") or "").lower())
        nm = re.sub(r"\s+", " ", nm).strip()[:70]
        return f"{ktru or p.get('okpd2') or ''}|{nm}"

    keys80 = {it["key"] for it in a["items"] if it.get("in_80")}

    name_country: dict[str, Counter] = defaultdict(Counter)
    for p in scope:
        if p.get("country"):
            name_country[p["name"]][p["country"]] += p["sum"] or 0

    items = []
    for it in a["items"]:
        cc = name_country.get(it["name"]) or Counter()
        top_country, top_sum = cc.most_common(1)[0] if cc else ("—", 0)
        items.append({
            "name": it["name"], "ktru": it.get("ktru"), "okpd2": it.get("okpd2"),
            "cat": it["category"], "kind": it["kind"], "unit": it.get("unit"),
            "qty": it.get("qty"), "sum": it["sum"], "n": it["n"],
            "sup": it.get("n_suppliers"), "in80": bool(it.get("in_80")),
            "med": it.get("price_median"), "min": it.get("price_min"),
            "max": it.get("price_max"), "p25": it.get("price_p25"),
            "p75": it.get("price_p75"), "months": it.get("months") or [],
            "country": top_country,
            "countryShare": round(top_sum / (it["sum"] or 1) * 100, 1) if cc else None,
        })

    cat80 = {c["category"] for c in a["by_category"] if c.get("in_80")}
    payload = {
        "meta": a["meta"],
        "totals": a["totals"],
        "kinds": a["by_kind"],
        "categories": a["by_category"],
        "months": a["by_month"],
        "countries": a["by_country"],
        "sources": a["by_source"],
        "methods": a["by_method"],
        "suppliers": sorted({p.get("supplier") for p in scope if p.get("supplier")}),
        "items": items,
        "positions": [
            {
                "name": p["name"], "cat": p["category"], "kind": p["kind"],
                "unit": p.get("unit"), "qty": p.get("qty"), "price": p.get("unit_price"),
                "ktru": p.get("ktru"), "okpd2": p.get("okpd2"),
                "sum": p.get("sum"), "country": p.get("country") or "не определена",
                "month": p.get("month"), "source": p.get("source"),
                "method": p.get("method"), "sup": p.get("supplier"),
                "est": bool(p.get("estimated")), "in80": p["category"] in cat80,
                "in80item": ikey(p) in keys80,
                "borderline": p["scope"] == "borderline",
            }
            for p in scope
        ],
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = TEMPLATE.replace("/*__DATA__*/null", data)
    lib = ECHARTS.read_text(encoding="utf-8")
    html = html.replace('<script src="echarts"></script>', f"<script>{lib}</script>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"-> {OUT} ({OUT.stat().st_size / 1e6:.1f} МБ), позиций: {len(scope)}")


TEMPLATE = r"""<!doctype html>
<html lang="ru" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Закупки МНКЦ им. С.П. Боткина — 2025</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f4e79'/%3E%3Cpath d='M8 22V10h3v5.5h2V10h3v12h-3v-4h-2v4z' fill='%23fff'/%3E%3Cpath d='M20 10h4v12h-4z' fill='%234fa3d1'/%3E%3C/svg%3E">
<script src="echarts"></script>
<style>
:root{
  --bg:#f4f7fb; --panel:#fff; --panel2:#f7f9fc; --ink:#17212b; --muted:#6b7787;
  --line:#e2e8f0; --accent:#1f4e79; --accent2:#2f80ed; --grid:#eef2f7;
  --green:#2e7d5b; --greenbg:#e7f3ec; --warn:#c77d1a; --warnbg:#fdf3e2;
  --red:#b4423a; --chip:#eaf1f9;
}
html[data-theme="dark"]{
  --bg:#0f1720; --panel:#151f2b; --panel2:#1a2634; --ink:#e8eef5; --muted:#9fb0c0;
  --line:#273446; --accent:#9cc3e6; --accent2:#5aa7f0; --grid:#233142;
  --green:#7ec9a4; --greenbg:#1c3329; --warn:#e0b06a; --warnbg:#332617;
  --red:#e08a84; --chip:#1b2a3a;
}
@media (prefers-color-scheme: dark){
  html[data-theme="auto"]{
    --bg:#0f1720; --panel:#151f2b; --panel2:#1a2634; --ink:#e8eef5; --muted:#9fb0c0;
    --line:#273446; --accent:#9cc3e6; --accent2:#5aa7f0; --grid:#233142;
    --green:#7ec9a4; --greenbg:#1c3329; --warn:#e0b06a; --warnbg:#332617;
    --red:#e08a84; --chip:#1b2a3a;
  }
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);
  font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
h1,h2,h3{margin:0;font-weight:650;letter-spacing:-.01em}
a{color:var(--accent2)}
.wrap{max-width:1460px;margin:0 auto;padding:22px 20px 60px}
header.top{background:linear-gradient(120deg,#12324f,#1f4e79 55%,#2c6c9e);color:#fff;
  border-radius:16px;padding:24px 28px;display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
header.top h1{font-size:25px;line-height:1.2}
header.top .sub{opacity:.9;margin-top:6px;font-size:13.5px;max-width:900px}
header.top .right{display:flex;flex-direction:column;gap:8px;align-items:flex-end}
header.top .badge{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.25);
  padding:9px 13px;border-radius:12px;font-size:12.5px;line-height:1.55;min-width:215px}
.topbtns{display:flex;gap:7px}
.topbtns button{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);
  color:#fff;border-radius:9px;padding:6px 11px;font:inherit;font-size:12px;cursor:pointer}
.topbtns button:hover{background:rgba(255,255,255,.24)}
.toolbar{position:sticky;top:0;z-index:30;background:color-mix(in srgb, var(--bg) 94%, transparent);
  backdrop-filter:blur(8px);padding:12px 0 10px;margin:14px 0 4px;border-bottom:1px solid var(--line)}
.filters{display:flex;gap:9px;flex-wrap:wrap;align-items:end}
.field{display:flex;flex-direction:column;gap:4px;flex:1 1 190px;min-width:0}
.field label{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
select,input[type=search],input[type=number]{background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:8px 10px;font:inherit;color:var(--ink);min-width:150px;outline:none}
select:focus,input:focus{border-color:var(--accent2);box-shadow:0 0 0 3px rgba(47,128,237,.12)}
select.wide{min-width:0}
input[type=number]{width:130px}
.field select,.field input{width:100%;min-width:0}
.chk{display:flex;align-items:center;gap:7px;padding:8px 10px;background:var(--panel);
  border:1px solid var(--line);border-radius:10px;cursor:pointer;user-select:none;font-size:13px}
button.ghost{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 12px;
  font:inherit;cursor:pointer;color:var(--ink)}
button.ghost:hover{border-color:var(--accent2);color:var(--accent2)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;min-height:0}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--chip);border:1px solid var(--line);
  border-radius:999px;padding:3px 9px;font-size:11.5px;color:var(--ink)}
.chip b{font-weight:650}
.chip button{border:0;background:none;color:var(--muted);cursor:pointer;font-size:14px;line-height:1;padding:0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin:14px 0 6px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:13px 15px}
.kpi .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.kpi .value{font-size:22px;font-weight:700;margin-top:5px;letter-spacing:-.02em}
.kpi .hint{font-size:11.5px;color:var(--muted);margin-top:3px}
nav.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0 0}
nav.tabs a{text-decoration:none;color:var(--muted);background:var(--panel);border:1px solid var(--line);
  padding:7px 11px;border-radius:9px;font-size:12.5px}
nav.tabs a:hover{color:var(--accent2);border-color:var(--accent2)}
section.block{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-top:14px;scroll-margin-top:240px}
section.block h2{font-size:15px}
section.block .note{font-size:12px;color:var(--muted);margin:3px 0 10px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.chart{height:330px;width:100%}
.chart.tall{height:380px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);white-space:nowrap}
th.sortable{cursor:pointer;user-select:none}
th.sortable:hover{color:var(--accent2)}
td.num,th.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
tr:hover td{background:var(--panel2)}
.badge80{display:inline-block;padding:2px 7px;border-radius:999px;background:var(--greenbg);color:var(--green);
  font-size:10.5px;font-weight:600;white-space:nowrap}
.badgeNo{display:inline-block;padding:2px 7px;border-radius:999px;background:var(--panel2);color:var(--muted);
  font-size:10.5px;white-space:nowrap}
.badgeEst{display:inline-block;padding:2px 7px;border-radius:999px;background:var(--warnbg);color:var(--warn);
  font-size:10.5px;white-space:nowrap}
.tablewrap{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:12px}
.tablewrap table{margin:0}
.tablewrap thead th{position:sticky;top:0;background:var(--panel2);z-index:2}
.hintbar{display:flex;justify-content:space-between;gap:10px;align-items:center;margin:8px 0;font-size:12px;color:var(--muted)}
.tbar{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin:8px 0 6px;font-size:12px}
.tbar input[type=search]{flex:1 1 170px;min-width:140px;max-width:300px;background:var(--panel2);
  border:1px solid var(--line);border-radius:9px;color:var(--ink);padding:6px 9px;font:inherit;font-size:12.5px;outline:none}
.tbar input[type=search]:focus{border-color:var(--accent2)}
.tbar select{background:var(--panel2);border:1px solid var(--line);border-radius:9px;color:var(--ink);
  padding:5px 7px;font:inherit;font-size:12px}
.tbar .lbl{color:var(--muted)}
.tbar .cnt{color:var(--muted);white-space:nowrap;margin-left:auto}
.tbar button{border:1px solid var(--line);background:var(--panel2);color:var(--ink);border-radius:9px;
  padding:5px 11px;font:inherit;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap}
.tbar button:hover{border-color:var(--accent2);color:var(--accent2)}
.tbar button.xl{border-color:var(--green);color:var(--green)}
th.sortable::after{content:' ↕';opacity:.35;font-size:9px}
th.sortable[data-dir="asc"]::after{content:' ▲';opacity:1;color:var(--accent2);font-size:9px}
th.sortable[data-dir="desc"]::after{content:' ▼';opacity:1;color:var(--accent2);font-size:9px}
.registry{position:relative;height:600px;overflow:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
.registry table{table-layout:fixed;min-width:1240px}
.registry thead th{position:sticky;top:0;z-index:3;background:var(--panel2);border-bottom:1px solid var(--line)}
.registry tbody{position:relative}
.registry tbody tr{position:absolute;left:0;right:0;height:38px}
.registry tbody td{height:38px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-bottom:1px solid var(--grid)}
.registry .spacer{position:static !important;visibility:hidden}
.registry .spacer td{padding:0;border:0}
.regname{max-width:360px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.pcard{border:1px solid var(--line);border-radius:12px;padding:13px 14px;background:var(--panel2)}
.pcard h3{font-size:13.5px;line-height:1.35;margin-bottom:8px}
.pcard .row{display:flex;justify-content:space-between;gap:10px;font-size:12px;padding:2px 0;color:var(--muted)}
.pcard .row b{color:var(--ink);font-weight:600;text-align:right}
.pcard .sum{font-size:17px;font-weight:700;color:var(--accent2);margin-bottom:6px}
.empty{padding:24px;text-align:center;color:var(--muted)}
.srcline{margin-top:12px;padding-top:8px;border-top:1px dashed var(--line);font-size:11px;color:var(--muted)}
.factlegend{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;margin:6px 0 10px;
  padding:6px 10px;border:1px solid var(--line);border-radius:10px;background:var(--panel2);
  font-size:11.5px;color:var(--muted)}
.factlegend b{color:var(--ink);font-weight:600}
.factlegend .tag{display:inline-flex;align-items:center;gap:5px}
.factlegend .sw{display:inline-block;width:10px;height:10px;border-radius:3px;background:var(--ok)}
.factlegend .sw.est{background:var(--warn)}
.howto{margin:2px 0 14px;border:1px solid var(--line);border-radius:12px;padding:10px 13px;background:var(--panel2)}
.howto summary{cursor:pointer;font-weight:650;font-size:13.5px;color:var(--ink)}
.howto ul{margin:8px 0 2px;padding-left:19px;font-size:12.5px;color:var(--muted)}
.howto li{margin:3px 0}
footer{margin-top:24px;color:var(--muted);font-size:12px;line-height:1.6}
.method p{margin:8px 0;font-size:13px;color:var(--ink)}
.method h3{font-size:13.5px;margin:14px 0 6px;color:var(--accent)}
.method ul{margin:6px 0;padding-left:20px;font-size:12.5px;color:var(--muted)}
.method li{margin:2px 0}
@media (max-width:1100px){.toolbar{position:static}.kpis{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}
@media (max-width:700px){.cards{grid-template-columns:1fr}}
@media print{
  :root{--bg:#fff;--panel:#fff;--panel2:#fff;--ink:#000;--muted:#444;--line:#bbb;--grid:#ddd}
  html[data-theme]{--bg:#fff;--panel:#fff;--panel2:#fff;--ink:#000;--muted:#444;--line:#bbb;--grid:#ddd}
  body{background:#fff}
  .toolbar,nav.tabs,.topbtns,.tbar,footer .noprint{display:none !important}
  header.top{background:#12324f !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  section.block{break-inside:auto;break-before:page;box-shadow:none;border-color:#bbb}
  section.block:first-of-type{break-before:auto}
  .tablewrap{max-height:none;overflow:visible}
  .tablewrap thead{display:table-header-group}
  .registry{height:auto;overflow:visible}
  .registry table{min-width:0}
  .registry thead{display:table-header-group}
  .registry tbody tr{position:static !important;display:table-row}
  .chart{height:300px;break-inside:avoid}
}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <h1>Закупки медицинских товаров — 2025 год</h1>
      <div class="sub" id="subtitle"></div>
    </div>
    <div class="right">
      <div class="topbtns">
        <button id="themeBtn" title="Светлая / тёмная / системная тема">Тема: светлая</button>
        <button id="printBtn" title="Печать или сохранение в PDF">Печать / PDF</button>
      </div>
      <div class="badge" id="srcdates"></div>
    </div>
  </header>

  <div class="toolbar">
    <div class="filters">
      <div class="field"><label for="fkind">Вид закупки</label><select id="fkind"><option value="">Все виды</option></select></div>
      <div class="field"><label for="fcat">Товарная группа</label><select id="fcat" class="wide"><option value="">Все группы</option></select></div>
      <div class="field"><label for="fcountry">Страна</label><select id="fcountry" class="wide"><option value="">Все страны</option></select></div>
      <div class="field"><label for="forigin">Происхождение</label><select id="forigin">
        <option value="">Россия и импорт</option><option value="ru">только Россия</option>
        <option value="import">только импорт</option><option value="unknown">страна не указана</option>
      </select></div>
      <div class="field"><label for="fsup">Поставщик</label><select id="fsup" class="wide"><option value="">Все поставщики</option></select></div>
      <div class="field"><label for="fmin">Сумма от, ₽</label><input id="fmin" type="number" min="0" step="1000" placeholder="0"></div>
      <div class="field"><label for="fmax">Сумма до, ₽</label><input id="fmax" type="number" min="0" step="1000" placeholder="без ограничения"></div>
      <div class="field"><label for="fq">Поиск</label><input id="fq" type="search" placeholder="наименование позиции"></div>
      <label class="chk"><input type="checkbox" id="f80"> номенклатура 80 %</label>
      <label class="chk"><input type="checkbox" id="fest"> без оценочных</label>
      <button class="ghost" id="reset">Сбросить</button>
      <button class="ghost" id="csv" title="Реестр позиций: UTF-8 с BOM, разделитель «;»">CSV — реестр</button>
      <button class="ghost" id="xlsx" title="Весь отчёт текущего среза одним файлом .xlsx">Excel — весь отчёт</button>
    </div>
    <div class="chips" id="chips"></div>
  </div>

  <nav class="tabs">
    <a href="#kpi">Показатели</a>
    <a href="#overview">Обзор</a>
    <a href="#categories">Категории 80 %</a>
    <a href="#items">Номенклатура</a>
    <a href="#country">Страны</a>
    <a href="#bench">Бенчмарки</a>
    <a href="#key">Ключевая номенклатура</a>
    <a href="#registry">Реестр</a>
    <a href="#method">Методика</a>
  </nav>

  <!-- ОСНОВНЫЕ ПОКАЗАТЕЛИ -->
  <section class="block" id="kpi">
    <h2>Основные показатели</h2>
    <div class="note">Показатели рассчитаны по выбранному срезу; фильтры в шапке действуют на все разделы одновременно.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <div class="kpis" id="kpis"></div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- ОБЗОР -->
  <section class="block" id="overview">
    <h2>Структура и динамика</h2>
    <div class="note">Суммы профильных позиций по выбранному срезу; фильтры сверху действуют на все разделы.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <div class="grid2">
      <div><div class="chart" id="chKind"></div><div class="note" id="kindNote" style="margin-top:2px"></div></div>
      <div><div class="chart" id="chMethod"></div></div>
      <div><div class="chart" id="chMonth"></div></div>
      <div><div class="chart" id="chCountry"></div></div>
    </div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- КАТЕГОРИИ -->
  <section class="block" id="categories">
    <h2>Категории по правилу 80 %</h2>
    <div class="note">Столбцы — сумма группы, линия — накопленная доля. Пунктир — порог 80 %. Зелёные столбцы — группы 80 %-набора.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <div class="chart tall" id="chParetoCat"></div>
    <div class="hintbar"><span id="catHint"></span><span>Нажмите на строку, чтобы показать позиции группы</span></div>
    <div class="tablewrap"><table id="catTable"></table></div>
    <div style="margin-top:14px">
      <h3 id="catDetailTitle" style="font-size:13.5px;margin:4px 0 8px"></h3>
      <div class="tablewrap" style="max-height:320px"><table id="catDetail"></table></div>
    </div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- НОМЕНКЛАТУРА -->
  <section class="block" id="items">
    <h2>Номенклатура по правилу 80 %</h2>
    <div class="note">Pareto по позициям и таблица набора. Поиск и фильтры — в верхней панели.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <div class="chart tall" id="chParetoItems"></div>
    <div class="hintbar"><span id="itemsHint"></span><span id="itemsShown"></span></div>
    <div class="tablewrap"><table id="itemsTable"></table></div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- СТРАНЫ -->
  <section class="block" id="country">
    <h2>Страна происхождения</h2>
    <div class="note">Россия, импорт и позиции без указания страны. Данные по выбранному срезу.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Страна указывается только по данным ЕИС; догадки не используются.</span></div>
    <div class="grid2">
      <div><div class="chart" id="chCountryBar"></div></div>
      <div><div class="chart" id="chOrigin"></div></div>
    </div>
    <div class="hintbar"><span id="countryHint"></span></div>
    <div class="tablewrap"><table id="countryTable"></table></div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- БЕНЧМАРКИ -->
  <section class="block" id="bench">
    <h2>Внутренние ценовые бенчмарки</h2>
    <div class="note">Разброс цен по позициям 80 %-набора с двумя и более закупками. На графике — цены к медиане позиции (100 %).</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Бенчмарки внутренние, по закупкам учреждения за 2025 год.</span></div>
    <div class="chart tall" id="chBox"></div>
    <div class="hintbar"><span id="benchHint"></span><span>Наведите курсор на «ящик», чтобы увидеть цены в рублях</span></div>
    <div class="tablewrap"><table id="benchTable"></table></div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- КЛЮЧЕВАЯ -->
  <section class="block" id="key">
    <h2>Ключевая номенклатура</h2>
    <div class="note">Карточки первых позиций 80 %-набора: объём, закупки, поставщики, цена, страна, месяцы.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <div class="cards" id="keyCards"></div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- РЕЕСТР -->
  <section class="block" id="registry">
    <h2>Реестр позиций</h2>
    <div class="note">Одна строка — одна позиция. Без номеров, дат и предметов контрактов; виртуальная прокрутка, сортировка по столбцам.</div>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Столбец «Класс» — признак достоверности позиции.</span></div>
    <div class="hintbar"><span id="regHint"></span><span>Клик по заголовку — сортировка</span></div>
    <div class="registry" id="regBox">
      <table>
        <thead><tr>
          <th class="sortable" data-k="idx" style="width:38px">№</th>
          <th class="sortable" data-k="name" style="width:330px">Позиция</th>
          <th class="sortable" data-k="cat" style="width:130px">Группа</th>
          <th style="width:60px">Ед.</th>
          <th class="sortable num" data-k="qty" style="width:80px">Кол-во</th>
          <th class="sortable num" data-k="price" style="width:100px">Цена</th>
          <th class="sortable num" data-k="sum" style="width:115px">Сумма</th>
          <th class="sortable" data-k="country" style="width:105px">Страна</th>
          <th class="sortable" data-k="month" style="width:62px">Месяц</th>
          <th class="sortable" data-k="sup" style="width:160px">Поставщик</th>
          <th style="width:60px">Класс</th>
        </tr></thead>
        <tbody id="regBody"></tbody>
      </table>
    </div>
    <div class="srcline" data-srcline></div>
  </section>

  <!-- МЕТОДИКА -->
  <section class="block method" id="method">
    <h2>Методика и ограничения</h2>
    <div class="factlegend"><span class="tag"><span class="sw"></span><b>факт</b> — данные первичного источника ЕИС без изменений</span><span class="tag"><span class="sw est"></span><b>оценка</b> — расчётное, агрегированное или неполное значение</span><span>Оценочные значения не предназначены для официальной отчётности.</span></div>
    <details class="howto">
      <summary>Как открыть и работать с дашбордом</summary>
      <ul>
        <li>Файл открывается двойным щелчком в Chrome, Edge или Firefox. Интернет и сервер не нужны: все данные встроены в файл, внешние библиотеки и запросы не используются.</li>
        <li>Фильтры верхней панели (вид закупки, товарная группа, страна, российский/импортный товар, поставщик, диапазон суммы позиции, поиск по наименованию) применяются одновременно ко всем разделам. Выбранные значения отображаются в шапке под фильтрами; кнопка «Сбросить» очищает их.</li>
        <li>Фильтры не меняют учёт: карточки «Профильный объём», «Отсечено фильтрами», «Исключено» и «Общий объём 2025» всегда дают проверяемое равенство — срез + отсечено фильтрами + исключено = общий объём.</li>
        <li>Кнопка «Тема» переключает светлую, тёмную и системную тему. Кнопка «Печать / PDF» готовит версию для печати: формат A4, светлая тема, разрывы страниц по разделам, повтор шапок таблиц и полный реестр позиций.</li>
        <li>Кнопка «CSV — реестр» в верхней панели выгружает текущий отфильтрованный срез реестра позиций: разделитель «;», кодировка UTF-8 с BOM, файл открывается в Excel без дополнительной настройки. Кнопка «Excel — весь отчёт» рядом собирает один файл .xlsx: описание среза, показатели, все таблицы в текущем виде и полный реестр среза.</li>
        <li>Над каждой таблицей — своя строка управления: поиск только по этой таблице, счётчик показанных строк, число выводимых строк для длинных таблиц и кнопки «Excel» и «CSV». Выгружаются ровно те строки, что видны в таблице после фильтров и сортировки; числа в .xlsx остаются числами, поэтому из файла можно строить сводные таблицы.</li>
        <li>В таблицах клик по заголовку сортирует строки: значок ▲ или ▼ показывает, по какому столбцу и в каком направлении идёт сортировка. Строки реестра подгружаются по мере прокрутки, а в печать выводятся полностью.</li>
        <li>Оценочные значения (сумма позиции распределена по цене контракта) помечены словом «оценка».</li>
      </ul>
    </details>
    <p id="methodMeta"></p>
    <h3>Источники и период</h3>
    <ul>
      <li>44-ФЗ — реестр контрактов ЕИС; 223-ФЗ — реестр договоров ЕИС.</li>
      <li>Период — 2025 год, учёт по дате заключения контракта (договора).</li>
      <li>Поиск по наименованию заказчика с проверкой ИНН, КПП, ОГРН; одноимённые учреждения исключены.</li>
    </ul>
    <h3>Классификатор</h3>
    <ul>
      <li>L1 — вид закупки: медицинское оборудование, расходные материалы, имплантаты, лабораторные реагенты, медицинская мебель и одежда, прочие медицинские товары.</li>
      <li>L2 — товарная группа по ОКПД2 и маркерам наименования; внутри 32.50.13 выделены роботизированная хирургия, офтальмология, катетеры и дренажи.</li>
      <li>L3 — номенклатурная позиция: КТРУ + нормализованное наименование.</li>
      <li>main — основной профиль; borderline — лабораторные реагенты, дезинфекция, мебель и одежда, запчасти; excluded — фармация, хозяйственные расходы, услуги и работы.</li>
    </ul>
    <h3>Правило 80 %</h3>
    <p>Все группы или позиции до достижения 80 % профильного объёма; это не фиксированный топ-10. Группы с равной суммой на границе включаются вместе.</p>
    <h3>Классы достоверности</h3>
    <ul>
      <li><b>факт</b> — данные первичного источника без изменений;</li>
      <li><b>оценка</b> — расчётное, агрегированное или неполное значение; в реестре помечено оранжевым.</li>
    </ul>
    <h3>Ограничения</h3>
    <ul>
      <li>Закрытые закупки и закупки, не подлежащие публикации, в реестрах отсутствуют.</li>
      <li>Закупки на Портале поставщиков Москвы в ЕИС не публикуются и в объём не входят.</li>
      <li>Часть контрактов не содержит количества и суммы позиций: сумма распределена по цене контракта и помечена как оценка.</li>
      <li>Ставка НДС в реестре контрактов не публикуется, поэтому не рассчитывается.</li>
      <li>В реестре договоров 223-ФЗ ЕИС не публикует наименование и ИНН поставщика — ни в карточке договора, ни в печатной форме, ни в реестре. Для таких позиций поставщик указан как «не указан в ЕИС (реестр 223-ФЗ)», счётчик поставщиков относится к контрактам 44-ФЗ.</li>
      <li>Страна происхождения указывается только по данным источника; догадки не используются.</li>
      <li>Бенчмарки — внутренние, по закупкам учреждения за 2025 год; внешние прайсы не используются.</li>
    </ul>
    <h3>Источники</h3>
    <ul>
      <li>https://zakupki.gov.ru/epz/contract/search/results.html</li>
      <li>https://zakupki.gov.ru/epz/contractfz223/search/results.html</li>
    </ul>
    <div class="srcline" data-srcline></div>
  </section>

  <footer>
    Профиль — основной и пограничные виды; фармация, хозяйственные расходы, услуги и работы исключены.
    Суммы — по данным ЕИС на <span id="fdate"></span>. Оценочные значения помечены.
    <span class="noprint">Дашборд описательный: без выводов, рекомендаций и оценок поставщиков.</span>
  </footer>
</div>

<script>
const DATA = /*__DATA__*/null;
const SUP_UNKNOWN = 'не указан в ЕИС (реестр 223-ФЗ)';
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const fmt0 = new Intl.NumberFormat('ru-RU', {maximumFractionDigits: 0});
const fmt2 = new Intl.NumberFormat('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2});
const money = (v) => v == null ? '—' : fmt2.format(v) + ' ₽';
const mln = (v) => v == null ? '—' : (v / 1e6).toLocaleString('ru-RU', {maximumFractionDigits: 1}) + ' млн ₽';
const pct = (v) => v == null ? '—' : v.toLocaleString('ru-RU', {maximumFractionDigits: 1}) + ' %';
const mln0 = (v) => (!v || v < 50000) ? '—' : mln(v);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const MON = {1:'янв',2:'фев',3:'мар',4:'апр',5:'май',6:'июн',7:'июл',8:'авг',9:'сен',10:'окт',11:'ноя',12:'дек'};
const KIND = Object.fromEntries(DATA.kinds.map(k => [k.kind, k.title]));
const KIND_SHORT = {
  equipment:'Медоборудование', consumable:'Расходные материалы', implant:'Имплантаты',
  lab:'Лабораторные реагенты', furniture:'Медмебель и одежда', medical_other:'Прочие медизделия'
};
const CATMETA = Object.fromEntries(DATA.categories.map(c => [c.category, c]));
const CAT_SHORT = {
  'Инструменты для роботизированной хирургии':'Робот. хирургия',
  'Реагенты диагностические (ИВД)':'Реагенты ИВД',
  'Инструменты и приспособления медицинские':'Инструменты',
  'Изделия медицинские прочие':'Изделия прочие',
  'Имплантаты, стенты и эндопротезы':'Имплантаты',
  'Катетеры, дренажи и троакары':'Катетеры',
  'Перчатки и изделия медицинские из резины':'Перчатки',
  'Офтальмологические наборы и инструменты':'Офтальмология',
  'Реагенты лабораторные прочие':'Реагенты лаб.',
  'Трубки, шланги и расходные материалы полимерные':'Трубки',
  'Медицинская одежда и белье':'Медодежда',
  'Материалы диагностические':'Диагностика',
  'Оптика и оптические приборы':'Оптика',
  'Оборудование для анестезии, ИВЛ и реанимации':'Анестезия и ИВЛ',
  'Оборудование лабораторное':'Оборуд. лаб.',
  'Оборудование для функциональной диагностики':'Оборуд. функц.',
  'Мебель медицинская':'Мебель мед.',
  'Оборудование электрическое прочее':'Оборуд. электр.',
  'Расходные материалы прочие':'Расходные мат.',
};
const shortCat = s => CAT_SHORT[s] || (s.length > 18 ? s.slice(0,17) + '…' : s);

// ---------- состояние ----------
const state = {kind:'', cat:'', country:'', origin:'', sup:'', min:null, max:null, q:'', only80:false, noEst:false};
const sortState = {cat:{k:'sum',d:-1}, items:{k:'sum',d:-1}, bench:{k:'sum',d:-1}, reg:{k:'sum',d:-1},
  country:{k:'orig',d:-1}, cd:{k:'sum',d:-1}};
// локальные фильтры и лимиты строк внутри таблиц (не трогают остальные разделы)
const tstate = {cat:{q:''}, catdet:{q:'',limit:12}, items:{q:'',limit:300},
  bench:{q:'',limit:200}, country:{q:''}, reg:{q:''}};
const TBL = {
  cat:{el:'#catTable', sheet:'Категории', title:'Категории по правилу 80 %'},
  catdet:{el:'#catDetail', sheet:'Позиции группы', title:'Позиции товарной группы'},
  items:{el:'#itemsTable', sheet:'Номенклатура', title:'Номенклатура по правилу 80 %'},
  bench:{el:'#benchTable', sheet:'Бенчмарки', title:'Ценовые бенчмарки'},
  country:{el:'#countryTable', sheet:'Страны', title:'Страна происхождения по товарным группам'},
  reg:{el:'#regBox', sheet:'Реестр', title:'Реестр позиций'}
};
let lastKpi = [];
const selected = {cat:''};

function matchPos(p){
  if (state.kind && p.kind !== state.kind) return false;
  if (state.cat && p.cat !== state.cat) return false;
  if (state.country && p.country !== state.country) return false;
  if (state.origin === 'ru' && p.country !== 'Россия') return false;
  if (state.origin === 'import' && (p.country === 'Россия' || p.country === 'не определена')) return false;
  if (state.origin === 'unknown' && p.country !== 'не определена') return false;
  if (state.sup && p.sup !== state.sup) return false;
  if (state.min != null && (p.sum || 0) < state.min) return false;
  if (state.max != null && (p.sum || 0) > state.max) return false;
  if (state.noEst && p.est) return false;
  if (state.only80 && !p.in80item) return false;
  if (state.q && !p.name.toLowerCase().includes(state.q)) return false;
  return true;
}
function matchItem(it){
  if (state.kind && it.kind !== state.kind) return false;
  if (state.cat && it.cat !== state.cat) return false;
  if (state.only80 && !it.in80) return false;
  if (state.q && !it.name.toLowerCase().includes(state.q)) return false;
  if (state.min != null && (it.sum || 0) < state.min) return false;
  if (state.max != null && (it.sum || 0) > state.max) return false;
  return true;
}
const P = () => DATA.positions.filter(matchPos);
const I = () => DATA.items.filter(matchItem);
let _fi = null;
function FI(){
  if (_fi) return _fi;
  const m = new Map();
  for (const p of P()){
    const ktru = (p.ktru || '').split('-')[0];
    const nm = (p.name || '').toLowerCase().replace(/[^а-яa-z0-9 ]/g, '').replace(/\s+/g, ' ').trim().slice(0, 70);
    const key = (ktru || p.okpd2 || '') + '|' + nm;
    let it = m.get(key);
    if (!it){
      it = {key, name:p.name, cat:p.cat, kind:p.kind, unit:p.unit, qty:null, sum:0, n:0,
            supSet:new Set(), prices:[], months:new Set(), cc:new Map(), in80:p.in80item};
      m.set(key, it);
    }
    it.sum += p.sum || 0;
    it.n += 1;
    if (p.qty != null) it.qty = (it.qty || 0) + p.qty;
    if (p.unit && !it.unit) it.unit = p.unit;
    if (p.sup) it.supSet.add(p.sup);
    if (p.price != null) it.prices.push(p.price);
    if (p.month) it.months.add(p.month);
    it.cc.set(p.country, (it.cc.get(p.country)||0) + (p.sum||0));
  }
  _fi = [...m.values()].map(it=>{
    const pr = it.prices.slice().sort((a,b)=>a-b);
    const med = pr.length ? (pr.length % 2 ? pr[(pr.length-1)/2] : (pr[pr.length/2-1]+pr[pr.length/2])/2) : null;
    const q = f => pr.length ? pr[Math.min(pr.length-1, Math.floor(pr.length*f))] : null;
    const cc = [...it.cc.entries()].sort((a,b)=>b[1]-a[1]);
    const top = cc[0];
    return {name:it.name, cat:it.cat, kind:it.kind, unit:it.unit, qty:it.qty, sum:it.sum,
      n:it.n, sup:it.supSet.size, med, min:pr.length?pr[0]:null,
      max:pr.length?pr[pr.length-1]:null, p25:q(.25), p75:q(.75),
      months:[...it.months].sort(), country: top?top[0]:'—',
      countryShare: top && it.sum ? top[1]/it.sum*100 : null, in80:false};
  });
  const sorted = _fi.slice().sort((a,b)=>b.sum-a.sum);
  const total = sorted.reduce((s,it)=>s+(it.sum||0),0);
  let acc = 0;
  for (const it of sorted){
    it.in80 = true; acc += it.sum || 0;
    if (total && acc/total >= 0.8) break;
  }
  return _fi;
}

function normMethod(s){
  const t = (s || '').toLowerCase();
  if (t.startsWith('электронный аукцион')) return 'Электронный аукцион';
  if (t.startsWith('аукцион')) return 'Аукцион';
  if (t.startsWith('запрос котировок')) return 'Запрос котировок';
  if (t.startsWith('закупка у единственного')) return 'Единственный поставщик';
  if (t.startsWith('конкурс')) return 'Конкурс';
  if (t.startsWith('закупка, осуществляемая')) return 'Закупка по ч. 12 ст. 93';
  return s && s.length > 32 ? s.slice(0,31) + '…' : (s || '—');
}
function agg(rows, key){
  const m = new Map();
  for (const r of rows){
    const k = key === 'method' ? normMethod(r[key]) : (r[key] || '—');
    m.set(k, (m.get(k) || 0) + (r.sum || 0));
  }
  return [...m.entries()].sort((a,b) => b[1]-a[1]);
}
function sortRows(rows, st, get){
  return rows.slice().sort((a,b) => {
    const va = get(a), vb = get(b);
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === 'string') return st.d * va.localeCompare(vb, 'ru');
    return st.d * (va - vb);
  });
}

// ---------- тема ----------
const THEME_KEY = 'botkina-theme';
function applyTheme(mode){
  document.documentElement.dataset.theme = mode;
  $('#themeBtn').textContent = 'Тема: ' + ({light:'светлая', dark:'тёмная', auto:'системная'}[mode]);
  localStorage.setItem(THEME_KEY, mode);
  setTimeout(() => { drawAll(); }, 30);
}
function cycleTheme(){
  const cur = document.documentElement.dataset.theme || 'light';
  applyTheme(cur === 'light' ? 'dark' : cur === 'dark' ? 'auto' : 'light');
}
function colors(){
  const cs = getComputedStyle(document.documentElement);
  const g = (n) => cs.getPropertyValue(n).trim();
  return {ink:g('--ink'), muted:g('--muted'), line:g('--line'), grid:g('--grid'),
    accent:g('--accent2'), green:g('--green'), warn:g('--warn'), panel:g('--panel')};
}

// ---------- KPI ----------
function median(arr){
  if (!arr.length) return null;
  const a = arr.slice().sort((x,y)=>x-y), m = Math.floor(a.length/2);
  return a.length % 2 ? a[m] : (a[m-1]+a[m])/2;
}
function renderKpis(){
  const rows = P();
  const sum = rows.reduce((s,p) => s + (p.sum || 0), 0);
  const sups = new Set(rows.map(p => p.sup).filter(s => s && s !== SUP_UNKNOWN)).size;
  const ru = rows.filter(p => p.country === 'Россия').reduce((s,p)=>s+(p.sum||0),0);
  const est = rows.filter(p => p.est).length;
  const t = DATA.totals;
  const catsIn80 = new Set(rows.filter(p => (CATMETA[p.cat]||{}).in_80).map(p=>p.cat)).size;
  const cut = Math.max(0, (t.sum_scope || 0) - sum);   // отсечено фильтрами
  const kpi = [
    ['Общий объём 2025', mln(t.sum_all), 'все позиции, включая исключённые'],
    ['Профильный объём', mln(sum), rows.length ? pct(sum / (t.sum_all || 1) * 100) + ' от общего' : 'нет данных'],
    ['Отсечено фильтрами', mln(cut), cut > 0 ? 'позиции профиля вне текущего среза' : 'фильтры не применены'],
    ['Исключено', mln(t.sum_excluded), 'срез + отсечено + исключено = общий объём'],
    ['Позиций в выборке', fmt0.format(rows.length), 'из ' + fmt0.format(t.positions_in_scope) + ' профильных'],
    ['Поставщиков', fmt0.format(sups), 'уникальные в выборке, по контрактам 44-ФЗ'],
    ['Доля России', sum ? pct(ru / sum * 100) : '—', mln(ru)],
    ['Категорий в 80 %', catsIn80 + ' из ' + DATA.categories.length, 'правило 80 %, не топ-10'],
    ['Медиана позиции', money(median(rows.map(p=>p.sum||0))), est ? pct(est / (rows.length||1) * 100) + ' оценочных' : 'оценочных нет'],
  ];
  lastKpi = kpi;
  $('#kpis').innerHTML = kpi.map(([l,v,h]) => `<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div><div class="hint">${h}</div></div>`).join('');
}

function renderChips(){
  const items = [];
  const add = (label, val, reset) => items.push(`<span class="chip"><b>${label}:</b> ${esc(val)} <button data-r="${reset}">×</button></span>`);
  if (state.kind) add('Вид', KIND[state.kind] || state.kind, 'kind');
  if (state.cat) add('Группа', state.cat, 'cat');
  if (state.country) add('Страна', state.country, 'country');
  if (state.origin) add('Происхождение', {ru:'Россия', import:'импорт', unknown:'не указана'}[state.origin], 'origin');
  if (state.sup) add('Поставщик', state.sup, 'sup');
  if (state.min != null) add('Сумма от', money(state.min), 'min');
  if (state.max != null) add('Сумма до', money(state.max), 'max');
  if (state.q) add('Поиск', state.q, 'q');
  if (state.only80) add('Набор', 'номенклатура 80 %', 'only80');
  if (state.noEst) add('Оценки', 'без оценочных', 'noEst');
  $('#chips').innerHTML = items.join('');
  $$('#chips button').forEach(b => b.addEventListener('click', () => resetOne(b.dataset.r)));
  $('#filterSummary') && ($('#filterSummary').textContent = '');
}
function resetOne(k){
  state[k] = ({only80:false, noEst:false}[k] ?? (k==='min'||k==='max' ? null : ''));
  ({kind:'#fkind',cat:'#fcat',country:'#fcountry',origin:'#forigin',sup:'#fsup',q:'#fq',min:'#fmin',max:'#fmax'})[k]
    && ($({kind:'#fkind',cat:'#fcat',country:'#fcountry',origin:'#forigin',sup:'#fsup',q:'#fq',min:'#fmin',max:'#fmax'}[k]).value = '');
  if (k==='only80') $('#f80').checked = false;
  if (k==='noEst') $('#fest').checked = false;
  refresh();
}

// ---------- графики ----------
const charts = {};
const AX = () => { const c = colors(); return {
  axisLine:{lineStyle:{color:c.line}},
  axisLabel:{color:c.muted,fontSize:11},
  splitLine:{lineStyle:{color:c.grid}}
};};
function initCharts(){
  ['chKind','chMethod','chMonth','chCountry','chParetoCat','chParetoItems','chCountryBar','chOrigin','chBox'].forEach(id=>{
    const el = document.getElementById(id);
    if (el) charts[id] = echarts.init(el, null, {renderer:'svg'});
  });
}
function baseGrid(extra){ return Object.assign({left:8,right:20,top:24,bottom:14,containLabel:true}, extra||{}); }
function drawKind(){
  const data = agg(P(), 'kind').map(([k,v]) => [KIND_SHORT[k] || KIND[k] || k, v]).reverse();
  const total = P().reduce((s,p)=>s+(p.sum||0),0);
  const bsum = P().filter(p=>p.borderline).reduce((s,p)=>s+(p.sum||0),0);
  if (!state.kind && bsum > 0) data.unshift(['Пограничные (справ.)', bsum]);
  const note = document.getElementById('kindNote');
  if (note) note.textContent = bsum > 0
    ? `Пограничные категории: ${mln(bsum)} (${pct(total ? bsum/total*100 : 0)} среза) — учтены в видах и показаны справочно.`
    : '';
  charts.chKind.setOption({
    title:{text:'По видам закупок',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({right:70}),
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},valueFormatter:v=>money(v)},
    xAxis:{type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
    yAxis:{type:'category',data:data.map(d=>d[0]),...AX(),axisLabel:{...AX().axisLabel,width:190,overflow:'truncate'}},
    series:[{type:'bar',data:data.map(d=>({value:d[1], itemStyle:{color:d[0].startsWith('Пограничные') ? colors().warn : colors().accent, borderRadius:[0,4,4,0]}})),barMaxWidth:20,
      label:{show:true,position:'right',formatter:p=>mln(p.value),color:colors().muted,fontSize:10}}]
  }, true);
}
function drawMethod(){
  const data = agg(P(), 'method').slice(0,6);
  charts.chMethod.setOption({
    title:{text:'По способам закупки',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    tooltip:{trigger:'item',formatter:p=>`${p.name}<br>${money(p.value)} (${p.percent} %)`},
    legend:{type:'scroll',orient:'vertical',right:0,top:30,bottom:10,textStyle:{fontSize:10.5,color:colors().muted},
      formatter:name=>name.length>26?name.slice(0,25)+'…':name},
    series:[{type:'pie',radius:['38%','62%'],center:['34%','56%'],data:data.map(([k,v])=>({name:k,value:v})),
      label:{show:false},labelLine:{show:false},itemStyle:{borderColor:colors().panel,borderWidth:2},
      color:['#1f4e79','#2f80ed','#4fa3d1','#7fb8d8','#2e7d5b','#c77d1a','#b4423a']}]
  }, true);
}
function drawMonth(){
  const m = new Map();
  for (const p of P()) if (p.month) m.set(p.month, (m.get(p.month)||0)+(p.sum||0));
  const keys = [...m.keys()].sort();
  charts.chMonth.setOption({
    title:{text:'Динамика по месяцам',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:36}),
    tooltip:{trigger:'axis',valueFormatter:v=>money(v)},
    xAxis:{type:'category',data:keys.map(k=>{const [y,mm]=k.split('-');return MON[+mm]+' '+y.slice(2)}),...AX()},
    yAxis:{type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
    series:[{type:'line',data:keys.map(k=>m.get(k)),smooth:true,symbolSize:5,
      lineStyle:{width:2.4,color:colors().accent},itemStyle:{color:colors().accent},
      areaStyle:{color:colors().accent,opacity:.10}}]
  }, true);
}
function drawCountry(){
  const all = agg(P(), 'country').slice(0,10);
  const data = all.map(([k,v])=>({name:k,value:v}));
  charts.chCountry.setOption({
    title:{text:'Топ-10 стран',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:36,right:70}),
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},valueFormatter:v=>money(v)},
    xAxis:{type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
    yAxis:{type:'category',data:data.map(d=>d.name).reverse(),...AX(),axisLabel:{...AX().axisLabel,width:150,overflow:'truncate'}},
    series:[{type:'bar',data:data.map(d=>({value:d.value, itemStyle:{color:d.name==='Россия'?colors().green:colors().accent, borderRadius:[0,4,4,0]}})).reverse(),barMaxWidth:18,
      label:{show:true,position:'right',formatter:p=>mln(p.value),color:colors().muted,fontSize:10}}]
  }, true);
}

function paretoOption(title, rows, total, colorIn, labelFn){
  const data = rows.map(r => [r[0], r[1]]);
  let acc = 0;
  const cum = data.map((d,i) => { acc += d[1]; return total ? +(acc/total*100).toFixed(1) : 0; });
  return {
    title:{text:title,left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:38,bottom:82,right:80,left:30}),
    tooltip:{trigger:'axis',axisPointer:{type:'cross'}},
    xAxis:{type:'category',data:data.map(d=>d[0]),...AX(),
      axisLabel:{...AX().axisLabel,rotate:30,interval:0,fontSize:9.5,
        formatter:v=>labelFn?labelFn(v):v}},
    yAxis:[
      {type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
      {type:'value',min:0,max:100,...AX(),splitLine:{show:false},axisLabel:{...AX().axisLabel,formatter:'{value} %'}}
    ],
    series:[
      {type:'bar',data:data.map((d,i)=>({value:d[1],itemStyle:{color:colorIn(i)?colors().green:colors().accent,
        borderRadius:[3,3,0,0]}})),barMaxWidth:26,
        label:{show:data.length<=12,position:'top',formatter:p=>mln(p.value),color:colors().muted,fontSize:9.5}},
      {type:'line',yAxisIndex:1,data:cum,smooth:false,symbolSize:4,
        lineStyle:{color:colors().warn,width:2},itemStyle:{color:colors().warn},
        markLine:{silent:true,symbol:'none',lineStyle:{color:colors().warn,type:'dashed',width:1.4},
          data:[{yAxis:80}]}}
    ]
  };
}
function drawParetoCat(){
  const rows = agg(P(), 'cat');
  const total = rows.reduce((s,x)=>s+x[1],0);
  charts.chParetoCat.setOption(paretoOption('Pareto: товарные группы', rows, total,
    i => (CATMETA[rows[i][0]]||{}).in_80, shortCat), true);
}
function drawParetoItems(){
  const all = FI().slice().sort((a,b)=>(b.sum||0)-(a.sum||0));
  const total = all.reduce((s,it)=>s+(it.sum||0),0);
  let acc = 0, n80 = all.length;
  for (let i=0;i<all.length;i++){
    acc += all[i].sum || 0;
    if (total && acc/total >= 0.8){ n80 = i+1; break; }
  }
  const rows = all.slice(0, n80);
  let a2 = 0;
  const cum = rows.map(it=>{ a2 += it.sum || 0; return total ? +(a2/total*100).toFixed(1) : 0; });
  charts.chParetoItems.setOption({
    title:{text:`Pareto номенклатуры: ${n80} позиций до 80 %`,left:0,top:0,
      textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:38,bottom:62,right:56,left:40}),
    tooltip:{trigger:'axis',formatter:ps=>{
      const i = ps[0].dataIndex, it = rows[i]; if (!it) return '';
      return `${i+1}. ${it.name}<br>${money(it.sum)}<br>накопленно ${cum[i]} %`;
    }},
    xAxis:{type:'category',data:rows.map((_,i)=>String(i+1)),...AX(),
      axisLabel:{...AX().axisLabel,interval:4,fontSize:9}},
    yAxis:[
      {type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
      {type:'value',min:0,max:100,...AX(),splitLine:{show:false},
        axisLabel:{...AX().axisLabel,formatter:'{value} %'}}
    ],
    series:[
      {type:'bar',data:rows.map(it=>it.sum||0),barMaxWidth:14,
        itemStyle:{color:colors().green,borderRadius:[2,2,0,0]}},
      {type:'line',yAxisIndex:1,data:cum,symbol:'none',
        lineStyle:{color:colors().warn,width:2},itemStyle:{color:colors().warn},
        markLine:{silent:true,symbol:'none',lineStyle:{color:colors().warn,type:'dashed',width:1.4},
          data:[{yAxis:80}]}}
    ]
  }, true);
}
function drawCountryBar(){
  const rows = agg(P(), 'country').slice(0,15).reverse();
  charts.chCountryBar.setOption({
    title:{text:'Страны по сумме',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:36,right:70}),
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},valueFormatter:v=>money(v)},
    xAxis:{type:'value',...AX(),axisLabel:{...AX().axisLabel,formatter:v=>(v/1e6)+' млн'}},
    yAxis:{type:'category',data:rows.map(d=>d[0]),...AX(),axisLabel:{...AX().axisLabel,width:160,overflow:'truncate'}},
    series:[{type:'bar',data:rows.map(d=>({value:d[1], itemStyle:{color:d[0]==='Россия'?colors().green:colors().accent, borderRadius:[0,4,4,0]}})),barMaxWidth:16,
      label:{show:true,position:'right',formatter:p=>mln(p.value),color:colors().muted,fontSize:10}}]
  }, true);
}
function drawOrigin(){
  const rows = P();
  const ru = rows.filter(p=>p.country==='Россия').reduce((s,p)=>s+(p.sum||0),0);
  const unk = rows.filter(p=>p.country==='не определена').reduce((s,p)=>s+(p.sum||0),0);
  const imp = rows.reduce((s,p)=>s+(p.sum||0),0) - ru - unk;
  charts.chOrigin.setOption({
    title:{text:'Россия / импорт / не указана',left:0,top:0,textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    tooltip:{trigger:'item',formatter:p=>`${p.name}<br>${money(p.value)} (${p.percent} %)`},
    legend:{bottom:0,textStyle:{fontSize:11,color:colors().muted}},
    series:[{type:'pie',radius:['44%','70%'],center:['50%','50%'],
      data:[{name:'Россия',value:ru},{name:'Импорт',value:imp},{name:'Не указана',value:unk}].filter(d=>d.value>0),
      label:{show:true,formatter:'{b}\n{d} %',fontSize:11,color:colors().ink},
      labelLayout:{hideOverlap:true},
      itemStyle:{borderColor:colors().panel,borderWidth:2},
      color:[colors().green, '#4fa3d1', '#a9b6c4']}]
  }, true);
}
function drawBox(){
  const items = FI().filter(it=>it.in80 && it.n>=2 && it.med && it.min && it.max && it.p25 && it.p75)
    .sort((a,b)=>b.sum-a.sum).slice(0,20);
  const names = items.map(it=>it.name);
  const data = items.map((it,i)=>[i, Math.max(0.5, it.min/it.med*100), it.max/it.med*100,
    Math.max(0.5, it.p25/it.med*100), it.p75/it.med*100]);
  charts.chBox.setOption({
    title:{text:'Разброс цен к медиане позиции (лог. шкала, 100 % = медиана)',left:0,top:0,
      textStyle:{fontSize:13,color:colors().ink,fontWeight:600}},
    grid:baseGrid({top:36,bottom:20,left:10,right:34}),
    tooltip:{trigger:'item',formatter:p=>{
      const it = items[p.dataIndex]; if(!it) return '';
      return `${it.name}<br>мин ${money(it.min)}<br>P25 ${money(it.p25)}<br>медиана ${money(it.med)}<br>P75 ${money(it.p75)}<br>макс ${money(it.max)}<br>закупок ${it.n}`;
    }},
    xAxis:{type:'log',min:1,...AX(),axisLabel:{...AX().axisLabel,formatter:'{value} %'}},
    yAxis:{type:'category',data:names,inverse:true,...AX(),
      axisLabel:{...AX().axisLabel,width:240,overflow:'truncate',fontSize:10}},
    series:[{type:'custom',encode:{x:[1,2],y:0},data,
      renderItem:(params, api)=>{
        const y = api.value(0);
        const lo = api.coord([api.value(1), y]);
        const hi = api.coord([api.value(2), y]);
        const q1 = api.coord([api.value(3), y]);
        const q3 = api.coord([api.value(4), y]);
        const med = api.coord([100, y]);
        const cy = lo[1];
        return {type:'group', children:[
          {type:'line', shape:{x1:lo[0],y1:cy,x2:hi[0],y2:cy},
            style:{stroke:colors().accent,lineWidth:1.3}},
          {type:'rect', shape:{x:q1[0],y:cy-5,width:Math.max(1,q3[0]-q1[0]),height:10},
            style:{fill:colors().accent,opacity:.28}},
          {type:'circle', shape:{cx:med[0],cy,r:3.4}, style:{fill:colors().warn}}
        ]};
      }}]
  }, true);
}
function drawAll(){
  if (!Object.keys(charts).length) return;
  const n = P().length;
  // при отсутствии данных показываем «Нет данных», а не нули (ТЗ § 8.6)
  document.querySelectorAll('.chart').forEach(el=>{
    const empty = el.querySelector('.chartempty');
    if (n === 0) {
      if (!empty){ const d = document.createElement('div'); d.className='empty chartempty';
        d.textContent='Нет данных'; el.appendChild(d); }
      el.style.visibility='hidden';
    } else {
      if (empty) empty.remove();
      el.style.visibility='visible';
    }
  });
  if (n === 0) return;
  drawKind(); drawMethod(); drawMonth(); drawCountry();
  drawParetoCat(); drawParetoItems(); drawCountryBar(); drawOrigin(); drawBox();
}

// ---------- таблицы ----------
const plural = (n, f) => { const a = Math.abs(n) % 100, b = a % 10;
  if (a > 10 && a < 20) return f[2];
  if (b > 1 && b < 5) return f[1];
  if (b === 1) return f[0];
  return f[2]; };
const words = (n) => plural(n, ['строка', 'строки', 'строк']);
const hay = (v) => String(v ?? '').toLowerCase();
function markSort(sel, st){
  $$(sel + ' th.sortable').forEach(th => {
    th.dataset.dir = (th.dataset.k === st.k) ? (st.d < 0 ? 'desc' : 'asc') : '';
  });
}
function setCnt(t, shown, total){
  const el = document.querySelector('[data-tcnt="' + t + '"]');
  if (!el) return;
  const cut = (tstate[t].limit && shown < total) || tstate[t].q;
  el.textContent = cut
    ? 'Показано ' + fmt0.format(shown) + ' из ' + fmt0.format(total) + ' ' + words(total)
    : fmt0.format(total) + ' ' + words(total);
}
function redrawTable(t){
  if (t === 'cat') renderCats();
  else if (t === 'catdet') renderCatDetail();
  else if (t === 'items') renderItems();
  else if (t === 'bench') renderBench();
  else if (t === 'country') renderCountryTable();
  else if (t === 'reg') regReset();
}
function renderCats(){
  const st = sortState.cat;
  const get = (r) => ({category:r.category,sum:r.sum,share:r.share,cum:r.cum_share,n:r.n,sup:r.suppliers,avg:r.avg_position}[st.k]);
  const present = new Set(P().map(p => p.cat));
  const rows = sortRows(DATA.categories.filter(c => present.has(c.category)), st, get);
  const totalSum = rows.reduce((s,c)=>s+(c.sum||0),0);
  let acc = 0;
  const enriched = rows.map(c=>{ acc += c.sum || 0;
    return {...c, _share: totalSum ? (c.sum||0)/totalSum*100 : 0, _cum: totalSum ? acc/totalSum*100 : 0}; });
  const q = hay(tstate.cat.q);
  const shown = q
    ? enriched.filter(c => hay(c.category + ' ' + money(c.sum) + ' ' + pct(c._share) + ' ' + fmt0.format(c.n)).includes(q))
    : enriched;
  const fSum = shown.reduce((s,c)=>s+(c.sum||0),0);
  const showCum = st.k === 'sum' && st.d === -1;
  const tN = shown.reduce((s,c)=>s+c.n,0);
  const tSup = q
    ? new Set(P().filter(p=>shown.some(c=>c.category===p.cat)).map(p=>p.sup).filter(Boolean)).size
    : new Set(P().map(p=>p.sup).filter(Boolean)).size;
  const body = shown.map((c,i)=>`<tr data-cat="${esc(c.category)}" style="cursor:pointer">
    <td class="num">${i+1}</td>
    <td>${esc(c.category)} ${c.in_80?'<span class="badge80">80 %</span>':''}</td>
    <td class="num">${money(c.sum)}</td><td class="num">${pct(c._share)}</td>
    <td class="num">${showCum?pct(c._cum):'—'}</td><td class="num">${fmt0.format(c.n)}</td>
    <td class="num">${fmt0.format(c.suppliers)}</td><td class="num">${money(c.avg_position)}</td>
  </tr>`).join('');
  $('#catTable').innerHTML = `<thead><tr>
    <th>№</th><th class="sortable" data-t="cat" data-k="category">Товарная группа</th>
    <th class="sortable num" data-t="cat" data-k="sum">Сумма</th>
    <th class="sortable num" data-t="cat" data-k="share">Доля</th>
    <th class="sortable num" data-t="cat" data-k="cum">Накопленно</th>
    <th class="sortable num" data-t="cat" data-k="n">Позиций</th>
    <th class="sortable num" data-t="cat" data-k="sup">Поставщиков</th>
    <th class="sortable num" data-t="cat" data-k="avg">Средняя</th></tr></thead>
    <tbody>${body}</tbody>
    <tfoot><tr><td></td><td>${q?'Итого по фильтру таблицы':'Итого по срезу'}</td><td class="num">${money(fSum)}</td>
      <td class="num">${q?pct(totalSum?fSum/totalSum*100:0):'100,0 %'}</td>
      <td class="num">${q?(showCum&&shown.length?pct(shown[shown.length-1]._cum):'—'):(showCum?'100,0 %':'—')}</td>
      <td class="num">${fmt0.format(tN)}</td><td class="num">${fmt0.format(tSup)}</td>
      <td class="num">${money(tN?fSum/tN:null)}</td></tr></tfoot>`;
  $$('#catTable tbody tr').forEach(tr => tr.addEventListener('click', () => {
    selected.cat = tr.dataset.cat;
    renderCatDetail();
    $$('#catTable tbody tr').forEach(x => x.style.background = '');
    tr.style.background = 'var(--panel2)';
  }));
  $('#catHint').textContent = rows.length === shown.length
    ? `${rows.length} групп, в 80 %-наборе ${rows.filter(c=>c.in_80).length}`
    : `${rows.length} групп, по фильтру таблицы — ${shown.length}`;
  markSort('#catTable', st);
  setCnt('cat', shown.length, rows.length);
  renderCatDetail();
}
function renderCatDetail(){
  const cat = selected.cat || state.cat || (DATA.categories[0]||{}).category || '';
  if (!cat){ $('#catDetail').innerHTML=''; setCnt('catdet', 0, 0); return; }
  const st = sortState.cd;
  const q = hay(tstate.catdet.q);
  let rows = DATA.positions.filter(p=>p.cat===cat);
  if (q) rows = rows.filter(p => hay(p.name + ' ' + (p.unit||'') + ' ' + money(p.sum) + ' '
    + (p.country||'') + ' ' + (p.sup||'')).includes(q));
  rows = sortRows(rows, st, p => ({name:p.name, qty:p.qty, price:p.price, sum:p.sum,
    country:p.country, sup:p.sup}[st.k]));
  const total = rows.length;
  rows = tstate.catdet.limit ? rows.slice(0, tstate.catdet.limit) : rows;
  const fSum = rows.reduce((s,p)=>s+(p.sum||0),0);
  $('#catDetailTitle').textContent = 'Позиции группы: ' + cat
    + (total !== rows.length ? ` · показано ${rows.length} из ${total}` : '');
  const body = rows.map((p,i)=>`<tr><td class="num">${i+1}</td><td>${esc(p.name)}</td>
    <td>${esc(p.unit||'—')}</td><td class="num">${!p.qty?'—':fmt0.format(p.qty)}</td>
    <td class="num">${money(p.price)}</td><td class="num">${money(p.sum)}</td>
    <td>${esc(p.country)}</td><td>${esc(p.sup||'—')}</td></tr>`).join('');
  $('#catDetail').innerHTML = `<thead><tr><th>№</th>
    <th class="sortable" data-t="cd" data-k="name">Позиция</th><th>Ед.</th>
    <th class="sortable num" data-t="cd" data-k="qty">Кол-во</th>
    <th class="sortable num" data-t="cd" data-k="price">Цена</th>
    <th class="sortable num" data-t="cd" data-k="sum">Сумма</th>
    <th class="sortable" data-t="cd" data-k="country">Страна</th>
    <th class="sortable" data-t="cd" data-k="sup">Поставщик</th></tr></thead>
    <tbody>${body || '<tr><td colspan="8" class="empty">Нет данных</td></tr>'}</tbody>
    <tfoot><tr><td></td><td>${q?'Итого по фильтру таблицы':'Итого по показанным позициям'}</td>
      <td></td><td></td><td></td><td class="num">${money(fSum)}</td><td></td><td></td></tr></tfoot>`;
  markSort('#catDetail', st);
  setCnt('catdet', rows.length, total);
}
function renderItems(){
  const st = sortState.items;
  const q = hay(tstate.items.q);
  let all = FI();
  if (q) all = all.filter(it => hay(it.name + ' ' + it.cat + ' ' + (it.unit||'') + ' '
    + money(it.sum) + ' ' + (it.country||'')).includes(q));
  const rows = sortRows(all, st, (it)=>({name:it.name,cat:it.cat,sum:it.sum,n:it.n,sup:it.sup,med:it.med}[st.k]))
    .slice(0, tstate.items.limit || 1e9);
  const body = rows.map((it,i)=>`<tr>
    <td class="num">${i+1}</td><td>${esc(it.name)}</td><td>${esc(it.cat)}</td>
    <td>${esc(it.unit||'—')}</td><td class="num">${!it.qty?'—':fmt0.format(it.qty)}</td>
    <td class="num">${money(it.sum)}</td><td class="num">${fmt0.format(it.n)}</td>
    <td class="num">${it.sup==null?'—':fmt0.format(it.sup)}</td><td class="num">${money(it.med)}</td>
    <td>${it.in80?'<span class="badge80">80 %</span>':'<span class="badgeNo">нет</span>'}</td></tr>`).join('');
  const totalSum = all.reduce((s,it)=>s+(it.sum||0),0);
  const totalN = all.reduce((s,it)=>s+it.n,0);
  const tSup = new Set(P().map(p=>p.sup).filter(Boolean)).size;
  $('#itemsTable').innerHTML = `<thead><tr><th>№</th>
    <th class="sortable" data-t="items" data-k="name">Позиция</th>
    <th class="sortable" data-t="items" data-k="cat">Группа</th><th>Ед.</th>
    <th class="num">Кол-во</th><th class="sortable num" data-t="items" data-k="sum">Сумма</th>
    <th class="sortable num" data-t="items" data-k="n">Закупок</th>
    <th class="sortable num" data-t="items" data-k="sup">Поставщиков</th>
    <th class="sortable num" data-t="items" data-k="med">Медиана</th><th>80 %</th></tr></thead>
    <tbody>${body || '<tr><td colspan="10" class="empty">Ничего не найдено</td></tr>'}</tbody>
    <tfoot><tr><td></td><td>${q?'Итого по фильтру таблицы':'Итого по срезу'}</td><td></td><td></td><td></td>
      <td class="num">${money(totalSum)}</td><td class="num">${fmt0.format(totalN)}</td>
      <td class="num">${q?'—':fmt0.format(tSup)}</td><td></td><td></td></tr></tfoot>`;
  $('#itemsHint').textContent = `Найдено ${all.length.toLocaleString('ru-RU')} позиций, из них в 80 %-наборе ${all.filter(i=>i.in80).length}`;
  const sh = $('#itemsShown');
  if (sh) sh.textContent = rows.length < all.length
    ? `Показаны первые ${fmt0.format(rows.length)}; полный список — в поле «Показать» над таблицей` : '';
  markSort('#itemsTable', st);
  setCnt('items', rows.length, all.length);
}
function renderBench(){
  const st = sortState.bench;
  const q = hay(tstate.bench.q);
  let all = FI().filter(it=>it.in80 && it.n>=2 && it.med && it.min);
  if (q) all = all.filter(it => hay(it.name + ' ' + it.cat + ' ' + (it.unit||'') + ' '
    + money(it.med) + ' ' + (it.country||'')).includes(q));
  const rows = sortRows(all, st, (it)=>({name:it.name,cat:it.cat,med:it.med,min:it.min,max:it.max,spread:(it.max/it.min-1)*100,n:it.n,sup:it.sup}[st.k]))
    .slice(0, tstate.bench.limit || 1e9);
  const body = rows.map((it,i)=>{
    const spread = it.min ? (it.max/it.min-1)*100 : null;
    return `<tr><td class="num">${i+1}</td><td>${esc(it.name)}</td><td>${esc(it.cat)}</td>
      <td>${esc(it.unit||'—')}</td><td class="num">${money(it.med)}</td><td class="num">${money(it.min)}</td>
      <td class="num">${money(it.max)}</td><td class="num">${spread==null?'—':pct(spread)}</td>
      <td class="num">${fmt0.format(it.n)}</td><td class="num">${it.sup==null?'—':fmt0.format(it.sup)}</td></tr>`;
  }).join('');
  $('#benchTable').innerHTML = `<thead><tr><th>№</th>
    <th class="sortable" data-t="bench" data-k="name">Позиция</th>
    <th class="sortable" data-t="bench" data-k="cat">Группа</th><th>Ед.</th>
    <th class="sortable num" data-t="bench" data-k="med">Медиана</th>
    <th class="sortable num" data-t="bench" data-k="min">Минимум</th>
    <th class="sortable num" data-t="bench" data-k="max">Максимум</th>
    <th class="sortable num" data-t="bench" data-k="spread">Разброс</th>
    <th class="sortable num" data-t="bench" data-k="n">Закупок</th>
    <th class="sortable num" data-t="bench" data-k="sup">Поставщиков</th></tr></thead>
    <tbody>${body || '<tr><td colspan="10" class="empty">Нет позиций с двумя и более закупками</td></tr>'}</tbody>
    <tfoot><tr><td></td><td>${q?'Итого по фильтру таблицы':'Итого по срезу'}</td><td></td><td></td><td></td>
      <td></td><td></td><td></td>
      <td class="num">${fmt0.format(rows.reduce((s,it)=>s+it.n,0))}</td><td></td></tr></tfoot>`;
  const extreme = all.filter(it=>it.min && it.max/it.min > 11).length;
  $('#benchHint').textContent = `${all.length} позиций с бенчмарком` +
    (extreme ? `; разброс выше 1000 % — у ${extreme} (разная фасовка или единица измерения)` : '');
  markSort('#benchTable', st);
  setCnt('bench', rows.length, all.length);
}
function renderCountryTable(){
  const rowsP = P();
  const cats = DATA.categories.filter(c => rowsP.some(p=>p.cat===c.category));
  const rows = cats.map(c=>{
    const pos = rowsP.filter(p=>p.cat===c.category);
    const ru = pos.filter(p=>p.country==='Россия').reduce((s,p)=>s+(p.sum||0),0);
    const unk = pos.filter(p=>p.country==='не определена').reduce((s,p)=>s+(p.sum||0),0);
    const imp = pos.reduce((s,p)=>s+(p.sum||0),0)-ru-unk;
    const cc = new Map(); for (const p of pos) if (p.country!=='Россия' && p.country!=='не определена') cc.set(p.country,(cc.get(p.country)||0)+(p.sum||0));
    const top = [...cc.entries()].sort((a,b)=>b[1]-a[1])[0];
    return {cat:c.category, ru, imp, unk, top};
  });
  const st = sortState.country;
  const q = hay(tstate.country.q);
  let view = rows;
  if (q) view = view.filter(r => hay(r.cat + ' ' + (r.top ? r.top[0] : '')).includes(q));
  if (st.k !== 'orig') view = sortRows(view, st, r => ({cat:r.cat, ru:r.ru, imp:r.imp, unk:r.unk,
    top:r.top ? r.top[0] : ''}[st.k]));
  const body = view.map(r=>`<tr><td>${esc(r.cat)}</td><td class="num">${mln0(r.ru)}</td>
    <td class="num">${mln0(r.imp)}</td><td class="num">${mln0(r.unk)}</td>
    <td>${r.top?esc(r.top[0])+' ('+mln(r.top[1])+')':'—'}</td></tr>`).join('');
  const tRu = view.reduce((s,r)=>s+r.ru,0), tImp = view.reduce((s,r)=>s+r.imp,0), tUnk = view.reduce((s,r)=>s+r.unk,0);
  $('#countryTable').innerHTML = `<thead><tr>
    <th class="sortable" data-t="country" data-k="cat">Товарная группа</th>
    <th class="sortable num" data-t="country" data-k="ru">Россия</th>
    <th class="sortable num" data-t="country" data-k="imp">Импорт</th>
    <th class="sortable num" data-t="country" data-k="unk">Не указана</th>
    <th class="sortable" data-t="country" data-k="top">Крупнейший импорт</th></tr></thead>
    <tbody>${body || '<tr><td colspan="5" class="empty">Нет данных</td></tr>'}</tbody>
    <tfoot><tr><td>${q?'Итого по фильтру таблицы':'Итого по срезу'}</td><td class="num">${mln0(tRu)}</td>
      <td class="num">${mln0(tImp)}</td><td class="num">${mln0(tUnk)}</td><td></td></tr></tfoot>`;
  const ru = rowsP.filter(p=>p.country==='Россия').reduce((s,p)=>s+(p.sum||0),0);
  const unk = rowsP.filter(p=>p.country==='не определена').reduce((s,p)=>s+(p.sum||0),0);
  const total = rowsP.reduce((s,p)=>s+(p.sum||0),0);
  $('#countryHint').textContent = total ? `Россия — ${pct(ru/total*100)}, импорт — ${pct((total-ru-unk)/total*100)}, не указана — ${pct(unk/total*100)}` : 'Нет данных';
  markSort('#countryTable', st);
  setCnt('country', view.length, rows.length);
}
function renderKey(){
  const rows = FI().filter(it=>it.in80).sort((a,b)=>b.sum-a.sum).slice(0,12);
  $('#keyCards').innerHTML = rows.map(it=>{
    const months = it.months || [];
    const spread = it.min ? (it.max/it.min-1)*100 : null;
    return `<div class="pcard">
      <div class="sum">${money(it.sum)}</div>
      <h3>${esc(it.name)}</h3>
      <div class="row"><span>Группа</span><b>${esc(it.cat)}</b></div>
      <div class="row"><span>Закупок / поставщиков</span><b>${it.n} / ${it.sup ?? '—'}</b></div>
      <div class="row"><span>Медиана</span><b>${money(it.med)}</b></div>
      <div class="row"><span>Диапазон</span><b>${money(it.min)} – ${money(it.max)}</b></div>
      <div class="row"><span>Разброс</span><b>${spread==null?'—':pct(spread)}</b></div>
      <div class="row"><span>Страна</span><b>${esc(it.country||'—')}${it.countryShare!=null?' ('+pct(it.countryShare)+')':''}</b></div>
      <div class="row"><span>Месяцы</span><b>${months.length?MON[+months[0].slice(5)]+' – '+MON[+months[months.length-1].slice(5)]:'—'}</b></div>
    </div>`;
  }).join('') || '<div class="empty">Нет данных</div>';
}

// ---------- реестр ----------
const reg = {rows:[], rowH:38, box:null, body:null, start:-1, end:-1};
function regSorted(){
  const st = sortState.reg;
  let rows = P();
  const q = hay(tstate.reg.q);
  if (q) rows = rows.filter(p => hay(p.name + ' ' + p.cat + ' ' + (p.sup||'') + ' ' + p.country).includes(q));
  return sortRows(rows, st, (p)=>({name:p.name,cat:p.cat,qty:p.qty,price:p.price,sum:p.sum,country:p.country,month:p.month,sup:p.sup}[st.k]));
}
function regCells(p, idx){
  return `<td class="num">${idx}</td>
      <td class="regname" title="${esc(p.name)}">${esc(p.name)}</td>
      <td title="${esc(p.cat)}">${esc(p.cat)}</td>
      <td>${esc(p.unit||'—')}</td>
      <td class="num">${!p.qty?'—':fmt0.format(p.qty)}</td>
      <td class="num">${money(p.price)}</td>
      <td class="num">${money(p.sum)}</td>
      <td>${esc(p.country)}</td>
      <td>${p.month?MON[+p.month.slice(5)]+' '+p.month.slice(2,4):'—'}</td>
      <td title="${esc(p.sup)}">${esc(p.sup||'—')}</td>
      <td>${p.est?'<span class="badgeEst">оценка</span>':'факт'}</td>`;
}
function regRender(){
  const rows = reg.rows;
  const box = reg.box;
  const total = rows.length;
  const view = Math.ceil(box.clientHeight / reg.rowH);
  const start = Math.max(0, Math.floor(box.scrollTop / reg.rowH) - 6);
  const end = Math.min(total, start + view + 12);
  if (start === reg.start && end === reg.end && reg.body.dataset.n === String(total)) return;
  reg.start = start; reg.end = end; reg.body.dataset.n = String(total);
  let spacer = reg.body.querySelector('.spacer');
  if (!spacer){
    spacer = document.createElement('tr'); spacer.className='spacer';
    spacer.innerHTML = '<td colspan="11" style="padding:0;border:0"></td>';
    reg.body.prepend(spacer);
  }
  spacer.firstChild.style.height = (total * reg.rowH) + 'px';
  const html = rows.slice(start,end).map((p,i)=>{
    const idx = start + i + 1;
    return `<tr style="top:${(start+i)*reg.rowH}px">${regCells(p, idx)}</tr>`;
  }).join('');
  [...reg.body.querySelectorAll('tr:not(.spacer)')].forEach(tr=>tr.remove());
  reg.body.insertAdjacentHTML('beforeend', html);
  const totalSum = rows.reduce((s,p)=>s+(p.sum||0),0);
  const allN = P().length;
  $('#regHint').textContent = (tstate.reg.q && total !== allN)
    ? `${total.toLocaleString('ru-RU')} из ${allN.toLocaleString('ru-RU')} позиций; сумма ${money(totalSum)}`
    : `${total.toLocaleString('ru-RU')} позиций; сумма ${money(totalSum)}`;
}
function regReset(){
  reg.rows = regSorted(); reg.start = -1; reg.end = -1;
  reg.body.dataset.n = ''; reg.box.scrollTop = 0; regRender();
  markSort('#regBox', sortState.reg);
  setCnt('reg', reg.rows.length, P().length);
}
// печать: разворачиваем весь реестр, чтобы в PDF/PDF-печати не осталось только видимых строк
function regAll(){
  const rows = reg.rows;
  const spacer = reg.body.querySelector('.spacer');
  if (spacer) spacer.remove();
  reg.body.innerHTML = rows.map((p,i)=>`<tr>${regCells(p, i+1)}</tr>`).join('');
}

// ---------- выгрузка: CSV и XLSX ----------
const FILTER_TXT = () => {
  const parts = [];
  if (state.kind) parts.push('вид: ' + (KIND[state.kind] || state.kind));
  if (state.cat) parts.push('группа: ' + state.cat);
  if (state.country) parts.push('страна: ' + state.country);
  if (state.origin) parts.push('происхождение: ' + ({ru:'Россия', import:'импорт', unknown:'не указана'}[state.origin]));
  if (state.sup) parts.push('поставщик: ' + state.sup);
  if (state.min != null) parts.push('сумма от ' + money(state.min));
  if (state.max != null) parts.push('сумма до ' + money(state.max));
  if (state.q) parts.push('поиск: ' + state.q);
  if (state.only80) parts.push('набор 80 %');
  if (state.noEst) parts.push('без оценочных');
  return parts.length ? parts.join('; ') : 'без фильтров';
};
const REG_HEAD = ['Позиция','Группа','Вид','Ед.','Количество','Цена','Сумма','Страна','Месяц','Поставщик','Класс'];
function tableData(t){
  if (t === 'reg'){
    const rows = regSorted();
    return {header: REG_HEAD.slice(), count: rows.length, foot: null, rows: rows.map(p => [
      p.name, p.cat, KIND[p.kind] || p.kind, p.unit || '', p.qty ?? '', p.price ?? '', p.sum ?? '',
      p.country, p.month || '', p.sup || '', p.est ? 'оценка' : 'факт'])};
  }
  const el = $(TBL[t].el);
  const header = [...el.querySelectorAll('thead th')].map(th => th.textContent.trim());
  const rows = [...el.querySelectorAll('tbody tr')]
    .filter(tr => !tr.querySelector('td.empty'))
    .map(tr => [...tr.querySelectorAll('td')].map(td => td.textContent.trim()));
  const foot = el.querySelector('tfoot')
    ? [...el.querySelectorAll('tfoot tr')].map(tr => [...tr.querySelectorAll('td')].map(td => td.textContent.trim()))
    : null;
  return {header, rows, foot, count: rows.length};
}
const saveBlob = (blob, name) => {
  const a = document.createElement('a');
  const url = URL.createObjectURL(blob);
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 8000);
};
const csvLine = (vals) => vals.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(';');
function downloadCsv(){
  const rows = regSorted();
  const lines = [REG_HEAD.join(';')].concat(rows.map(p=>[
    p.name,p.cat,KIND[p.kind]||p.kind,p.unit||'',p.qty??'',p.price??'',p.sum??'',
    p.country,p.month||'',p.sup||'',p.est?'оценка':'факт'
  ].map(v=>`"${String(v).replace(/"/g,'""')}"`).join(';')));
  saveBlob(new Blob(['\ufeff'+lines.join('\r\n')], {type:'text/csv;charset=utf-8'}),
    'botkina_2025_registry.csv');
}
function exportCsv(t){
  if (t === 'reg'){ downloadCsv(); return; }
  const d = tableData(t);
  const lines = [csvLine(d.header)].concat(d.rows.map(csvLine), (d.foot || []).map(csvLine));
  saveBlob(new Blob(['\ufeff'+lines.join('\r\n')], {type:'text/csv;charset=utf-8'}),
    'botkina_2025_' + TBL[t].sheet + '.csv');
}

// --- XLSX: ZIP без сжатия (CRC32) и XML листа, без внешних библиотек ---
const xesc = (s) => String(s ?? '').replace(/[&<>"']/g,
  c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;'}[c]));
const sheetName = (n) => String(n).replace(/[\\/?*[\]:]/g, '-').slice(0, 31);
function colN(i){
  let s = ''; let n = i + 1;
  while (n > 0){ const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
function parseCell(raw){
  const s = String(raw ?? '').replace(/\u00A0/g, ' ').trim();
  if (s === '' || s === '—' || s === '-') return {t:'empty'};
  let t = s.replace(/\s+/g, '');
  let isPct = false;
  if (t.endsWith('%')){ isPct = true; t = t.slice(0, -1); }
  if (t.endsWith('₽')) t = t.slice(0, -1);
  let mult = 1;
  if (/млн\.?$/i.test(t)){ mult = 1e6; t = t.replace(/млн\.?$/i, ''); }
  else if (/тыс\.?$/i.test(t)){ mult = 1e3; t = t.replace(/тыс\.?$/i, ''); }
  if (!/^[+-]?\d+(?:[.,]\d+)?$/.test(t)) return {t:'text', v:s};
  const num = parseFloat(t.replace(',', '.'));
  if (!isFinite(num)) return {t:'text', v:s};
  if (isPct) return {t:'num', v:num / 100, s:4};
  const scaled = mult > 1 || /[.,]\d/.test(t) || s.includes('₽');
  return {t:'num', v:num * mult, s: scaled ? 2 : 3};
}
function cellXml(ref, v, style, forceText){
  if (v == null) return `<c r="${ref}"/>`;
  if (forceText) return `<c r="${ref}" s="${style||0}" t="inlineStr"><is><t xml:space="preserve">${xesc(v)}</t></is></c>`;
  if (typeof v === 'number' && isFinite(v)){
    const s = style === 1 ? (Number.isInteger(v) ? 6 : 5) : (style || (Number.isInteger(v) ? 3 : 2));
    return `<c r="${ref}" s="${s}"><v>${v}</v></c>`;
  }
  const p = parseCell(v);
  if (p.t === 'empty') return `<c r="${ref}"/>`;
  if (p.t === 'num'){
    const s = style === 1 ? ({2:5, 3:6, 4:7}[p.s] || 1) : (style || p.s);
    return `<c r="${ref}" s="${s}"><v>${p.v}</v></c>`;
  }
  return `<c r="${ref}" s="${style||0}" t="inlineStr"><is><t xml:space="preserve">${xesc(p.v)}</t></is></c>`;
}
function sheetXml(sh){
  const out = [];
  let r = 0;
  const addRow = (vals, style, forceText) => {
    r++;
    let cells = '';
    for (let i = 0; i < vals.length; i++) cells += cellXml(colN(i) + r, vals[i], style, forceText);
    out.push(`<row r="${r}">${cells}</row>`);
  };
  sh.meta.forEach((m, i) => addRow([m], i === 0 ? 1 : 0, true));
  addRow([], 0, false);
  addRow(sh.header, 1, true);
  const first = r + 1;
  sh.rows.forEach(x => addRow(x, 0, false));
  const lastData = r;
  if (sh.foot) sh.foot.forEach(x => addRow(x, 1, false));
  const widths = sh.header.map((h, i) => {
    let len = String(h).length;
    for (const row of sh.rows.slice(0, 300)){
      const v = row[i];
      if (v != null) len = Math.max(len, Math.min(56, String(v).length));
    }
    return Math.min(58, Math.max(9, Math.round(len * 1.15) + 2));
  });
  const cols = widths.map((w, i) => `<col min="${i+1}" max="${i+1}" width="${w}" customWidth="1"/>`).join('');
  const lastCol = colN(Math.max(0, sh.header.length - 1));
  const filter = sh.rows.length ? `<autoFilter ref="A${first}:${lastCol}${lastData}"/>` : '';
  const pane = first > 1
    ? `<pane ySplit="${first-1}" topLeftCell="A${first}" activePane="bottomLeft" state="frozen"/>` +
      `<selection pane="bottomLeft" activeCell="A${first}" sqref="A${first}"/>`
    : '';
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>` +
    `<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">` +
    `<dimension ref="A1:${lastCol}${r}"/>` +
    `<sheetViews><sheetView workbookViewId="0">${pane}</sheetView></sheetViews>` +
    `<sheetFormatPr defaultRowHeight="15"/><cols>${cols}</cols><sheetData>` +
    out.join('') + `</sheetData>${filter}</worksheet>`;
}
function crc32(u8){
  if (!crc32.t){
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++){
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      t[n] = c >>> 0;
    }
    crc32.t = t;
  }
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < u8.length; i++) crc = (crc >>> 8) ^ crc32.t[(crc ^ u8[i]) & 0xFF];
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function zipStore(files){
  const enc = new TextEncoder();
  const u16 = n => [n & 255, (n >>> 8) & 255];
  const u32 = n => [n & 255, (n >>> 8) & 255, (n >>> 16) & 255, (n >>> 24) & 255];
  const parts = [], cen = [];
  let offset = 0;
  for (const f of files){
    const name = enc.encode(f.name), crc = crc32(f.u8), size = f.u8.length;
    const lh = new Uint8Array([...u32(0x04034b50), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
      ...u32(crc), ...u32(size), ...u32(size), ...u16(name.length), ...u16(0)]);
    parts.push(lh, name, f.u8);
    cen.push({name, crc, size, offset});
    offset += lh.length + name.length + size;
  }
  const cd = []; let cdLen = 0;
  for (const c of cen){
    const h = new Uint8Array([...u32(0x02014b50), ...u16(20), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
      ...u32(c.crc), ...u32(c.size), ...u32(c.size), ...u16(c.name.length), ...u16(0), ...u16(0), ...u16(0),
      ...u16(0), ...u32(0), ...u32(c.offset)]);
    cd.push(h, c.name); cdLen += h.length + c.name.length;
  }
  const eocd = new Uint8Array([...u32(0x06054b50), ...u16(0), ...u16(0), ...u16(cen.length), ...u16(cen.length),
    ...u32(cdLen), ...u32(offset), ...u16(0)]);
  return new Blob([...parts, ...cd, eocd],
    {type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
}
const STYLES_XML = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFDCE6F1"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="8">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1"/>
<xf numFmtId="3" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1"/>
<xf numFmtId="10" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1"/>
</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`;
const XLSX_CT = 'application/vnd.openxmlformats-officedocument.spreadsheetml';
function xlsxDownload(sheets, fname){
  const enc = new TextEncoder();
  const files = [];
  const push = (name, text) => files.push({name, u8: enc.encode(text)});
  const overrides = sheets.map((s, i) =>
    `<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="${XLSX_CT}.worksheet+xml"/>`).join('');
  push('[Content_Types].xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="${XLSX_CT}.sheet.main+xml"/>${overrides}
<Override PartName="/xl/styles.xml" ContentType="${XLSX_CT}.styles+xml"/></Types>`);
  push('_rels/.rels', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>`);
  push('xl/workbook.xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>` +
    sheets.map((s, i) => `<sheet name="${xesc(sheetName(s.name))}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join('') +
    `</sheets></workbook>`);
  push('xl/_rels/workbook.xml.rels', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">` +
    sheets.map((s, i) => `<Relationship Id="rId${i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join('') +
    `<Relationship Id="rIdS" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`);
  push('xl/styles.xml', STYLES_XML);
  sheets.forEach((s, i) => push(`xl/worksheets/sheet${i+1}.xml`, sheetXml(s)));
  saveBlob(zipStore(files), fname);
}
const metaLines = (title, n) => [
  title + ' — Анализ закупок МНКЦ им. С.П. Боткина за 2025 год',
  'Источник: ЕИС, реестры 44-ФЗ и 223-ФЗ · дата выгрузки данных: ' + DATA.meta.extracted_at
    + ' · учёт по дате заключения контракта',
  'Срез: ' + FILTER_TXT() + ' · строк: ' + fmt0.format(n)
    + ' · факт — данные ЕИС, оценка — расчётное значение (не для официальной отчётности)'
];
function exportTable(t){
  const d = tableData(t);
  xlsxDownload([{name: TBL[t].sheet, meta: metaLines(TBL[t].title, d.count),
    header: d.header, rows: d.rows, foot: d.foot}],
    'Боткина_2025_' + TBL[t].sheet + '.xlsx');
}
function exportReport(){
  const sheets = [];
  sheets.push({name:'Описание', meta: metaLines('Описание среза', P().length),
    header:['Параметр','Значение'], foot:null, rows:[
      ['Заказчик', DATA.meta.customer_full || DATA.meta.customer],
      ['ИНН / КПП', DATA.meta.inn + ' / ' + DATA.meta.kpp],
      ['Период', DATA.meta.period],
      ['Дата выгрузки данных', DATA.meta.extracted_at],
      ['Источники', 'ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ'],
      ['Фильтры', FILTER_TXT()],
      ['Позиций в срезе', P().length],
      ['Сумма среза', P().reduce((s,p)=>s+(p.sum||0),0)],
      ['Позиций в профиле', DATA.totals.positions_in_scope],
      ['Профильный объём', DATA.totals.sum_scope],
      ['Охват страны', pct(DATA.totals.country_coverage)],
      ['Классы достоверности', 'факт — данные ЕИС; оценка — расчётное значение, не для официальной отчётности']
    ]});
  sheets.push({name:'Показатели', meta: metaLines('Основные показатели', lastKpi.length),
    header:['Показатель','Значение','Пояснение'], foot:null,
    rows: lastKpi.map(k => k.slice())});
  ['cat','items','bench','country'].forEach(t => {
    const d = tableData(t);
    sheets.push({name:TBL[t].sheet, meta: metaLines(TBL[t].title, d.count),
      header:d.header, rows:d.rows, foot:d.foot});
  });
  const r = tableData('reg');
  sheets.push({name:TBL.reg.sheet, meta: metaLines(TBL.reg.title, r.count),
    header:r.header, rows:r.rows, foot:null});
  xlsxDownload(sheets, 'Боткина_2025_отчёт_по_срезу.xlsx');
}
// --- панель управления над каждой таблицей ---
function makeToolbars(){
  Object.keys(TBL).forEach(t => {
    const cfg = TBL[t];
    const tbl = $(cfg.el);
    if (!tbl) return;
    const host = tbl.closest('.tablewrap') || tbl.closest('.registry') || tbl.parentNode;
    const limits = t === 'items' ? [[100,'100 строк'],[300,'300 строк'],[0,'все строки']]
      : t === 'bench' ? [[100,'100 строк'],[200,'200 строк'],[0,'все строки']]
      : t === 'catdet' ? [[12,'12 строк'],[50,'50 строк'],[0,'все строки']] : null;
    const bar = document.createElement('div');
    bar.className = 'tbar';
    bar.innerHTML =
      '<input type="search" placeholder="Поиск по этой таблице" data-tsearch="' + t + '" ' +
        'title="Фильтр строк таблицы; на другие разделы не влияет">' +
      (limits ? '<span class="lbl">Показать:</span><select data-tlimit="' + t + '">' +
        limits.map(([v,l]) => `<option value="${v}" ${v === tstate[t].limit ? 'selected' : ''}>${l}</option>`).join('') +
        '</select>' : '') +
      `<span class="cnt" data-tcnt="${t}"></span>` +
      `<button class="xl" data-xlsx="${t}" title="Выгрузить показанные строки в Excel (.xlsx)">Excel</button>` +
      `<button data-csvx="${t}" title="Выгрузить показанные строки в CSV (UTF-8 с BOM, разделитель «;»)">CSV</button>`;
    host.parentNode.insertBefore(bar, host);
  });
  $$('[data-tsearch]').forEach(inp => {
    const t = inp.dataset.tsearch;
    let tmr;
    inp.addEventListener('input', () => { clearTimeout(tmr);
      tmr = setTimeout(() => { tstate[t].q = inp.value.trim(); redrawTable(t); }, 160); });
  });
  $$('[data-tlimit]').forEach(sel => {
    const t = sel.dataset.tlimit;
    sel.addEventListener('change', () => { tstate[t].limit = +sel.value; redrawTable(t); });
  });
  $$('[data-xlsx]').forEach(b => b.addEventListener('click', () => exportTable(b.dataset.xlsx)));
  $$('[data-csvx]').forEach(b => b.addEventListener('click', () => exportCsv(b.dataset.csvx)));
}

// ---------- обновление ----------
function updateSrcLines(){
  const m = DATA.meta, t = DATA.totals;
  const n = P().length;
  const txt = `Источник: ЕИС, реестры 44-ФЗ и 223-ФЗ · выгрузка ${m.extracted_at} · `
    + `профиль ${mln(t.sum_scope)} · охват страны ${pct(t.country_coverage)} профильного объёма · `
    + `позиций в срезе: ${fmt0.format(n)} из ${fmt0.format(t.positions_in_scope)}`;
  $$('[data-srcline]').forEach(el=>{ el.textContent = txt; });
}

function refresh(){
  _fi = null;
  renderChips();
  renderKpis();
  drawAll();
  renderCats();
  renderItems();
  renderBench();
  renderCountryTable();
  renderKey();
  regReset();
  updateSrcLines();
}

function fillSelects(){
  $('#fkind').innerHTML = '<option value="">Все виды</option>' +
    DATA.kinds.map(k=>`<option value="${k.kind}">${esc(KIND[k.kind]||k.kind)}</option>`).join('');
  $('#fcat').innerHTML = '<option value="">Все группы</option>' +
    DATA.categories.map(c=>`<option value="${esc(c.category)}">${esc(c.category)}</option>`).join('');
  $('#fcountry').innerHTML = '<option value="">Все страны</option>' +
    DATA.countries.map(c=>`<option value="${esc(c.country)}">${esc(c.country)}</option>`).join('');
  $('#fsup').innerHTML = '<option value="">Все поставщики</option>' +
    DATA.suppliers.map(s=>`<option value="${esc(s)}">${esc(s)}</option>`).join('');
}

function init(){
  const m = DATA.meta, t = DATA.totals;
  $('#subtitle').textContent = `${m.customer} · период ${m.period} · учёт по дате заключения контракта`;
  $('#srcdates').innerHTML = `Источники: 44-ФЗ и 223-ФЗ<br>Контрактов: <b>${fmt0.format(m.contracts_total)}</b><br>Позиций в профиле: <b>${fmt0.format(t.positions_in_scope)}</b><br>Дата выгрузки: <b>${m.extracted_at}</b>`;
  $('#fdate').textContent = m.extracted_at;
  $('#methodMeta').textContent = `Заказчик: ${m.customer_full || m.customer}. ИНН ${m.inn}, КПП ${m.kpp}. Период: ${m.period}. Дата выгрузки: ${m.extracted_at}. Профильных позиций: ${fmt0.format(t.positions_in_scope)} на ${money(t.sum_scope)}.`;
  fillSelects();
  initCharts();
  reg.box = $('#regBox'); reg.body = $('#regBody');
  reg.box.addEventListener('scroll', regRender);

  $('#fkind').addEventListener('change', e=>{state.kind=e.target.value; refresh();});
  $('#fcat').addEventListener('change', e=>{state.cat=e.target.value; selected.cat=e.target.value; refresh();});
  $('#fcountry').addEventListener('change', e=>{state.country=e.target.value; refresh();});
  $('#forigin').addEventListener('change', e=>{state.origin=e.target.value; refresh();});
  $('#fsup').addEventListener('change', e=>{state.sup=e.target.value; refresh();});
  $('#fmin').addEventListener('input', e=>{state.min = e.target.value ? +e.target.value : null; refresh();});
  $('#fmax').addEventListener('input', e=>{state.max = e.target.value ? +e.target.value : null; refresh();});
  let timer;
  $('#fq').addEventListener('input', e=>{clearTimeout(timer);timer=setTimeout(()=>{state.q=e.target.value.trim().toLowerCase();refresh();},180);});
  $('#f80').addEventListener('change', e=>{state.only80=e.target.checked; refresh();});
  $('#fest') && $('#fest').addEventListener('change', e=>{state.noEst=e.target.checked; refresh();});
  $('#reset').addEventListener('click', ()=>{
    Object.assign(state,{kind:'',cat:'',country:'',origin:'',sup:'',min:null,max:null,q:'',only80:false,noEst:false});
    ['#fkind','#fcat','#fcountry','#forigin','#fsup','#fq','#fmin','#fmax'].forEach(s=>$(s).value='');
    $('#f80').checked=false; selected.cat='';
    refresh();
  });
  $('#csv').addEventListener('click', downloadCsv);
  $('#xlsx').addEventListener('click', exportReport);
  $('#themeBtn').addEventListener('click', cycleTheme);
  $('#printBtn').addEventListener('click', ()=>{ Object.values(charts).forEach(c=>c.resize()); window.print(); });
  window.addEventListener('beforeprint', ()=>{ regAll(); });
  window.addEventListener('afterprint', ()=>{ regReset(); });

  // сортировка таблиц (клик по заголовку; у реестра — отдельный обработчик ниже)
  document.addEventListener('click', (e)=>{
    const th = e.target.closest('th.sortable');
    if (!th || !th.dataset.t) return;
    const t = th.dataset.t, k = th.dataset.k;
    if (!sortState[t]) return;
    const st = sortState[t];
    if (st.k === k) st.d *= -1;
    else { st.k = k; st.d = (['name','cat','country','sup','month','orig','top'].includes(k)) ? 1 : -1; }
    redrawTable(t);
  });
  // сортировка реестра
  $$('#regBox th.sortable').forEach(th=>th.addEventListener('click', ()=>{
    const k = th.dataset.k; if (k==='idx') return;
    if (sortState.reg.k === k) sortState.reg.d *= -1;
    else { sortState.reg.k = k; sortState.reg.d = ['name','cat','country','sup','month'].includes(k) ? 1 : -1; }
    regReset();
  }));
  window.addEventListener('resize', ()=>Object.values(charts).forEach(c=>c.resize()));

  const saved = localStorage.getItem(THEME_KEY) || 'light';
  document.documentElement.dataset.theme = saved;
  $('#themeBtn').textContent = 'Тема: ' + ({light:'светлая',dark:'тёмная',auto:'системная'}[saved]);
  makeToolbars();
  refresh();
}
init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
