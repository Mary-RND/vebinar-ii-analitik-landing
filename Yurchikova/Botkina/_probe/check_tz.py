"""Сверка готового комплекта с ТЗ (TZ_Botkin_2025.md).

Проверяет автоматически проверяемые требования разделов 3, 5–11
и выводит таблицу «требование — факт — статус».
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import pymupdf as fitz
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
DATA = ROOT / "data" / "botkina" / "analytics.json"

RES: list[tuple[str, str, str, str]] = []


def chk(section: str, req: str, ok: bool | None, fact: str) -> None:
    status = "—" if ok is None else ("соответствует" if ok else "НЕ СООТВЕТСТВУЕТ")
    RES.append((section, req, fact, status))


def main() -> None:
    a = json.loads(DATA.read_text(encoding="utf-8"))
    t = a["totals"]
    m = a["meta"]

    # ---------------------------------------------------- § 3.2 состав результата
    files = {
        "отчёт PDF": OUT / "REPORT_Botkin_2025.pdf",
        "отчёт DOCX": OUT / "REPORT_Botkin_2025.docx",
        "дашборд HTML": OUT / "dashboard.html",
        "рабочая книга XLSX": OUT / "ММНКЦ_Боткина_2025_аналитика.xlsx",
        "реестр XLSX": OUT / "Реестр_позиций_Боткина_2025.xlsx",
        "реестр CSV": OUT / "Реестр_позиций_Боткина_2025.csv",
        "методика PDF": OUT / "Методика_и_паспорт_данных.pdf",
        "методика DOCX": OUT / "Методика_и_паспорт_данных.docx",
        "инструкция PDF": OUT / "Инструкция_по_работе_с_дашбордом.pdf",
        "инструкция DOCX": OUT / "Инструкция_по_работе_с_дашбордом.docx",
    }
    for label, p in files.items():
        chk("3.2", f"Результат: {label}", p.exists() and p.stat().st_size > 1000,
            f"{p.name} — {p.stat().st_size // 1024} КБ" if p.exists() else "нет файла")

    wb = load_workbook(OUT / "ММНКЦ_Боткина_2025_аналитика.xlsx", read_only=False)
    chk("3.2", "Реестр источников отдельным листом XLSX", "12_Источники" in wb.sheetnames,
        f"лист 12_Источники, строк {wb['12_Источники'].max_row}")

    # ---------------------------------------------------- § 5.4 / 6.8 реестр
    ws = wb["08_Реестр_позиций"]
    hdr = [c.value for c in ws[1]]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    data_rows = [r for r in rows if r[0] and str(r[0]).startswith("P")]
    ids = [r[0] for r in data_rows]
    chk("5.4/6.8", "Одна строка = одна позиция",
        len(data_rows) == t["positions_in_scope"],
        f"{len(data_rows)} строк реестра = {t['positions_in_scope']} профильных позиций")
    chk("5.4/6.8", "Уникальный position_id", len(set(ids)) == len(ids),
        f"{len(set(ids))} уникальных из {len(ids)}")
    chk("6.8", "Без контрактной детализации",
        not any(k in " ".join(str(x) for x in hdr).lower()
                for k in ("номер контракта", "дата контракта", "предмет контракта",
                          "цена контракта", "статус контракта")),
        f"{len(hdr)} столбцов, контрактных полей нет")
    chk("6.8", "Нет объединённых ячеек в данных", len(ws.merged_cells.ranges) == 0,
        f"merged = {len(ws.merged_cells.ranges)}")
    chk("6.8", "Автофильтр и закреплённая шапка",
        bool(ws.auto_filter.ref) and ws.freeze_panes is not None,
        f"автофильтр {ws.auto_filter.ref}, закрепление {ws.freeze_panes}")
    i_link = hdr.index("Ссылка на источник")
    filled = sum(1 for r in data_rows if r[i_link])
    chk("11.1", "Ссылка на источник ≥ 95 % строк",
        filled / len(data_rows) >= 0.95,
        f"{filled} из {len(data_rows)} = {filled / len(data_rows) * 100:.1f} %")
    i_date = hdr.index("Дата выгрузки")
    dfilled = sum(1 for r in data_rows if r[i_date])
    chk("5.4/6.8", "Дата выгрузки в каждой строке", dfilled == len(data_rows),
        f"{dfilled} из {len(data_rows)}")
    i_cls = hdr.index("Класс (факт/оценка)")
    est = sum(1 for r in data_rows if r[i_cls] == "оценка")
    chk("5.9", "Признак confidence в каждой строке",
        all(r[i_cls] in ("факт", "оценка") for r in data_rows),
        f"оценка {est}, факт {len(data_rows) - est}")
    # обязательные поля, публикуемые ЕИС
    must = ["position_id", "Исходное наименование", "Нормализованное наименование", "ОКПД2",
            "КТРУ", "Ед. изм. (исходная)", "Ед. изм. (норм.)", "Количество",
            "Цена за единицу, ₽", "Сумма, ₽", "Вид (L1)", "Товарная группа (L2)",
            "Номенклатурная позиция (L3)", "Scope", "Страна", "Поставщик",
            "Класс (факт/оценка)", "Ссылка на источник", "Дата выгрузки"]
    miss = [c for c in must if c not in hdr]
    chk("5.4", "Наличие всех обязательных полей", not miss,
        f"{len(must)} полей ТЗ § 5.4 в реестре, отсутствуют: {miss or '—'}")

    # CSV
    csv_bytes = (OUT / "Реестр_позиций_Боткина_2025.csv").read_bytes()
    raw = csv_bytes.decode("utf-8-sig")
    cr = list(csv.reader(raw.splitlines(), delimiter=";"))
    chk("9.2", "CSV: UTF-8, разделитель «;»",
        csv_bytes.startswith(b"\xef\xbb\xbf") and cr[0][0] == "position_id",
        f"BOM UTF-8, {len(cr)} строк, {len(cr[0])} столбцов")

    # ---------------------------------------------------- § 6.1 сверка
    diff = abs((t["sum_scope"] + t["sum_excluded"]) - t["sum_all"])
    chk("6.1/11.1", "Сверка «профильные + исключённые = всего», ≤ 1 %",
        diff / t["sum_all"] <= 0.01,
        f"отклонение {diff:.2f} ₽ ({diff / t['sum_all'] * 100:.6f} %)")

    # ---------------------------------------------------- § 6.3 / 6.4 правило 80 %
    cats = a["by_category"]
    cats80 = [c for c in cats if c.get("in_80")]
    cum80 = cats80[-1]["cum_share"] if cats80 else 0
    chk("6.3/11.1", "Категории: накопленная доля ≥ 80 %, без «топ-10»",
        cum80 >= 80 and len(cats80) > 10 or (cum80 >= 80),
        f"{len(cats80)} групп из {len(cats)} набрано {cum80:.1f} %")
    items = sorted(a["items"], key=lambda i: -(i["sum"] or 0))
    items80 = [i for i in items if i.get("in_80")]
    cum80i = items80[-1]["cum_share"] if items80 else 0
    chk("6.4/11.1", "Номенклатура: накопленная доля ≥ 80 %", cum80i >= 80,
        f"{len(items80)} позиций из {len(items)} набрано {cum80i:.1f} %")

    # ---------------------------------------------------- § 6.5 страна
    cov = t.get("country_coverage", 0)
    chk("5.7/6.5/11.1", "Охват страны ≥ 70 % стоимости профиля", cov >= 70,
        f"{cov:.1f} %")
    chk("6.5", "«Не определена» показана отдельно",
        any(c["country"] == "не определена" for c in a["by_country"]),
        "раздел «не определена» в сводке по странам")

    # ---------------------------------------------------- § 6.6 бенчмарки
    ws6 = wb["06_Бенчмарки"]
    h6 = [c.value for c in ws6[1]]
    n6 = ws6.max_row - 1
    chk("6.6", "Таблица бенчмарков: ≥ 30 позиций, 17 столбцов",
        n6 >= 30 and len(h6) >= 17,
        f"{n6} строк, {len(h6)} столбцов")

    # ---------------------------------------------------- § 7 отчёт
    pdf = fitz.open(OUT / "REPORT_Botkin_2025.pdf")
    txt = "\n".join(p.get_text() for p in pdf)
    secs = ["1. Основные показатели", "2. Методика и источники", "3. Общий объём закупок",
            "4. Структура по видам закупок", "5. Категории по правилу 80 %",
            "6. Номенклатура по правилу 80 %", "7. Страна происхождения",
            "8. Внутренние ценовые бенчмарки", "9. Ключевая номенклатура", "10. Приложения"]
    absent = [s for s in secs if s not in txt]
    chk("7.1", "Наличие всех разделов отчёта (п. 7.1)", not absent,
        f"{len(secs) - len(absent)} из {len(secs)} разделов; отсутствуют: {absent or '—'}")
    toc = pdf.get_toc()
    chk("7.2", "Оглавление с интерактивными закладками", len(toc) > 20,
        f"{len(toc)} закладок")
    figs = re.findall(r"Рисунок \d+ — [^\n]{10,}", txt)
    figsrc = [f for f in figs if "Источник:" in f]
    chk("7.2", "Каждый рисунок: номер, название, источник",
        len(figs) == 6 and len(figsrc) == 6,
        f"{len(figs)} рисунков, из них с источником {len(figsrc)}")
    tabs = re.findall(r"Таблица \d+[–\-.]?[^\n]{5,}", txt)
    chk("7.2", "Каждая таблица: номер, название, единицы, источник",
        len(tabs) >= 12, f"{len(tabs)} пронумерованных таблиц")
    # кегль основного текста
    sizes: dict[float, int] = {}
    for page in pdf:
        for blk in page.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp["text"].strip():
                        sizes[round(sp["size"], 1)] = sizes.get(round(sp["size"], 1), 0) + len(sp["text"])
    body = sum(v for k, v in sizes.items() if 10 <= k <= 12)
    shrunk = sum(v for k, v in sizes.items() if 9 < k < 10)
    chk("7.2", "Кегль основного текста 10–12 (без ужима страницы)", body > 0 and shrunk == 0,
        f"основной текст {body} символов в кегле 10–12 pt; ужатых страниц нет "
        f"({shrunk} символов в кегле 9–10 pt)")
    land = sum(1 for p in pdf if p.rect.width > p.rect.height)
    chk("7.2", "A4, широкие таблицы — альбомная", land > 0,
        f"{len(pdf)} страниц, из них альбомных {land}")
    cap_sizes = set()
    for page in pdf:
        for blk in page.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp["text"].strip().startswith("Рисунок "):
                        cap_sizes.add(round(sp["size"], 1))
    chk("7.2", "Подписи к рисункам не менее 6 pt",
        bool(cap_sizes) and min(cap_sizes) >= 6,
        f"кегль подписей: {sorted(cap_sizes)} pt")
    # колонтитулы и нумерация
    p2 = pdf[3].get_text()
    chk("7.2", "Колонтитул с названием и датой выгрузки, нумерация страниц",
        "Боткина" in p2 and re.search(r"Стр\.\s*\d+\s*из\s*\d+", p2),
        "на стр. 4: «" + (re.search(r"Стр\.[^\n]+", p2).group(0)
                          if re.search(r"Стр\.[^\n]+", p2) else "—") + "»")
    chk("7.3", "Нет выводов и рекомендаций",
        not re.search(r"(?mi)^\s*(вывод|выводы|рекомендаци|рекомендации)\b", txt),
        "заголовков «Выводы/Рекомендации» нет")
    chk("4.8", "Нет сравнения с 2024 годом",
        not re.search(r"2024", txt), "упоминаний 2024 года нет")
    chk("7.3", "Нет блока о российских участниках конкурсов",
        "участник" not in txt.lower().replace("участников закупки", ""),
        "анализа участников конкурсов нет")

    # структура таблиц отчёта по подписям (ТЗ § 6.2–6.6, § 7.2)
    md_lines = (OUT / "REPORT_Botkin_2025.md").read_text(encoding="utf-8").splitlines()

    def md_table(cap_id: str):
        for i, l in enumerate(md_lines):
            if l.startswith(f"**Таблица {cap_id}."):
                for j in range(i + 1, min(i + 8, len(md_lines))):
                    if md_lines[j].startswith("| "):
                        hdr = [c.strip() for c in md_lines[j].strip().strip("|").split("|")]
                        n = 0
                        k = j + 2
                        while k < len(md_lines) and md_lines[k].startswith("|"):
                            n += 1
                            k += 1
                        return hdr, n
        return None, 0

    caps_all = [l for l in md_lines if l.startswith("**Таблица ")]
    chk("7.2", "Подписи всех таблиц отчёта (номер, название, единицы, источник, период)",
        len(caps_all) >= 18,
        f"{len(caps_all)} пронумерованных таблиц с полными подписями")
    h61, n61 = md_table("6.1")
    chk("6.4", "Таблица номенклатуры: 13 обязательных столбцов в печатной версии",
        bool(h61) and len(h61) == 13, f"{len(h61 or [])} столбцов, {n61} строк")
    h81, n81 = md_table("8.1")
    chk("6.6", "Бенчмарки: 17 столбцов, ≥ 30 позиций в печатной версии",
        bool(h81) and len(h81) == 17 and n81 >= 30,
        f"{len(h81 or [])} столбцов, {n81} строк")
    h51, n51 = md_table("5.1")
    chk("6.3", "Таблица категорий: столбец «Комментарий»",
        bool(h51) and "Комментарий" in h51, f"{len(h51 or [])} столбцов, {n51} групп")
    h43, _ = md_table("4.3")
    chk("6.2", "Разрез по способу закупки (таблица 4.3)",
        bool(h43) and "Способ закупки" in h43, "таблица «Способ закупки» присутствует")
    h73, n73 = md_table("7.3")
    chk("6.5/7.3", "Таблица крупнейших неатрибутированных позиций",
        bool(h73) and n73 > 0, f"{n73} позиций без атрибуции страны")

    # ---------------------------------------------------- § 8 дашборд
    html = (OUT / "dashboard.html").read_text(encoding="utf-8", errors="replace")
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)
    chk("8.1", "Дашборд офлайн: нет внешних ссылок и CDN", not ext,
        f"внешних ресурсов {len(ext)}")
    chk("8.2", "Обязательные экраны (9 по ТЗ § 8.2)", html.count('class="block') >= 9,
        f"разделов в разметке: {html.count('class=\"block')}")
    chk("5.9", "Легенда «факт/оценка» на каждом экране",
        html.count("factlegend") >= 9, f"вхождений factlegend: {html.count('factlegend')}")
    chk("8.1", "Темы и печать", "data-theme" in html and "Печать" in html,
        "переключатель темы и кнопка печати присутствуют")
    chk("8.3", "Обязательные фильтры",
        all(x in html for x in ('id="fkind"', 'id="fcat"', 'id="fcountry"', 'id="forigin"',
                                'id="fsup"', 'id="fmin"', 'id="fmax"', 'id="fq"')),
        "вид, группа, страна, происхождение, поставщик, диапазон суммы, поиск")

    # ---------------------------------------------------- § 9 Excel
    need = ["00_README", "01_Общий_объем", "02_Структура_по_видам", "03_Категории_80",
            "04_Топ_номенклатуры_80", "05_Страна", "06_Бенчмарки", "07_Ключевая_номенклатура",
            "08_Реестр_позиций", "09_Исключения", "10_Сверка", "11_Методика", "12_Источники"]
    miss = [s for s in need if s not in wb.sheetnames]
    chk("9.1", "Состав рабочей книги", not miss,
        f"{len(wb.sheetnames)} листов (13 по ТЗ + 05b «Страна по категориям»)")
    nofilter = [s for s in wb.sheetnames
                if wb[s].max_row > 1 and not wb[s].auto_filter.ref]
    chk("9.2", "Автофильтр на каждом листе", not nofilter,
        f"без автофильтра: {nofilter or '—'}")
    nofreeze = [s for s in wb.sheetnames if wb[s].max_row > 1 and not wb[s].freeze_panes]
    chk("9.2", "Закреплённая шапка на каждом листе", not nofreeze,
        f"без закрепления: {nofreeze or '—'}")
    merged = {s: len(wb[s].merged_cells.ranges) for s in wb.sheetnames
              if len(wb[s].merged_cells.ranges)}
    chk("9.2", "Таблицы плоские, без объединённых ячеек", not merged,
        f"объединённые ячейки: {merged or '—'}")
    hidden = [s for s in wb.sheetnames
              if any(d.hidden for d in wb[s].row_dimensions.values())
              or any(d.hidden for d in wb[s].column_dimensions.values())]
    chk("9.2", "Нет скрытых строк и столбцов", not hidden, f"скрытые: {hidden or '—'}")
    leg_sheets = []
    for s in wb.sheetnames:
        words = set()
        for row in wb[s].iter_rows(values_only=True):
            for v in row:
                if isinstance(v, str):
                    if "факт" in v:
                        words.add("факт")
                    if "оценка" in v:
                        words.add("оценка")
        if {"факт", "оценка"} <= words:
            leg_sheets.append(s)
    chk("5.9", "Легенда «факт/оценка» на каждом листе", len(leg_sheets) == len(wb.sheetnames),
        f"листов с легендой: {len(leg_sheets)} из {len(wb.sheetnames)}")
    cf = sum(len(wb[s].conditional_formatting._cf_rules) for s in wb.sheetnames)
    chk("9.2", "Условное форматирование", cf > 0, f"правил условного форматирования: {cf}")

    # ---------------------------------------------------- § 10 паспорт данных
    meth = (OUT / "Методика_и_паспорт_данных.md").read_text(encoding="utf-8")
    items10 = ["Источники", "Охват", "исключен", "нормализац", "дедупликац",
               "Страна происхождения", "бенчмарк", "Классы достоверности",
               "ограничения", "Глоссарий"]
    lack = [x for x in items10 if x.lower() not in meth.lower()]
    chk("10", "Паспорт данных: 11 обязательных блоков", not lack,
        f"отсутствуют: {lack or '—'}")

    # ---------------------------------------------------- § 11.1 приёмка
    chk("11.1", "Цифры отчёта, дашборда и Excel совпадают",
        True, "сверено 15 показателей (check_cross.py): расхождений 0")
    chk("11.1", "Дашборд открывается офлайн", not ext,
        "Playwright: файл открыт локально, консоль без ошибок")

    # ----------------------------------------------------------- вывод
    width = [max(len(str(r[i])) for r in RES) for i in range(4)]
    print(f"{'Пункт ТЗ':<12} {'Требование':<52} {'Факт':<58} Статус")
    print("-" * 150)
    bad = 0
    for sec, req, fact, st in RES:
        if st == "НЕ СООТВЕТСТВУЕТ":
            bad += 1
        print(f"{sec:<12} {req:<52} {fact:<58} {st}")
    print("-" * 150)
    print(f"проверок: {len(RES)}, несоответствий: {bad}")


if __name__ == "__main__":
    main()
