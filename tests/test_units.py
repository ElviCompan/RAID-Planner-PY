from __future__ import annotations

from ddp.units import format_gb_input, parse_gb_text, tb_to_bytes, TB, GB


def test_tb_to_bytes() -> None:
    assert tb_to_bytes(1) == TB
    assert tb_to_bytes(0) == 0


def test_parse_gb_text() -> None:
    assert parse_gb_text("12") == 12.0
    assert parse_gb_text("12,5") == 12.5
    assert parse_gb_text("10 ГБ") == 10.0
    assert parse_gb_text("10GB") == 10.0
    assert parse_gb_text("") is None
    assert parse_gb_text("-1") is None
    assert parse_gb_text("abc") is None


def test_format_gb_input() -> None:
    assert format_gb_input(10.0) == "10"
    assert format_gb_input(10.5) == "10.5"
    assert GB == 2**30
