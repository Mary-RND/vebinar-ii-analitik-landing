"""Аналитика по собранным контрактам 44-ФЗ и 223-ФЗ.

Строит data/botkina/analytics.json:
  * итоги и структура по видам (L1);
  * товарные группы (L2) и правило 80 %;
  * номенклатура (L3) и правило 80 %;
  * страна происхождения и охват атрибуции;
  * внутренние ценовые бенчмарки;
  * реестр позиций для Excel и дашборда.

Режимы:
  python analyze.py catalog   -- каталог ОКПД2 для настройки классификатора
  python analyze.py build     -- analytics.json + сводка в консоль
"""
from __future__ import annotations

import collections
import json
import re
import statistics as st
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify as cls  # noqa: E402
import config as cfg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = cfg.DEFAULT_LPU
LPU = cfg.get(SLUG)
D_DIR = ROOT / "data" / SLUG
JSONL_44 = D_DIR / "contracts.jsonl"
JSONL_223 = D_DIR / "contracts223.jsonl"
OUT = D_DIR / "analytics.json"

YEAR = 2025

# ЕИС не публикует наименование поставщика в реестре договоров 223-ФЗ
SUPPLIER_UNKNOWN = "не указан в ЕИС (реестр 223-ФЗ)"

COUNTRY_MAP = {
    "РОССИЙСКАЯ ФЕДЕРАЦИЯ": "Россия",
    "РОССИЯ": "Россия",
    "СОЕДИНЕННОЕ КОРОЛЕВСТВО ВЕЛИКОБРИТАНИИ И СЕВЕРНОЙ ИРЛАНДИИ": "Великобритания",
    "СОЕДИНЕННОЕ КОРОЛЕВСТВО": "Великобритания",
    "КИТАЙСКАЯ НАРОДНАЯ РЕСПУБЛИКА": "Китай",
    "КИТАЙ": "Китай",
    "СОЕДИНЕННЫЕ ШТАТЫ АМЕРИКИ": "США",
    "США": "США",
    "РЕСПУБЛИКА КОРЕЯ": "Корея",
    "КОРЕЯ, РЕСПУБЛИКА": "Корея",
    "ГЕРМАНИЯ": "Германия",
    "ФРАНЦИЯ": "Франция",
    "ИТАЛИЯ": "Италия",
    "ЯПОНИЯ": "Япония",
    "ИНДИЯ": "Индия",
    "ТУРЦИЯ": "Турция",
    "ШВЕЙЦАРИЯ": "Швейцария",
    "НИДЕРЛАНДЫ": "Нидерланды",
    "БЕЛЬГИЯ": "Бельгия",
    "ИСПАНИЯ": "Испания",
    "ПОЛЬША": "Польша",
    "ЧЕХИЯ": "Чехия",
    "АВСТРИЯ": "Австрия",
    "ШВЕЦИЯ": "Швеция",
    "ДАНИЯ": "Дания",
    "ФИНЛЯНДИЯ": "Финляндия",
    "ИЗРАИЛЬ": "Израиль",
    "БЕЛАРУСЬ": "Беларусь",
    "КАЗАХСТАН": "Казахстан",
    "ЛИТВА": "Литва",
    "ЛАТВИЯ": "Латвия",
    "ЭСТОНИЯ": "Эстония",
    "СЛОВАКИЯ": "Словакия",
    "ВЕНГРИЯ": "Венгрия",
    "РУМЫНИЯ": "Румыния",
    "СЛОВЕНИЯ": "Словения",
    "ХОРВАТИЯ": "Хорватия",
    "СЕРБИЯ": "Сербия",
    "ИРЛАНДИЯ": "Ирландия",
    "НОРВЕГИЯ": "Норвегия",
    "ПОРТУГАЛИЯ": "Португалия",
    "ГРЕЦИЯ": "Греция",
    "МЕКСИКА": "Мексика",
    "БРАЗИЛИЯ": "Бразилия",
    "ВЬЕТНАМ": "Вьетнам",
    "МАЛАЙЗИЯ": "Малайзия",
    "СИНГАПУР": "Сингапур",
    "ТАЙВАНЬ": "Тайвань",
    "УКРАИНА": "Украина",
    "МОЛДОВА": "Молдова",
    "УЗБЕКИСТАН": "Узбекистан",
    "АРМЕНИЯ": "Армения",
    "ГРУЗИЯ": "Грузия",
    "АВСТРАЛИЯ": "Австралия",
    "КАНАДА": "Канада",
    "ЮЖНАЯ АФРИКА": "ЮАР",
    "КОРОЛЕВСТВО ТАИЛАНД": "Таиланд",
    "ТАИЛАНД": "Таиланд",
    "РЕСПУБЛИКА КОСТА-РИКА": "Коста-Рика",
    "КОСТА-РИКА": "Коста-Рика",
    "ФЕДЕРАТИВНАЯ РЕСПУБЛИКА ГЕРМАНИЯ": "Германия",
    "ИТАЛЬЯНСКАЯ РЕСПУБЛИКА": "Италия",
    "РЕСПУБЛИКА ИНДИЯ": "Индия",
    "РЕСПУБЛИКА БЕЛАРУСЬ": "Беларусь",
    "РЕСПУБЛИКА КАЗАХСТАН": "Казахстан",
    "РЕСПУБЛИКА УЗБЕКИСТАН": "Узбекистан",
    "РЕСПУБЛИКА АРМЕНИЯ": "Армения",
    "ФРАНЦУЗСКАЯ РЕСПУБЛИКА": "Франция",
    "ШВЕЙЦАРСКАЯ КОНФЕДЕРАЦИЯ": "Швейцария",
    "АВСТРИЙСКАЯ РЕСПУБЛИКА": "Австрия",
    "РЕСПУБЛИКА ПОЛЬША": "Польша",
    "ЧЕШСКАЯ РЕСПУБЛИКА": "Чехия",
    "РЕСПУБЛИКА ФИНЛЯНДИЯ": "Финляндия",
    "КОРОЛЕВСТВО БЕЛЬГИЯ": "Бельгия",
    "КОРОЛЕВСТВО НИДЕРЛАНДОВ": "Нидерланды",
    "КОРОЛЕВСТВО ШВЕЦИЯ": "Швеция",
    "КОРОЛЕВСТВО ДАНИЯ": "Дания",
    "КОРОЛЕВСТВО ИСПАНИЯ": "Испания",
    "КОРОЛЕВСТВО НОРВЕГИЯ": "Норвегия",
    "ПОРТУГАЛЬСКАЯ РЕСПУБЛИКА": "Португалия",
    "ГРЕЧЕСКАЯ РЕСПУБЛИКА": "Греция",
    "РЕСПУБЛИКА СЛОВЕНИЯ": "Словения",
    "РЕСПУБЛИКА ХОРВАТИЯ": "Хорватия",
    "РЕСПУБЛИКА СЕРБИЯ": "Сербия",
    "ТУРЕЦКАЯ РЕСПУБЛИКА": "Турция",
    "МЕКСИКАНСКИЕ СОЕДИНЕННЫЕ ШТАТЫ": "Мексика",
    "ФЕДЕРАТИВНАЯ РЕСПУБЛИКА БРАЗИЛИЯ": "Бразилия",
    "СОЦИАЛИСТИЧЕСКАЯ РЕСПУБЛИКА ВЬЕТНАМ": "Вьетнам",
    "РЕСПУБЛИКА СИНГАПУР": "Сингапур",
    "ОБЪЕДИНЕННЫЕ АРАБСКИЕ ЭМИРАТЫ": "ОАЭ",
    "ТАЙВАНЬ (КИТАЙ)": "Тайвань",
}


