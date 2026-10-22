"""Последовательный сбор всех контрактов 2025 года: 44-ФЗ, затем 223-ФЗ.

Запускается в фоне на несколько часов. Останавливается по Ctrl-C;
повторный запуск продолжит с недособранных контрактов (jsonl уже есть).
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect  # noqa: E402
import collect223  # noqa: E402
from eis_client import warmup  # noqa: E402


def main() -> None:
    started = time.time()
    warmup()
    for name, fn in (("44-ФЗ", collect.stage_cards), ("223-ФЗ", collect223.stage_cards)):
        print(f"=== {name}: старт {time.strftime('%H:%M:%S')} ===", flush=True)
        try:
            fn()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
        print(f"=== {name}: готово {time.strftime('%H:%M:%S')} ===", flush=True)
    print(f"всего {(time.time() - started) / 3600:.1f} ч", flush=True)


if __name__ == "__main__":
    main()
