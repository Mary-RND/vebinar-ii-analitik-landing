"""Сборка аналитического отчёта в Markdown из analytics.json.

Вход:  data/<slug>/analytics.json
Выход: output/REPORT_Botkin_2025.md

Отчёт описательный: без выводов, рекомендаций и сравнения с другими годами.
Все цифры берутся из analytics.json, чтобы совпадать с Excel и дашбордом.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from classify import KIND_TITLES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = cfg.DEFAULT_LPU
LPU = cfg.get(SLUG)
ANALYTICS = ROOT / "data" / SLUG / "analytics.json"
OUT = ROOT / "output" / "REPORT_Botkin_2025.md"
TOC_PAGES = ROOT / "_probe" / "toc_pages.json"
FIGURES_JSON = ROOT / "output" / "img" / "figures.json"

_FIGS: dict[int, dict] = {}


def load_figures() -> dict[int, dict]:
    """Рисунки отчёта (ТЗ § 7.2: номер, название, источник)."""
    global _FIGS
    if not _FIGS and FIGURES_JSON.exists():
        data = json.loads(FIGURES_JSON.read_text(encoding="utf-8"))
        _FIGS = {int(f["num"]): f for f in data}
    return _FIGS


def figure(num: int) -> str:
    f = load_figures().get(num)
    if not f:
        return ""
    cap = f"Рисунок {num} — {f['title']}. Источник: {f['source']}."
    return f"![{cap}]({f['file']})"

MONTHS = {
    "01": "январь", "02": "февраль", "03": "март", "04": "апрель",
    "05": "май", "06": "июнь", "07": "июль", "08": "август",
    "09": "сентябрь", "10": "октябрь", "11": "ноябрь", "12": "декабрь",
}


# --------------------------------------------------------------------- формат
def plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def money(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    s = f"{v:,.{digits}f}".replace(",", "\u00a0").replace(".", ",")
    return f"{s}\u00a0₽"


def mln(v: float | None, digits: int = 1) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1e9:
        s = f"{v / 1e9:.{digits}f}".replace(".", ",")
        return f"{s}\u00a0млрд\u00a0₽"
    if abs(v) >= 1e6:
        s = f"{v / 1e6:.{digits}f}".replace(".", ",")
        return f"{s}\u00a0млн\u00a0₽"
    if abs(v) >= 1e3:
        s = f"{v / 1e3:.0f}".replace(".", ",")
        return f"{s}\u00a0тыс.\u00a0₽"
    return f"{v:.0f}\u00a0₽"


def pct(v: float | None, digits: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v:.{digits}f}".replace(".", ",") + "\u00a0%"


def num(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:,.0f}".replace(",", "\u00a0")


def month_label(m: str | None) -> str:
    if not m:
        return "—"
    y, mm = m.split("-")
    return f"{MONTHS.get(mm, mm)} {y}"


def short(s: str | None, n: int = 80) -> str:
    s = (s or "—").replace("|", "/").replace("\n", " ")
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def cell(v) -> str:
    return str(v).replace("|", "/").replace("\n", " ")


def table(headers: list[str], rows: list[list], align: list[str] | None = None) -> str:
    sep = []
    for i in range(len(headers)):
        a = (align[i] if align and i < len(align) else "left")
        sep.append({"left": ":---", "right": "---:", "center": ":---:"}[a])
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(sep) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return "\n".join(out)


def top_by(d: dict[str, float], n: int) -> list[tuple[str, float]]:
    return sorted(d.items(), key=lambda kv: -kv[1])[:n]


def cap(num_id: str, title: str, meta: dict, units: str = "") -> str:
    """Подпись таблицы: номер, название, единицы измерения, период, источник (ТЗ § 7.2)."""
    line = []
    if units:
        line.append(f"Единицы измерения: {units}.")
    line.append(f"Период: {meta['period']}.")
    line.append(f"Источник: {meta['sources']}.")
    return "\n".join([f"**Таблица {num_id}. {title}**", "", " ".join(line)])


# --------------------------------------------------------------------- данные
def build(pages: dict[str, int] | None = None) -> str:
    a = json.loads(ANALYTICS.read_text(encoding="utf-8"))
    m, t = a["meta"], a["totals"]
    positions = a["positions"]
    in_scope = [p for p in positions if p["scope"] in ("main", "borderline")]
    items = a["items"]
    items80 = [i for i in items if i.get("in_80")]
    cat80 = [c for c in a["by_category"] if c.get("in_80")]
    scope_sum = t["sum_scope"] or 1.0
    items80_sum = sum(i["sum"] for i in items80) or 1.0

    # агрегаты, которых нет в analytics.json
    kind_cat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    kind_items: dict[str, list[dict]] = defaultdict(list)
    kind_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for p in in_scope:
        kind_cat[p["kind"]][p["category"]] += p["sum"] or 0
        kind_month[p["kind"]][p["month"] or "—"] += p["sum"] or 0
    for it in items:
        kind_items[it["kind"]].append(it)

    cat_suppliers: dict[str, set[str]] = defaultdict(set)
    cat_sup_sum: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    cat_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    name_country: dict[str, set[str]] = defaultdict(set)
    cat_country: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    country_cats: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    country_est: dict[str, int] = defaultdict(int)
    for p in in_scope:
        cat_suppliers[p["category"]].add(p.get("supplier") or "—")
        cat_sup_sum[p["category"]][p.get("supplier") or "—"] += p["sum"] or 0
        cat_month[p["category"]][p["month"] or "—"] += p["sum"] or 0
        cat_country[p["category"]][p["country"] or "не определена"] += p["sum"] or 0
        country_cats[p["country"] or "не определена"][p["category"]] += p["sum"] or 0
        if p.get("estimated"):
            country_est[p["country"] or "не определена"] += 1
        if p.get("country"):
            name_country[p["name"]].add(p["country"])

    bench = [i for i in items80 if i.get("n", 0) >= 2 and i.get("price_median")]
    bench.sort(key=lambda x: -x["sum"])
    with_spread = [i for i in bench if i.get("price_spread") is not None]
    high_spread = [i for i in with_spread if i["price_spread"] > 100]
    mid_spread = [i for i in with_spread if 30 < i["price_spread"] <= 100]

    def cat_comment(c: dict) -> str:
        """Короткий комментарий к товарной группе (ТЗ § 6.3, столбец «Комментарий»)."""
        name = c["category"]
        total = c["sum"] or 1.0
        parts: list[str] = []
        cc = cat_country.get(name, {})
        ru_s = cc.get("Россия", 0.0)
        unknown = cc.get("не определена", 0.0)
        imp = sum(v for k, v in cc.items() if k not in ("Россия", "не определена"))
        if imp / total > 0.5:
            parts.append(f"импортные закупки — {pct(imp / total * 100)} объёма")
        elif ru_s / total > 0.8:
            parts.append("преимущественно российское производство")
        sup = cat_sup_sum.get(name, {})
        if sup:
            top_s, top_v = max(sup.items(), key=lambda kv: kv[1])
            if top_v / total > 0.3:
                parts.append(f"концентрация: TOP-1 поставщик — {pct(top_v / total * 100)} объёма")
        if unknown / total > 0.05:
            parts.append(f"страна не указана для {pct(unknown / total * 100)} объёма")
        if c.get("main_sum", 0) == 0:
            parts.append("группа пограничная")
        if not parts:
            parts.append(f"{num(c['n'])} позиций, {num(c['suppliers'])} поставщиков")
        return "; ".join(parts)

    L: list[str] = []
    add = L.append

    # ------------------------------------------------------------------ обложка
    add("# Анализ закупок медицинских товаров")
    add("## МНКЦ им. С.П. Боткина, 2025 год")
    add("")
    add("| Параметр | Значение |")
    add("|---|---|")
    add(f"| Заказчик | {m.get('customer_full') or m['customer']} |")
    add(f"| ИНН / КПП | {m['inn']} / {m['kpp']} |")
    add(f"| Период | {m['period']} |")
    add(f"| Учёт | по дате заключения контракта (договора) |")
    add(f"| Источники | {m['sources']} |")
    add(f"| Дата выгрузки | {m['extracted_at']} |")
    add(f"| Версия | 1.0 |")
    add("")
    add(
        "**Расшифровка классов достоверности.** *Факт* — данные первичного источника ЕИС без "
        "изменений. *Оценка* — расчётное, агрегированное или неполное значение (например, сумма "
        "позиции, распределённая по цене контракта, если количество не опубликовано). Оценочные "
        "значения не предназначены для официальной отчётности."
    )
    add("")
    add("---")
    add("")

    # ------------------------------------------------------------------ содержание
    toc = [
        ("1", "Основные показатели"),
        ("2", "Методика и источники"),
        ("3", "Общий объём закупок"),
        ("4", "Структура по видам закупок"),
        ("5", "Категории по правилу 80 %"),
        ("6", "Номенклатура по правилу 80 %"),
        ("7", "Страна происхождения"),
        ("8", "Внутренние ценовые бенчмарки"),
        ("9", "Ключевая номенклатура"),
        ("10", "Приложения"),
    ]
    add("## Содержание")
    add("")
    for n, title in toc:
        pg = pages.get(f"{n}. {title}") if pages else None
        suffix = f" — стр. {pg}" if pg else ""
        add(f"- **{n}.** {title}{suffix}")
    add("")
    add("[[pagebreak]]")
    add("")

    # ------------------------------------------------------------------ 1
    add("## 1. Основные показатели")
    add("")
    add(
        f"В 2025 году по дате заключения учтено {num(m['contracts_total'])} "
        f"{plural(m['contracts_total'], 'контракт и договор', 'контракта и договора', 'контрактов и договоров')}, "
        f"в том числе {num(m['contracts_44'])} по 44-ФЗ и {num(m['contracts_223'])} по 223-ФЗ. "
        f"Профильные медицинские товары присутствуют в {num(m['contracts_in_scope'])} "
        f"{plural(m['contracts_in_scope'], 'контракте', 'контрактах', 'контрактах')}."
    )
    add("")
    add(
        f"Суммарный объём профильных позиций — {money(t['sum_scope'])} "
        f"({pct(t['sum_scope'] / (t['sum_all'] or 1) * 100)} от суммы всех позиций). "
        f"Основной профиль формирует {money(t['sum_main'])}, пограничные категории — "
        f"{money(t['sum_borderline'])}. Исключённые позиции (фармация, хозяйственные расходы, "
        f"услуги и работы) — {money(t['sum_excluded'])}."
    )
    add("")
    kpi = [
        ("Контрактов и договоров всего", num(m["contracts_total"])),
        ("в том числе 44-ФЗ", num(m["contracts_44"])),
        ("в том числе 223-ФЗ", num(m["contracts_223"])),
        ("Контрактов с профильными товарами", num(m["contracts_in_scope"])),
        ("Профильный объём", money(t["sum_scope"])),
        ("в том числе основной профиль", money(t["sum_main"])),
        ("в том числе пограничные категории", money(t["sum_borderline"])),
        ("Исключённые позиции", money(t["sum_excluded"])),
        ("Позиций всего", num(t["positions"])),
        ("Позиций в профиле", num(t["positions_in_scope"])),
        ("Поставщиков в профиле", num(t["suppliers"])),
        ("Медиана цены контракта", money(t["median_contract"])),
        ("Средняя сумма позиции", money(t["avg_position"])),
        ("Медианная сумма позиции", money(t["median_position"])),
        ("Категорий в 80 %-наборе", f"{num(t['categories_in_80'])} из {num(t['categories_total'])}"),
        ("Позиций в 80 %-наборе", f"{num(t['items_in_80'])} из {num(t['items_total'])}"),
        ("Охват страной происхождения", pct(t["country_coverage"])),
    ]
    add(cap("1.1", "Основные показатели закупок МНКЦ им. С.П. Боткина за 2025 год", m,
            "₽, шт., %, шт./поз."))
    add("")
    add(table(["Показатель", "Значение"], [[k, v] for k, v in kpi], ["left", "right"]))
    add("")
    add("Примечания: показатели рассчитаны по позициям закупок (единица учёта — позиция). "
        "Медиана и средняя сумма позиции — по профильным позициям; "
        "счётчик поставщиков относится к контрактам 44-ФЗ (в реестре договоров 223-ФЗ "
        "ЕИС не публикует поставщика).")
    by_kind_top = sorted(a["by_kind"], key=lambda k: -k["sum"])[:3]
    add("**Структура.** Наибольшие виды: " + "; ".join(
        f"{k['title'].lower()} — {mln(k['sum'])} ({pct(k['share'])} профиля)" for k in by_kind_top
    ) + ".")
    add("")
    cat_top = cat80[:3]
    add("**80 %-набор.** Профильный объём концентрируется в " + "; ".join(
        f"группе «{c['category']}» — {mln(c['sum'])} ({pct(c['share'])})" for c in cat_top
    ) + ". " + (
        f"Всего в набор входят {num(len(cat80))} {plural(len(cat80), 'группа', 'группы', 'групп')} "
        f"и {num(len(items80))} {plural(len(items80), 'позиция', 'позиции', 'позиций')}."
    ))
    add("")
    ru = next((c["sum"] for c in a["by_country"] if c["country"] == "Россия"), 0.0)
    add(
        f"**Страна происхождения.** Россия — {mln(ru)} ({pct(ru / (t['sum_country_known'] or 1) * 100)} "
        f"объёма с указанной страной), импорт — {mln(t['sum_country_known'] - ru)}. "
        f"Страна не указана для {mln(t['sum_country_unknown'])} ({pct(100 - t['country_coverage'])} профиля)."
    )
    add("")
    add(
        f"**Цены.** Медиана цены контракта — {money(t['median_contract'])}, "
        f"средняя сумма позиции — {money(t['avg_position'])}, медианная — {money(t['median_position'])}. "
        f"Бенчмарки рассчитаны по {num(len(bench))} {plural(len(bench), 'позиции', 'позициям', 'позициям')} "
        f"80 %-набора с двумя и более закупками."
    )
    add("")

    # ------------------------------------------------------------------ 2
    add("## 2. Методика и источники")
    add("")
    add("### 2.1. Период и единица учёта")
    add("")
    add(
        "Период анализа — 01.01.2025–31.12.2025. Единица учёта — контракт (договор) по дате заключения. "
        "Для 223-ФЗ дата размещения использовалась только как окно отбора; в выборку попали договоры "
        "с датой заключения в 2025 году. Позиция контракта — отдельная строка спецификации; "
        "если спецификация не опубликована, сумма распределяется по цене контракта и помечается как оценка."
    )
    add("")
    add("### 2.2. Источники")
    add("")
    add(
        "44-ФЗ — реестр контрактов ЕИС (zakupki.gov.ru/epz/contract/search/results.html), карточки "
        "«Общая информация» и «Платёжная информация и объект закупки». 223-ФЗ — реестр договоров ЕИС "
        "(zakupki.gov.ru/epz/contractfz223/search/results.html), карточки «Информация о договоре» и "
        "«Предмет договора». Поиск вёлся по наименованию заказчика с проверкой ИНН, КПП и ОГРН; "
        "одноимённые учреждения в других регионах исключены."
    )
    add("")
    add(
        "Параметры выборки. 44-ФЗ: строка поиска «Боткина» с морфологией, признак «закупки по 44-ФЗ», "
        "все публикуемые этапы контракта, интервал даты заключения 01.01.2025 – 31.12.2025, сортировка "
        "по дате обновления, постраничный обход реестра. 223-ФЗ: строка поиска «Боткина» с морфологией, "
        "интервал даты размещения 01.01.2025 – 31.12.2025 с последующим отбором по дате заключения "
        "2025 года, постраничный обход реестра. Отбор заказчика — по совпадению ИНН 7714082636 и "
        "КПП 771401001; записи с другими реквизитами отброшены. Из каждой карточки извлекались "
        "цена и дата заключения, поставщик, способ закупки и позиции с количеством, ценой за единицу, "
        "суммой, ОКПД2, КТРУ и страной происхождения."
    )
    add("")
    add("### 2.3. Область анализа")
    add("")
    add(
        "main — основной медицинский профиль: медицинское оборудование, расходные материалы, "
        "имплантируемые изделия и металлоконструкции, прочие медицинские товары. "
        "borderline — лабораторные реагенты, дезинфекция, медицинская мебель и одежда, "
        "запчасти к оборудованию. excluded — фармация, хозяйственные расходы, услуги и работы, "
        "прочее вне профиля. Профильный объём — сумма main и borderline."
    )
    add("")
    add("### 2.4. Классификатор")
    add("")
    add(
        "Три уровня: L1 — вид закупки (шесть укрупнённых видов и отдельно пограничные категории, "
        "§ 6.2 ТЗ); L2 — товарная группа по ОКПД2 "
        "и маркерам наименования; L3 — номенклатурная позиция (КТРУ + нормализованное наименование). "
        "Каждая позиция получает вид, группу, область и признак достоверности. Правила классификации "
        "и полный перечень групп приведены в приложении Б."
    )
    add("")
    add("### 2.5. Нормализация и дедупликация")
    add("")
    add(
        "Единицы измерения приводятся к базовым (шт., мл, г, м, упаковка) с сохранением исходного "
        "значения. Повторные публикации, лоты, дополнительные соглашения и расторжения не создают "
        "новых позиций. Контроль — по номеру реестровой записи и набору «наименование + ОКПД2 + "
        "количество + цена + сумма». Контрактная детализация (номера, даты, предметы, цены контрактов) "
        "в результат не выводится."
    )
    add("")
    add("### 2.6. Страна происхождения")
    add("")
    add(
        "Приоритет — поле страны в контракте или спецификации. Если поле не заполнено, страна не "
        "подставляется по догадке и указывается как «не определена». Для каждой позиции фиксируется "
        "источник атрибуции; охват страной показан в разделе 7 и в паспорте данных."
    )
    add("")
    add("### 2.7. Внутренние бенчмарки")
    add("")
    add(
        "Рассчитываются только по закупкам учреждения за 2025 год: средневзвешенная цена, медиана, "
        "минимум, максимум, P25, P75, количество закупок и поставщиков, разброс max/min, коэффициент "
        "вариации, расчётная разница к медиане и минимуму. Средневзвешенная цена считается по позициям "
        "с опубликованным количеством; оценочные суммы в расчёт не входят. Внешние прайс-листы и "
        "данные других учреждений не используются."
    )
    add("")
    add("### 2.8. Классы достоверности и ограничения")
    add("")
    add(
        "«Факт» — данные первичного источника без изменений. «Оценка» — расчётное, агрегированное "
        "или неполное значение; оценочные позиции помечены в реестре. Закрытые закупки и закупки, "
        "не подлежащие публикации, в реестрах отсутствуют; закупки на Портале поставщиков Москвы "
        "в ЕИС не публикуются. Часть контрактов не содержит количества и суммы позиций; ставка НДС "
        "в реестре контрактов не публикуется, поэтому не рассчитывается. Полный паспорт данных — "
        "в приложении В."
    )
    add("")
    add(
        f"Отдельно ограничение по поставщикам: в реестре договоров 223-ФЗ ЕИС не публикует "
        f"наименование и ИНН поставщика — ни в карточке договора, ни в печатной форме, ни в "
        f"реестре. Поэтому для {num(t['positions_supplier_unknown'])} позиций 223-ФЗ "
        f"({money(t['sum_supplier_unknown'])}, {pct(t['share_supplier_unknown'])} профиля) "
        f"поставщик указан как «{m.get('supplier_unknown') or 'не указан в ЕИС (реестр 223-ФЗ)'}». "
        f"Число поставщиков профиля ({num(t['suppliers'])}) относится к контрактам 44-ФЗ, где "
        f"реквизиты поставщика опубликованы."
    )
    add("")

    # ------------------------------------------------------------------ 3
    add("## 3. Общий объём закупок")
    add("")
    add(
        f"Сумма всех позиций за 2025 год — {money(t['sum_all'])}, из них профильных — "
        f"{money(t['sum_scope'])} ({pct(t['sum_scope'] / (t['sum_all'] or 1) * 100)}). "
        f"Разница между суммой позиций и суммой цен контрактов — {money(t['reconciliation_diff'])} "
        f"({pct(t['reconciliation_diff'] / (t['sum_contracts'] or 1) * 100)}), что связано с "
        f"округлениями и неопубликованными спецификациями."
    )
    add("")
    add("### 3.1. По источникам")
    add("")
    rows = []
    for s in a["by_source"]:
        rows.append([
            s["source"],
            num(s["n"]),
            money(s["sum"]),
            pct(s["sum"] / scope_sum * 100),
        ])
    rows.append(["Итого", num(t["positions_in_scope"]), money(t["sum_scope"]), "100,0 %"])
    add(cap("3.1", "Профильный объём закупок по источникам данных", m, "₽, позиции, %"))
    add("")
    add(table(["Источник", "Позиций", "Сумма", "Доля профиля"], rows, ["left", "right", "right", "right"]))
    add("")
    add("Примечания: учёт — по дате заключения контракта (договора); "
        "доля рассчитана от профильного объёма.")
    add(
        f"44-ФЗ: {num(m['contracts_44'])} "
        f"{plural(m['contracts_44'], 'контракт', 'контракта', 'контрактов')}; "
        f"223-ФЗ: {num(m['contracts_223'])} "
        f"{plural(m['contracts_223'], 'договор', 'договора', 'договоров')}. "
        f"Позиции 223-ФЗ составляют {pct(next((s['sum'] for s in a['by_source'] if s['source'] == '223-ФЗ'), 0) / scope_sum * 100)} "
        f"профильного объёма."
    )
    add("")
    add("### 3.2. По кварталам")
    add("")
    rows = []
    for q in a["by_quarter"]:
        rows.append([q["quarter"], num(q["n"]), money(q["sum"]), pct(q["sum"] / scope_sum * 100)])
    add(cap("3.2", "Профильный объём закупок по кварталам 2025 года", m, "₽, позиции, %"))
    add("")
    add(table(["Квартал", "Позиций", "Сумма", "Доля профиля"], rows, ["left", "right", "right", "right"]))
    add("")
    add("Примечания: квартал определяется по дате заключения контракта (договора).")
    if figure(1):
        add(figure(1))
        add("")
    add("По месяцам объём распределён неравномерно: " + "; ".join(
        f"{month_label(mo['month'])} — {mln(mo['sum'])}" for mo in sorted(a["by_month"], key=lambda x: -x["sum"])[:3]
    ) + ".")
    add("")
    add("### 3.3. По размеру контрактов")
    add("")
    total_contracts = sum(b["contracts"] for b in a["by_size"]) or 1
    rows = []
    for b in a["by_size"]:
        rows.append([
            b["bucket"], num(b["contracts"]), pct(b["contracts"] / total_contracts * 100),
            money(b["sum"]), money(b["scope_sum"]),
        ])
    add(cap("3.3", "Распределение закупок по цене контракта", m, "₽, контракты, %"))
    add("")
    add(table(["Цена контракта", "Контрактов", "Доля по количеству", "Сумма контрактов", "Профильные позиции"],
              rows, ["left", "right", "right", "right", "right"]))
    add("")
    add("Примечания: границы ценовых групп заданы исполнителем для описания распределения; "
        "последняя группа — все контракты дороже верхней границы.")
    add(
        f"Медиана цены контракта — {money(t['median_contract'])}, средняя — {money(t['mean_contract'])}, "
        f"максимальная — {money(t['max_contract'])}. Средний срок исполнения — "
        f"{num(t['avg_term_days'])} {plural(t['avg_term_days'] or 0, 'день', 'дня', 'дней')}."
    )
    add("")
    add("### 3.4. Сверка")
    add("")
    add(
        f"Профильные позиции ({money(t['sum_scope'])}) и исключённые ({money(t['sum_excluded'])}) "
        f"в сумме дают {money(t['sum_all'])} — общее значение по всем позициям; отклонение от суммы "
        f"профиля и исключений равно нулю. Отдельно сумма всех позиций сопоставлена с суммой цен "
        f"контрактов ({money(t['sum_contracts'])}): расхождение — {money(t['reconciliation_diff'])}, "
        f"или {pct(abs(t['reconciliation_diff']) / (t['sum_contracts'] or 1) * 100)}. "
        f"Оценочные позиции: {num(t['positions_estimated'])} "
        f"({pct(t['positions_estimated'] / (t['positions_in_scope'] or 1) * 100)} профиля). "
        f"Смешанных контрактов, где вместе с товарами закупаются услуги, — {num(t['mixed_contracts'])}; "
        f"они разделены по позициям, услуги исключены."
    )
    add("")
    add(
        f"Сверка с первичным источником выполнена по всем {num(m['contracts_total'])} контрактам и "
        f"договорам, а не по выборке: сумма позиций каждого контракта сопоставлена с ценой контракта "
        f"в карточке ЕИС. Расхождений не выявлено — итоговое расхождение "
        f"{money(t['reconciliation_diff'])}. Дополнительно по 26 контрактам с неполной спецификацией "
        f"выполнена дозагрузка позиций с ценами из платёжной информации; до дозагрузки расхождение "
        f"составляло около 561 млн ₽ (5,6 % общей суммы), после — {money(t['reconciliation_diff'])}."
    )
    add("")

    # ------------------------------------------------------------------ 4
    add("## 4. Структура по видам закупок")
    add("")
    add(
        "Виды выделены по § 6.2 ТЗ. Сумма и доля считаются по профильному объёму; пограничные виды "
        "включены в общую структуру и отмечены в таблице."
    )
    add("")
    rows = []
    for i, k in enumerate(a["by_kind"], 1):
        rows.append([
            i, k["title"], money(k["sum"]), pct(k["share"]), num(k["n"]), num(k["suppliers"]),
            money(k["avg_position"]),
            "пограничный" if k["scope"] == "borderline" else "основной",
        ])
    border = [p for p in in_scope if p["scope"] == "borderline"]
    b_sum = sum(p["sum"] or 0 for p in border)
    b_sup = len({p.get("supplier") for p in border if p.get("supplier")})
    b_avg = b_sum / len(border) if border else 0
    rows.append(["", "Итого", money(t["sum_scope"]), "100,0 %", num(t["positions_in_scope"]),
                 num(t["suppliers"]), money(t["avg_position"]), ""])
    rows.append(["", "В том числе пограничные категории (справочно)", money(b_sum),
                 pct(b_sum / (t["sum_scope"] or 1) * 100), num(len(border)), num(b_sup),
                 money(b_avg), "справочно"])
    add(cap("4.1", "Структура профильных закупок по видам", m, "₽, позиции, %, поставщики"))
    add("")
    add(table(["№", "Вид", "Сумма", "Доля", "Позиций", "Поставщиков", "Средняя позиция", "Область"],
              rows, ["right", "left", "right", "right", "right", "right", "right", "left"]))
    add("")
    add("Примечания: строка «в том числе пограничные категории» — справочная, её сумма уже учтена "
        "в видах выше и не суммируется с итогом. Счётчик поставщиков относится к контрактам 44-ФЗ.")
    add("Строка «в том числе пограничные» справочная: её сумма уже учтена в видах выше и не суммируется с итогом. "
        "Без пограничных категорий профильный объём составляет " + money(t["sum_main"]) + ".")
    add("")
    if figure(2):
        add(figure(2))
        add("")
    for k in a["by_kind"]:
        cats = top_by(kind_cat[k["kind"]], 3)
        its = kind_items[k["kind"]][:3]
        months = top_by(kind_month[k["kind"]], 2)
        add(f"### 4.{a['by_kind'].index(k) + 1}. {k['title']}")
        add("")
        add(
            f"Объём — {money(k['sum'])} ({pct(k['share'])} профиля), {num(k['n'])} "
            f"{plural(k['n'], 'позиция', 'позиции', 'позиций')}, {num(k['suppliers'])} "
            f"{plural(k['suppliers'], 'поставщик', 'поставщика', 'поставщиков')}; средняя сумма позиции — "
            f"{money(k['avg_position'])}."
        )
        add("")
        if cats:
            add("Ведущие товарные группы: " + "; ".join(
                f"«{c}» — {mln(v)} ({pct(v / (k['sum'] or 1) * 100)})" for c, v in cats
            ) + ".")
            add("")
        if its:
            add("Крупнейшие позиции: " + "; ".join(
                f"{short(i['name'], 70)} — {mln(i['sum'])}" for i in its
            ) + ".")
            add("")
        if months:
            add("Основные месяцы закупки: " + "; ".join(
                f"{month_label(mo)} — {mln(v)}" for mo, v in months
            ) + ".")
            add("")

    # ------------------------------------------------------------------ 5
    add("### 4.7. Пограничные категории (справочно)")
    add("")
    add(
        f"К пограничным отнесены лабораторные реагенты и расходные материалы, медицинская мебель "
        f"и одежда, а также отдельные спорные группы. Их сумма — {money(b_sum)} "
        f"({pct(b_sum / (t['sum_scope'] or 1) * 100)} профиля), {num(len(border))} "
        f"{plural(len(border), 'позиция', 'позиции', 'позиций')}, {num(b_sup)} "
        f"{plural(b_sup, 'поставщик', 'поставщика', 'поставщиков')}. Эти позиции уже входят в виды "
        f"выше; строка приводится для оценки «чистого» профиля."
    )
    add("")
    bc: dict[str, float] = {}
    for p in border:
        bc[p["category"]] = bc.get(p["category"], 0) + (p["sum"] or 0)
    bc_rows = [[c, money(v), pct(v / (b_sum or 1) * 100)]
               for c, v in sorted(bc.items(), key=lambda kv: -kv[1])]
    add(cap("4.2", "Пограничные категории в разрезе товарных групп", m, "₽, %"))
    add("")
    add(table(["Товарная группа", "Сумма", "Доля пограничных"], bc_rows,
              ["left", "right", "right"]))
    add("")
    add("Примечания: доля рассчитана от суммы пограничных позиций; эти позиции входят в общий "
        "объём профиля и выделены признаком scope = borderline.")
    add(f"Без пограничных категорий профильный объём — {money(t['sum_main'])} "
        f"({pct(t['sum_main'] / (t['sum_scope'] or 1) * 100)} профиля).")
    add("")

    # ------------------------------------------------- 4.8 способы закупки
    add("### 4.8. Разрез по способу закупки")
    add("")
    add(
        "Профильный объём в разрезе способа закупки и закона (44-ФЗ / 223-ФЗ). Способ закупки "
        "указан в карточке контракта; для части записей поле не заполнено — такие позиции "
        "отнесены к строке «не указан»."
    )
    add("")
    ms: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    mn: dict[str, int] = defaultdict(int)
    for p in in_scope:
        key = p.get("method") or "не указан"
        ms[key][p.get("source") or "—"] += p.get("sum") or 0
        mn[key] += 1
    m_rows = []
    for key, by_src in sorted(ms.items(), key=lambda kv: -sum(kv[1].values())):
        s44 = by_src.get("44-ФЗ", 0.0)
        s223 = by_src.get("223-ФЗ", 0.0)
        tot = s44 + s223
        m_rows.append([
            key, money(s44), money(s223), money(tot), pct(tot / (t["sum_scope"] or 1) * 100), num(mn[key]),
        ])
    tot44 = sum(by_src.get("44-ФЗ", 0.0) for by_src in ms.values())
    tot223 = sum(by_src.get("223-ФЗ", 0.0) for by_src in ms.values())
    m_rows.append([
        "Итого", money(tot44), money(tot223), money(tot44 + tot223),
        pct((tot44 + tot223) / (t["sum_scope"] or 1) * 100), num(t["positions_in_scope"]),
    ])
    add(cap("4.3", "Профильный объём в разрезе способа закупки и закона", m, "₽, позиции, %"))
    add("")
    add(table(["Способ закупки", "44-ФЗ", "223-ФЗ", "Итого", "Доля", "Позиций"], m_rows,
              ["left", "right", "right", "right", "right", "right"]))
    add("")
    add("Примечания: способ закупки указан в карточке контракта ЕИС; для части записей поле "
        "не заполнено — такие позиции отнесены к строке «не указан». "
        "Карточки контрактов, номера и даты в отчёт не выводятся.")

    # ------------------------------------------------------------------ 5
    add("## 5. Категории по правилу 80 %")
    add("")
    add(
        "Правило 80 % применено к товарным группам: группы отсортированы по сумме, в набор включаются "
        "все группы до достижения 80 % профильного объёма. Это не фиксированный топ-10; группы с равной "
        "суммой на границе включаются вместе. Группы за пределами набора приведены в Excel и дашборде."
    )
    add("")
    rows = []
    for i, c in enumerate(a["by_category"], 1):
        rows.append([
            i, c["category"], money(c["sum"]), pct(c["share"]), pct(c["cum_share"]),
            num(c["n"]), num(c["suppliers"]), money(c["avg_position"]),
            "да" if c["in_80"] else "нет",
            cat_comment(c),
        ])
    add(cap("5.1", "Товарные группы 80 %-набора: объём, накопленная доля и характеристика группы",
            m, "₽, позиции, %, поставщики"))
    add("")
    add(table(["№", "Товарная группа", "Сумма", "Доля", "Накопленно", "Позиций", "Поставщиков",
               "Средняя позиция", "В 80 %", "Комментарий"], rows,
              ["right", "left", "right", "right", "right", "right", "right", "right", "center", "left"]))
    add("")
    add("Примечания: правило 80 % — в таблицу включены все товарные группы до достижения 80 % "
        "профильного объёма, а не фиксированный «топ-10»; группы с равной суммой на границе "
        "включены вместе. Столбец «Комментарий» — краткая характеристика группы "
        "(импортозависимость, концентрация поставщика, состояние атрибуции страны). "
        "Суммы и доли — по позициям профиля.")
    add(
        f"В 80 %-набор входят {num(len(cat80))} {plural(len(cat80), 'группа', 'группы', 'групп')} "
        f"с суммарным объёмом {money(sum(c['sum'] for c in cat80))} "
        f"({pct(sum(c['sum'] for c in cat80) / scope_sum * 100)} профиля)."
    )
    add("")
    if figure(3):
        add(figure(3))
        add("")
    for i, c in enumerate(cat80, 1):
        cats_items = [it for it in items if it["category"] == c["category"]][:4]
        months = top_by(cat_month[c["category"]], 2)
        share_main = c["main_sum"] / (c["sum"] or 1) * 100
        add(f"### 5.{i}. {c['category']}")
        add("")
        add(
            f"Сумма — {money(c['sum'])} ({pct(c['share'])} профиля; накопленная доля — {pct(c['cum_share'])}), "
            f"{num(c['n'])} {plural(c['n'], 'позиция', 'позиции', 'позиций')}, "
            f"{num(c['suppliers'])} {plural(c['suppliers'], 'поставщик', 'поставщика', 'поставщиков')}; "
            f"средняя сумма позиции — {money(c['avg_position'])}. Основной профиль — {pct(share_main)}, "
            f"пограничные позиции — {pct(100 - share_main)}."
        )
        add("")
        if cats_items:
            add("Ведущие позиции: " + "; ".join(
                f"{short(it['name'], 70)} — {mln(it['sum'])}" for it in cats_items
            ) + ".")
            add("")
        tops = sorted(cat_sup_sum[c["category"]].items(), key=lambda kv: -kv[1])[:3]
        if tops:
            add("Поставщики: " + "; ".join(
                f"{short(s, 55)} — {mln(v)} ({pct(v / (c['sum'] or 1) * 100)})" for s, v in tops
            ) + ".")
            add("")
        if months:
            add("Основные месяцы: " + "; ".join(f"{month_label(mo)} — {mln(v)}" for mo, v in months) + ".")
            add("")

    # ------------------------------------------------------------------ 6
    add("## 6. Номенклатура по правилу 80 %")
    add("")
    add(
        "Правило 80 % применено к номенклатурным позициям: позиции отсортированы по сумме, в набор "
        "включаются все позиции до достижения 80 % профильного объёма. Позиции с одинаковой суммой "
        "на границе включаются вместе. Полный набор приведён в приложении Д."
    )
    add("")
    top10 = sum(i["sum"] for i in items80[:10]) / items80_sum * 100
    top50 = sum(i["sum"] for i in items80[:50]) / items80_sum * 100
    single = sum(1 for i in items80 if i["n"] == 1)
    multi_sup = sum(1 for i in items80 if (i.get("n_suppliers") or 0) >= 2)
    add(
        f"В набор входят {num(len(items80))} {plural(len(items80), 'позиция', 'позиции', 'позиций')} "
        f"на {money(sum(i['sum'] for i in items80))} ({pct(sum(i['sum'] for i in items80) / scope_sum * 100)} "
        f"профиля). Первые 10 позиций дают {pct(top10)} объёма 80 %-набора, первые 50 — {pct(top50)}. "
        f"Единственная закупка — у {num(single)} {plural(single, 'позиции', 'позиций', 'позиций')}; "
        f"два и более поставщика — у {num(multi_sup)}."
    )
    add("")
    repeat = sum(1 for i in items80 if (i.get("n") or 0) >= 2)
    single_sup = sum(1 for i in items80 if (i.get("n_suppliers") or 0) <= 1)
    import_dep = 0
    for i in items80:
        cs = i.get("country_sum") or {}
        tot = sum((v or 0) for v in cs.values()) or 1.0
        imp = sum((v or 0) for k, v in cs.items()
                  if k not in ("Россия", "не определена", "Страна не указана"))
        if imp / tot > 0.9:
            import_dep += 1
    above_med = sum(1 for i in items80
                    if i.get("price_weighted") and i.get("price_median")
                    and i["price_weighted"] > i["price_median"])
    no_price = sum(1 for i in items80 if not i.get("price_weighted"))
    add(
        f"Ключевыми позициями набора считаются позиции, которые дают наибольшую часть "
        f"профильного объёма и одновременно имеют признаки, важные для проверки закупочной "
        f"деятельности: объём (доля в профиле), повторяемость (число закупок и поставщиков), "
        f"зависимость от импорта (страна происхождения и число поставщиков), уровень и разброс "
        f"цены (средневзвешенная цена, медиана, минимум и максимум по закупкам). "
        f"В наборе: повторные закупки (две и более) — у {num(repeat)} позиций; "
        f"единственный поставщик — у {num(single_sup)} позиций; "
        f"преимущественно импортные (доля импорта в позиции свыше 90 %) — у {num(import_dep)} позиций; "
        f"средневзвешенная цена выше медианы по своей позиции — у {num(above_med)} позиций; "
        f"без расчётной цены за единицу (нет количества) — у {num(no_price)} позиций."
    )
    add("")
    rows = []
    for i, it in enumerate(items80[:40], 1):
        rows.append([
            i, short(it["name"], 64), it.get("ktru") or it.get("okpd2") or "—",
            short(it["category"], 32), it.get("unit") or "—",
            num(it.get("qty")) if it.get("qty") else "—",
            money(it["sum"]), pct(it["sum"] / scope_sum * 100), pct(it["cum_share"]),
            money(it.get("price_weighted")), money(it.get("price_median")),
            num(it.get("n_suppliers")), it.get("country") or "—",
        ])
    add(cap("6.1", "Объёмы, цены, поставщики и страна по позициям 80 %-набора", m,
            "₽, шт., позиции, %, поставщики"))
    add("")
    add(table(["№", "Позиция", "ОКПД2/КТРУ", "Категория", "Ед.", "Кол-во", "Сумма", "Доля",
               "Накопленно", "Средняя цена", "Медиана", "Поставщиков", "Страна"],
              rows, ["right", "left", "left", "left", "center", "right", "right", "right",
                     "right", "right", "right", "right", "left"]))
    add("")
    add("Примечания: в таблице — первые 40 позиций набора; полный набор приведён в приложении Д. "
        "Средняя цена — средневзвешенная по позициям с известным количеством; медиана — по цене "
        "за единицу отдельных закупок. Для позиций без опубликованного количества расчётная цена "
        "не определяется.")
    add(
        f"В таблице — первые 40 позиций набора ({pct(sum(i['sum'] for i in items80[:40]) / scope_sum * 100)} "
        f"профиля). Остальные {num(max(0, len(items80) - 40))} позиций — в приложении Д. "
        f"Средняя цена — средневзвешенная по позициям с известным количеством; медиана — по цене "
        f"за единицу отдельных закупок."
    )
    add("")
    if figure(4):
        add(figure(4))
        add("")

    # ------------------------------------------------------------------ 7
    add("## 7. Страна происхождения")
    add("")
    ru = next((c["sum"] for c in a["by_country"] if c["country"] == "Россия"), 0.0)
    known = t["sum_country_known"] or 1.0
    add(
        f"Страна указана для {pct(t['country_coverage'])} профильного объёма ({money(t['sum_country_known'])}). "
        f"Россия — {money(ru)} ({pct(ru / known * 100)} объёма с указанной страной), импорт — "
        f"{money(t['sum_country_known'] - ru)} ({pct((t['sum_country_known'] - ru) / known * 100)}). "
        f"Без указания страны — {money(t['sum_country_unknown'])} ({pct(100 - t['country_coverage'])} профиля)."
    )
    add("")
    add("### 7.1. Сводка по странам")
    add("")
    add(
        "Источник атрибуции — поле «Страна происхождения» в спецификации или карточке контракта "
        "ЕИС; по стране поставщика страна не подставляется. Уровень confidence: «факт» — все "
        "позиции страны имеют опубликованные суммы, «оценка» — есть позиции с расчётными суммами."
    )
    add("")
    rows = []
    for i, c in enumerate(a["by_country"][:20], 1):
        cats = top_by(country_cats.get(c["country"], {}), 2)
        rows.append([
            i, c["country"], money(c["sum"]), pct(c["share"]), num(c["n"]), num(c["suppliers"]),
            "; ".join(short(x, 34) for x, _ in cats) if cats else "—",
            "оценка" if country_est.get(c["country"], 0) else "факт",
        ])
    add(cap("7.1", "Сводка по странам происхождения", m, "₽, позиции, %, поставщики"))
    add("")
    add(table(["№", "Страна", "Сумма", "Доля профиля", "Позиций", "Поставщиков",
               "Основные категории", "Confidence"], rows,
              ["right", "left", "right", "right", "right", "right", "left", "center"]))
    add("")
    add("Примечания: страна указана по полю «Страна происхождения» спецификации или карточки "
        "контракта ЕИС; по стране поставщика страна не подставляется. Доля рассчитана от "
        "профильного объёма; строка «не определена» приведена отдельно и в доли России/импорта "
        "не включается. Confidence «оценка» означает наличие позиций страны с расчётными суммами.")
    add(
        f"Всего стран — {num(len(a['by_country']))}; в таблице — первые 20. "
        f"На пять крупнейших стран приходится {pct(sum(c['sum'] for c in a['by_country'][:5]) / scope_sum * 100)} "
        f"профильного объёма."
    )
    add("")
    if figure(5):
        add(figure(5))
        add("")
    add("### 7.2. Страна по категориям 80 %-набора")
    add("")
    rows = []
    for c in cat80:
        cc = cat_country[c["category"]]
        ru_s = cc.get("Россия", 0.0)
        unknown = cc.get("не определена", 0.0)
        imp = sum(v for k, v in cc.items() if k not in ("Россия", "не определена"))
        top_imp = max(
            ((k, v) for k, v in cc.items() if k not in ("Россия", "не определена")),
            key=lambda kv: kv[1], default=("—", 0.0),
        )
        rows.append([
            short(c["category"], 42), mln(ru_s), mln(imp), mln(unknown),
            f"{top_imp[0]} ({mln(top_imp[1])})" if top_imp[0] != "—" else "—",
        ])
    add(cap("7.2", "Россия и импорт в разрезе товарных групп 80 %-набора", m, "млн ₽"))
    add("")
    add(table(["Товарная группа", "Россия", "Импорт", "Не указана", "Крупнейшая страна импорта"],
              rows, ["left", "right", "right", "right", "left"]))
    add("")
    add("Примечания: суммы приведены в млн ₽; в раздел попадают только товарные группы "
        "80 %-набора. Колонка «Не указана» — позиции без атрибуции страны.")
    unknown_pos = sorted(
        [p for p in in_scope if not p.get("country")], key=lambda p: -(p["sum"] or 0)
    )[:10]
    add("### 7.3. Крупнейшие неатрибутированные позиции")
    add("")
    add(
        "Позиции, по которым страна происхождения в ЕИС не указана. Причина отсутствия атрибуции "
        "у всех позиций таблицы одна: поле «Страна происхождения» в спецификации контракта не "
        "заполнено. Страна по бренду, производителю или документации не подставляется, чтобы не "
        "подменять данные источника; такие позиции в реестре помечены комментарием."
    )
    add("")
    if unknown_pos:
        u_rows = []
        for i, p in enumerate(unknown_pos, 1):
            u_rows.append([
                i, short(p["name"], 80), short(p.get("category") or "—", 34),
                money(p["sum"]), pct((p["sum"] or 0) / scope_sum * 100),
                "поле «Страна происхождения» в ЕИС не заполнено",
            ])
        add(cap("7.3", "Крупнейшие неатрибутированные позиции (страна не указана)", m,
                "₽, %"))
        add("")
        add(table(["№", "Позиция", "Товарная группа", "Сумма", "Доля профиля", "Причина"],
                  u_rows, ["right", "left", "left", "right", "right", "left"]))
        add("")
        add("Примечания: причина отсутствия атрибуции — поле «Страна происхождения» в ЕИС "
            "не заполнено; страна по бренду, производителю или документации не подставляется.")
        add(
            f"Всего без указания страны — {num(t['positions_in_scope'] - sum(1 for p in in_scope if p.get('country')))} "
            f"{plural(t['positions_in_scope'] - sum(1 for p in in_scope if p.get('country')), 'позиция', 'позиции', 'позиций')} "
            f"на {money(t['sum_country_unknown'])} ({pct(100 - t['country_coverage'])} профиля). "
            f"Полный перечень — в листе «09_Исключения» и в реестре позиций."
        )
        add("")
    else:
        add("Позиций без указания страны в профиле нет.")
        add("")

    # ------------------------------------------------------------------ 8
    add("## 8. Внутренние ценовые бенчмарки")
    add("")
    add(
        "Бенчмарки рассчитаны по закупкам учреждения за 2025 год. В таблицу включены позиции "
        "80 %-набора, по которым было не менее двух закупок с ценой за единицу. Показатели: "
        "средневзвешенная цена, медиана, минимум, максимум, P25, P75, разброс max/min, коэффициент "
        "вариации, количество закупок и поставщиков, расчётная разница между фактической "
        "средневзвешенной ценой и медианой/минимумом."
    )
    add("")
    add(
        "Формулы: средневзвешенная цена — сумма позиций с известным количеством, делённая на сумму "
        "количества; медиана, P25, P75 и разброс — по цене за единицу отдельных закупок; отклонение "
        "от медианы — (средневзвешенная ÷ медиана − 1); потенциал к медиане — "
        "(средневзвешенная − медиана) × количество; потенциал к минимуму — "
        "(средневзвешенная − минимум) × количество. Расчёт выполнен только по внутренним закупкам "
        "за 2025 год, внешние прайс-листы и данные других учреждений не используются. Значения "
        "потенциала — оценка при одинаковых объёмах и фасовках; сопоставимость условий поставки "
        "отдельно не проверялась, поэтому расхождение не означает, что цена завышена."
    )
    add("")
    add(
        f"Бенчмарк построен для {num(len(bench))} {plural(len(bench), 'позиции', 'позиций', 'позиций')} "
        f"({pct(len(bench) / max(1, len(items80)) * 100)} набора). Разброс цен выше 100 % — у "
        f"{num(len(high_spread))} позиций, от 30 до 100 % — у {num(len(mid_spread))}."
    )
    add("")
    rows = []
    for i, it in enumerate(bench[:30], 1):
        dev = None
        if it.get("price_weighted") and it.get("price_median"):
            dev = round((it["price_weighted"] / it["price_median"] - 1) * 100, 1)
        rows.append([
            i, short(it["name"], 58), it.get("unit") or "—",
            num(it.get("qty")) if it.get("qty") else "—",
            money(it["sum"]),
            money(it.get("price_weighted")), money(it.get("price_median")),
            money(it.get("price_min")), money(it.get("price_max")),
            money(it.get("price_p25")), money(it.get("price_p75")),
            num(it["n"]), num(it.get("n_suppliers")),
            pct(dev) if dev is not None else "—",
            money(it.get("saving_to_median")), money(it.get("saving_to_min")),
            it.get("confidence") or "факт",
        ])
    add(cap("8.1", "Внутренние ценовые бенчмарки по 30 ключевым позициям", m,
            "₽, шт., %, закупки, поставщики"))
    add("")
    add(table(["№", "Позиция", "Ед.", "Кол-во", "Сумма", "Средневзвеш.", "Медиана",
               "Минимум", "Максимум", "P25", "P75", "Закупок", "Поставщиков",
               "Отклонение от медианы", "Потенциал к медиане", "Потенциал к минимуму",
               "Confidence"], rows,
              ["right", "left", "center", "right", "right", "right", "right", "right", "right",
               "right", "right", "right", "right", "right", "right", "right", "center"]))
    add("")
    add("Примечания: бенчмарк рассчитан только по закупкам учреждения за 2025 год; внешние "
        "прайс-листы и данные других учреждений не используются. Потенциал снижения — оценка "
        "при одинаковых объёмах и фасовках; сопоставимость условий поставки отдельно "
        "не проверялась, поэтому расхождение не означает, что цена завышена. Полный набор "
        "бенчмарков — в листе «06_Бенчмарки» Excel и на экране дашборда.")
    add(
        "Разброс цен (max/min) и коэффициент вариации по всем позициям бенчмарка — в листе "
        "«06_Бенчмарки» Excel и на экране «Ценовые бенчмарки» дашборда."
    )
    add("")
    if figure(6):
        add(figure(6))
        add("")
    total_gap = sum(i.get("saving_to_median") or 0 for i in bench)
    above = [i for i in bench
             if i.get("price_weighted") and i.get("price_median")
             and i["price_weighted"] > i["price_median"]]
    add(
        f"Суммарная расчётная разница между фактической средневзвешенной и медианной ценой по "
        f"позициям бенчмарка — {money(total_gap)}. Это описательный показатель, а не оценка "
        f"гарантированной экономии."
    )
    add("")
    if above:
        top_above = sorted(above, key=lambda x: -(x.get("saving_to_median") or 0))[:3]
        add(
            f"Средневзвешенная цена выше медианы у {num(len(above))} позиций бенчмарка "
            f"(совокупное превышение над медианой — {money(sum(i.get('saving_to_median') or 0 for i in above))}). "
            f"Наибольшее превышение: "
            + "; ".join(
                f"{short(i['name'], 70)} — {pct(round((i['price_weighted'] / i['price_median'] - 1) * 100, 1))}, "
                f"{money(i.get('saving_to_median'))}"
                for i in top_above
            )
            + ". Превышение связано с разной фасовкой, объёмом и условиями поставки; сопоставимость "
            "отдельных закупок по условиям не проверялась."
        )
        add("")
    if with_spread:
        add("Наибольший разброс цен:")
        add("")
        for it in sorted(with_spread, key=lambda x: -x["price_spread"])[:5]:
            add(
                f"- {short(it['name'], 90)} — от {money(it.get('price_min'))} до "
                f"{money(it.get('price_max'))} за единицу, разброс {pct(it['price_spread'])}, "
                f"{num(it['n'])} закупок."
            )
        add("")
    add(
        "Позиции с одной закупкой в бенчмарк не включены: для них нельзя рассчитать разброс. "
        "Выбросы (ниже P5 или выше P95) отдельно не удалялись; их влияние видно по разбросу и "
        "коэффициенту вариации."
    )
    add("")

    # ------------------------------------------------------------------ 9
    add("## 9. Ключевая номенклатура")
    add("")
    add(
        "Ключевая номенклатура — позиции 80 %-набора. Для каждой позиции показаны объём, количество "
        "закупок и поставщиков, цена и месяцы закупки. Сводная таблица содержит первые 50 позиций "
        "набора; карточки приведены для первых десяти; полный набор — в приложении Д."
    )
    add("")
    rows = []
    for i, it in enumerate(items80[:50], 1):
        months = it.get("months") or []
        rows.append([
            i, short(it["name"], 62), short(it["category"], 34), it.get("unit") or "—",
            num(it.get("qty")) if it.get("qty") else "—",
            money(it["sum"]), pct(it["sum"] / scope_sum * 100),
            num(it["n"]), num(it.get("n_suppliers")),
            money(it.get("price_median")),
            f"{money(it.get('price_min'))} – {money(it.get('price_max'))}" if it.get("price_min") else "—",
            f"{month_label(months[0])} – {month_label(months[-1])}" if months else "—",
        ])
    add(cap("9.1", "Ключевая номенклатура 80 %-набора: сводка по первым 50 позициям", m,
            "₽, шт., %, закупки, поставщики"))
    add("")
    add(table(["№", "Позиция", "Группа", "Ед.", "Кол-во", "Сумма", "Доля", "Закупок", "Поставщиков",
               "Медиана", "Диапазон цен", "Период"], rows,
              ["right", "left", "left", "center", "right", "right", "right", "right", "right",
               "right", "right", "left"]))
    add("")
    add("Примечания: в таблице — первые 50 позиций 80 %-набора, карточки — по первым десяти; "
        "полный набор — в приложении Д, в Excel и в дашборде. Период — месяцы закупки позиции "
        "в 2025 году.")
    for i, it in enumerate(items80[:10], 1):
        cs = it.get("country_sum") or {}
        top_c = max(cs.items(), key=lambda kv: kv[1]) if cs else ("—", 0.0)
        months = it.get("months") or []
        add(f"### 9.{i}. {short(it['name'], 110)}")
        add("")
        add(f"- КТРУ: {it.get('ktru') or '—'}; ОКПД2: {it.get('okpd2') or '—'}.")
        add(f"- Товарная группа: {it['category']}; вид: {KIND_TITLES.get(it['kind'], it['kind'])}.")
        add(
            f"- Объём: {money(it['sum'])} ({pct(it['sum'] / scope_sum * 100)} профиля); "
            f"количество — {num(it.get('qty'))} {it.get('unit') or ''}."
            if it.get("qty") else
            f"- Объём: {money(it['sum'])} ({pct(it['sum'] / scope_sum * 100)} профиля); "
            f"количество по опубликованным позициям не указано."
        )
        add(
            f"- Закупок: {num(it['n'])}; поставщиков: {num(it.get('n_suppliers'))}; "
            f"страна: {top_c[0]} ({pct(top_c[1] / (it['sum'] or 1) * 100)} объёма позиции)."
            if top_c[0] != "—" else
            f"- Закупок: {num(it['n'])}; поставщиков: {num(it.get('n_suppliers'))}; страна не указана."
        )
        if it.get("trademark") or it.get("ru_number"):
            parts = []
            if it.get("trademark"):
                parts.append(f"товарный знак — {short(it['trademark'], 60)}")
            if it.get("ru_number"):
                parts.append(f"регистрационное удостоверение — {it['ru_number']}")
            add(f"- Производитель и модель: " + "; ".join(parts) + ".")
        if it.get("price_median"):
            add(
                f"- Цена за единицу: средневзвешенная — {money(it.get('price_weighted'))}, "
                f"медиана — {money(it.get('price_median'))}, диапазон — "
                f"{money(it.get('price_min'))} – {money(it.get('price_max'))}."
            )
            dev = None
            if it.get("price_weighted") and it.get("price_median"):
                dev = round((it["price_weighted"] / it["price_median"] - 1) * 100, 1)
            if dev is not None:
                add(
                    f"- Отклонение средневзвешенной цены от медианы — {pct(dev)}; расчётный "
                    f"потенциал к медиане — {money(it.get('saving_to_median'))}, "
                    f"к минимуму — {money(it.get('saving_to_min'))}."
                )
        if months:
            add(f"- Месяцы закупки: {month_label(months[0])} – {month_label(months[-1])}.")
        add("")

    # ------------------------------------------------------------------ 10
    add("## 10. Приложения")
    add("")
    add("### Приложение А. Глоссарий")
    add("")
    for term, definition in [
        ("80 %-набор", "все группы или позиции до достижения 80 % профильного объёма, а не фиксированный топ-10."),
        ("Профильный объём", "сумма позиций main и borderline; фармация, хозяйственные расходы, услуги и работы исключены."),
        ("main", "основной медицинский профиль."),
        ("borderline", "пограничные категории: лабораторные реагенты, дезинфекция, медицинская мебель и одежда, запчасти."),
        ("excluded", "фармация, хозяйственные расходы, услуги и работы, прочее вне профиля."),
        ("КТРУ", "каталог товаров, работ, услуг для обеспечения государственных и муниципальных нужд."),
        ("ОКПД2", "общероссийский классификатор продукции по видам экономической деятельности."),
        ("Бенчмарк", "внутренняя цена за единицу по закупкам учреждения за 2025 год."),
        ("Оценка", "расчётное, агрегированное или неполное значение; помечено в реестре."),
        ("Факт", "данные первичного источника без изменений."),
    ]:
        add(f"- **{term}** — {definition}")
    add("")
    add("### Приложение Б. Классификатор")
    add("")
    add("Виды (L1) и области:")
    add("")
    rows = []
    for k in a["by_kind"]:
        rows.append([k["title"], "пограничный" if k["scope"] == "borderline" else "основной",
                     num(k["n"]), money(k["sum"])])
    add(cap("Б.1", "Виды закупок (L1) и области профиля", m, "₽, позиции"))
    add("")
    add(table(["Вид", "Область", "Позиций", "Сумма"], rows, ["left", "left", "right", "right"]))
    add("")
    add("Примечания: область «пограничный» — признак scope = borderline; такие позиции входят "
        "в общий объём профиля и выделены отдельным признаком.")
    add(
        "Товарная группа (L2) определяется по ОКПД2 и маркерам наименования; позиция (L3) — по КТРУ "
        "и нормализованному наименованию. Правила применяются последовательно: сначала область, затем "
        "вид, затем группа. Спорные позиции проверялись вручную; часть из них отнесена к пограничным."
    )
    add("")
    add("### Приложение В. Паспорт данных")
    add("")
    passport = [
        ("Заказчик", m.get("customer_full") or m["customer"]),
        ("ИНН / КПП", f"{m['inn']} / {m['kpp']}"),
        ("Период", m["period"]),
        ("Дата выгрузки", m["extracted_at"]),
        ("Источники", m["sources"]),
        ("Контрактов и договоров", num(m["contracts_total"])),
        ("в том числе 44-ФЗ", num(m["contracts_44"])),
        ("в том числе 223-ФЗ", num(m["contracts_223"])),
        ("Профильных контрактов", num(m["contracts_in_scope"])),
        ("Поставщиков в профиле", num(t["suppliers"])),
        ("Позиций без указания поставщика (223-ФЗ)", num(t["positions_supplier_unknown"])),
        ("Сумма позиций без поставщика", money(t["sum_supplier_unknown"])),
        ("Доля позиций без поставщика", pct(t["share_supplier_unknown"])),
        ("Позиций всего", num(t["positions"])),
        ("Профильных позиций", num(t["positions_in_scope"])),
        ("Позиций с количеством", num(t["positions_with_qty"])),
        ("Оценочных позиций", num(t["positions_estimated"])),
        ("Товарных групп (L2)", num(len(a["by_category"]))),
        ("из них в 80 %-наборе", num(sum(1 for c in a["by_category"] if c.get("in_80")))),
        ("Номенклатурных позиций (L3)", num(len(a["items"]))),
        ("из них в 80 %-наборе", num(len(items80))),
        ("Сумма профиля", money(t["sum_scope"])),
        ("Доля профиля в общем объёме", pct(t["sum_scope"] / (t["sum_all"] or 1) * 100)),
        ("Сумма исключённых позиций", money(t["sum_excluded"])),
        ("Сумма всех позиций", money(t["sum_all"])),
        ("Сумма цен контрактов", money(t["sum_contracts"])),
        ("Расхождение (позиции − контракты)", money(t["reconciliation_diff"])),
        ("Отклонение от суммы контрактов", pct(abs(t["reconciliation_diff"]) / (t["sum_contracts"] or 1) * 100)),
        ("Охват страной", pct(t["country_coverage"])),
        ("Сумма без указания страны", money(t["sum_country_unknown"])),
        ("Смешанных контрактов", num(t["mixed_contracts"])),
        ("Средний срок исполнения", f"{num(t['avg_term_days'])} дн."),
        ("Сверка с первичным источником", f"выполнена по всем {num(m['contracts_total'])} "
                                          f"контрактам и договорам, расхождений нет"),
        ("Расхождение после дозагрузки спецификаций", money(t["reconciliation_diff"])),
    ]
    add(cap("В.1", "Паспорт данных: параметры выборки, охват и сверка", m, "₽, позиции, %"))
    add("")
    add(table(["Параметр", "Значение"], [[k, v] for k, v in passport], ["left", "right"]))
    add("")
    add("**Состав паспорта данных**")
    add("")
    add(cap("В.2", "Состав паспорта данных и ссылки на разделы отчёта", m))
    add("")
    add(table(["Элемент паспорта", "Где приведён"], [
        ["Источники и даты выгрузки", "строки «Источники» и «Дата выгрузки» выше; приложение Г"],
        ["Поисковые запросы и параметры выборки", "§ 2.2"],
        ["Охват: позиции, сумма, доля", "строки «Позиций всего», «Сумма профиля», "
                                        "«Доля профиля в общем объёме»"],
        ["Правила исключения и классификатор", "§ 2.3, § 2.4; приложение Б"],
        ["Правила нормализации единиц и упаковок", "§ 2.5"],
        ["Правила дедупликации", "§ 2.5"],
        ["Методика определения страны происхождения", "§ 2.6"],
        ["Методика внутренних ценовых бенчмарков и обработки выбросов", "§ 2.7"],
        ["Классы достоверности", "§ 2.8"],
        ["Ограничения и известные расхождения", "§ 2.8, § 3.4"],
        ["Глоссарий", "приложение А"],
    ], ["left", "left"]))
    add("")
    add("### Приложение Г. Источники")
    add("")
    add("- Реестр контрактов 44-ФЗ: https://zakupki.gov.ru/epz/contract/search/results.html")
    add("- Реестр договоров 223-ФЗ: https://zakupki.gov.ru/epz/contractfz223/search/results.html")
    add("- Карточка 44-ФЗ: /epz/contract/contractCard/common-info.html?reestrNumber=…")
    add("- Платёжная информация 44-ФЗ: /epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=…")
    add("- Карточка 223-ФЗ: /epz/contractfz223/card/contract-info.html?reestrNumber=…")
    add("- Предмет договора 223-ФЗ: /epz/contractfz223/card/contract-subject.html?reestrNumber=…")
    add("")
    add(
        "Внешние прайс-листы, коммерческие базы, данные других учреждений и презентационные материалы "
        "не использовались. Все суммы — по данным ЕИС на дату выгрузки."
    )
    add("")
    add("### Приложение Д. Полный 80 %-набор номенклатуры")
    add("")
    add(
        f"В таблицу включены все {num(len(items80))} позиций набора. Сортировка — по убыванию суммы. "
        f"Столбец «Накопленно» показывает долю профиля нарастающим итогом."
    )
    add("")
    rows = []
    for i, it in enumerate(items80, 1):
        rows.append([
            i, short(it["name"], 70), it.get("ktru") or it.get("okpd2") or "—",
            it.get("unit") or "—", num(it.get("qty")) if it.get("qty") else "—", money(it["sum"]),
            pct(it["sum"] / scope_sum * 100), pct(it["cum_share"]),
            money(it.get("price_weighted")), money(it.get("price_median")),
            num(it.get("n_suppliers")), it.get("country") or "—",
            short(it["category"], 34), KIND_TITLES.get(it["kind"], it["kind"]),
        ])
    add(cap("Д.1", "Полный 80 %-набор номенклатуры", m, "₽, шт., позиции, %, поставщики"))
    add("")
    add(table(["№", "Позиция", "ОКПД2/КТРУ", "Ед.", "Кол-во", "Сумма", "Доля", "Накопленно",
               "Средняя цена", "Медиана", "Поставщиков", "Страна", "Категория", "Вид"], rows,
              ["right", "left", "left", "center", "right", "right", "right", "right",
               "right", "right", "right", "left", "left", "left"]))
    add("")
    add("Примечания: включены все позиции 80 %-набора; сортировка — по убыванию суммы, "
        "столбец «Накопленно» — доля профиля нарастающим итогом. "
        "Средняя цена — средневзвешенная по позициям с известным количеством.")

    text = "\n".join(L)
    for n in range(2, 11):
        text = text.replace(f"\n## {n}. ", f"\n[[pagebreak]]\n\n## {n}. ", 1)
    for letter in ("А", "Б", "В", "Г", "Д"):
        text = text.replace(f"\n### Приложение {letter}.", f"\n[[pagebreak]]\n\n### Приложение {letter}.", 1)
    return text


def main() -> None:
    pages = None
    if TOC_PAGES.exists():
        try:
            pages = json.loads(TOC_PAGES.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pages = None
    text = build(pages)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"-> {OUT}")
    print(f"строк: {text.count(chr(10)) + 1}, символов: {len(text)}")


if __name__ == "__main__":
    main()
