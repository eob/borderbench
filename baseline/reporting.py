"""Shared scorecard integrity checks for report consumers."""

from __future__ import annotations

import json
from pathlib import Path

from baseline.evaluator import GRADING_VERSION, cohort_fingerprint, evaluation_protocol_fingerprint

DIMENSIONS = (
    "has_border",
    "border_sides",
    "stroke_style",
    "stroke_width",
    "corner_radius",
    "corner_uniformity",
    "elevation",
)


def read_report_json(path: Path, warnings: list[str]) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Expected an object")
        return value
    except (OSError, ValueError) as error:
        warnings.append(f"Excluded malformed {path.name}: {error}")
        return {}


def scorecard_tasks(card: dict, *, dataset_fingerprint: str) -> list[dict]:
    """Reject incomplete provenance and malformed rows before computing metrics."""
    tasks = card.get("tasks")
    if not isinstance(tasks, list) or any(not isinstance(task, dict) for task in tasks):
        raise ValueError("Malformed task rows")
    ids = [task.get("task_id") for task in tasks]
    if (any(not isinstance(task_id, str) or not task_id for task_id in ids)
            or len(set(ids)) != len(ids)
            or type(card.get("total_tasks")) is not int or card["total_tasks"] != len(tasks)
            or type(card.get("expected_task_count")) is not int
            or card["expected_task_count"] <= 0 or len(tasks) > card["expected_task_count"]):
        raise ValueError("Inconsistent task coverage")
    if (str(card.get("grading_version")) != GRADING_VERSION
            or card.get("evaluation_protocol") != evaluation_protocol_fingerprint()
            or card.get("dataset_fingerprint") != dataset_fingerprint
            or card.get("cohort_sha256") != cohort_fingerprint(ids)
            or not isinstance(card.get("mock"), bool)):
        raise ValueError("Incompatible dataset, protocol, or mock provenance")
    if card.get("status") not in ("complete", "partial") or (
            card["status"] == "complete" and len(tasks) != card["expected_task_count"]):
        raise ValueError("Inconsistent completion status")
    for task in tasks:
        if type(task.get("all_correct")) is not bool or any(
                type(task.get(f"{key}_correct")) is not bool for key in DIMENSIONS):
            raise ValueError("Invalid grading flags")
        if (task.get("error_kind") not in (None, "invalid_response")
                or task.get("error") and task.get("error_kind") != "invalid_response"):
            raise ValueError("Infrastructure failures are not completed measurements")
        if task.get("error_kind") == "invalid_response" and (
                task["all_correct"] or any(task[f"{key}_correct"] for key in DIMENSIONS)):
            raise ValueError("Invalid model answers must receive zero credit")
    return tasks


def metrics(tasks: list[dict]) -> dict:
    """Aggregate exact match and per-attribute accuracy over task rows."""
    total = len(tasks)
    if total == 0:
        return {"count": 0, "exact": None, **{key: None for key in DIMENSIONS}}
    exact = sum(1 for task in tasks if task["all_correct"]) / total
    return {
        "count": total,
        "exact": round(exact, 4),
        **{key: round(sum(1 for task in tasks if task[f"{key}_correct"]) / total, 4) for key in DIMENSIONS},
    }
