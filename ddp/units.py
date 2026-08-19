"""Двоичные единицы объёма (ГиБ/ТиБ). В интерфейсе пока подписываются как ГБ/ТБ."""

from __future__ import annotations

GB = 2**30
TB = 2**40


def tb_to_bytes(tb: float) -> int:
    """ТБ (двоичные, 2**40) → байты."""
    return int(tb * TB)


def format_bytes(n: int) -> str:
    """Человекочитаемый объём в байтах с разделителями тысяч."""
    return f"{n:,}".replace(",", " ")


def format_tb(bytes_val: int) -> str:
    """Байты → ТБ (÷ 2**40)."""
    return f"{bytes_val / TB:.3f}"


def format_gb(bytes_val: int) -> str:
    """Байты → ГБ (÷ 2**30)."""
    return f"{bytes_val / GB:.0f}"


def format_gb_tb(bytes_val: int) -> str:
    """ГБ и ТБ в скобках — как у бегунка LUN: «56000 ГБ  (54.688 ТБ)»."""
    return f"{format_gb(bytes_val)} ГБ  ({format_tb(bytes_val)} ТБ)"


def parse_gb_text(text: str) -> float | None:
    """Разобрать объём в ГБ из поля ввода. None — пустое или некорректное значение."""
    s = str(text).strip().replace(",", ".")
    for suffix in ("ГиБ", "GiB", "ГБ", "GB", "гб", "gb"):
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
            break
    if not s:
        return None
    try:
        value = float(s)
    except (TypeError, ValueError):
        return None
    if value < 0 or value != value or value == float("inf"):
        return None
    return value


def format_gb_input(gb: float) -> str:
    """Число ГБ для поля ввода: целое без дроби, иначе без хвостовых нулей."""
    if abs(gb - round(gb)) < 1e-9:
        return str(int(round(gb)))
    return f"{gb:.3f}".rstrip("0").rstrip(".")