def norm_country(value: str | None) -> str | None:
    if not value:
        return None
    v = re.sub(r"\s+", " ", value).strip(" .,;")
    if not v or v == "-":
        return None
    up = v.upper()
    if up in COUNTRY_MAP:
        return COUNTRY_MAP[up]
    for key, short in COUNTRY_MAP.items():
        if up.startswith(key):
            return short
    return v[:60]


def load() -> list[dict]:
    rows: list[dict] = []
    for path, source in ((JSONL_44, "44-ФЗ"), (JSONL_223, "223-ФЗ")):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # незавершённая строка при параллельном сборе
            row["_source"] = source
            rows.append(row)
    # дедупликация по регистрационному номеру: при параллельном сборе одна
    # карточка могла попасть в два файла — оставляем запись с большим числом позиций
    best: dict[str, dict] = {}
    order: list[str] = []
    for r in rows:
        rn = r.get("reestr")
        if not rn:
            continue
        if rn not in best:
            best[rn] = r
            order.append(rn)
        elif len(r.get("positions") or []) > len(best[rn].get("positions") or []):
            best[rn] = r
    return [best[rn] for rn in order]


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", s)
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def clean_name(name: str | None) -> str:
    n = re.sub(r"\s+", " ", name or "").strip()
    return n


def norm_method(m: str | None) -> str:
    s = (m or "").strip()
    low = s.lower()
    if not s:
        return "не указан"
    if low.startswith("электронный аукцион"):
        return "Электронный аукцион"
    if "запрос котировок" in low:
        return "Запрос котировок"
    if "единственного поставщика" in low:
        return "Единственный поставщик"
    if low.startswith("аукцион"):
        return "Аукцион"
    if "конкурс" in low:
        return "Конкурс"
    if "запрос предложений" in low:
        return "Запрос предложений"
    return s[:60]


