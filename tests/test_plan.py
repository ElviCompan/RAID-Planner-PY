from __future__ import annotations

import json
from pathlib import Path

import pytest

from ddp.plan import PlanError, dumps_plan, loads_plan, parse_plan, write_plan, read_plan


def test_roundtrip() -> None:
    src = {
        "version": 1,
        "pool": {"disk_count": 20, "disk_tb": 14.0},
        "groups": [
            {
                "disk_count": 5,
                "luns": [{"raid": "1", "width": 3, "size_gb": 12.5}],
            }
        ],
    }
    back = loads_plan(dumps_plan(src))
    assert back["pool"]["disk_count"] == 20
    assert back["groups"][0]["luns"][0]["raid"] == "1"
    assert back["groups"][0]["luns"][0]["width"] == 3
    assert back["groups"][0]["luns"][0]["size_gb"] == 12.5


def test_empty_groups_gets_one() -> None:
    plan = parse_plan({"pool": {"disk_count": 8, "disk_tb": 2}, "groups": []})
    assert len(plan["groups"]) == 1
    assert plan["groups"][0]["disk_count"] == 10
    assert plan["groups"][0]["luns"] == []


def test_raid10_width_normalized() -> None:
    plan = parse_plan(
        {
            "pool": {"disk_count": 10, "disk_tb": 1},
            "groups": [{"disk_count": 6, "luns": [{"raid": "10", "width": 5, "size_gb": 1}]}],
        }
    )
    assert plan["groups"][0]["luns"][0]["width"] == 6


def test_bad_raid() -> None:
    with pytest.raises(PlanError):
        parse_plan(
            {
                "pool": {"disk_count": 1, "disk_tb": 1},
                "groups": [{"disk_count": 1, "luns": [{"raid": "99", "width": 2, "size_gb": 0}]}],
            }
        )


def test_bad_json() -> None:
    with pytest.raises(PlanError):
        loads_plan("{")


def test_file_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "plan.json"
    plan = parse_plan({"pool": {"disk_count": 4, "disk_tb": 1.5}, "groups": []})
    write_plan(path, plan)
    assert json.loads(path.read_text(encoding="utf-8"))["pool"]["disk_tb"] == 1.5
    assert read_plan(path)["pool"]["disk_count"] == 4
