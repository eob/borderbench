"""Export integrity: metered costs, explicit inputs, malformed-row warnings."""

import json
import os
import time
from pathlib import Path

import pytest

from baseline.export_structured import build_structured_benchmark


def _scorecard(model_id: str, rows: list[dict], **overrides) -> dict:
    card = {
        "model_id": model_id,
        "model_name": model_id,
        "display_name": model_id,
        "provider": "google",
        "pricing": {"input_per_m": 2.0, "output_per_m": 12.0},
        "timestamp": "2026-09-10T00:00:00+00:00",
        "overall_exact_match": 100.0,
        "has_border_accuracy": 100.0,
        "border_sides_accuracy": 100.0,
        "stroke_style_accuracy": 100.0,
        "stroke_width_accuracy": 100.0,
        "corner_radius_accuracy": 100.0,
        "corner_uniformity_accuracy": 100.0,
        "elevation_accuracy": 100.0,
        "avg_latency_sec": 1.0,
        "tasks": rows,
        **overrides,
    }
    return card


def _row(task_id: str, correct: bool, cost: float = 0.01) -> dict:
    flags = {
        "has_border_correct": correct,
        "border_sides_correct": correct,
        "stroke_style_correct": correct,
        "stroke_width_correct": correct,
        "corner_radius_correct": correct,
        "corner_uniformity_correct": correct,
        "elevation_correct": correct,
    }
    return {
        "task_id": task_id,
        "all_correct": correct,
        **flags,
        "latency_sec": 1.0,
        "cost_usd": cost,
        "theme": "white-on-gray",
        "corner_radius_gt": "medium",
        "stroke_width_gt": "1px",
        "border_sides_gt": "all-4",
        "elevation_gt": "none",
    }


def test_metrics_and_costs_come_from_task_rows(tmp_path):
    card = _scorecard("m1", [_row("t1", True), _row("t2", False)])
    path = tmp_path / "scorecard_m1.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    summary = build_structured_benchmark([path])
    (model,) = summary["models"]
    assert model["all_correct_accuracy"] == 50.0
    assert model["avg_cost_usd"] == pytest.approx(0.01)
    assert summary["total_tasks_per_model"] == 2


def test_duplicate_model_inputs_rejected(tmp_path):
    first = tmp_path / "a_scorecard_m1.json"
    first.write_text(json.dumps(_scorecard("m1", [_row("t1", True)])), encoding="utf-8")
    time.sleep(0.02)
    second = tmp_path / "b_scorecard_m1.json"
    second.write_text(json.dumps(_scorecard("m1", [_row("t1", False)])), encoding="utf-8")
    assert os.path.getmtime(second) > os.path.getmtime(first)
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        build_structured_benchmark([first, second])


def test_malformed_rows_warn_and_preserve_peers(tmp_path):
    bad = _row("t2", True)
    bad["theme"] = {"not": "a string"}
    card = _scorecard("m1", [_row("t1", True), bad])
    path = tmp_path / "scorecard_m1.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    summary = build_structured_benchmark([path])
    (model,) = summary["models"]
    assert model["all_correct_accuracy"] == 100.0
    assert summary["warnings"], "malformed rows must warn, not crash or poison peers"