UNIT_MAP = (
    ("шт", ("шт", "штука", "пар", "пара", "п")),
    ("упаковка", ("упак", "уп")),
    ("набор", ("набор", "компл", "комплект")),
    ("мл", ("см3", "мл", "дм3", "литр", "кубический сантиметр")),
    ("г", ("мг", "г", "грамм")),
    ("м", ("м3", "кубический метр", "см", "м")),
)


def norm_unit(u: str | None) -> str | None:
    """Приведение единицы измерения к базовой (ТЗ § 5.5, п. 1)."""
    if not u:
        return None
    s = re.sub(r"\s+", " ", u.strip().lower())
    s = re.sub(r"^\d+\s+", "", s)  # «6 набор» -> «набор»
    for base, keys in UNIT_MAP:
        for k in keys:
            if s.startswith(k):
                return base
    return u.strip()


def position_comment(p: dict) -> str:
    """Фактический комментарий к позиции реестра (ТЗ § 5.4, блок «Качество»)."""
    parts: list[str] = []
    if p.get("estimated"):
        parts.append("сумма оценена по цене контракта: количество в ЕИС не опубликовано")
    if not p.get("qty"):
        parts.append("количество не опубликовано")
    if not p.get("country"):
        parts.append("страна происхождения в ЕИС не указана")
    if not p.get("okpd2") and not p.get("ktru"):
        parts.append("код ОКПД2/КТРУ отсутствует")
    return "; ".join(parts)


CHARS_PROD = re.compile(r"Производитель\s*:\s*([^;\n]+)", re.I)
CHARS_MODEL = re.compile(r"Модель\s*[:=]?\s*([^;\n]+)", re.I)


def chars_attr(chars: str | None, pattern: re.Pattern) -> str | None:
    """Извлечение атрибута товара из строки характеристик спецификации ЕИС."""
    if not chars:
        return None
    m = pattern.search(chars)
    if not m:
        return None
    val = m.group(1)
    val = re.split(r"Страна происхождения", val, flags=re.I)[0]
    val = re.sub(r"\s+", " ", val).strip(" .,;")
    return val[:120] or None


def mk_position(p: dict, cprice: float, single: bool, remainder: float, wsum: float,
                n_unknown: int, contract: dict) -> dict:
    s = p.get("sum")
    est = False
    if not s and p.get("qty") and p.get("unit_price"):
        s = round(p["qty"] * p["unit_price"], 2)
    if not s:
        if single:
            s = round(remainder, 2)
        else:
            w = p.get("unit_price") or 0
            s = round(remainder * (w / wsum if wsum else 1 / n_unknown), 2)
        est = True
    kind, bucket, scope, reason = cls.classify(p.get("okpd2"), p.get("ktru"), p.get("name"))
    ptype = (p.get("type") or "").lower()
    if "услуг" in ptype or "работ" in ptype:
        kind, bucket, scope, reason = "service", "Услуги и работы", "excluded", "тип позиции"
    country = norm_country(p.get("country"))
    pos = {
        "n": p.get("n"), "name": clean_name(p.get("name")),
        "okpd2": p.get("okpd2"), "okpd2_name": clean_name(p.get("okpd2_name")),
        "ktru": p.get("ktru"), "type": p.get("type"),
        "unit": p.get("unit"), "unit_norm": norm_unit(p.get("unit")), "qty": p.get("qty"),
        "unit_price": p.get("unit_price"), "sum": s,
        "country": country,
        "country_src": ("спецификация ЕИС, поле «Страна происхождения»" if country
                        else "не определена — данные в ЕИС отсутствуют"),
        "nkmi": p.get("nkmi"), "is_med": p.get("is_med"),
        "trademark": p.get("trademark"), "ru_name": p.get("ru_name"),
        "ru_number": p.get("ru_number"), "estimated": est,
        "producer": chars_attr(p.get("chars"), CHARS_PROD),
        "model": chars_attr(p.get("chars"), CHARS_MODEL),
        "pos_src": "спецификация ЕИС",
        "kind": kind, "category": bucket, "scope": scope, "reason": reason,
        "date": contract.get("signed_date"), "year": contract["_year"],
        "quarter": contract["_quarter"], "month": contract["_month"],
        "source": contract["_source"], "method": norm_method(contract.get("method")),
        "supplier": contract["_supplier_name"],
        "supplier_inn": contract.get("_supplier_inn"),
        "href": contract.get("href"),
        "contract_price": cprice,
    }
    pos["comment"] = position_comment(pos)
    return pos


