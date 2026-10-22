"""Клиент ЕИС (zakupki.gov.ru) с дисковым кэшем, валидацией ответов и мягким троттлингом.

Особенности:
  * кэш: data/raw/<sha1(url)>.html (повторный запуск не ходит в сеть);
  * страницы-заглушки ЕИС («подозрительная активность», «страница не найдена»)
    не кэшируются и вызывают паузу с нарастающим интервалом;
  * троттлинг настраивается переменной окружения EIS_THROTTLE (сек).

Служебно:
  python eis_client.py purge    -- удалить из кэша страницы-заглушки
  python eis_client.py stats    -- статистика кэша
"""
from __future__ import annotations

import hashlib
import http.cookiejar
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://zakupki.gov.ru"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
INDEX = RAW / "_index.tsv"
COOKIES = RAW / "_cookies.txt"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Connection": "keep-alive",
}

BAD_MARKERS = ("подозрительная активность", "Страница не найдена", "Произошла ошибка")
MIN_LEN = 3000
THROTTLE = float(os.environ.get("EIS_THROTTLE", "7.0"))
COOLDOWN = float(os.environ.get("EIS_COOLDOWN", "60"))

_last_call = [0.0]
_jar = http.cookiejar.MozillaCookieJar(str(COOKIES))
if COOKIES.exists():
    try:
        _jar.load(ignore_discard=True, ignore_expires=True)
    except Exception:  # noqa: BLE001
        pass
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))


class FetchError(RuntimeError):
    pass


def is_bad(text: str) -> bool:
    return (len(text) < MIN_LEN) or any(m in text for m in BAD_MARKERS)


def _cache_path(url: str) -> Path:
    return RAW / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".html")


def _log(url: str, path: Path) -> None:
    with INDEX.open("a", encoding="utf-8") as fh:
        fh.write(f"{url}\t{path.name}\t{time.time():.0f}\n")


def fetch(url: str, *, cache: bool = True, throttle: float | None = None,
          retries: int = 4, timeout: int = 60) -> str:
    """GET с кэшем и валидацией. Возвращает HTML (utf-8)."""
    thr = THROTTLE if throttle is None else throttle
    path = _cache_path(url)
    if cache and path.exists():
        cached = path.read_text(encoding="utf-8", errors="replace")
        if not is_bad(cached):
            return cached
        path.unlink(missing_ok=True)

    last_err: Exception | None = None
    for attempt in range(retries):
        wait = thr - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with _opener.open(req, timeout=timeout) as resp:
                data = resp.read()
            _last_call[0] = time.time()
            text = data.decode("utf-8", errors="replace")
            if is_bad(text):
                last_err = FetchError(
                    "ЕИС вернул страницу-заглушку "
                    f"({'антибот' if 'подозрительная активность' in text else f'{len(text)} байт'})"
                )
                time.sleep(COOLDOWN * (attempt + 1))
                continue
            if cache:
                path.write_text(text, encoding="utf-8")
                _log(url, path)
            return text
        except urllib.error.HTTPError as exc:
            last_err = exc
            _last_call[0] = time.time()
            # 403/429 -> длинная пауза, остальные коды -> короткая
            pause = COOLDOWN * (attempt + 1) if exc.code in (403, 429, 503) else 2.0 * (attempt + 1)
            time.sleep(pause)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            _last_call[0] = time.time()
            time.sleep(2.0 * (attempt + 1))
    raise FetchError(f"{url}: {last_err}")


def warmup() -> None:
    """Открыть сессию на сайте: главная страница + сохранение куки."""
    if _jar:
        return
    try:
        req = urllib.request.Request(BASE + "/epz/main/public/home.html", headers=HEADERS)
        with _opener.open(req, timeout=60) as resp:
            resp.read()
        _jar.save(ignore_discard=True, ignore_expires=True)
        print("сессия ЕИС инициализирована")
    except Exception as exc:  # noqa: BLE001
        print("предупреждение: прогрев сессии не удался:", exc)


def purge() -> None:
    n = 0
    for p in RAW.glob("*.html"):
        txt = p.read_text(encoding="utf-8", errors="replace")
        if is_bad(txt):
            p.unlink()
            n += 1
    print(f"удалено страниц-заглушек: {n}")


def stats() -> None:
    files = list(RAW.glob("*.html"))
    bad = sum(1 for p in files if is_bad(p.read_text(encoding="utf-8", errors="replace")))
    size = sum(p.stat().st_size for p in files) / 1e6
    print(f"файлов в кэше: {len(files)}, заглушек: {bad}, объём: {size:.1f} МБ")


def absolute(url: str) -> str:
    return url if url.startswith("http") else BASE + url


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    purge() if cmd == "purge" else stats()
