"""Ширина страйпа, диски данных/чётности и размер куска LUN."""

from __future__ import annotations

RAID_TYPES = ("0", "1", "5", "6", "10")

# Типичный у нас RAID-6 8+2: группа и LUN сразу на 10 дисков.
DEFAULT_GROUP_DISKS = 10
DEFAULT_LUN_RAID = "6"
DEFAULT_LUN_WIDTH = 10


def preferred_group_disks(remaining: int, preferred: int = DEFAULT_GROUP_DISKS) -> int:
    """Сколько дисков дать новой группе: не больше остатка, вручную потом можно набрать больше."""
    return min(preferred, max(0, remaining))


def min_width(raid_type: str) -> int:
    rt = str(raid_type).strip().lower()
    if rt == "0":
        return 2
    if rt == "1":
        return 2
    if rt == "5":
        return 3
    if rt == "6":
        return 4
    if rt == "10":
        return 4
    return 2


def suggest_width(raid_type: str) -> int:
    rt = str(raid_type).strip().lower()
    if rt == "0":
        return 2
    if rt == "1":
        return 2
    if rt == "5":
        return 4
    if rt == "6":
        return DEFAULT_LUN_WIDTH
    if rt == "10":
        return 4
    return 2


def normalize_width(raid_type: str, width: int) -> int:
    """Минимальная ширина; RAID-10 — чётное число дисков.

    RAID-1 — N-стороннее зеркало: любое число дисков ≥ 2 (тройное, четверное и т.д.).
    """
    rt = str(raid_type).strip().lower()
    w = max(min_width(rt), width)
    if rt == "10" and w % 2:
        w += 1
    return w


def data_disks(raid_type: str, width: int) -> int:
    rt = str(raid_type).strip().lower()
    w = max(0, width)
    if rt == "0":
        return w
    if rt == "1":
        return 1 if w >= 2 else 0
    if rt == "10":
        return w // 2
    if rt == "5":
        return max(0, w - 1)
    if rt == "6":
        return max(0, w - 2)
    return w


def parity_disks(raid_type: str, width: int) -> int:
    return max(0, width - data_disks(raid_type, width))


def extent_bytes(usable: int, raid_type: str, width: int) -> int:
    n = data_disks(raid_type, width)
    if n <= 0 or usable <= 0:
        return 0
    return usable // n


def usable_from_extent(extent: int, raid_type: str, width: int) -> int:
    return extent * data_disks(raid_type, width)


def parity_kind(raid_type: str, index_in_stripe: int, width: int) -> str:
    """Метка страйпа: '' данные, 'P' чётность/зеркало."""
    rt = str(raid_type).strip().lower()
    if rt == "0":
        return ""
    if rt == "1":
        return "P" if index_in_stripe > 0 else ""
    if rt == "10":
        return "P" if index_in_stripe % 2 == 1 else ""
    if rt == "5":
        return "P" if index_in_stripe >= width - 1 else ""
    if rt == "6":
        return "P" if index_in_stripe >= width - 2 else ""
    return ""