def positions_of(contract: dict) -> list[dict]:
    cprice = contract.get("price") or 0.0
    positions = contract.get("positions") or []
    if not positions:
        subject = (clean_name(contract.get("subjects_preview"))
                   or clean_name(contract.get("subject"))
                   or "(объект закупки не детализирован)")
        kind, bucket, scope, reason = cls.classify(None, None, subject)
        return [{
            "n": 1, "name": subject, "okpd2": None, "okpd2_name": None, "ktru": None,
            "type": "—", "unit": None, "unit_norm": None, "qty": None, "unit_price": cprice or None,
            "sum": cprice or None, "country": None,
            "country_src": "не определена — данные в ЕИС отсутствуют",
            "nkmi": None, "is_med": None,
            "trademark": None, "ru_name": None, "ru_number": None, "estimated": False,
            "producer": None, "model": None,
            "pos_src": "предмет договора 223-ФЗ",
            "kind": kind, "category": bucket, "scope": scope, "reason": reason,
            "date": contract.get("signed_date"), "year": contract["_year"],
            "quarter": contract["_quarter"], "month": contract["_month"],
            "source": contract["_source"], "method": norm_method(contract.get("method")),
            "supplier": contract["_supplier_name"],
            "supplier_inn": contract.get("_supplier_inn"),
            "href": contract.get("href"),
            "contract_price": cprice,
            "comment": "спецификация договора в ЕИС не опубликована: сумма позиции принята равной цене договора",
        }]

    known = 0.0
    unknown = 0
    for p in positions:
        s = p.get("sum") or (p.get("qty") * p.get("unit_price") if p.get("qty") and p.get("unit_price") else 0)
        if s:
            known += s
        else:
            unknown += 1
    remainder = max(0.0, cprice - known)
    single = len(positions) == 1
    wsum = sum((p.get("unit_price") or 0) for p in positions if not p.get("sum")) or unknown
    return [
        mk_position(p, cprice, single, remainder, wsum, unknown or 1, contract)
        for p in positions
    ]


def pareto_set(rows: list[dict], key_sum: str = "sum") -> tuple[list[dict], float, float]:
    """Все строки до накопленной доли >= 80 %, с учётом равных сумм на границе."""
    total = sum(r[key_sum] or 0 for r in rows) or 1.0
    acc = 0.0
    out: list[dict] = []
    for r in rows:
        out.append(r)
        acc += r[key_sum] or 0
        if acc / total >= 0.8:
            break
    if out:
        edge = out[-1][key_sum] or 0
        rest = [r for r in rows[len(out):] if r[key_sum] == edge]
        out.extend(rest)
    return out, acc, total


def pct(x: float) -> float:
    return round(x * 100, 1)


def stage_catalog() -> None:
    rows = load()
    agg: dict[str, dict] = collections.defaultdict(
        lambda: {"n": 0, "sum": 0.0, "names": collections.Counter(), "sample": ""}
    )
    for c in rows:
        if parse_date(c.get("signed_date")) is None:
            continue
        c["_year"] = parse_date(c.get("signed_date")).year
        c["_quarter"] = ""
        c["_month"] = ""
        c["_supplier_name"] = ""
        for p in positions_of(c):
            key = (p["okpd2"] or "—")[:9]
            a = agg[key]
            a["n"] += 1
            a["sum"] += p["sum"] or 0
            a["names"][p["okpd2_name"] or p["name"][:60]] += 1
            if not a["sample"]:
                a["sample"] = p["name"][:80]
    print(f"{'ОКПД2':<14}{'n':>6}{'сумма, ₽':>16}  вид / группа / пример")
    for key, a in sorted(agg.items(), key=lambda kv: -kv[1]["sum"]):
        kind, bucket, scope, _ = cls.classify(key if key != "—" else None)
        nm = a["names"].most_common(1)[0][0]
        print(f"{key:<14}{a['n']:>6}{a['sum']:>16,.0f}  [{kind}/{scope}] {bucket[:34]:<36} {nm[:48]}")


