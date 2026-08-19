"""Раскладка LUN: сначала ещё свободные диски группы, затем наименее заполненные."""

from __future__ import annotations

from dataclasses import dataclass

from ddp.raid import data_disks, extent_bytes, parity_kind, usable_from_extent


@dataclass
class Segment:
    lun_index: int
    name: str
    color: str
    size: int
    parity_kind: str = ""


@dataclass
class LunSpec:
    name: str
    color: str
    raid_type: str
    width: int
    usable: int


def pick_disks(
    free: list[int],
    extent: int,
    width: int,
    segments: list[list[Segment]],
) -> list[int] | None:
    """Сначала диски без страйпов, затем наименее заполненные.

    «Свободный» диск — на нём ещё нет страйпов предыдущих LUN. Если таких
    меньше, чем width, добираем уже занятые: больше свободного остатка
    (меньше занято), при равенстве — меньший индекс (слева направо).
    Итоговый набор сортируется по индексу диска, чтобы данные/чётность
    шли слева направо.
    """
    if extent <= 0 or width <= 0 or width > len(free):
        return None
    unused = [i for i, segs in enumerate(segments) if not segs and free[i] >= extent]
    used = [i for i, segs in enumerate(segments) if segs and free[i] >= extent]
    used.sort(key=lambda i: (-free[i], i))
    chosen = unused + used
    if len(chosen) < width:
        return None
    picked = chosen[:width]
    picked.sort()
    return picked


def max_extent(free: list[int], width: int) -> int:
    if width <= 0 or width > len(free):
        return 0
    return sorted(free, reverse=True)[width - 1]


def remaining_max_usable(free: list[int], raid_type: str, width: int) -> int:
    """Максимальная полезная нагрузка следующего LUN при текущих остатках."""
    return usable_from_extent(max_extent(free, width), raid_type, width)


def try_place_lun(
    free: list[int],
    segments: list[list[Segment]],
    lun: LunSpec,
    lun_index: int,
) -> bool:
    """Разместить один LUN. Меняет free и segments. False — не влез."""
    ext = extent_bytes(lun.usable, lun.raid_type, lun.width)
    if ext <= 0:
        return False
    chosen = pick_disks(free, ext, lun.width, segments)
    if chosen is None:
        return False
    for j, d in enumerate(chosen):
        segments[d].append(
            Segment(
                lun_index=lun_index,
                name=lun.name,
                color=lun.color,
                size=ext,
                parity_kind=parity_kind(lun.raid_type, j, lun.width),
            )
        )
        free[d] -= ext
    return True


def place_luns(
    disk_count: int, disk_bytes: int, luns: list[LunSpec]
) -> tuple[list[list[Segment]], list[int]]:
    """Разложить LUN-ы по порядку: свободные диски первыми."""
    free = [disk_bytes] * disk_count
    segments: list[list[Segment]] = [[] for _ in range(disk_count)]
    for i, lun in enumerate(luns):
        try_place_lun(free, segments, lun, i)
    return segments, free
