"""Сборка веб-публикуемой версии дашборда под паролем.

Дашборд шифруется AES-256-GCM, ключ выводится из пароля через PBKDF2-HMAC-SHA-256.
В каталоге публикации оказываются только шлюз `index.html` и шифротекст `payload.bin`:
без пароля данные недоступны, даже скачав файлы сайта напрямую.

Использование:
    python pipeline/build_web.py --password "сложноеПароле2026"
    BOTKINA_WEB_PASSWORD=... python pipeline/build_web.py

Выход: output/web/ (index.html, payload.bin, README.md)
"""
from __future__ import annotations

import argparse
import os
import secrets
import sys
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "dashboard.html"
OUT = ROOT / "output" / "web"

SALT_LEN, IV_LEN, ITERATIONS = 16, 12, 250_000
GATE = ROOT / "pipeline" / "web_gate.html"
README_SRC = ROOT / "pipeline" / "web_README.md"


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                     iterations=ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


def encrypt(payload: bytes, password: str) -> bytes:
    salt = secrets.token_bytes(SALT_LEN)
    iv = secrets.token_bytes(IV_LEN)
    key = derive_key(password, salt)
    ct = AESGCM(key).encrypt(iv, payload, None)
    return salt + iv + ct


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--password", default=os.environ.get("BOTKINA_WEB_PASSWORD"))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--repo", default=str(ROOT / "output" / "botkina-dashboard"),
                    help="каталог-репозиторий для публикации на GitVerse Pages")
    args = ap.parse_args()

    if not args.password:
        sys.exit("укажите пароль: --password \"...\" или переменная BOTKINA_WEB_PASSWORD")
    if len(args.password) < 8:
        sys.exit("пароль слишком короткий: минимум 8 символов")
    if not SRC.exists():
        sys.exit(f"нет файла {SRC} — сначала соберите дашборд")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    raw = SRC.read_bytes()
    blob = encrypt(raw, args.password)
    (out / "payload.bin").write_bytes(blob)

    gate = GATE.read_text(encoding="utf-8")
    gate = (gate
            .replace("__ITERATIONS__", str(ITERATIONS))
            .replace("__BUILT__", date.today().strftime("%d.%m.%Y"))
            .replace("__SIZE_MB__", f"{len(raw) / 1024 / 1024:.1f}".replace(".", ","))
            .replace("__TITLE__", "Анализ закупок МНКЦ им. С.П. Боткина — 2025"))
    (out / "index.html").write_text(gate, encoding="utf-8", newline="\n")

    (out / "README.md").write_text(
        README_SRC.read_text(encoding="utf-8").replace("__BUILT__", date.today().strftime("%d.%m.%Y")),
        encoding="utf-8", newline="\n")

    wf_dir = out / ".gitverse" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "publish-pages.yml").write_text(
        (ROOT / "pipeline" / "web_workflow.yml").read_text(encoding="utf-8"),
        encoding="utf-8", newline="\n")

    print(f"-> {out / 'index.html'} ({(out / 'index.html').stat().st_size / 1024:.0f} КБ)")
    print(f"-> {out / 'payload.bin'} ({len(blob) / 1024 / 1024:.1f} МБ)")
    print(f"алгоритм: AES-256-GCM, ключ — PBKDF2-HMAC-SHA-256, {ITERATIONS:,} итераций".replace(",", " "))

    # --- папка-репозиторий для GitVerse Pages ---
    import shutil
    import subprocess

    repo = Path(args.repo)

    def git(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(repo), *a], check=check,
                              capture_output=True, text=True, encoding="utf-8")

    def ident(key: str, default: str) -> str:
        r = subprocess.run(["git", "-C", str(ROOT), "config", key],
                           capture_output=True, text=True, encoding="utf-8")
        return (r.stdout or "").strip() or default

    repo.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "payload.bin", "README.md"):
        shutil.copy2(out / name, repo / name)
    wf = repo / ".gitverse" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out / ".gitverse" / "workflows" / "publish-pages.yml", wf / "publish-pages.yml")
    (repo / ".gitignore").write_text(
        "# Сайт статический, ничего не собирается\n*.log\n", encoding="utf-8", newline="\n")

    print(f"-> репозиторий: {repo} "
          f"({sum(f.stat().st_size for f in repo.rglob('*') if f.is_file()) / 1024 / 1024:.1f} МБ)")

    if not (repo / ".git").exists():
        git("init", "-b", "main")
    # автор берётся из конфига основного репозитория проекта (он задан локально)
    if not (git("config", "user.email", check=False).stdout or "").strip():
        git("config", "user.name", ident("user.name", "Marina Petrushina"))
        git("config", "user.email", ident("user.email", "mar.petrushina@yandex.ru"))
    git("add", "-A")
    if git("status", "--porcelain").stdout.strip():
        git("commit", "-q", "-m",
            "feat: дашборд закупок МНКЦ им. С.П. Боткина за 2025 год под паролем",
            "-m", "Шлюз с проверкой пароля (AES-256-GCM) и зашифрованный дашборд; "
                  "публикация на GitVerse Pages workflow'ом из .gitverse/workflows/")
        print("   коммит создан (ветка main)")
    print("   git remote add origin https://gitverse.ru/<ЛОГИН>/botkina-dashboard.git")
    print("   git push -u origin main")


if __name__ == "__main__":
    main()