def stage_build() -> None:
    contracts = load()
    in_year: list[dict] = []
    for c in contracts:
        d = parse_date(c.get("signed_date"))
        if not d or d.year != YEAR:
            continue
        c["_date"] = d
        c["_year"] = d.year
        c["_quarter"] = f"{d.year}-Q{(d.month - 1) // 3 + 1}"
        c["_month"] = d.strftime("%Y-%m")
        c["_price"] = c.get("price") or 0.0
        c["_supplier_inn"] = (c.get("supplier") or {}).get("inn")
        c["_supplier_name"] = (c.get("supplier") or {}).get("name") or SUPPLIER_UNKNOWN
        c["_positions"] = positions_of(c)
        in_year.append(c)

    all_positions: list[dict] = []
    for c in in_year:
        positions = c["_positions"]
        goods = any(p["scope"] in ("main", "borderline") for p in positions)
        other = any(p["scope"] == "excluded" and p["kind"] in ("service", "work")
                    for p in positions)
        is_mixed = goods and other
        for p in positions:
            p["contract_reestr"] = c["reestr"]
            p["mixed"] = "да" if is_mixed else "нет"
            all_positions.append(p)

    in_scope = [p for p in all_positions if p["scope"] in ("main", "borderline")]
    main = [p for p in all_positions if p["scope"] == "main"]
    borderline = [p for p in all_positions if p["scope"] == "borderline"]

    # --- агрегаты
    def agg_by(keyfn, src):
        d: dict[str, dict] = collections.defaultdict(
            lambda: {"sum": 0.0, "n": 0, "suppliers": set(), "main": 0.0, "borderline": 0.0}
        )
        for p in src:
            k = keyfn(p)
            a = d[k]
            a["sum"] += p["sum"] or 0
            a["n"] += 1
            a["suppliers"].add(p.get("supplier") or "—")
            if p["scope"] == "main":
                a["main"] += p["sum"] or 0
            else:
                a["borderline"] += p["sum"] or 0
        return d

    by_kind_d = agg_by(lambda p: p["kind"], in_scope)
    by_cat_d = agg_by(lambda p: p["category"], in_scope)
    by_month_d = agg_by(lambda p: p["month"], in_scope)
    by_quarter_d = agg_by(lambda p: p["quarter"], in_scope)
    by_source_d = agg_by(lambda p: p["source"], in_scope)
    by_method_d = agg_by(lambda p: norm_method(p.get("method")), in_scope)
    by_country_d = agg_by(lambda p: p["country"] or "не определена", in_scope)

    total_scope = sum(p["sum"] or 0 for p in in_scope)
    total_all = sum(p["sum"] or 0 for p in all_positions)
    contracts_scope = [c for c in in_year if any(p["scope"] in ("main", "borderline") for p in c["_positions"])]

    # --- виды
    by_kind = []
    for kind, a in sorted(by_kind_d.items(), key=lambda kv: -kv[1]["sum"]):
        by_kind.append({
            "kind": kind, "title": cls.KIND_TITLES.get(kind, kind),
            "sum": round(a["sum"], 2), "share": pct(a["sum"] / (total_scope or 1)),
            "n": a["n"], "suppliers": len(a["suppliers"]),
            "avg_position": round(a["sum"] / a["n"], 2) if a["n"] else None,
            "scope": "borderline" if kind in cls.BORDERLINE_KINDS else (
                "excluded" if kind in cls.EXCLUDED_KINDS else "main"
            ),
        })

    # --- категории: полный список + 80 % набор
    by_cat = []
    for cat, a in sorted(by_cat_d.items(), key=lambda kv: -kv[1]["sum"]):
        by_cat.append({
            "category": cat, "sum": round(a["sum"], 2),
            "share": pct(a["sum"] / (total_scope or 1)),
            "n": a["n"], "suppliers": len(a["suppliers"]),
            "avg_position": round(a["sum"] / a["n"], 2) if a["n"] else None,
            "main_sum": round(a["main"], 2), "borderline_sum": round(a["borderline"], 2),
        })
    cat80, cat80_sum, _ = pareto_set(by_cat)
    acc = 0.0
    for r in by_cat:
        acc += r["sum"]
        r["cum_share"] = pct(acc / (total_scope or 1))
        r["in_80"] = r in cat80

    # --- номенклатура: сквозная группировка по КТРУ/ОКПД2 + нормализованному имени
    def item_key(p: dict) -> str:
        ktru = (p.get("ktru") or "").split("-")[0]
        nm = re.sub(r"[^а-яa-z0-9 ]", "", (p.get("name") or "").lower())
        nm = re.sub(r"\s+", " ", nm).strip()[:70]
        return f"{ktru or p.get('okpd2') or ''}|{nm}"

    items: dict[str, dict] = {}
    for p in in_scope:
        k = item_key(p)
        it = items.get(k)
        if not it:
            it = {
                "key": k, "name": p["name"], "ktru": (p.get("ktru") or "").split("-")[0] or None,
                "okpd2": p.get("okpd2"), "category": p["category"], "kind": p["kind"],
                "unit": p.get("unit"), "sum": 0.0, "qty": 0.0, "sum_qty": 0.0, "prices": [],
                "n": 0, "suppliers": set(), "country": p.get("country"),
                "country_sum": {}, "months": set(), "estimated": 0,
                "marks": {}, "ru_numbers": set(),
            }
            items[k] = it
        it["sum"] += p["sum"] or 0
        it["n"] += 1
        if p.get("qty"):
            it["qty"] += p["qty"]
            it["sum_qty"] += p["sum"] or 0
        if p.get("unit_price"):
            it["prices"].append(p["unit_price"])
        if p.get("supplier"):
            it["suppliers"].add(p["supplier"])
        if p.get("estimated"):
            it["estimated"] += 1
        tm = (p.get("trademark") or "").strip()
        if tm and tm.lower() not in ("отсутствует", "не указан", "нет", "н/д", "-"):
            it["marks"][tm] = it["marks"].get(tm, 0) + 1
        if p.get("ru_number"):
            it["ru_numbers"].add(p["ru_number"])
        if p.get("country"):
            it["country_sum"][p["country"]] = it["country_sum"].get(p["country"], 0) + (p["sum"] or 0)
        if p.get("month"):
            it["months"].add(p["month"])

    def finalize_items(d: dict) -> list[dict]:
        out = []
        for it in d.values():
            prices = sorted(it["prices"])
            it["n_suppliers"] = len(it["suppliers"])
            if it.get("country_sum"):
                it["country"] = max(it["country_sum"].items(), key=lambda kv: kv[1])[0]
            it["suppliers"] = sorted(it["suppliers"])[:8]
            it["months"] = sorted(it["months"])
            it["price_min"] = prices[0] if prices else None
            it["price_max"] = prices[-1] if prices else None
            it["price_median"] = round(st.median(prices), 2) if prices else None
            it["price_p25"] = round(prices[int(len(prices) * 0.25)], 2) if prices else None
            it["price_p75"] = round(prices[int(len(prices) * 0.75)], 2) if prices else None
            it["price_weighted"] = (
                round(it["sum_qty"] / it["qty"], 2) if it["qty"] else None
            )
            it["confidence"] = "оценка" if it["estimated"] else "факт"
            it["trademark"] = (
                max(it["marks"].items(), key=lambda kv: kv[1])[0] if it["marks"] else None
            )
            it["ru_number"] = sorted(it["ru_numbers"])[0] if it["ru_numbers"] else None
            it["marks"] = {}
            it["ru_numbers"] = []
            it["price_spread"] = (
                round((prices[-1] / prices[0] - 1) * 100, 1) if prices and prices[0] else None
            )
            it["price_cv"] = (
                round(st.pstdev(prices) / (sum(prices) / len(prices)) * 100, 1)
                if len(prices) > 1 and sum(prices) else None
            )
            if it["price_weighted"] and it["price_median"]:
                it["saving_to_median"] = round(
                    max(0.0, it["price_weighted"] - it["price_median"]) * it["qty"], 2
                )
                it["saving_to_min"] = round(
                    max(0.0, it["price_weighted"] - it["price_min"]) * it["qty"], 2
                ) if it["price_min"] else None
            out.append(it)
        out.sort(key=lambda x: -x["sum"])
        return out

    all_items = finalize_items(items)
    items80, items80_sum, _ = pareto_set(all_items)
    acc = 0.0
    for it in all_items:
        acc += it["sum"]
        it["cum_share"] = pct(acc / (total_scope or 1))
        it["in_80"] = it in items80
        it.pop("prices", None)

    # --- страна
    country_cats: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    country_est: dict[str, int] = defaultdict(int)
    for p in in_scope:
        ckey = p.get("country") or "не определена"
        country_cats[ckey][p["category"]] += p["sum"] or 0
        if p.get("estimated"):
            country_est[ckey] += 1
    by_country = []
    for country, a in sorted(by_country_d.items(), key=lambda kv: -kv[1]["sum"]):
        top_cats = [c for c, _ in sorted(country_cats[country].items(), key=lambda kv: -kv[1])[:2]]
        by_country.append({
            "country": country, "sum": round(a["sum"], 2),
            "share": pct(a["sum"] / (total_scope or 1)),
            "n": a["n"], "suppliers": len(a["suppliers"]),
            "cats": top_cats,
            "confidence": "оценка" if country_est.get(country, 0) else "факт",
        })
    sum_country_known = sum(v["sum"] for k, v in by_country_d.items() if k != "не определена")
    sum_country_unknown = by_country_d.get("не определена", {}).get("sum", 0.0)

    # --- поставщики
    by_supplier_d = agg_by(lambda p: p.get("supplier") or SUPPLIER_UNKNOWN, in_scope)
    by_supplier = []
    for name, a in sorted(by_supplier_d.items(), key=lambda kv: -kv[1]["sum"]):
        by_supplier.append({
            "supplier": name, "sum": round(a["sum"], 2),
            "share": pct(a["sum"] / (total_scope or 1)), "n": a["n"],
        })
    n_suppliers_known = sum(1 for r in by_supplier if r["supplier"] != SUPPLIER_UNKNOWN)
    sum_supplier_unknown = by_supplier_d.get(SUPPLIER_UNKNOWN, {}).get("sum", 0.0)
    n_supplier_unknown = by_supplier_d.get(SUPPLIER_UNKNOWN, {}).get("n", 0)

    sc = sorted(c["_price"] for c in contracts_scope if c["_price"])
    terms = [
        (parse_date(c.get("due_date")) - c["_date"]).days
        for c in in_year
        if c.get("due_date") and parse_date(c.get("due_date")) and parse_date(c.get("due_date")) > c["_date"]
    ]

    # распределение контрактов по размеру цены
    size_buckets = [
        ("до 100 тыс. ₽", 0, 100_000),
        ("100–600 тыс. ₽", 100_000, 600_000),
        ("600 тыс. – 1 млн ₽", 600_000, 1_000_000),
        ("1–5 млн ₽", 1_000_000, 5_000_000),
        ("5–10 млн ₽", 5_000_000, 10_000_000),
        ("10–50 млн ₽", 10_000_000, 50_000_000),
        ("свыше 50 млн ₽", 50_000_000, float("inf")),
    ]
    by_size = []
    for title, lo, hi in size_buckets:
        grp = [c for c in in_year if lo <= c["_price"] < hi]
        by_size.append({
            "bucket": title, "contracts": len(grp),
            "sum": round(sum(c["_price"] for c in grp), 2),
            "scope_sum": round(sum(
                p["sum"] or 0 for c in grp for p in c["_positions"]
                if p["scope"] in ("main", "borderline")
            ), 2),
        })

    mixed = sum(
        1 for c in in_year
        if any(p["scope"] in ("main", "borderline") for p in c["_positions"])
        and any(p["scope"] == "excluded" and p["kind"] == "service" for p in c["_positions"])
    )

    analytics = {
        "meta": {
            "customer": f'{LPU["name"]} (ИНН {LPU["inn"]})',
            "customer_full": LPU.get("full_name"),
            "inn": LPU["inn"], "kpp": LPU["kpp"],
            "period": f"{cfg.DATE_FROM} – {cfg.DATE_TO}",
            "year": YEAR,
            "extracted_at": date.today().isoformat(),
            "sources": "ЕИС: реестр контрактов 44-ФЗ и реестр договоров 223-ФЗ",
            "scope_rule": "main + borderline; фармация, хозяйственные расходы, услуги и работы исключены",
            "contracts_total": len(in_year),
            "contracts_in_scope": len(contracts_scope),
            "contracts_44": sum(1 for c in in_year if c["_source"] == "44-ФЗ"),
            "contracts_223": sum(1 for c in in_year if c["_source"] == "223-ФЗ"),
        },
        "totals": {
            "sum_all": round(total_all, 2),
            "sum_contracts": round(sum(c["_price"] for c in in_year), 2),
            "reconciliation_diff": round(total_all - sum(c["_price"] for c in in_year), 2),
            "sum_scope": round(total_scope, 2),
            "sum_main": round(sum(p["sum"] or 0 for p in main), 2),
            "sum_borderline": round(sum(p["sum"] or 0 for p in borderline), 2),
            "sum_excluded": round(total_all - total_scope, 2),
            "positions": len(all_positions),
            "positions_in_scope": len(in_scope),
            "positions_with_qty": sum(1 for p in all_positions if p.get("qty")),
            "positions_estimated": sum(1 for p in in_scope if p.get("estimated")),
            "suppliers": n_suppliers_known,
            "suppliers_total": len(by_supplier),
            "positions_supplier_unknown": n_supplier_unknown,
            "sum_supplier_unknown": round(sum_supplier_unknown, 2),
            "share_supplier_unknown": pct(sum_supplier_unknown / (total_scope or 1)),
            "median_contract": round(st.median(sc), 2) if sc else None,
            "mean_contract": round(sum(sc) / len(sc), 2) if sc else None,
            "max_contract": max(sc) if sc else None,
            "avg_position": round(total_scope / len(in_scope), 2) if in_scope else None,
            "median_position": round(st.median([p["sum"] or 0 for p in in_scope]), 2) if in_scope else None,
            "sum_country_known": round(sum_country_known, 2),
            "sum_country_unknown": round(sum_country_unknown, 2),
            "country_coverage": pct(sum_country_known / (total_scope or 1)),
            "categories_in_80": len(cat80),
            "categories_total": len(by_cat),
            "cat80_share": pct(cat80_sum / (total_scope or 1)),
            "items_in_80": len(items80),
            "items_total": len(all_items),
            "items80_share": pct(items80_sum / (total_scope or 1)),
            "unique_ktru": len({p["ktru"].split("-")[0] for p in in_scope if p.get("ktru")}),
            "multi_contract_ktru": sum(
                1 for k, v in collections.Counter(
                    p["ktru"].split("-")[0] for p in in_scope if p.get("ktru")
                ).items() if v > 1
            ),
            "avg_term_days": round(sum(terms) / len(terms)) if terms else None,
            "mixed_contracts": mixed,
        },
        "by_size": by_size,
        "by_kind": by_kind,
        "by_category": by_cat,
        "by_month": [
            {"month": k, "sum": round(a["sum"], 2), "n": a["n"]}
            for k, a in sorted(by_month_d.items())
        ],
        "by_quarter": [
            {"quarter": k, "sum": round(a["sum"], 2), "n": a["n"]}
            for k, a in sorted(by_quarter_d.items())
        ],
        "by_source": [
            {"source": k, "sum": round(a["sum"], 2), "n": a["n"]}
            for k, a in sorted(by_source_d.items(), key=lambda kv: -kv[1]["sum"])
        ],
        "by_method": [
            {"method": k, "sum": round(a["sum"], 2), "n": a["n"]}
            for k, a in sorted(by_method_d.items(), key=lambda kv: -kv[1]["sum"])
        ],
        "by_country": by_country,
        "by_supplier": by_supplier[:60],
        "items": all_items,
        "positions": [
            {
                "name": (p["name"] or "")[:200], "okpd2": p["okpd2"], "ktru": p["ktru"],
                "category": p["category"], "kind": p["kind"], "scope": p["scope"],
                "reason": p["reason"], "unit": p["unit"], "unit_norm": p.get("unit_norm"),
                "qty": p["qty"],
                "unit_price": p["unit_price"], "sum": p["sum"],
                "country": p["country"], "country_src": p.get("country_src"),
                "nkmi": p["nkmi"], "type": p["type"],
                "ru_name": p.get("ru_name"), "ru_number": p.get("ru_number"),
                "trademark": p.get("trademark"), "nkmi_name": p.get("nkmi"),
                "producer": p.get("producer"), "model": p.get("model"),
                "pos_src": p.get("pos_src"),
                "month": p["month"], "quarter": p["quarter"], "source": p["source"],
                "method": p["method"], "supplier": p["supplier"],
                "supplier_inn": p.get("supplier_inn"), "href": p.get("href"),
                "mixed": p.get("mixed", "нет"), "comment": p.get("comment"),
                "estimated": p["estimated"],
            }
            for p in sorted(all_positions, key=lambda x: -(x["sum"] or 0))
        ],
    }
    OUT.write_text(json.dumps(analytics, ensure_ascii=False, indent=1), encoding="utf-8")
    t = analytics["totals"]
    print(json.dumps(analytics["meta"], ensure_ascii=False, indent=1))
    print(json.dumps(t, ensure_ascii=False, indent=1))
    print("виды:")
    for r in by_kind:
        print(f"  {r['title'][:46]:<48}{r['sum']:>16,.0f}  {r['share']:>5.1f}%  n={r['n']}")
    print("категории (80 %):")
    for r in cat80:
        print(f"  {r['category'][:50]:<52}{r['sum']:>14,.0f}  {r['share']:>5.1f}%  cum={r['cum_share']:>5.1f}%")
    print(f"  ... всего категорий {len(by_cat)}, в 80 %-наборе {len(cat80)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "catalog":
        stage_catalog()
    else:
        stage_build()
