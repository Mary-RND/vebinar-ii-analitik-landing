"""Сборка защищённого сайта дашборда и папки-репозитория для GitVerse Pages.

Генерирует пароль (если не задан в BOTKINA_WEB_PASSWORD), запускает pipeline/build_web.py,
печатает пароль в консоль и кладёт его в файл передачи заказчику (в git не попадает).
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
ABC = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # без похожих 0/O/1/l
LOGIN = "marina-rnd"  # логин GitVerse для поддомена Pages (без точек)


def gen_password() -> str:
    tail = "".join(secrets.choice(ABC) for _ in range(10))
    # первая буква хвоста — строчная, остальные — как выпадут, для читаемости
    return "Botkina-2025-" + tail


def main() -> None:
    pw = os.environ.get("BOTKINA_WEB_PASSWORD") or gen_password()
    if len(pw) < 8:
        sys.exit("пароль короче 8 символов")

    env = dict(os.environ, BOTKINA_WEB_PASSWORD=pw, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "build_web.py"),
                        "--password", pw],
                       cwd=str(ROOT), env=env, capture_output=True, encoding="utf-8")
    sys.stdout.write(r.stdout)
    if r.returncode:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)

    # файл передачи заказчику: ссылка, пароль, как войти
    card = OUT / "Доступ_к_веб_дашборду.txt"
    card.write_text(
        "\n".join([
            "ДОСТУП К ИНТЕРАКТИВНОМУ ДАШБОРДУ",
            "Анализ закупок МНКЦ им. С.П. Боткина за 2025 год",
            f"Дата сборки: {date.today().strftime('%d.%m.%Y')}",
            "",
            "ССЫЛКА:  https://marina-rnd.gitverse.site/botkina-dashboard/",
            f"ПАРОЛЬ: {pw}",
            "",
            "Как войти:",
            "  1. Открыть ссылку в браузере (Chrome, Edge, Firefox или Safari).",
            "  2. Ввести пароль и нажать «Открыть».",
            "  3. Данные дашборда загрузятся в браузере (несколько секунд).",
            "",
            "Что можно делать:",
            "  - 9 разделов: показатели, структура и динамика, категории, номенклатура,",
            "    страны, бенчмарки, ключевые позиции, построчный реестр, методика;",
            "  - фильтры по виду закупки, товарной группе, стране, поставщику, сумме,",
            "    поиску по наименованию — все показатели пересчитываются;",
            "  - в каждой таблице: поиск по этой таблице, сортировка по столбцу (▲/▼),",
            "    выбор числа строк и выгрузка показанных строк в Excel или CSV;",
            "  - кнопка «Excel — весь отчёт» — один файл .xlsx на 7 листов по текущему срезу,",
            "    кнопка «CSV — реестр» — полный реестр позиций;",
            "  - темы (светлая/тёмная/системная), кнопка «Печать / PDF»;",
            "  - работает офлайн после входа, внешних запросов не делает.",
            "",
            "Если пароль не открывает страницу: проверить раскладку клавиатуры и регистр.",
            "Для смены пароля — обратитесь к аналитику (дашборд пересобирается под новый).",
        ]) + "\n",
        encoding="utf-8")

    print(f"файл передачи: {card}")
    print(f"ПАРОЛЬ ДЛЯ ЗАКАЗЧИКА: {pw}")
    # передаём пароль дальше в тест страницы входа
    (OUT / "_password.tmp").write_text(pw, encoding="utf-8")


if __name__ == "__main__":
    main()
