from __future__ import annotations

from ddp.raid import (
    data_disks,
    extent_bytes,
    min_width,
    normalize_width,
    parity_disks,
    parity_kind,
    preferred_group_disks,
    suggest_width,
    usable_from_extent,
)


def test_raid1_nway_width() -> None:
    assert min_width("1") == 2
    assert suggest_width("1") == 2
    assert normalize_width("1", 2) == 2
    assert normalize_width("1", 3) == 3
    assert normalize_width("1", 5) == 5
    assert normalize_width("1", 1) == 2


def test_raid1_nway_capacity() -> None:
    assert data_disks("1", 2) == 1
    assert data_disks("1", 3) == 1
    assert data_disks("1", 4) == 1
    assert parity_disks("1", 4) == 3
    assert usable_from_extent(100, "1", 4) == 100


def test_raid1_parity_marks_mirrors() -> None:
    assert parity_kind("1", 0, 4) == ""
    assert parity_kind("1", 1, 4) == "P"
    assert parity_kind("1", 2, 4) == "P"
    assert parity_kind("1", 3, 4) == "P"


def test_raid10_still_pairs() -> None:
    assert normalize_width("10", 5) == 6
    assert data_disks("10", 6) == 3
    assert parity_disks("10", 6) == 3
    assert parity_kind("10", 0, 6) == ""
    assert parity_kind("10", 1, 6) == "P"
    assert parity_kind("10", 2, 6) == ""


def test_raid5_and_6() -> None:
    assert min_width("5") == 3
    assert data_disks("5", 4) == 3
    assert parity_disks("5", 4) == 1
    assert parity_kind("5", 3, 4) == "P"
    assert data_disks("6", 10) == 8
    assert parity_disks("6", 10) == 2
    assert parity_kind("6", 8, 10) == "P"
    assert suggest_width("6") == 10


def test_extent_truncates_remainder() -> None:
    assert extent_bytes(10, "0", 3) == 3
    assert usable_from_extent(3, "0", 3) == 9


def test_preferred_group_disks_caps_to_remaining() -> None:
    assert preferred_group_disks(20) == 10
    assert preferred_group_disks(10) == 10
    assert preferred_group_disks(3) == 3
    assert preferred_group_disks(0) == 0
    assert preferred_group_disks(-4) == 0
