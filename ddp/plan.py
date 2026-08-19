"""Сохранение и загрузка плана (JSON)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ddp.raid import RAID_TYPES, normalize_width

PLAN_VERSION = 1
APP_DIR_NAME = "RAID-Planner"
AUTOSAVE_NAME = "autosave.json"


class PlanError(ValueError):
    """План повреждён или не того формата."""


def autosave_path() -> Path:
    roaming = os.environ.get("APPDATA")
    root = Path(roaming) if roaming else Path.home() / "AppData" / "Roaming"
    return root / APP_DIR_NAME / AUTOSAVE_NAME


def default_plan() -> dict[str, Any]:
    return {
        "version": PLAN_VERSION,
        "pool": {"disk_count": 20, "disk_tb": 14.0},
        "groups": [{"disk_count": 5, "luns": []}],
    }


def parse_plan(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PlanError("в корне JSON нужен объект")
    pool = raw.get("pool")
    if not isinstance(pool, dict):
        raise PlanError("нет блока pool")
    disk_count = _as_int(pool.get("disk_count"), "pool.disk_count")
    disk_tb = _as_float(pool.get("disk_tb"), "pool.disk_tb")
    if disk_count < 0 or disk_tb < 0:
        raise PlanError("число дисков и объём не могут быть отрицательными")

    groups_raw = raw.get("groups")
    if groups_raw is None:
        groups_raw = []
    if not isinstance(groups_raw, list):
        raise PlanError("groups должен быть списком")

    groups: list[dict[str, Any]] = []
    for i, g in enumerate(groups_raw):
        if not isinstance(g, dict):
            raise PlanError(f"groups[{i}] не объект")
        n = _as_int(g.get("disk_count"), f"groups[{i}].disk_count")
        if n < 0:
            raise PlanError(f"groups[{i}].disk_count отрицательный")
        luns_raw = g.get("luns") or []
        if not isinstance(luns_raw, list):
            raise PlanError(f"groups[{i}].luns должен быть списком")
        luns: list[dict[str, Any]] = []
        for j, lun in enumerate(luns_raw):
            if not isinstance(lun, dict):
                raise PlanError(f"groups[{i}].luns[{j}] не объект")
            raid = str(lun.get("raid", "0")).strip().lower()
            if raid not in RAID_TYPES:
                raise PlanError(f"неизвестный RAID: {raid}")
            width = normalize_width(raid, _as_int(lun.get("width"), f"lun.width"))
            size_gb = _as_float(lun.get("size_gb"), f"lun.size_gb")
            if size_gb < 0:
                raise PlanError("size_gb не может быть отрицательным")
            luns.append({"raid": raid, "width": width, "size_gb": size_gb})
        groups.append({"disk_count": n, "luns": luns})

    if not groups:
        groups = [{"disk_count": 5, "luns": []}]

    return {
        "version": PLAN_VERSION,
        "pool": {"disk_count": disk_count, "disk_tb": disk_tb},
        "groups": groups,
    }


def loads_plan(text: str) -> dict[str, Any]:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PlanError(f"некорректный JSON: {exc}") from exc
    return parse_plan(raw)


def dumps_plan(plan: dict[str, Any]) -> str:
    return json.dumps(parse_plan(plan), ensure_ascii=False, indent=2) + "\n"


def read_plan(path: Path) -> dict[str, Any]:
    return loads_plan(path.read_text(encoding="utf-8"))


def write_plan(path: Path, plan: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps_plan(plan), encoding="utf-8")


def _as_int(value: Any, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise PlanError(f"{name}: ожидалось целое") from exc


def _as_float(value: Any, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise PlanError(f"{name}: ожидалось число") from exc
