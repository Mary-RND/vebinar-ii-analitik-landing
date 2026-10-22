"""Рабочая книга Excel по требованиям § 9 ТЗ.

Вход:  data/<slug>/analytics.json
Выход: output/ММНКЦ_Боткина_2025_аналитика.xlsx

13 листов: README, общий объём, виды, категории 80 %, номенклатура 80 %,
страны, бенчмарки, ключевая номенклатура, реестр, исключения, сверка,
методика, источники.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from classify import KIND_TITLES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = cfg.DEFAULT_LPU
LPU = cfg.get(SLUG)
ANALYTICS = ROOT / "data" / SLUG / "analytics.json"
OUT = ROOT / "output" / "ММНКЦ_Боткина_2025_аналитика.xlsx"

HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=14, color="1F4E79")
SUB_FONT = Font(bold=True, size=11, color="1F4E79")
TOTAL_FILL = PatternFill("solid", fgColor="DDEBF7")
GREEN_FILL = PatternFill("solid", fgColor="E7F3EC")
ORANGE_FILL = PatternFill("solid", fgColor="FDF3E2")
YELLOW_FILL = PatternFill("solid", fgColor="FFF6D9")
NOTE_FONT = Font(italic=True, size=9, color="595959")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONEY = '# ##0.00'
PCT = '0.0'
INT = '# ##0'

SCOPE_TITLES = {"main": "основной", "borderline": "пограничная", "excluded": "исключено"}

# Расшифровка классов достоверности — приводится на каждом листе (ТЗ § 5.9)
LEGEND = ("Классы достоверности: «факт» — данные первичного источника ЕИС без изменений; "
          "«оценка» — расчётное, агрегированное или неполное значение. Оценочные значения "
          "не предназначены для официальной отчётности.")


def norm_name(name: str | None) -> str:
    n = (name or "").lower()
    n = re.sub(r"[^а-яёa-z0-9 ]", " ", n)
    return re.sub(r"\s+", " ", n).strip()[:120]


def add_legend(ws) -> int:
    """Строка расшифровки классов достоверности — на каждом листе (ТЗ § 5.9)."""
    ws.append([LEGEND])
    c = ws.cell(row=ws.max_row, column=1)
    c.font = NOTE_FONT
    c.alignment = Alignment(vertical="top")
    return ws.max_row


def sheet(wb: Workbook, title: str, headers: list[str], rows: list[list],
          widths: list[int] | None = None, money_cols: tuple = (), pct_cols: tuple = (),
          int_cols: tuple = (), total_row: list | None = None, freeze: str = "A2",
          autofilter: bool = True, note: str | None = None) -> None:
    ws = wb.create_sheet(title)
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    for row in rows:
        ws.append(row)
    if total_row:
        ws.append(total_row)
        r = ws.max_row
        for cell in ws[r]:
            cell.font = Font(bold=True)
            cell.fill = TOTAL_FILL
            cell.border = BORDER
    ws.data_end_row = ws.max_row   # последняя строка данных (без примечаний)
    # форматы
    for i in range(2, ws.max_row + 1):
        for col in money_cols:
            ws.cell(row=i, column=col).number_format = MONEY
        for col in pct_cols:
            ws.cell(row=i, column=col).number_format = PCT
        for col in int_cols:
            ws.cell(row=i, column=col).number_format = INT
    # ширины
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    else:
        for i in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(i)].width = 18
    ws.freeze_panes = freeze
    if autofilter and ws.max_row > 1:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row if not note else ws.max_row}"
    if note:
        ws.append([note])
        c = ws.cell(row=ws.max_row, column=1)
        c.font = NOTE_FONT
        c.alignment = Alignment(vertical="top")   # без объединения ячеек: текст выходит вправо
    add_legend(ws)
    ws.row_dimensions[1].height = 34


def text_sheet(wb: Workbook, title: str, lines: list[str], width: int = 120,
               legend: bool = True) -> None:
    ws = wb.create_sheet(title)
    ws.column_dimensions["A"].width = width
    rows = list(lines)
    if legend:
        rows += ["", LEGEND]
    for line in rows:
        ws.append([line])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        if line.startswith("## "):
            cell.font = SUB_FONT
        elif line.startswith("# "):
            cell.font = TITLE_FONT
        elif line.startswith("- "):
            cell.font = Font(size=10)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:A{ws.max_row}"   # автофильтр на каждом листе (ТЗ § 9.2)


def build() -> None:
    a = json.loads(ANALYTICS.read_text(encoding="utf-8"))
    t = a["totals"]
    m = a["meta"]
    wb = Workbook()
    wb.remove(wb.active)

    # ---------------------------------------------------------------- README
    readme = [
        "# Анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
        "",
        f"Заказчик: {m.get('customer_full') or m['customer']}",
        f"ИНН/КПП: {m['inn']} / {m['kpp']}",
        f"Период: {m['period']}",
        f"Дата выгрузки: {m['extracted_at']}",
        f"Источники: {m['sources']}",
        "",
        "## Объём",
        f"Контрактов всего: {m['contracts_total']:,}".replace(",", " ") + f" (44-ФЗ — {m['contracts_44']}, 223-ФЗ — {m['contracts_223']})",
        f"Профильных контрактов: {m['contracts_in_scope']:,}".replace(",", " "),
        f"Сумма всех позиций: {t['sum_all']:,.2f} ₽".replace(",", " "),
        f"Профильный объём (main + borderline): {t['sum_scope']:,.2f} ₽".replace(",", " "),
        "",
        "## Навигация по листам",
        "- 01_Общий_объем — ключевые показатели, сверка, источники, кварталы",
        "- 02_Структура_по_видам — медицинское оборудование, расходные материалы, имплантаты, реагенты, мебель и одежда, прочее",
        "- 03_Категории_80 — все товарные группы с признаком вхождения в 80 %-набор",
        "- 04_Топ_номенклатуры_80 — все позиции с признаком вхождения в 80 %-набор",
        "- 05_Страна — сводка по странам и матрица «категория × страна»",
        "- 06_Бенчмарки — внутренние ценовые бенчмарки и потенциал снижения",
        "- 07_Ключевая_номенклатура — карточки позиций 80 %-набора",
        "- 08_Реестр_позиций — полный построчный реестр без контрактной детализации",
        "- 09_Исключения — исключённые позиции с причиной",
        "- 10_Сверка — расхождения сумм, дубли, пропуски",
        "- 11_Методика — классификатор, правила, глоссарий",
        "- 12_Источники — ссылки, даты выгрузки, охват",
        "",
        "## Классы достоверности",
        "- «факт» — данные первичного источника без изменений;",
        "- «оценка» — расчётное, агрегированное или неполное значение;",
        "- оценочные значения помечены в реестре и не предназначены для официальной отчётности.",
        "",
        "## Ограничения",
        "- в реестрах ЕИС отсутствуют закрытые закупки и закупки, не подлежащие публикации;",
        "- закупки на Портале поставщиков Москвы в ЕИС не публикуются и в объём не входят;",
        "- часть контрактов не содержит количества и суммы позиций в реестре — суммы распределены по цене контракта и помечены как оценка;",
        "- ставка НДС в реестре контрактов не публикуется, поэтому не рассчитывается;",
        "- контрактная детализация (номера, даты, предметы, цены контрактов) в результат не выводится.",
    ]
    text_sheet(wb, "00_README", readme, legend=False)

    # ---------------------------------------------------------------- 01
    ws = wb.create_sheet("01_Общий_объем")
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 14
    ws.append(["Ключевые показатели"])
    ws["A1"].font = TITLE_FONT
    for i, h in enumerate(["Показатель", "Значение", "Ед. изм."], 1):
        c = ws.cell(row=2, column=i, value=h)
        c.fill = HEAD_FILL
        c.font = HEAD_FONT
        c.border = BORDER
        c.alignment = Alignment(horizontal="center", vertical="center")
    kpi = [
        ("Контрактов всего", m["contracts_total"], "шт."),
        ("в том числе 44-ФЗ", m["contracts_44"], "шт."),
        ("в том числе 223-ФЗ", m["contracts_223"], "шт."),
        ("Контрактов с профильными товарами", m["contracts_in_scope"], "шт."),
        ("Сумма всех позиций", t["sum_all"], "₽"),
        ("Профильный объём (main + borderline)", t["sum_scope"], "₽"),
        ("в том числе основной профиль", t["sum_main"], "₽"),
        ("в том числе пограничные категории", t["sum_borderline"], "₽"),
        ("Исключено из профиля", t["sum_excluded"], "₽"),
        ("Позиций всего", t["positions"], "шт."),
        ("Позиций в профиле", t["positions_in_scope"], "шт."),
        ("Позиций с количеством", t["positions_with_qty"], "шт."),
        ("Позиций с оценочной суммой", t["positions_estimated"], "шт."),
        ("Поставщиков в профиле", t["suppliers"], "шт."),
        ("Медиана контракта", t["median_contract"], "₽"),
        ("Средняя сумма позиции", t["avg_position"], "₽"),
        ("Медианная сумма позиции", t["median_position"], "₽"),
        ("Категорий в 80 %-наборе", t["categories_in_80"], "шт."),
        ("Позиций в 80 %-наборе", t["items_in_80"], "шт."),
        ("Охват страной происхождения", t["country_coverage"] / 100, "%"),
    ]
    r = 3
    for label, value, unit in kpi:
        ws.cell(row=r, column=1, value=label).border = BORDER
        c = ws.cell(row=r, column=2, value=value)
        c.border = BORDER
        c.font = Font(bold=True)
        if unit == "₽":
            c.number_format = MONEY
        elif unit == "%":
            c.number_format = PCT
        else:
            c.number_format = INT
        ws.cell(row=r, column=3, value=unit).border = BORDER
        r += 1
    ws.auto_filter.ref = f"A2:C{r - 1}"

    r += 2
    ws.cell(row=r, column=1, value="Сверка сумм").font = SUB_FONT
    r += 1
    recon = [
        ("Профильные позиции (main + borderline)", t["sum_scope"]),
        ("Исключённые позиции", t["sum_excluded"]),
        ("Итого по позициям", t["sum_all"]),
        ("Сумма цен контрактов", t["sum_contracts"]),
        ("Расхождение (позиции − контракты)", t["reconciliation_diff"]),
        ("Отклонение, %", (t["reconciliation_diff"] / t["sum_contracts"] * 100) if t["sum_contracts"] else 0),
    ]
    for label, value in recon:
        ws.cell(row=r, column=1, value=label).border = BORDER
        c = ws.cell(row=r, column=2, value=value)
        c.border = BORDER
        c.number_format = PCT if label.endswith("%") else MONEY
        if label.startswith("Отклонение"):
            dev01 = f"B{r}"
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="По источникам").font = SUB_FONT
    r += 1
    headers = ["Источник", "Позиций", "Сумма, ₽", "Доля, %"]
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=r, column=i, value=h)
        c.fill = HEAD_FILL
        c.font = HEAD_FONT
        c.border = BORDER
    r += 1
    for src in a["by_source"]:
        ws.cell(row=r, column=1, value=src["source"]).border = BORDER
        c = ws.cell(row=r, column=2, value=src["n"])
        c.number_format = INT
        c.border = BORDER
        c = ws.cell(row=r, column=3, value=src["sum"])
        c.number_format = MONEY
        c.border = BORDER
        c = ws.cell(row=r, column=4, value=src["sum"] / (t["sum_scope"] or 1))
        c.number_format = PCT
        c.border = BORDER
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="По кварталам").font = SUB_FONT
    r += 1
    for i, h in enumerate(["Квартал", "Позиций", "Сумма, ₽"], 1):
        c = ws.cell(row=r, column=i, value=h)
        c.fill = HEAD_FILL
        c.font = HEAD_FONT
        c.border = BORDER
    r += 1
    for q in a["by_quarter"]:
        ws.cell(row=r, column=1, value=q["quarter"]).border = BORDER
        c = ws.cell(row=r, column=2, value=q["n"])
        c.number_format = INT
        c.border = BORDER
        c = ws.cell(row=r, column=3, value=q["sum"])
        c.number_format = MONEY
        c.border = BORDER
        r += 1
    ws.freeze_panes = "A3"
    add_legend(ws)
    # условное форматирование: отклонение сверки сверх 1 %
    red_font = Font(bold=True, color="B4423A")
    red_fill = PatternFill("solid", fgColor="FBE9E7")
    ws.conditional_formatting.add(dev01, CellIsRule(
        operator="greaterThan", formula=["1"], font=red_font, fill=red_fill))
    ws.conditional_formatting.add(dev01, CellIsRule(
        operator="lessThan", formula=["-1"], font=red_font, fill=red_fill))

    # ---------------------------------------------------------------- 02
    sheet(
        wb, "02_Структура_по_видам",
        ["№", "Вид закупки", "Сумма, ₽", "Доля, %", "Позиций", "Поставщиков", "Средняя сумма позиции, ₽", "Scope"],
        [[i, k["title"], k["sum"], k["share"] / 100, k["n"], k["suppliers"], k["avg_position"], SCOPE_TITLES.get(k["scope"], k["scope"])]
         for i, k in enumerate(a["by_kind"], 1)],
        widths=[5, 46, 18, 10, 10, 12, 18, 14],
        money_cols=(3, 7), pct_cols=(4,), int_cols=(1, 5, 6),
        total_row=["", "Итого профиль", t["sum_scope"], t["sum_scope"] / (t["sum_scope"] or 1), t["positions_in_scope"], t["suppliers"], t["avg_position"], ""],
        note="Профиль = main + borderline. Пограничные категории включены в общую сумму и выделены отдельной строкой.",
    )

    # ---------------------------------------------------------------- 03
    sheet(
        wb, "03_Категории_80",
        ["№", "Товарная группа", "Сумма, ₽", "Доля, %", "Накопленная доля, %", "Позиций", "Поставщиков",
         "Средняя сумма позиции, ₽", "В 80 %-наборе"],
        [[i, c["category"], c["sum"], c["share"] / 100, c["cum_share"] / 100, c["n"], c["suppliers"],
          c["avg_position"], "да" if c["in_80"] else "нет"]
         for i, c in enumerate(a["by_category"], 1)],
        widths=[5, 52, 18, 10, 16, 10, 12, 18, 14],
        money_cols=(3, 8), pct_cols=(4, 5), int_cols=(1, 6, 7),
        total_row=["", "Итого профиль", t["sum_scope"], 1.0, "", t["positions_in_scope"],
                   t["suppliers"], t["avg_position"], ""],
        note="80 %-набор — все группы до достижения 80 % профильного объёма, а не фиксированный топ-10. "
             "Группы за пределами набора оставлены для полноты.",
    )
    ws3 = wb["03_Категории_80"]
    for r in range(2, ws3.max_row + 1):
        if ws3.cell(row=r, column=9).value == "да":
            ws3.cell(row=r, column=9).fill = GREEN_FILL

    # ---------------------------------------------------------------- 04
    items = [it for it in a["items"] if it.get("in_80")]
    sheet(
        wb, "04_Топ_номенклатуры_80",
        ["№", "Номенклатурная позиция", "КТРУ", "ОКПД2", "Товарная группа", "Вид", "Ед. изм.",
         "Количество", "Сумма, ₽", "Доля, %", "Накопленная доля, %", "Позиций", "Поставщиков",
         "В 80 %-наборе", "Цена средневзвешенная", "Медиана", "Страна"],
        [[i, it["name"][:200], it.get("ktru"), it.get("okpd2"), it["category"],
          cfg_kind(it["kind"]), it.get("unit"), it.get("qty"), it["sum"], it["sum"] / (t["sum_scope"] or 1),
          it["cum_share"] / 100, it["n"], it.get("n_suppliers"), "да" if it["in_80"] else "нет",
          it.get("price_weighted"), it.get("price_median"), it.get("country") or "не определена"]
         for i, it in enumerate(items, 1)],
        widths=[5, 70, 18, 14, 40, 24, 10, 12, 18, 9, 16, 9, 11, 13, 16, 12, 18],
        money_cols=(9, 15, 16), pct_cols=(10, 11), int_cols=(1, 8, 12, 13),
        total_row=["", "Итого 80 %-набор", "", "", "", "", "", "",
                   sum(it["sum"] for it in items), sum(it["sum"] for it in items) / (t["sum_scope"] or 1),
                   "", sum(it["n"] for it in items), "", "", "", "", ""],
        note="Все позиции 80 %-набора; полный перечень позиций — на листе 08_Реестр_позиций.",
    )

    # ---------------------------------------------------------------- 05
    countries = a["by_country"]
    sheet(
        wb, "05_Страна",
        ["№", "Страна происхождения", "Сумма, ₽", "Доля, %", "Позиций", "Поставщиков",
         "Основные категории", "Confidence"],
        [[i, c["country"], c["sum"], c["share"] / 100, c["n"], c["suppliers"],
          "; ".join(c.get("cats") or []) or "—", c.get("confidence") or "факт"]
         for i, c in enumerate(countries, 1)],
        widths=[5, 34, 18, 10, 10, 12, 56, 12],
        money_cols=(3,), pct_cols=(4,), int_cols=(1, 5, 6),
        note="Страна — по полю «Страна происхождения» в спецификации; по стране поставщика не подставляется. "
             "Confidence: «факт» — все суммы опубликованы, «оценка» — есть позиции с расчётными суммами.",
    )
    ws5 = wb["05_Страна"]
    ru_sum = next((c["sum"] for c in countries if c["country"] == "Россия"), 0.0)
    known = t["sum_country_known"] or 1.0
    r = ws5.max_row + 2
    ws5.cell(row=r, column=1, value="Россия / импорт").font = SUB_FONT
    r += 1
    for i, h in enumerate(["Категория", "Сумма, ₽", "Доля профиля, %"], 1):
        c = ws5.cell(row=r, column=i, value=h)
        c.fill = HEAD_FILL
        c.font = HEAD_FONT
        c.border = BORDER
    summary = [
        ("Россия", ru_sum, ru_sum / (t["sum_scope"] or 1)),
        ("Импорт", t["sum_country_known"] - ru_sum, (t["sum_country_known"] - ru_sum) / (t["sum_scope"] or 1)),
        ("Не указана", t["sum_country_unknown"], t["sum_country_unknown"] / (t["sum_scope"] or 1)),
        ("Итого профиль", t["sum_scope"], 1.0),
    ]
    r += 1
    for label, value, share in summary:
        ws5.cell(row=r, column=1, value=label).border = BORDER
        c = ws5.cell(row=r, column=2, value=value)
        c.number_format = MONEY
        c.border = BORDER
        c = ws5.cell(row=r, column=3, value=share)
        c.number_format = PCT
        c.border = BORDER
        r += 1
    c = ws5.cell(row=r + 1, column=1,
                 value=f"Охват страной происхождения — {t['country_coverage']:.1f} % профильного объёма. "
                       f"Страна не указана для {t['sum_country_unknown']:.2f} ₽.")
    c.font = NOTE_FONT
    c.alignment = Alignment(vertical="top")

    # матрица категория × страна (топ-10)
    top_cats = [c["category"] for c in a["by_category"][:10]]
    top_countries = [c["country"] for c in countries[:10]]
    matrix: dict[tuple[str, str], float] = {}
    for p in a["positions"]:
        if p["scope"] not in ("main", "borderline"):
            continue
        cat = p["category"]
        ctry = p["country"] or "не определена"
        if cat in top_cats and ctry in top_countries:
            matrix[(cat, ctry)] = matrix.get((cat, ctry), 0.0) + (p["sum"] or 0)
    ws = wb.create_sheet("05b_Страна_по_категориям")
    headers = ["Товарная группа"] + top_countries + ["Итого"]
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = BORDER
    for cat in top_cats:
        row = [cat] + [matrix.get((cat, c), 0.0) for c in top_countries]
        row.append(sum(matrix.get((cat, c), 0.0) for c in top_countries))
        ws.append(row)
    for i in range(2, ws.max_row + 1):
        for j in range(2, len(headers) + 1):
            ws.cell(row=i, column=j).number_format = MONEY
            ws.cell(row=i, column=j).border = BORDER
        ws.cell(row=i, column=1).border = BORDER
    ws.column_dimensions["A"].width = 50
    for j in range(2, len(headers) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 16
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row}"
    add_legend(ws)

    # ---------------------------------------------------------------- 06
    bench = [it for it in items if it.get("price_median") and it["n"] >= 2]
    sheet(
        wb, "06_Бенчмарки",
        ["№", "Номенклатурная позиция", "КТРУ", "ОКПД2", "Ед. изм.", "Количество", "Сумма, ₽",
         "Цена средневзвешенная", "Медиана", "Минимум", "Максимум", "P25", "P75",
         "Позиций", "Поставщиков", "Разброс max/min, %", "Коэф. вариации, %",
         "Отклонение от медианы, %", "Потенциал к медиане, ₽", "Потенциал к минимуму, ₽", "Confidence"],
        [[i, it["name"][:180], it.get("ktru"), it.get("okpd2"), it.get("unit"), it.get("qty"), it["sum"],
          it.get("price_weighted"), it.get("price_median"), it.get("price_min"), it.get("price_max"),
          it.get("price_p25"), it.get("price_p75"), it["n"], it.get("n_suppliers"),
          it.get("price_spread"), it.get("price_cv"),
          (round((it["price_weighted"] / it["price_median"] - 1) * 100, 1)
           if it.get("price_weighted") and it.get("price_median") else None),
          it.get("saving_to_median"), it.get("saving_to_min"),
          it.get("confidence") or "факт"]
         for i, it in enumerate(bench, 1)],
        widths=[5, 66, 18, 14, 10, 12, 18, 16, 12, 12, 12, 12, 12, 9, 11, 14, 14, 16, 18, 18, 12],
        money_cols=(7, 8, 9, 10, 11, 12, 13, 19, 20), pct_cols=(16, 17, 18), int_cols=(1, 6, 14, 15),
        note="Бенчмарки рассчитаны только по закупкам учреждения за 2025 год. Внешние прайсы и другие ЛПУ не используются. "
             "Средневзвешенная цена — по позициям с опубликованным количеством. "
             "Потенциал снижения — оценка, а не гарантия экономии.",
    )
    # условное форматирование бенчмарков: отклонение от медианы и потенциал
    ws6 = wb["06_Бенчмарки"]
    end6 = getattr(ws6, "data_end_row", ws6.max_row)
    ws6.conditional_formatting.add(
        f"R2:R{end6}",
        CellIsRule(operator="greaterThan", formula=["20"], fill=ORANGE_FILL))
    ws6.conditional_formatting.add(
        f"S2:S{end6}",
        CellIsRule(operator="greaterThan", formula=["0"], fill=GREEN_FILL))
    ws6.conditional_formatting.add(
        f"U2:U{end6}",
        FormulaRule(formula=['$U2="оценка"'], fill=ORANGE_FILL, stopIfTrue=False))

    # ---------------------------------------------------------------- 07
    key = items[:30]
    sheet(
        wb, "07_Ключевая_номенклатура",
        ["№", "Номенклатурная позиция", "КТРУ", "ОКПД2", "Товарная группа", "Вид", "Ед. изм.",
         "Количество", "Сумма, ₽", "Доля профиля, %", "Накопленная доля, %", "Позиций", "Поставщиков",
         "Цена средневзвешенная", "Медиана", "Минимум", "Максимум", "Месяцы закупки", "Страна",
         "Товарный знак", "Рег. удостоверение", "Отклонение от медианы, %",
         "Потенциал к медиане, ₽", "Потенциал к минимуму, ₽", "Confidence"],
        [[i, it["name"][:200], it.get("ktru"), it.get("okpd2"), it["category"], cfg_kind(it["kind"]),
          it.get("unit"), it.get("qty"), it["sum"], it["sum"] / (t["sum_scope"] or 1),
          it["cum_share"] / 100, it["n"], it.get("n_suppliers"), it.get("price_weighted"),
          it.get("price_median"), it.get("price_min"), it.get("price_max"),
          ", ".join(it.get("months") or []), it.get("country") or "не определена",
          it.get("trademark") or "—", it.get("ru_number") or "—",
          (round((it["price_weighted"] / it["price_median"] - 1) * 100, 1)
           if it.get("price_weighted") and it.get("price_median") else None),
          it.get("saving_to_median"), it.get("saving_to_min"), it.get("confidence") or "факт"]
         for i, it in enumerate(key, 1)],
        widths=[5, 64, 18, 14, 38, 24, 10, 12, 18, 12, 16, 9, 11, 16, 12, 12, 12, 22, 18,
                28, 20, 16, 18, 18, 12],
        money_cols=(9, 14, 15, 16, 17, 23, 24), pct_cols=(10, 11, 22), int_cols=(1, 8, 12, 13),
        note="Ключевая номенклатура — первые 30 позиций 80 %-набора; полный набор — на листе 04. "
             "Производитель и модель приведены по товарному знаку и регистрационному удостоверению из ЕИС.",
    )

    # ---------------------------------------------------------------- 08
    pos = [p for p in a["positions"] if p["scope"] in ("main", "borderline")]
    extracted = a["meta"].get("extracted_at", "")
    src_name = {"44-ФЗ": "ЕИС, реестр контрактов 44-ФЗ", "223-ФЗ": "ЕИС, реестр договоров 223-ФЗ"}
    registry = []
    for i, p in enumerate(pos, 1):
        norm = norm_name(p["name"])
        l3 = f"{p.get('ktru') or p.get('okpd2') or '—'}|{norm}"
        registry.append([
            f"P{i:06d}",
            # Позиция
            p["name"], norm, p.get("okpd2"), p.get("ktru"),
            p.get("unit"), p.get("unit_norm") or "—", p.get("qty"),
            p.get("unit_price"), p.get("sum"), "—",
            # Классификация
            cfg_kind(p["kind"]), p["category"], l3,
            SCOPE_TITLES.get(p["scope"], p["scope"]), p.get("reason") or "—",
            # Товар
            p.get("country") or "не определена", p.get("country_src") or "—",
            p.get("producer") or "—", p.get("trademark") or "—",
            p.get("model") or "—", p.get("ru_number") or p.get("ru_name") or "—",
            # Поставщик
            p.get("supplier") or "—", p.get("supplier_inn") or "—", "—", "—",
            # Качество
            p.get("mixed") or "нет", "оценка" if p.get("estimated") else "факт",
            p.get("comment") or "—", p.get("pos_src") or "—", "нет",
            # Источник
            p.get("href") or "—", extracted, p.get("month"), p.get("quarter"),
            p.get("method") or "не указан", src_name.get(p.get("source"), p.get("source")),
        ])
    registry_headers = [
        "position_id",
        "Исходное наименование", "Нормализованное наименование", "ОКПД2", "КТРУ",
        "Ед. изм. (исходная)", "Ед. изм. (норм.)", "Количество", "Цена за единицу, ₽",
        "Сумма, ₽", "НДС",
        "Вид (L1)", "Товарная группа (L2)", "Номенклатурная позиция (L3)",
        "Scope", "Причина классификации",
        "Страна", "Источник атрибуции страны", "Производитель", "Бренд / товарный знак",
        "Модель", "Регистрационное удостоверение",
        "Поставщик", "ИНН поставщика", "КПП поставщика", "Регион поставщика",
        "Смешанный лот", "Класс (факт/оценка)", "Комментарий", "Источник атрибуции позиции",
        "Признак дубля",
        "Ссылка на источник", "Дата выгрузки", "Месяц", "Квартал", "Способ закупки",
        "Источник данных",
    ]
    total_registry = [""] * len(registry_headers)
    total_registry[1] = f"Итого: {len(pos)} позиций"
    total_registry[9] = sum(p["sum"] or 0 for p in pos)
    sheet(
        wb, "08_Реестр_позиций",
        registry_headers,
        registry,
        widths=[12, 70, 60, 14, 20, 14, 12, 12, 16, 16, 8,
                26, 40, 56, 12, 26, 18, 34, 34, 26, 26, 30,
                40, 14, 14, 14, 12, 14, 44, 24, 12,
                60, 13, 9, 10, 20, 30],
        money_cols=(9, 10), int_cols=(8,), freeze="B2",
        total_row=total_registry,
        note="Без номеров, дат и предметов контрактов. Одна строка = одна позиция. Пригоден для сводных "
             "таблиц. НДС, КПП и регион поставщика в ЕИС не публикуются — значения «—». "
             "«Ссылка на источник» ведёт на карточку первичной записи ЕИС.",
    )
    ws8 = wb["08_Реестр_позиций"]
    col_class = registry_headers.index("Класс (факт/оценка)") + 1
    col_country = registry_headers.index("Страна") + 1
    col_qty = registry_headers.index("Количество") + 1
    for r in range(2, ws8.max_row):
        if ws8.cell(row=r, column=col_class).value == "оценка":
            ws8.cell(row=r, column=col_class).fill = ORANGE_FILL
        if ws8.cell(row=r, column=col_country).value == "не определена":
            ws8.cell(row=r, column=col_country).fill = YELLOW_FILL
        if ws8.cell(row=r, column=col_qty).value is None:
            ws8.cell(row=r, column=col_qty).fill = YELLOW_FILL
    # условное форматирование: отклонения и пропуски (ТЗ § 9.2)
    end8 = getattr(ws8, "data_end_row", ws8.max_row)
    cl8 = get_column_letter(col_class)
    cc8 = get_column_letter(col_country)
    cq8 = get_column_letter(col_qty)
    ws8.conditional_formatting.add(
        f"{cl8}2:{cl8}{end8}",
        FormulaRule(formula=[f'${cl8}2="оценка"'], fill=ORANGE_FILL, stopIfTrue=False))
    ws8.conditional_formatting.add(
        f"{cc8}2:{cc8}{end8}",
        FormulaRule(formula=[f'${cc8}2="не определена"'], fill=YELLOW_FILL, stopIfTrue=False))
    ws8.conditional_formatting.add(
        f"{cq8}2:{cq8}{end8}",
        FormulaRule(formula=[f"ISBLANK(${cq8}2)"], fill=YELLOW_FILL, stopIfTrue=False))

    # ---------------------------------------------------------------- 09
    exc = [p for p in a["positions"] if p["scope"] == "excluded"]
    sheet(
        wb, "09_Исключения",
        ["№", "Наименование позиции", "ОКПД2", "КТРУ", "Причина исключения", "Вид", "Сумма, ₽", "Доля от всех позиций, %"],
        [[i, p["name"][:200], p.get("okpd2"), p.get("ktru"), p.get("reason") or "—",
          cfg_kind(p["kind"]), p.get("sum"), (p.get("sum") or 0) / (t["sum_all"] or 1)]
         for i, p in enumerate(exc, 1)],
        widths=[5, 70, 14, 20, 26, 30, 16, 18],
        money_cols=(7,), pct_cols=(8,), int_cols=(1,),
        note="Исключения: фармация, хозяйственные расходы, услуги и работы, прочее вне профиля.",
    )

    # ---------------------------------------------------------------- 10
    dup_counter: dict[tuple, int] = {}
    for p in pos:
        key = (p["name"], p.get("okpd2"), p.get("qty"), p.get("unit_price"), p.get("sum"))
        dup_counter[key] = dup_counter.get(key, 0) + 1
    dups = sum(1 for v in dup_counter.values() if v > 1)
    no_country = sum(1 for p in pos if not p.get("country"))
    no_qty = sum(1 for p in pos if not p.get("qty"))
    ws = wb.create_sheet("10_Сверка")
    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 16
    ws.append(["Показатель", "Значение", "Комментарий"])
    for cell in ws[1]:
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.border = BORDER
    rows = [
        ("Сумма профильных позиций", t["sum_scope"], "main + borderline"),
        ("Сумма исключённых позиций", t["sum_excluded"], "фармация, хозяйственные, услуги, прочее"),
        ("Итого по позициям", t["sum_all"], ""),
        ("Сумма цен контрактов", t["sum_contracts"], "по реестрам ЕИС"),
        ("Расхождение", t["reconciliation_diff"], "позиции − контракты"),
        ("Отклонение, %", (t["reconciliation_diff"] / t["sum_contracts"] * 100) if t["sum_contracts"] else 0, "норма — до 1 %"),
        ("Позиций с оценочной суммой", t["positions_estimated"], f"{t['positions_estimated'] / (t['positions_in_scope'] or 1) * 100:.1f} % профиля"),
        ("Позиций без количества", no_qty, "количество не опубликовано в реестре"),
        ("Позиций без страны", no_country, "страна не указана в источнике"),
        ("Групп дублей (наименование + ОКПД2 + количество + цена + сумма)", dups, "проверка на повторные публикации"),
        ("Профильных позиций", t["positions_in_scope"], ""),
        ("Всего позиций", t["positions"], ""),
    ]
    r = 2
    dev_cell = None
    for label, value, comment in rows:
        ws.cell(row=r, column=1, value=label).border = BORDER
        c = ws.cell(row=r, column=2, value=value)
        c.border = BORDER
        c.font = Font(bold=True)
        if isinstance(value, float):
            c.number_format = PCT if "%" in label else MONEY
        else:
            c.number_format = INT
        if label.startswith("Отклонение"):
            dev_cell = f"B{r}"
            if abs(value) > 1:
                c.font = Font(bold=True, color="B4423A")
                c.fill = PatternFill("solid", fgColor="FBE9E7")
        ws.cell(row=r, column=3, value=comment).border = BORDER
        r += 1
    dups_list = sorted(
        ((k, v) for k, v in dup_counter.items() if v > 1), key=lambda kv: -kv[1]
    )[:10]
    if dups_list:
        r += 2
        ws.cell(row=r, column=1, value="Группы дублей (примеры)").font = SUB_FONT
        r += 1
        for i, h in enumerate(["Наименование", "ОКПД2", "Количество", "Цена", "Сумма", "Повторов"], 1):
            c = ws.cell(row=r, column=i, value=h)
            c.fill = HEAD_FILL
            c.font = HEAD_FONT
            c.border = BORDER
        r += 1
        for key, cnt in dups_list:
            name, okpd2, qty, price, total = key
            ws.cell(row=r, column=1, value=(name or "")[:90]).border = BORDER
            ws.cell(row=r, column=2, value=okpd2).border = BORDER
            c = ws.cell(row=r, column=3, value=qty)
            c.number_format = INT
            c.border = BORDER
            c = ws.cell(row=r, column=4, value=price)
            c.number_format = MONEY
            c.border = BORDER
            c = ws.cell(row=r, column=5, value=total)
            c.number_format = MONEY
            c.border = BORDER
            c = ws.cell(row=r, column=6, value=cnt)
            c.number_format = INT
            c.border = BORDER
            r += 1
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:C{len(rows) + 1}"
    add_legend(ws)
    # условное форматирование: отклонение сверки сверх 1 %
    if dev_cell:
        red_font = Font(bold=True, color="B4423A")
        red_fill = PatternFill("solid", fgColor="FBE9E7")
        ws.conditional_formatting.add(dev_cell, CellIsRule(
            operator="greaterThan", formula=["1"], font=red_font, fill=red_fill))
        ws.conditional_formatting.add(dev_cell, CellIsRule(
            operator="lessThan", formula=["-1"], font=red_font, fill=red_fill))

    # ---------------------------------------------------------------- 11
    method = [
        "# Методика",
        "",
        "## 1. Период и учёт",
        "Период: 01.01.2025 — 31.12.2025. Учёт по дате заключения контракта (договора).",
        "Для 223-ФЗ дата размещения использовалась только как окно отбора; в анализ попали договоры с датой заключения в 2025 году.",
        "",
        "## 2. Источники",
        "44-ФЗ: реестр контрактов ЕИС (zakupki.gov.ru/epz/contract/search/results.html).",
        "223-ФЗ: реестр договоров ЕИС (zakupki.gov.ru/epz/contractfz223/search/results.html).",
        "Карточки: вкладки «Платежная информация и объект закупки» (44-ФЗ) и «Предмет договора» (223-ФЗ).",
        "",
        "## 3. Классификатор",
        "L1 — вид закупки: медицинское оборудование; расходные материалы; имплантируемые изделия и металлоконструкции;",
        "лабораторные реагенты и расходные материалы; медицинская мебель и одежда; прочие медицинские товары.",
        "L2 — товарная группа: по ОКПД2 и маркерам наименования.",
        "L3 — номенклатурная позиция: КТРУ + нормализованное наименование.",
        "",
        "## 4. Область (scope)",
        "main — основной медицинский профиль;",
        "borderline — лабораторные реагенты, дезинфекция, медицинская мебель и одежда, запчасти к оборудованию;",
        "excluded — фармация, хозяйственные расходы, услуги и работы, прочее.",
        "",
        "## 5. Нормализация единиц",
        "Единицы приводятся к базовым (шт., мл, г, м, упаковка) с сохранением исходного значения.",
        "В 223-ФЗ единицы приходят в полной форме, в 44-ФЗ — в сокращённой.",
        "",
        "## 6. Дедупликация",
        "Повторные публикации, лоты, дополнительные соглашения и расторжения не создают новых позиций.",
        "Контроль — по номеру реестровой записи и набору «наименование + ОКПД2 + количество + цена + сумма».",
        "",
        "## 7. Страна происхождения",
        "Приоритет — поле страны в контракте/спецификации.",
        "Если поле не заполнено — страна не подставляется по догадке; указывается «не определена».",
        "Для каждой позиции фиксируется источник атрибуции и класс достоверности.",
        "",
        "## 8. Внутренние бенчмарки",
        "Рассчитываются только по закупкам учреждения за 2025 год.",
        "Метрики: средневзвешенная цена, медиана, минимум, максимум, P25, P75, количество закупок и поставщиков,",
        "разброс max/min, коэффициент вариации, потенциал снижения к медиане и минимуму.",
        "Выбросы (ниже P5 или выше P95) анализируются отдельно.",
        "",
        "## 9. Классы достоверности",
        "факт — данные первичного источника без изменений;",
        "оценка — расчётное, агрегированное или неполное значение.",
        "",
        "## 10. Ограничения",
        "Закрытые закупки и закупки, не подлежащие публикации, в реестрах отсутствуют.",
        "Закупки на Портале поставщиков Москвы в ЕИС не публикуются.",
        "Часть контрактов не содержит количества и суммы позиций; суммы распределены по цене контракта (оценка).",
        "Ставка НДС в реестре контрактов не публикуется.",
        "",
        "## 11. Глоссарий",
        "80 %-набор — все группы/позиции до достижения 80 % профильного объёма, а не топ-10.",
        "Профильный объём — сумма позиций main + borderline.",
        "КТРУ — каталог товаров, работ, услуг для обеспечения государственных и муниципальных нужд.",
        "ОКПД2 — общероссийский классификатор продукции по видам экономической деятельности.",
    ]
    text_sheet(wb, "11_Методика", method)

    # ---------------------------------------------------------------- 12
    sources = [
        "# Источники",
        "",
        "## 44-ФЗ",
        "Реестр контрактов ЕИС",
        "https://zakupki.gov.ru/epz/contract/search/results.html",
        f"Поиск: «Боткина», дата заключения 01.01.2025–31.12.2025, все статусы",
        f"Контрактов: {m['contracts_44']:,}".replace(",", " "),
        "",
        "## 223-ФЗ",
        "Реестр договоров ЕИС",
        "https://zakupki.gov.ru/epz/contractfz223/search/results.html",
        f"Поиск: «Боткина», дата размещения 01.11.2024–31.03.2026, затем фильтр по дате заключения 2025",
        f"Договоров: {m['contracts_223']:,}".replace(",", " "),
        "",
        "## Карточки",
        "44-ФЗ: /epz/contract/contractCard/common-info.html?reestrNumber=…",
        "44-ФЗ: /epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=…",
        "223-ФЗ: /epz/contractfz223/card/contract-info.html?reestrNumber=…",
        "223-ФЗ: /epz/contractfz223/card/contract-subject.html?reestrNumber=…",
        "",
        f"Дата выгрузки: {m['extracted_at']}",
        f"Охват: {t['positions_in_scope']:,} профильных позиций, {t['sum_scope']:,.2f} ₽".replace(",", " "),
        "",
        "## Не использовались",
        "Внешние прайс-листы, коммерческие базы, данные других ЛПУ, презентационные материалы.",
    ]
    text_sheet(wb, "12_Источники", sources)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"-> {OUT}")
    print(f"листов: {len(wb.sheetnames)}, позиций в реестре: {len(pos)}")

    # ---------------------------------------------- реестр позиций в CSV
    csv_path = OUT.parent / "Реестр_позиций_Боткина_2025.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
        w.writerow(registry_headers)
        for row in registry:
            w.writerow(["" if v is None else v for v in row])
        w.writerow(total_registry)
        w.writerow([f"Дата выгрузки: {extracted}", f"Источник: {m['sources']}"])
    print(f"-> {csv_path}")

    # ------------------------------- реестр позиций отдельным файлом XLSX
    wb_reg = Workbook()
    wb_reg.remove(wb_reg.active)
    sheet(
        wb_reg, "Реестр_позиций",
        registry_headers, registry,
        widths=[12, 70, 60, 14, 20, 14, 12, 12, 16, 16, 8,
                26, 40, 56, 12, 26, 18, 34, 34, 26, 26, 30,
                40, 14, 14, 14, 12, 14, 44, 24, 12,
                60, 13, 9, 10, 20, 30],
        money_cols=(9, 10), int_cols=(8,), freeze="B2",
        total_row=total_registry,
        note="Полный построчный реестр профильных позиций за 2025 год (основной профиль и "
             "пограничные категории). Одна строка = одна позиция. Без номеров, дат и предметов "
             "контрактов. НДС, КПП и регион поставщика в ЕИС не публикуются — значения «—». "
             "«Ссылка на источник» ведёт на карточку первичной записи ЕИС. "
             f"Дата выгрузки: {extracted}. Источник: {m['sources']}.",
    )
    ws_r = wb_reg["Реестр_позиций"]
    for r in range(2, ws_r.max_row):
        if ws_r.cell(row=r, column=col_class).value == "оценка":
            ws_r.cell(row=r, column=col_class).fill = ORANGE_FILL
        if ws_r.cell(row=r, column=col_country).value == "не определена":
            ws_r.cell(row=r, column=col_country).fill = YELLOW_FILL
        if ws_r.cell(row=r, column=col_qty).value is None:
            ws_r.cell(row=r, column=col_qty).fill = YELLOW_FILL
    end_r = getattr(ws_r, "data_end_row", ws_r.max_row)
    cl_r = get_column_letter(col_class)
    cc_r = get_column_letter(col_country)
    cq_r = get_column_letter(col_qty)
    ws_r.conditional_formatting.add(
        f"{cl_r}2:{cl_r}{end_r}",
        FormulaRule(formula=[f'${cl_r}2="оценка"'], fill=ORANGE_FILL, stopIfTrue=False))
    ws_r.conditional_formatting.add(
        f"{cc_r}2:{cc_r}{end_r}",
        FormulaRule(formula=[f'${cc_r}2="не определена"'], fill=YELLOW_FILL, stopIfTrue=False))
    ws_r.conditional_formatting.add(
        f"{cq_r}2:{cq_r}{end_r}",
        FormulaRule(formula=[f"ISBLANK(${cq_r}2)"], fill=YELLOW_FILL, stopIfTrue=False))
    reg_path = OUT.parent / "Реестр_позиций_Боткина_2025.xlsx"
    wb_reg.save(reg_path)
    print(f"-> {reg_path}")


def cfg_kind(kind: str | None) -> str:
    return KIND_TITLES.get(kind or "", kind or "—")


if __name__ == "__main__":
    build()
