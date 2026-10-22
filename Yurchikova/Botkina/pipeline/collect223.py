"""Сбор реестра договоров 223-ФЗ по заказчику.

Отличия от 44-ФЗ:
  * адрес реестра: /epz/contractfz223/search/results.html;
  * фильтр по дате — дата размещения (publishDateFrom/To), а не дата заключения;
  * карточка: contract-info.html + contract-subject.html (перечень товаров);
  * в блоке выдачи сразу есть ИНН/КПП заказчика в ссылке на организацию.

Режимы:
  python collect223.py list [макс.страниц]
  python collect223.py cards [--limit N]
  python collect223.py reparse
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

from lxml import html as LH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from eis_client import fetch, warmup  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LPU = cfg.get()
D_DIR = ROOT / "data" / LPU["slug"]
D_DIR.mkdir(parents=True, exist_ok=True)
LIST_PATH = D_DIR / "contracts223_list.json"
JSONL_PATH = D_DIR / "contracts223.jsonl"
JSONL_REV_PATH = D_DIR / "contracts223_rev.jsonl"

BASE = "https://zakupki.gov.ru"
SEARCH = BASE + "/epz/contractfz223/search/results.html"
CARD = BASE + "/epz/contractfz223/card/{tab}.html?reestrNumber={rn}"

DATE_FROM = "01.11.2024"
DATE_TO = "31.03.2026"
TARGET_INN = LPU["inn"]
TARGET_KPP = LPU["kpp"]
TARGET_NAME = LPU["match"]

SPACES = re.compile(r"[\s\u00a0\u2009]+")


def norm(s: str) -> str:
    return SPACES.sub(" ", s or "").strip()


def money(s: str | None) -> float | None:
    if not s:
        return None
    m = re.search(r"-?\d[\d\s\u00a0]*(?:[.,]\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0).replace("\u00a0", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def serp_url(page: int) -> str:
    return (
        f"{SEARCH}?searchString={quote(LPU['query'])}&morphology=on"
        f"&publishDateFrom={DATE_FROM}&publishDateTo={DATE_TO}"
        f"&sortBy=UPDATE_DATE&recordsPerPage=_50&pageNumber={page}"
    )


# ---------------------------------------------------------------- список

def parse_block(block) -> dict | None:
    t = norm(block.text_content())
    hrefs = block.xpath(".//a/@href")
    card = next((h for h in hrefs if "/contractfz223/card/contract-info" in h), None)
    if not card:
        return None
    m = re.search(r"reestrNumber=(\d+)", card)
    if not m:
        return None
    rec: dict = {"reestr": m.group(1), "href": BASE + card}

    org = next((h for h in hrefs if "/organization/view223/info" in h), None)
    if org:
        mi = re.search(r"inn=(\d+)", org)
        mk = re.search(r"kpp=(\d+)", org)
        rec["customer_inn"] = mi.group(1) if mi else None
        rec["customer_kpp"] = mk.group(1) if mk else None

    def between(start: str, end: list[str]) -> str | None:
        i = t.find(start)
        if i < 0:
            return None
        i += len(start)
        j = len(t)
        for e in end:
            k = t.find(e, i)
            if k >= 0:
                j = min(j, k)
        return norm(t[i:j])

    rec["status"] = between("Исполнение", ["Номер договора"]) or None
    rec["contract_no"] = between("Номер договора", ["Заказчик"])
    rec["customer_name"] = between("Заказчик", ["Цена договора"])
    rec["price"] = money(between("Цена договора", ["Заключение договора"]))
    rec["signed_date"] = between("Заключение договора", ["Срок исполнения"])
    rec["due_date"] = between("Срок исполнения", ["Размещено"])
    rec["placed_date"] = between("Размещено", ["Обновлено"])
    rec["updated_date"] = between("Обновлено", ["Журнал событий"])
    return rec


def stage_list(max_pages: int = 40) -> None:
    out: list[dict] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        html = fetch(serp_url(page))
        doc = LH.fromstring(html)
        blocks = doc.xpath("//div[contains(@class,'search-registry-entry-block')]")
        if not blocks:
            print(f"page {page}: пусто -> стоп", flush=True)
            break
        got = 0
        for b in blocks:
            rec = parse_block(b)
            if not rec or rec["reestr"] in seen:
                continue
            is_target = (
                rec.get("customer_inn") == TARGET_INN
                or TARGET_NAME in (rec.get("customer_name") or "").upper()
            )
            if not is_target:
                continue
            seen.add(rec["reestr"])
            out.append(rec)
            got += 1
        print(f"page {page}: +{got} (всего {len(out)})", flush=True)
        if len(blocks) < 50:
            break
    LIST_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"итого {len(out)} -> {LIST_PATH}")


# ---------------------------------------------------------------- карточка

def parse_common(html: str) -> dict:
    doc = LH.fromstring(html)
    t = norm(doc.text_content())
    res: dict = {}
    res["method"] = (
        re.search(r"Способ закупки\s*(.+?)\s*Предмет договора", t) or [None, None]
    )[1]
    res["subject"] = (
        re.search(r"Предмет договора\s*(.+?)\s*Версия сведений", t) or [None, None]
    )[1]
    res["price"] = money((re.search(r"Цена договора\s*([\d\s\u00a0]+[.,]\d\d)", t) or [None, None])[1])
    res["signed_date"] = (re.search(r"Дата заключения договора\s*(\d{2}\.\d{2}\.\d{4})", t) or [None, None])[1]
    res["customer_inn"] = (re.search(r"ИНН\s*(\d{10})", t) or [None, None])[1]
    res["customer_kpp"] = (re.search(r"КПП\s*(\d{9})", t) or [None, None])[1]
    return {k: v for k, v in res.items() if v}


def parse_positions(html: str) -> list[dict]:
    doc = LH.fromstring(html)
    rows: list[dict] = []
    for table in doc.xpath("//table"):
        head = " | ".join(norm(th.text_content()) for th in table.xpath(".//thead//th"))
        if "Наименование товаров" not in head or "ОКПД2" not in head:
            continue
        for tr in table.xpath(".//tbody/tr"):
            cells = [norm(td.text_content()) for td in tr.xpath("./td")]
            if len(cells) < 7 or not re.match(r"^\d+$", cells[0]):
                continue
            pos: dict = {"n": int(cells[0])}
            body = cells[1]
            tm = re.search(r"Тип объекта закупки:\s*(.+)$", body)
            pos["type"] = norm(tm.group(1)) if tm else None
            pos["name"] = norm(body.split("Тип объекта закупки:")[0])
            om = re.match(r"^([\d.]+)\s*(.*)$", cells[2])
            pos["okpd2"] = om.group(1) if om else None
            pos["okpd2_name"] = norm(om.group(2)) if om else norm(cells[2])
            qm = re.match(r"^\s*([\d][\d\s\u00a0]*(?:[.,]\d+)?)\s*(.*)$", cells[3])
            pos["qty"] = money(qm.group(1)) if qm and qm.group(1).strip() else None
            pos["unit"] = norm(qm.group(2)) if qm else None
            pos["unit_price"] = money(cells[4])
            country = cells[5]
            cm = re.search(r"([А-ЯЁа-яё][А-ЯЁа-яё \-]+)\s*\((\d+)\)", country)
            pos["country"] = norm(cm.group(1)) if cm else (None if country.strip() == "-" else country)
            pos["country_code"] = cm.group(2) if cm else None
            pos["manufacturer_country"] = cells[6] if len(cells) > 6 else None
            pos["sum"] = money(cells[-1])
            pos["is_med"] = False
            rows.append(pos)
    return rows


def parse_all_positions(html: str, rn: str) -> list[dict]:
    """Все позиции договора: первая страница + пагинация списка предметов.

    В карточке 223-ФЗ таблица предметов по��азывается по 10 строк, остальные
    подгружаются запросом contract-subject-search.html (itemIndex, pageSize).
    """
    rows = parse_positions(html)
    try:
        doc = LH.fromstring(html)
        el = doc.xpath("//*[@id='ulrGetTable']")
        list_url = el[0].get("value") if el else None
    except Exception:  # noqa: BLE001
        list_url = None
    if not list_url:
        return rows
    full = list_url if list_url.startswith("http") else BASE + list_url
    sep = "&" if "?" in full else "?"
    seen = {r.get("n") for r in rows}
    index = len(rows)
    while index < 300:
        url = (f"{full}{sep}name=&withoutOkpd=off&okpd2Codes=&itemIndex={index}&pageSize=10")
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
        added = 0
        for r in extra:
            if r.get("n") not in seen:
                rows.append(r)
                seen.add(r.get("n"))
                added += 1
        if not added:
            break
        index += added
    return rows


def collect_card(rec: dict) -> dict:
    rn = rec["reestr"]
    out = dict(rec)
    try:
        out.update(parse_common(fetch(CARD.format(tab="contract-info", rn=rn))))
    except Exception as exc:  # noqa: BLE001
        out["error_common"] = str(exc)[:200]
    try:
        out["positions"] = parse_all_positions(
            fetch(CARD.format(tab="contract-subject", rn=rn)), rn)
    except Exception as exc:  # noqa: BLE001
        out["error_positions"] = str(exc)[:200]
        out["positions"] = []
    return out


def stage_cards(limit: int | None = None, reverse: bool = False) -> None:
    recs = json.loads(LIST_PATH.read_text(encoding="utf-8"))
    recs = [r for r in recs if (r.get("signed_date") or "").endswith(cfg.DATE_TO[-4:])]
    if reverse:
        recs = list(reversed(recs))
    out_path = JSONL_REV_PATH if reverse else JSONL_PATH
    if limit:
        recs = recs[:limit]
    done: set[str] = set()
    for path in (JSONL_PATH, JSONL_REV_PATH):
        if not path.exists():
            continue
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


def stage_merge() -> None:
    """Слить contracts223_rev.jsonl в contracts223.jsonl (без дублей)."""
    recs: dict[str, dict] = {}
    order: list[str] = []
    for path in (JSONL_PATH, JSONL_REV_PATH):
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
            elif len(r.get("positions") or []) > len(recs[rn].get("positions") or []):
                recs[rn] = r
    tmp = JSONL_PATH.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(recs[rn], ensure_ascii=False) for rn in order) + "\n",
                   encoding="utf-8")
    tmp.replace(JSONL_PATH)
    print(f"слито: {len(order)} договоров -> {JSONL_PATH}")


def stage_reparse() -> None:
    recs = json.loads(LIST_PATH.read_text(encoding="utf-8"))
    tmp = JSONL_PATH.with_suffix(".jsonl.tmp")
    n = 0
    with tmp.open("w", encoding="utf-8") as fh:
        for rec in recs:
            rn = rec["reestr"]
            card = dict(rec)
            try:
                card.update(parse_common(fetch(CARD.format(tab="contract-info", rn=rn))))
                card["positions"] = parse_all_positions(
                    fetch(CARD.format(tab="contract-subject", rn=rn)), rn)
            except Exception as exc:  # noqa: BLE001
                card["error"] = str(exc)[:200]
                card["positions"] = []
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")
            n += 1
    tmp.replace(JSONL_PATH)
    print(f"пересобрано {n} -> {JSONL_PATH}")


def stage_fixgaps() -> None:
    """Дозагрузка позиций договоров, где сумма позиций меньше цены договора.

    Причина — обрезанная пагинация списка предметов (по 10 строк на странице).
    """
    state_path = ROOT / "_probe" / "fixgaps223_state.json"
    done: set[str] = set()
    if state_path.exists():
        st = json.loads(state_path.read_text(encoding="utf-8"))
        done = set(st.get("done", []))
    recs = []
    for line in JSONL_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                recs.append(json.loads(line))
            except Exception:  # noqa: BLE001
                continue
    todo = []
    for r in recs:
        if r["reestr"] in done:
            continue
        pos = r.get("positions") or []
        if not pos:
            continue  # спецификация не опубликована: сумма оценивается в analyze.py
        price = r.get("price") or 0
        psum = sum((p.get("qty") or 0) * (p.get("unit_price") or 0) for p in pos)
        if price - psum > 1:
            todo.append(r)
    print(f"договоров: {len(recs)}, к дозагрузке: {len(todo)}")

    def flush() -> None:
        JSONL_PATH.write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in recs) + "\n", encoding="utf-8")
        state_path.write_text(json.dumps({"done": sorted(done)}, ensure_ascii=False), encoding="utf-8")

    fixed = 0
    for i, r in enumerate(todo, 1):
        try:
            html = fetch(CARD.format(tab="contract-subject", rn=r["reestr"]))
            newpos = parse_all_positions(html, r["reestr"]) if html else []
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {r['reestr']}: {exc}")
            newpos = []
        old = sum((p.get("qty") or 0) * (p.get("unit_price") or 0)
                  for p in r.get("positions") or [])
        new = sum((p.get("qty") or 0) * (p.get("unit_price") or 0) for p in newpos)
        if newpos and new > old:
            r["positions"] = newpos
            fixed += 1
        done.add(r["reestr"])
        if i % 10 == 0 or i == len(todo):
            flush()
            print(f"  [{i}/{len(todo)}] восстановлено: {fixed}")
    flush()
    print(f"готово: восстановлено {fixed} из {len(todo)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "list"
    warmup()
    if cmd == "list":
        stage_list(int(args[1]) if len(args) > 1 else 40)
    elif cmd == "cards":
        stage_cards(int(args[1]) if len(args) > 1 else None)
    elif cmd == "cards_rev":
        stage_cards(int(args[1]) if len(args) > 1 else None, reverse=True)
    elif cmd == "merge":
        stage_merge()
    elif cmd == "reparse":
        stage_reparse()
    elif cmd == "fixgaps":
        stage_fixgaps()
