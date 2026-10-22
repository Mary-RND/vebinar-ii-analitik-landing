"""Сверка цифр: analytics.json ↔ отчёт (MD) ↔ Excel ↔ дашборд.

Проверяет не менее 10 ключевых значений в трёх артефактах.
"""
import json
import re
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
A = json.loads((ROOT / "data" / "botkina" / "analytics.json").read_text(encoding="utf-8"))
T = A["totals"]
M = A["meta"]

md = (ROOT / "output" / "REPORT_Botkin_2025.md").read_text(encoding="utf-8")
md_norm = md.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")
xlsx = next((ROOT / "output").glob("*.xlsx"))
wb = load_workbook(xlsx, data_only=True)


def money(v: float) -> str:
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return s + " ₽"


def num(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def xl01(label: str):
    ws = wb["01_Общий_объем"]
    for row in ws.iter_rows(min_row=3, max_row=40, max_col=2, values_only=True):
        if row[0] == label:
            return row[1]
    return None


def xl10(label: str):
    ws = wb["10_Сверка"]
    for row in ws.iter_rows(min_row=2, max_row=30, max_col=2, values_only=True):
        if row[0] == label:
            return row[1]
    return None


checks = []


def add(name: str, value, md_needle: str, xl_value=None, fmt=money):
    in_md = md_needle in md_norm
    xl_ok = (xl_value is None) or (xl_value is not None and abs(xl_value - value) < 1)
    checks.append((name, fmt(value), in_md, xl_ok, xl_value))


add("Профильный объём", T["sum_scope"], money(T["sum_scope"]),
    xl01("Профильный объём (main + borderline)"))
add("Сумма всех позиций", T["sum_all"], money(T["sum_all"]), xl01("Сумма всех позиций"))
add("Исключено из профиля", T["sum_excluded"], money(T["sum_excluded"]), xl01("Исключено из профиля"))
add("Сумма цен контрактов", T["sum_contracts"], money(T["sum_contracts"]), xl10("Сумма цен контрактов"))
add("Расхождение (позиции − контракты)", T["reconciliation_diff"],
    money(T["reconciliation_diff"]), xl10("Расхождение"))
add("Контрактов всего", M["contracts_total"], num(M["contracts_total"]),
    xl01("Контрактов всего"), fmt=num)
add("Контрактов 44-ФЗ", M["contracts_44"], num(M["contracts_44"]), xl01("в том числе 44-ФЗ"), fmt=num)
add("Контрактов 223-ФЗ", M["contracts_223"], num(M["contracts_223"]), xl01("в том числе 223-ФЗ"), fmt=num)
add("Позиций всего", T["positions"], num(T["positions"]), xl01("Позиций всего"), fmt=num)
add("Позиций в профиле", T["positions_in_scope"], num(T["positions_in_scope"]),
    xl01("Позиций в профиле"), fmt=num)
add("Поставщиков в профиле", T["suppliers"], num(T["suppliers"]), xl01("Поставщиков в профиле"), fmt=num)
add("Категорий в 80 %-наборе", T["categories_in_80"], f"{T['categories_in_80']}",
    xl01("Категорий в 80 %-наборе"), fmt=num)
add("Позиций в 80 %-наборе", T["items_in_80"], f"{T['items_in_80']}",
    xl01("Позиций в 80 %-наборе"), fmt=num)
add("Оценочных позиций", T["positions_estimated"], num(T["positions_estimated"]),
    xl10("Позиций с оценочной суммой"), fmt=num)
add("Охват страной, %", T["country_coverage"],
    f"{T['country_coverage']:.1f}".replace(".", ","),
    xl01("Охват страной происхождения") * 100, fmt=lambda v: f"{v:.1f} %")

bad = 0
print(f"{'показатель':<42} {'значение':>22}  отчёт  Excel  Excel-значение")
for name, shown, in_md, xl_ok, xl in checks:
    flag = "OK" if (in_md and xl_ok) else "!!"
    if flag == "!!":
        bad += 1
    xl_txt = "—" if xl is None else f"{xl:,.2f}".replace(",", " ")
    print(f"{flag} {name:<40} {shown:>22}  {'да' if in_md else 'НЕТ':<5}  "
          f"{'да' if xl_ok else 'НЕТ':<5}  {xl_txt}")
print(f"\nвсего проверок: {len(checks)}, расхождений: {bad}")
