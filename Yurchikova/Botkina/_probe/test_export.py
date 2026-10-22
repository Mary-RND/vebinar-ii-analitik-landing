"""Проверка таблиц дашборда: поиск внутри таблицы, сортировка, лимит строк, экспорт Excel/CSV.

XLSX открывается openpyxl — подтверждаем, что файл валиден, числа остались числами,
в шапке есть дата выгрузки и источник, а число строк совпадает с таблицей на экране.
"""
from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path

from openpyxl import load_workbook
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "output"
DL = ROOT / "_probe" / "downloads"
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
OK = True


def say(flag: bool, label: str, detail: str = "") -> bool:
    global OK
    OK &= bool(flag)
    print(f"[{'ok ' if flag else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    return flag


def serve(port: int = 8751):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{port}/dashboard.html"


def main() -> None:
    DL.mkdir(parents=True, exist_ok=True)
    for f in DL.glob("*"):
        f.unlink()
    httpd, url = serve()
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        ctx = browser.new_context(viewport={"width": 1500, "height": 950},
                                  accept_downloads=True)
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url, wait_until="load")
        page.wait_for_selector("#kpis .kpi", timeout=20000)
        extract = page.evaluate("DATA.meta.extracted_at")
        reg_n = page.evaluate("DATA.totals.positions_in_scope")

        # 1. панели управления над таблицами
        bars = page.locator(".tbar").count()
        say(bars == 6, "панели над таблицами", f"найдено {bars}, ожидалось 6")
        cnt = page.locator('[data-tcnt="cat"]').inner_text()
        say("строк" in cnt, "счётчик строк у таблицы категорий", cnt)

        # 2. поиск внутри таблицы категорий
        base_rows = page.locator("#catTable tbody tr").count()
        page.fill('[data-tsearch="cat"]', "реагент")
        page.wait_for_timeout(500)
        hit_rows = page.locator("#catTable tbody tr").count()
        cnt2 = page.locator('[data-tcnt="cat"]').inner_text()
        footer_lbl = page.locator("#catTable tfoot tr td").nth(1).inner_text()
        say(0 < hit_rows < base_rows and cnt2.startswith("Показано"),
            "поиск по таблице сузил строки", f"{base_rows} -> {hit_rows}; {cnt2}")
        say(footer_lbl == "Итого по фильтру таблицы", "итог пересчитан по фильтру таблицы", footer_lbl)
        # поиск не трогает другие таблицы
        other = page.locator("#itemsTable tbody tr").count()
        say(other > 0, "другая таблица не пострадала", f"строк в номенклатуре: {other}")
        page.fill('[data-tsearch="cat"]', "")
        page.wait_for_timeout(500)
        say(page.locator("#catTable tbody tr").count() == base_rows,
            "сброс поиска вернул строки", f"{page.locator('#catTable tbody tr').count()}")

        # 3. сортировка со стрелкой
        page.click('#itemsTable th[data-k="name"]')
        page.wait_for_timeout(300)
        d1 = page.get_attribute('#itemsTable th[data-k="name"]', "data-dir")
        first = page.locator("#itemsTable tbody tr td").nth(1).inner_text()
        page.click('#itemsTable th[data-k="name"]')
        page.wait_for_timeout(300)
        d2 = page.get_attribute('#itemsTable th[data-k="name"]', "data-dir")
        say(d1 == "asc" and d2 == "desc", "сортировка по столбцу (▲/▼)", f"{d1} -> {d2}, первая: {first[:40]}")

        # 4. лимит строк
        sel = page.locator('[data-tlimit="items"]')
        sel.select_option("100")
        page.wait_for_timeout(400)
        n100 = page.locator("#itemsTable tbody tr").count()
        say(n100 == 100, "лимит 100 строк", f"в таблице {n100}")
        sel.select_option("0")
        page.wait_for_timeout(400)
        n_all = page.locator("#itemsTable tbody tr").count()
        say(n_all > 300, "«все строки» снимает лимит", f"в таблице {n_all}")

        # 5. Excel по таблице (категории)
        with page.expect_download(timeout=30000) as di:
            page.click('[data-xlsx="cat"]')
        path1 = DL / "cat.xlsx"
        di.value.save_as(str(path1))
        wb = load_workbook(path1)
        sh = wb["Категории"]
        say(len(wb.sheetnames) == 1, "файл одной таблицы — один лист", ", ".join(wb.sheetnames))
        say("Анализ закупок" in str(sh.cell(1, 1).value) and
            extract in str(sh.cell(2, 1).value),
            "шапка листа: название и дата выгрузки", str(sh.cell(2, 1).value)[:70])
        header_row = [c.value for c in sh[5]]
        say(header_row[1] == "Товарная группа", "строка заголовков — 5-я", str(header_row[:3]))
        nums = [c.value for c in sh["C"][5:] if isinstance(c.value, (int, float))]
        say(len(nums) >= 5, "суммы остались числами", f"числовых ячеек {len(nums)}, пример {nums[:2]}")
        say(sh.freeze_panes == "A6" and sh.auto_filter.ref is not None,
            "закреплённая шапка и автофильтр", f"{sh.freeze_panes}, {sh.auto_filter.ref}")
        xrows = sh.max_row
        say(xrows > 8, "строк в выгрузке", f"{xrows}")

        # 6. CSV по таблице
        with page.expect_download(timeout=30000) as di2:
            page.click('[data-csvx="items"]')
        path2 = DL / "items.csv"
        di2.value.save_as(str(path2))
        raw = path2.read_bytes()
        say(raw.startswith(b"\xef\xbb\xbf") and b";" in raw[:200],
            "CSV: UTF-8 с BOM и разделитель «;»", f"{len(raw)} байт")

        # 7. экспорт всего отчёта
        with page.expect_download(timeout=60000) as di3:
            page.click("#xlsx")
        path3 = DL / "report.xlsx"
        di3.value.save_as(str(path3))
        wb3 = load_workbook(path3, read_only=True)
        need = ["Описание", "Показатели", "Категории", "Номенклатура", "Бенчмарки", "Страны", "Реестр"]
        miss = [s for s in need if s not in wb3.sheetnames]
        say(not miss, "весь отчёт: все листы", ", ".join(wb3.sheetnames))
        reg = wb3["Реестр"]
        reg_rows = reg.max_row
        say(reg_rows == reg_n + 5, "в отчёт попал полный реестр",
            f"{reg_rows} строк с шапкой ({reg_n} данных)")
        desc = wb3["Описание"]
        vals = [str(c.value) for row in desc.iter_rows(min_row=6, max_row=17, max_col=2) for c in row]
        say(any("без фильтров" in v for v in vals) or any("фильтр" in v.lower() for v in vals),
            "в описании указан активный срез", next((v for v in vals if "фильтр" in v.lower()), "?")[:60])
        wb3.close()

        # 8. поиск по реестру
        page.fill('[data-tsearch="reg"]', "катетер")
        page.wait_for_timeout(700)
        hint = page.locator("#regHint").inner_text()
        say("из" in hint, "поиск в реестре сужает строки", hint[:80])

        # 9. чистота консоли
        say(not errors, "консоль без ошибок", "; ".join(errors[:3]))

        page.screenshot(path=str(ROOT / "output" / "tables_filters.png"))
        browser.close()
    httpd.shutdown()
    print("\nИТОГ:", "все проверки прошли" if OK else "ЕСТЬ ПРОБЛЕМЫ")


if __name__ == "__main__":
    main()
