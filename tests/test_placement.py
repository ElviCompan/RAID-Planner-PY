from __future__ import annotations

from ddp.placement import LunSpec, max_extent, pick_disks, place_luns, remaining_max_usable, try_place_lun
from ddp.raid import parity_kind


def _spec(name: str, raid: str, width: int, usable: int, color: str = "#000") -> LunSpec:
    return LunSpec(name=name, color=color, raid_type=raid, width=width, usable=usable)


def test_prefers_unused_disks() -> None:
    """Второй LUN садится на ещё пустые диски, а не докладывается слева."""
    segs, free = place_luns(
        disk_count=5,
        disk_bytes=1000,
        luns=[
            _spec("LUN1", "0", 2, 200),
            _spec("LUN2", "0", 2, 200),
        ],
    )
    lun1_disks = [i for i, row in enumerate(segs) if any(s.name == "LUN1" for s in row)]
    lun2_disks = [i for i, row in enumerate(segs) if any(s.name == "LUN2" for s in row)]
    assert lun1_disks == [0, 1]
    assert lun2_disks == [2, 3]
    assert free == [900, 900, 900, 900, 1000]


def test_fills_used_when_unused_not_enough() -> None:
    segs, _free = place_luns(
        disk_count=4,
        disk_bytes=1000,
        luns=[
            _spec("LUN1", "0", 3, 300),
            _spec("LUN2", "0", 3, 300),
        ],
    )
    lun2_disks = [i for i, row in enumerate(segs) if any(s.name == "LUN2" for s in row)]
    assert lun2_disks == [0, 1, 3]


def test_skip_if_cannot_place() -> None:
    segs, free = place_luns(
        disk_count=2,
        disk_bytes=100,
        luns=[_spec("LUN1", "0", 3, 50)],
    )
    assert segs == [[], []]
    assert free == [100, 100]


def test_raid1_three_way_mirror() -> None:
    segs, free = place_luns(
        disk_count=3,
        disk_bytes=1000,
        luns=[_spec("LUN1", "1", 3, 400)],
    )
    assert [len(row) for row in segs] == [1, 1, 1]
    assert [row[0].parity_kind for row in segs] == ["", "P", "P"]
    assert all(row[0].size == 400 for row in segs)
    assert free == [600, 600, 600]


def test_max_extent_is_wth_largest() -> None:
    assert max_extent([10, 50, 30, 40], 3) == 30
    assert remaining_max_usable([10, 50, 30, 40], "0", 3) == 90


def test_try_place_mutates() -> None:
    free = [100, 100, 100]
    segments: list[list] = [[], [], []]
    ok = try_place_lun(free, segments, _spec("LUN1", "5", 3, 80), 0)
    assert ok
    assert free == [60, 60, 60]
    assert parity_kind("5", 2, 3) == "P"
    assert segments[2][0].parity_kind == "P"


def test_pick_disks_sorts_by_index() -> None:
    free = [100, 100, 100]
    segments: list[list] = [[], [], []]
    picked = pick_disks(free, 10, 2, segments)
    assert picked == [0, 1]
