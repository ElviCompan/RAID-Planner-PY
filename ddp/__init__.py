"""Доменная логика планировщика DDP: единицы, RAID, раскладка LUN."""

from ddp.placement import (
    LunSpec,
    Segment,
    max_extent,
    place_luns,
    remaining_max_usable,
    try_place_lun,
)
from ddp.raid import (
    RAID_TYPES,
    data_disks,
    extent_bytes,
    min_width,
    normalize_width,
    parity_disks,
    parity_kind,
    suggest_width,
    usable_from_extent,
)
from ddp.units import (
    GB,
    TB,
    format_bytes,
    format_gb,
    format_gb_input,
    format_gb_tb,
    format_tb,
    parse_gb_text,
    tb_to_bytes,
)

__all__ = [
    "GB",
    "LUN_PALETTE",
    "LunSpec",
    "RAID_TYPES",
    "Segment",
    "TB",
    "data_disks",
    "extent_bytes",
    "format_bytes",
    "format_gb",
    "format_gb_input",
    "format_gb_tb",
    "format_tb",
    "max_extent",
    "min_width",
    "normalize_width",
    "parity_disks",
    "parity_kind",
    "parse_gb_text",
    "place_luns",
    "remaining_max_usable",
    "suggest_width",
    "tb_to_bytes",
    "try_place_lun",
    "usable_from_extent",
]

LUN_PALETTE = (
    "#2563eb",
    "#dc2626",
    "#16a34a",
    "#d97706",
    "#7c3aed",
    "#0891b2",
    "#ea580c",
    "#db2777",
    "#0d9488",
    "#65a30d",
)
