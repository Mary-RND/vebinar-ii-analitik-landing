"""Сбор данных ЕИС по одному заказчику.

Режимы:
  python collect.py list                 -- обойти реестр контрактов, сохранить список
  python collect.py cards [--limit N]    -- по каждому контракту собрать карточку и позиции
  python collect.py sample N             -- показать N случайных контрактов (отладка парсинга)
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from eis_client import BASE, fetch, warmup  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# значения ниже переопределяются set_lpu()
LPU_SLUG = cfg.DEFAULT_LPU
LPU = cfg.get(LPU_SLUG)
CUSTOMER = LPU["query"]
CUSTOMER_INN = LPU["inn"]
CUSTOMER_MATCH = LPU.get("match") or ""
DATE_FROM = cfg.DATE_FROM
DATE_TO = cfg.DATE_TO
D_DIR = DATA / LPU_SLUG
CONTRACTS_LIST = D_DIR / "contracts_list.json"
CONTRACTS_JSONL = D_DIR / "contracts.jsonl"
CARD = "https://zakupki.gov.ru/epz/contract/contractCard/{tab}.html?reestrNumber={rn}"
PRINT = "https://zakupki.gov.ru/epz/contract/printForm/view.html?contractReestrNumber={rn}"


def set_lpu(slug: str) -> None:
    global LPU_SLUG, LPU, CUSTOMER, CUSTOMER_INN, CUSTOMER_MATCH, D_DIR, CONTRACTS_LIST, CONTRACTS_JSONL
    LPU_SLUG = slug
    LPU = cfg.get(slug)
    CUSTOMER = LPU["query"]
    CUSTOMER_INN = LPU["inn"]
    CUSTOMER_MATCH = LPU.get("match") or ""
    D_DIR = DATA / slug
    D_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACTS_LIST = D_DIR / "contracts_list.json"
    CONTRACTS_JSONL = D_DIR / "contracts.jsonl"

SPACES = re.compile(r"[\s\u00a0\u2009]+")
NUM = re.compile(r"^-?[\d\s\u00a0]*[.,]?\d*$")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def money(s: str | None) -> float | None:
    if not s:
        return None
    s = norm(s).replace("\u00a0", " ").replace("₽", "").replace("RUB", "")
    m = re.search(r"-?\d[\d\s]*(?:[.,]\d+)?", s)
    if not m:
        return None
    v = m.group(0).replace(" ", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def text_of(el) -> str:
    return norm(el.text_content())


def serp_url(page: int) -> str:
    """URL выдачи реестра контрактов. EIS_STAGES — статусы контрактов (0,1,2,3)."""
    stages = os.environ.get("EIS_STAGES", "0,1,2,3")
    return (
        "https://zakupki.gov.ru/epz/contract/search/results.html"
        f"?searchString={quote(CUSTOMER)}&morphology=on&fz44=on&contractStageList={stages}"
        f"&contractDateFrom={DATE_FROM}&contractDateTo={DATE_TO}"
        f"&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber={page}"
    )


# ---------------------------------------------------------------- список

def parse_serp_block(block) -> dict:
    t = text_of(block)
    hrefs = block.xpath(".//a/@href")
    rec = {
        "href": next((h for h in hrefs if "contractCard/common-info" in h), None),
        "notice": next((h for h in hrefs if "/order/notice/view/common-info" in h), None),
        "rdik": next((h for h in hrefs if "/rdik/card/info" in h), None),
        "supplier_cards": [h for h in hrefs if "/organization/view/info" in h],
    }
    rec["reestr"] = (
        re.search(r"reestrNumber=(\d+)", rec["href"]).group(1) if rec["href"] else None
    )

    def between(start: str, end: list[str], src: str = t) -> str | None:
        i = src.find(start)
        if i < 0:
            return None
        i += len(start)
        j = len(src)
        for e in end:
            k = src.find(e, i)
            if k >= 0:
                j = min(j, k)
        return norm(src[i:j])

    rec["status"] = between("№ " + (rec["reestr"] or ""), ["Заказчик"])
    rec["customer_name"] = between("Заказчик", ["Контракт", "Объекты закупки"])
    rec["contract_no"] = between("Контракт №", ["Объекты закупки", "Объект закупки"])
    rec["subjects_preview"] = between(
        "Объекты закупки", ["Цена контракта", "Объект закупки"]
    )
    rec["price"] = money(between("Цена контракта", ["Заключение контракта"]))
    rec["signed_date"] = between("Заключение контракта", ["Срок исполнения"])
    rec["due_date"] = between("Срок исполнения", ["Размещен", "Обновлен"])
    rec["published_date"] = between("Размещен контракт в реестре контрактов", ["Обновлен"])
    rec["updated_date"] = between("Обновлен контракт в реестре контрактов", ["Вложения"])
    m = re.search(r"Посмотреть все \((\d+)\)", t)
    rec["subjects_count"] = int(m.group(1)) if m else 1
    return rec


def stage_list() -> None:
    out: list[dict] = []
    seen: set[str] = set()
    for page in range(1, 40):
        html = fetch(serp_url(page))
        doc = LH.fromstring(html)
        blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
        if not blocks:
            print(f"page {page}: пусто -> стоп")
            break
        got = 0
        skipped = 0
        for b in blocks:
            rec = parse_serp_block(b)
            if not rec["reestr"] or rec["reestr"] in seen:
                continue
            if CUSTOMER_MATCH and CUSTOMER_MATCH not in (rec.get("customer_name") or "").upper():
                skipped += 1
                continue
            seen.add(rec["reestr"])
            out.append(rec)
            got += 1
        print(f"page {page}: +{got} (всего {len(out)})" + (f", отсеяно {skipped}" if skipped else ""), flush=True)
        if len(blocks) < 50:
            break
    CONTRACTS_LIST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"итого контрактов: {len(out)} -> {CONTRACTS_LIST}")


# ---------------------------------------------------------------- карточка

def parse_common_info(html: str) -> dict:
    doc = LH.fromstring(html)
    t = text_of(doc.body if doc.body is not None else doc)
    res: dict = {}
    res["ikz"] = (re.search(r"ИКЗ\)\s*(\d{30,})", t) or [None, None])[1]
    res["econtract_id"] = (
        re.search(r"заключенного в электронной форме\s*(\d{15,})", t) or [None, None]
    )[1]
    res["plan_position"] = (
        re.search(r"Уникальный номер позиции плана-графика\s*(\d{15,})", t) or [None, None]
    )[1]
    res["price"] = money((re.search(r"Цена контракта\s*([\d\s\u00a0]+[.,]\d\d)", t) or [None, None])[1])
    res["signed_date"] = (re.search(r"Заключение контракта\s*(\d{2}\.\d{2}\.\d{4})", t) or [None, None])[1]
    res["due_date"] = (re.search(r"Срок исполнения\s*(\d{2}\.\d{2}\.\d{4})", t) or [None, None])[1]
    res["place"] = (re.search(r"Место поставки товара[^А-ЯЁ]*([^|]{5,200}?)(?:Информация о поставщиках|$)", t) or [None, None])[1]
    res["place"] = norm(res["place"]) if res["place"] else None
    # способ определения поставщика
    res["method"] = (
        re.search(r"Способ определения поставщика \(подрядчика, исполнителя\)\s*([^А-ЯЁ]{0,10}?[А-ЯЁ][^А-ЯЁ]{0,120})", t)
        or re.search(r"Способ определения поставщика[^А-ЯЁ]*([А-ЯЁ][^А-ЯЁ]{0,120})", t)
        or [None, None]
    )[1]
    res["method"] = norm(res["method"]) if res["method"] else None
    # заказчик
    res["customer_name"] = (
        re.search(r"Наименование заказчика\s*(.+?)(?:\(ФГБУ|Тип информации)", t) or [None, None]
    )[1]
    res["customer_name"] = norm(res["customer_name"]) if res["customer_name"] else None
    res["customer_inn"] = (re.search(r"ИНН\s*(\d{10})", t) or [None, None])[1]
    res["supplier"] = parse_supplier(t)
    return res


def parse_supplier(t: str) -> dict:
    """Блок 'Информация о поставщиках' карточки контракта."""
    out: dict = {}
    m_mark = re.search(r"[Ии]нформация о поставщик", t)
    if not m_mark:
        return out
    seg = t[m_mark.start():]
    m = re.search(r"ИНН:\s*(\d{10}|\d{12})(?:\s*КПП:\s*(\d{9}))?", seg)
    if not m:
        return out
    out["inn"] = m.group(1)
    if m.group(2) and m.group(2) != "-":
        out["kpp"] = m.group(2)
    before = seg[:m.start()]
    j = before.find("электронная почта")
    if j >= 0:
        before = before[j + len("электронная почта"):]
    # отбрасываем служебные заголовки таблицы, оставляя последний осмысленный фрагмент
    parts = [
        x.strip(" ,;·")
        for x in re.split(
            r"Организация|Страна, код|Адрес места нахождения|Почтовый адрес|"
            r"Телефон, электронная почта|Статус|Наименование организации",
            before,
        )
        if x.strip(" ,;·")
    ]
    name = parts[-1] if parts else before.strip()
    is_ip = "Индивидуальный предприниматель" in name
    name = norm(name.replace("Индивидуальный предприниматель", " "))
    if is_ip:
        name = "ИП " + name
    out["name"] = name
    out["is_ip"] = is_ip
    return out


def parse_positions(html: str) -> list[dict]:
    doc = LH.fromstring(html)
    rows: list[dict] = []
    for table in doc.xpath("//table"):
        head = " | ".join(text_of(th) for th in table.xpath(".//thead//th"))
        if "Цена за единицу" not in head:
            continue
        for tr in table.xpath(".//tbody/tr"):
            cells = [text_of(td) for td in tr.xpath("./td")]
            if len(cells) < 7 or not re.match(r"^\d+\.\s", cells[1] or ""):
                continue
            pos = parse_position_cells(cells)
            rows.append(pos)
    return rows


def parse_positions_total(html: str) -> int | None:
    doc = LH.fromstring(html)
    for table in doc.xpath("//table"):
        head = " | ".join(text_of(th) for th in table.xpath(".//thead//th"))
        if "Цена за единицу" not in head:
            continue
        foot = table.xpath(".//tfoot")
        t = text_of(foot[0]) if foot else ""
        m = re.search(r"Итого\s*\((\d+)\s+запис", t)
        if m:
            return int(m.group(1))
    return None


def parse_all_positions(html: str) -> list[dict]:
    """Все позиции карточки: первая страница + AJAX-страницы пагинации.

    В карточке 44-ФЗ таблица объектов закупки показывает 10 строк, остальные
    подгружаются через payment-info-and-target-of-order-list.html.
    При сбое загрузки страницы делаются повторы: иначе позиции контракта
    молча теряются, а сумма позиций расходится с ценой контракта.
    """
    rows = parse_positions(html)
    total = parse_positions_total(html)
    um = re.search(r'id="ulrRefresh"\s+value="([^"]+)"', html)
    if not total or total <= len(rows) or not um:
        return rows
    seen = {r.get("n") for r in rows}
    list_url = um.group(1)
    page = 2
    while len(rows) < total and page <= 60:
        url = BASE + list_url + f"&page={page}&pageSize=10"
        page_html = None
        for attempt in range(3):
            try:
                page_html = fetch(url)
                break
            except Exception:  # noqa: BLE001
                time.sleep(8 * (attempt + 1))
        if not page_html:
            break
        extra = parse_positions(page_html)
        if not extra:
            break
        for r in extra:
            if r.get("n") not in seen:
                rows.append(r)
                seen.add(r.get("n"))
        page += 1
    return rows


def parse_position_cells(cells: list[str]) -> dict:
    raw = cells[1]
    m = re.match(r"^(\d+)\.\s*(.*)$", raw, re.S)
    n = int(m.group(1)) if m else None
    body = norm(m.group(2)) if m else norm(raw)
    pos: dict = {"n": n}
    pos["is_med"] = "Медицинское изделие" in body

    # наименование изделия по регистрационному удостоверению (детализация до изделия/модели)
    rum = re.search(
        r"Наименование медицинского изделия в соответствии с регистрационным удостоверением:\s*(.+)$",
        body,
    )
    if rum:
        txt = rum.group(1)
        parts = re.split(r"Регистрационное удостоверение на медицинское изделие", txt)
        pos["ru_name"] = norm(parts[0].strip(" ;"))
        if len(parts) > 1:
            mm = re.search(r"№\s*([^\s;]+(?:\s+[^\s;]+)?)", parts[1])
            pos["ru_number"] = norm(mm.group(1)) if mm else None
            dm = re.search(r"от\s+(\d{1,2}\s+\S+\s+\d{4})", parts[1])
            pos["ru_date"] = dm.group(1) if dm else None
    # базовая часть наименования
    base = re.split(
        r"Товарный знак:|Медицинское изделие|Наименование медицинского изделия|Страна происхождения",
        body,
    )[0]
    pos["name"] = norm(base)
    tm = re.search(r"Товарный знак:\s*([^А-ЯЁ]{0,90}?)(?=Медицинское изделие|Наименование медицинского|Страна происхождения|$)", body)
    pos["trademark"] = norm(tm.group(1)) if tm else None
    nm = re.search(r"НКМИ:\s*(\d*)", body)
    pos["nkmi"] = nm.group(1) or None if nm else None
    cm = re.search(r"Страна происхождения:\s*(.+?)\s*\((\d+)\)", body)
    if not cm and len(cells) >= 8:
        cm = re.match(r"\s*(.+?),\s*\((\d+),?\)", cells[6] or "")
    pos["country"] = norm(cm.group(1)) if cm else None
    pos["country_code"] = cm.group(2) if cm else None
    pos["chars"] = body[:2000]

    kt = cells[2]
    km = re.search(r"\(\s*([\d.]+-\d+)\s*\)", kt)
    pos["ktru"] = km.group(1) if km else None
    om = re.search(r"\(([\d]{2}(?:\.\d+){1,5})\)\s*$", kt)
    if not om:
        om = re.search(r"\(([\d]{2}(?:\.\d+){1,5})\)", kt)
    pos["okpd2"] = om.group(1) if om else None
    pos["okpd2_name"] = norm(kt[:om.start()]) if om else norm(kt)
    pos["type"] = cells[3]
    qu = cells[4]
    qm = re.match(r"^\s*([\d][\d\s\u00a0]*(?:[.,]\d+)?)\s*(.*)$", qu)
    if qm and qm.group(1).strip():
        pos["qty"] = money(qm.group(1))
        pos["unit"] = norm(qm.group(2)) or None
    else:
        pos["qty"] = None
        pos["unit"] = qu or None
    pos["unit_price"] = money(cells[5])
    pos["sum"] = money(cells[-1])
    return pos


def parse_financing(print_html: str) -> dict:
    """График финансирования по годам (Раздел I печатной формы)."""
    doc = LH.fromstring(print_html)
    t = text_of(doc.body if doc.body is not None else doc)
    m = re.search(r"Раздел I[^.]{0,40}?График финансирования(.{0,1500}?)Раздел II", t, re.S)
    if not m:
        return {}
    return {"_fin_raw": norm(m.group(1))}


def collect_card(rec: dict) -> dict:
    rn = rec["reestr"]
    out = dict(rec)
    try:
        ci = fetch(CARD.format(tab="common-info", rn=rn))
        out.update({k: v for k, v in parse_common_info(ci).items() if v is not None})
    except Exception as exc:  # noqa: BLE001
        out["error_common"] = str(exc)[:200]
    try:
        pi = fetch(CARD.format(tab="payment-info-and-target-of-order", rn=rn))
        out["positions"] = parse_all_positions(pi)
        out["positions_total"] = parse_positions_total(pi)
    except Exception as exc:  # noqa: BLE001
        out["error_positions"] = str(exc)[:200]
        out["positions"] = []
    return out


def stage_cards(limit: int | None = None) -> None:
    recs = json.loads(CONTRACTS_LIST.read_text(encoding="utf-8"))
    if limit:
        recs = recs[:limit]
    done: set[str] = set()
    if CONTRACTS_JSONL.exists():
        for line in CONTRACTS_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    done.add(json.loads(line)["reestr"])
                except Exception:  # noqa: BLE001
                    pass
    with CONTRACTS_JSONL.open("a", encoding="utf-8") as fh:
        for i, rec in enumerate(recs, 1):
            if rec["reestr"] in done:
                continue
            card = collect_card(rec)
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")
            fh.flush()
            np_ = len(card.get("positions") or [])
            print(f"{i}/{len(recs)} {rec['reestr']} позиций={np_} "
                  f"поставщик={(card.get('supplier') or {}).get('inn')}", flush=True)
    print("готово")


def stage_sample(count: int) -> None:
    recs = json.loads(CONTRACTS_LIST.read_text(encoding="utf-8"))
    random.seed(7)
    for rec in random.sample(recs, min(count, len(recs))):
        card = collect_card(rec)
        print("=" * 100)
        print(card["reestr"], "|", card.get("contract_no"), "|", card.get("price"),
              "|", card.get("signed_date"), "|", (card.get("supplier") or {}).get("name", "")[:60])
        print("  заказчик:", (card.get("customer_name") or card.get("customer_name", ""))[:80])
        for p in card.get("positions", []):
            print(f"   [{p['n']}] {p['name'][:60]!r} | ktru={p['ktru']} okpd2={p['okpd2']} "
                  f"type={p['type']} qty={p['qty']} {p['unit']} price={p['unit_price']} sum={p['sum']} "
                  f"med={p['is_med']} nkmi={p['nkmi']} country={p['country']}")


def stage_retry() -> None:
    """Удалить из contracts.jsonl записи с ошибками, чтобы собрать их заново."""
    if not CONTRACTS_JSONL.exists():
        print("нет файла", CONTRACTS_JSONL)
        return
    keep, drop = [], 0
    for line in CONTRACTS_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:  # noqa: BLE001
            drop += 1
            continue
        if row.get("error_common") or row.get("error_positions"):
            drop += 1
            continue
        keep.append(line)
    CONTRACTS_JSONL.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
    print(f"оставлено {len(keep)}, удалено с ошибками {drop}")


def stage_reparse() -> None:
    """Пересобрать contracts.jsonl из закэшированных карточек (без сети)."""
    recs = json.loads(CONTRACTS_LIST.read_text(encoding="utf-8"))
    out_path = CONTRACTS_JSONL
    tmp = out_path.with_suffix(".jsonl.tmp")
    n, miss = 0, 0
    with tmp.open("w", encoding="utf-8") as fh:
        for rec in recs:
            rn = rec["reestr"]
            card = dict(rec)
            ci_html = fetch(CARD.format(tab="common-info", rn=rn))
            if not ci_html or len(ci_html) < 3000:
                miss += 1
                continue
            card.update({k: v for k, v in parse_common_info(ci_html).items() if v is not None})
            pi_html = fetch(CARD.format(tab="payment-info-and-target-of-order", rn=rn))
            card["positions"] = parse_all_positions(pi_html) if pi_html else []
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")
            n += 1
    tmp.replace(out_path)
    print(f"пересобрано {n} контрактов (пропущено {miss}) -> {out_path}")


def stage_cards_rev(out_name: str = "contracts_rev.jsonl") -> None:
    """Сбор карточек в обратном порядке — для параллельного второго прохода."""
    recs = json.loads(CONTRACTS_LIST.read_text(encoding="utf-8"))
    recs = list(reversed(recs))
    out_path = D_DIR / out_name
    done: set[str] = set()
    for path in (CONTRACTS_JSONL, out_path):
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        done.add(json.loads(line)["reestr"])
                    except Exception:  # noqa: BLE001
                        pass
    with out_path.open("a", encoding="utf-8") as fh:
        for i, rec in enumerate(recs, 1):
            if rec["reestr"] in done:
                continue
            card = collect_card(rec)
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"{i}/{len(recs)} {rec['reestr']} позиций={len(card.get('positions') or [])}",
                  flush=True)
    print("готово")


def stage_merge(files: list[str]) -> None:
    """Слить дополнительные jsonl в основной contracts.jsonl (без дублей)."""
    recs: dict[str, dict] = {}
    order: list[str] = []
    for name in ["contracts.jsonl"] + list(files):
        path = D_DIR / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            rn = r.get("reestr")
            if not rn:
                continue
            if rn not in recs:
                recs[rn] = r
                order.append(rn)
            else:
                old = recs[rn]
                if len(r.get("positions") or []) > len(old.get("positions") or []):
                    recs[rn] = r
    tmp = CONTRACTS_JSONL.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(recs[rn], ensure_ascii=False) for rn in order) + "\n",
                   encoding="utf-8")
    tmp.replace(CONTRACTS_JSONL)
    print(f"слито: {len(order)} контрактов -> {CONTRACTS_JSONL}")


def stage_fixgaps() -> None:
    """Дозагрузка позиций по контрактам, где позиции обрезаны пагинацией.

    В карточке 44-ФЗ таблица объектов закупки показывает по 10 строк, остальные
    подгружаются AJAX-пагинацией. При сбое загрузки страницы позиции терялись,
    и сумма позиций расходилась с ценой контракта. Здесь такие контракты
    находятся по «Итого (N записей)» в подвале таблицы и перезагружаются.

    Контракты, где суммы позиций не опубликованы вовсе, не трогаются: их
    суммы оцениваются в analyze.py.
    """
    state_path = ROOT / "_probe" / "fixgaps_state.json"
    done: set[str] = set()
    failed: list[str] = []
    if state_path.exists():
        st = json.loads(state_path.read_text(encoding="utf-8"))
        done = set(st.get("done", []))
        failed = list(st.get("failed", []))
    src_files = ["contracts.jsonl", "contracts_rev.jsonl"]
    files_recs: dict[str, list[dict]] = {}
    for name in src_files:
        path = D_DIR / name
        if not path.exists():
            continue
        recs: list[dict] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    recs.append(json.loads(line))
                except Exception:  # noqa: BLE001
                    continue
        files_recs[name] = recs
    todo = []
    for name, recs in files_recs.items():
        for r in recs:
            if r["reestr"] in done:
                continue
            price = r.get("price") or 0
            pos = r.get("positions") or []
            psum = sum((p.get("sum") or 0) for p in pos)
            if not any(p.get("sum") for p in pos):
                continue  # суммы не опубликованы — оцениваются в analyze.py
            if price - psum > 1:
                todo.append(r)
    print(f"всего контрактов: {sum(len(v) for v in files_recs.values())}, "
          f"к дозагрузке: {len(todo)}, уже обработано: {len(done)}")

    def flush() -> None:
        for name, recs in files_recs.items():
            (D_DIR / name).write_text(
                "\n".join(json.dumps(x, ensure_ascii=False) for x in recs) + "\n", encoding="utf-8")
        state_path.write_text(json.dumps(
            {"done": sorted(done), "failed": sorted(failed)}, ensure_ascii=False), encoding="utf-8")

    fixed = 0
    for i, r in enumerate(todo, 1):
        try:
            html = fetch(CARD.format(tab="payment-info-and-target-of-order", rn=r["reestr"]))
            total = parse_positions_total(html) if html else None
            if not total or total <= len(r.get("positions") or []):
                done.add(r["reestr"])   # обрезки нет — страницы не грузились зря
                continue
            newpos = parse_all_positions(html) if html else []
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {r['reestr']}: {exc}")
            newpos = []
            total = None
        old_sum = sum((p.get("sum") or 0) for p in r.get("positions") or [])
        new_sum = sum((p.get("sum") or 0) for p in newpos)
        if newpos and len(newpos) >= (total or 0) and new_sum > old_sum:
            r["positions"] = newpos
            r["positions_total"] = total
            fixed += 1
        elif total and len(newpos) < total:
            failed.append(r["reestr"])
        else:
            done.add(r["reestr"])
        if i % 10 == 0 or i == len(todo):
            flush()
            print(f"  [{i}/{len(todo)}] восстановлено: {fixed}, без изменений: {i - fixed}")
    flush()
    print(f"готово: восстановлено {fixed} из {len(todo)}, с ошибкой: {len(failed)}")
    if failed:
        print("не удалось:", ", ".join(failed))


def stage_verify() -> None:
    """Сверка сумм позиций с ценами контрактов (без обращения к сети)."""
    rows = []
    for name in ("contracts.jsonl", "contracts_rev.jsonl", "contracts223.jsonl"):
        path = D_DIR / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:  # noqa: BLE001
                    continue
    gaps = []
    for r in rows:
        price = r.get("price") or 0
        pos = r.get("positions") or []
        psum = sum((p.get("sum") or 0) for p in pos)
        with_sum = sum(1 for p in pos if p.get("sum"))
        if price - psum > 1 and with_sum:
            gaps.append((price - psum, r["reestr"], len(pos), with_sum))
    gaps.sort(reverse=True)
    print(f"контрактов: {len(rows)}, с расхождением (есть опубликованные суммы): {len(gaps)}")
    print(f"суммарное расхождение: {sum(g for g, _, _, _ in gaps):,.2f} ₽")
    for g, rn, npos, ns in gaps[:20]:
        print(f"  {g/1e6:10,.2f} млн | позиций {npos} (с суммой {ns}) | {rn}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--lpu" in args:
        i = args.index("--lpu")
        set_lpu(args[i + 1])
        del args[i:i + 2]
    cmd = args[0] if args else "list"
    warmup()
    if cmd == "list":
        stage_list()
    elif cmd == "cards":
        lim = int(args[1]) if len(args) > 1 else None
        stage_cards(lim)
    elif cmd == "reparse":
        stage_reparse()
    elif cmd == "fixgaps":
        stage_fixgaps()
    elif cmd == "verify":
        stage_verify()
    elif cmd == "cards_rev":
        stage_cards_rev()
    elif cmd == "merge":
        stage_merge(sys.argv[2:])
    elif cmd == "retry":
        stage_retry()
    elif cmd == "sample":
        stage_sample(int(args[1]) if len(args) > 1 else 3)
