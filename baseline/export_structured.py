"""BorderBench Structured Summary Aggregator.

Builds a cross-model summary from explicit scorecard files. Every measured
number comes from task rows; guessed token counts, hardcoded totals, and
implicit latest-file selection are refused.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ATTRIBUTES = (
    "has_border",
    "border_sides",
    "stroke_style",
    "stroke_width",
    "corner_radius",
    "corner_uniformity",
    "elevation",
)

GROUP_LABELS = {
    "by_theme": "theme",
    "by_curvature": "corner_radius_gt",
    "by_thickness": "stroke_width_gt",
    "by_sides": "border_sides_gt",
    "by_elevation": "elevation_gt",
}


def _is_finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _valid_row(row: object) -> dict | None:
    if not isinstance(row, dict):
        return None
    if not isinstance(row.get("task_id"), str) or not row["task_id"].strip():
        return None
    if type(row.get("all_correct")) is not bool:
        return None
    for attribute in ATTRIBUTES:
        if type(row.get(f"{attribute}_correct")) is not bool:
            return None
    if row["all_correct"] != all(row[f"{attribute}_correct"] for attribute in ATTRIBUTES):
        return None
    if row.get("error_kind") not in (None, "invalid_response") or row.get("error") and row.get("error_kind") != "invalid_response":
        return None
    if row.get("error_kind") == "invalid_response" and any(row[f"{attribute}_correct"] for attribute in ATTRIBUTES):
        return None
    latency = row.get("latency_sec")
    if latency is not None and (not _is_finite_number(latency) or latency < 0):
        return None
    cost = row.get("cost_usd", 0.0)
    if cost is not None and (not _is_finite_number(cost) or cost < 0):
        return None
    for label in GROUP_LABELS.values():
        if label in row and (not isinstance(row[label], str) or not row[label].strip()):
            return None
    return row


def _breakdown(rows: list[dict], label: str) -> Dict[str, Dict[str, float]]:
    buckets: Dict[str, Dict[str, int]] = {}
    for row in rows:
        key = row.get(label)
        if not isinstance(key, str) or not key.strip():
            continue
        bucket = buckets.setdefault(key, {"total": 0, "exact": 0})
        bucket["total"] += 1
        if row["all_correct"]:
            bucket["exact"] += 1
    return {
        key: {
            "total": bucket["total"],
            "exact_accuracy": round((bucket["exact"] / bucket["total"]) * 100, 1),
        }
        for key, bucket in sorted(buckets.items())
    }


def _summarize_model(model_id: str, card: dict, warnings: list[str]) -> dict | None:
    tasks = card.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        warnings.append(f"{model_id}: scorecard has no task rows; skipped")
        return None
    ids = [row.get("task_id") for row in tasks if isinstance(row, dict)]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate task rows for {model_id!r}")
    rows = []
    for row in tasks:
        valid = _valid_row(row)
        if valid is None:
            warnings.append(f"{model_id}: malformed task row; entire scorecard excluded to preserve the denominator")
            return None
        else:
            rows.append(valid)
    if not rows:
        warnings.append(f"{model_id}: no valid task rows; skipped")
        return None
    total = len(rows)
    costs = [row["cost_usd"] for row in rows if row.get("cost_usd") is not None]
    entry: Dict[str, Any] = {
        "model_id": model_id,
        "display_name": card.get("display_name") or card.get("model_name") or model_id,
        "provider": card.get("provider") or "other",
        "total_tasks": total,
        "evaluated_at": card.get("timestamp"),
        "all_correct_accuracy": round(sum(1 for r in rows if r["all_correct"]) / total * 100, 1),
        "avg_latency_sec": round(sum(r["latency_sec"] for r in rows) / total, 2) if all(r.get("latency_sec") is not None for r in rows) else None,
        "avg_cost_usd": round(sum(float(c) for c in costs) / total, 6) if len(costs) == total else None,
        "pricing": card.get("pricing") or {},
    }
    for attribute in ATTRIBUTES:
        entry[f"{attribute}_accuracy"] = round(
            sum(1 for r in rows if r[f"{attribute}_correct"]) / total * 100, 1
        )
    for key, label in GROUP_LABELS.items():
        entry[key] = _breakdown(rows, label)
    return entry


def build_structured_benchmark(scorecards: list[str | Path]) -> Dict[str, Any]:
    """Aggregate explicit scorecard files; duplicate models are refused."""
    warnings: list[str] = []
    models_output = []
    seen = set()
    for path in scorecards:
        card = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(card, dict):
            warnings.append(f"{path}: scorecard is not an object; skipped")
            continue
        model_id = card.get("model_id") or card.get("model_name")
        if not isinstance(model_id, str) or not model_id.strip():
            warnings.append(f"{path}: scorecard has no model id; skipped")
            continue
        if model_id in seen:
            raise ValueError(f"Duplicate model scorecards for {model_id!r}; select one explicitly")
        seen.add(model_id)
        entry = _summarize_model(model_id, card, warnings)
        if entry is not None:
            models_output.append(entry)
    if not models_output:
        raise ValueError("No valid model scorecards to summarize")
    models_output.sort(key=lambda m: m["display_name"])
    totals = {model["total_tasks"] for model in models_output}
    return {
        "benchmark_id": "borderbench-unversioned",
        "release": None,
        "comparison_policy": "Descriptive observed scores only; differing cohorts are not ranked.",
        "name": "BorderBench unversioned observations",
        "description": "Visual border, corner radius, stroke style, and elevation identification benchmark for multimodal vision-language models.",
        "eval_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tasks_per_model": models_output[0]["total_tasks"] if len(totals) == 1 else sorted(totals),
        "taxonomies": {
            "attributes": ["all_correct", *ATTRIBUTES],
            "border_sides": ["all-4", "bottom-only", "left-only", "top-only", "none"],
            "stroke_styles": ["solid", "dashed", "dotted", "none"],
            "stroke_widths": ["0px", "1px", "2px", "4px", "8px"],
            "corner_radii": ["sharp", "subtle", "medium", "large", "pill"],
            "corner_uniformity": ["all-corners", "top-only", "asymmetric"],
            "elevations": ["none", "subtle-drop", "floating-drop"],
            "themes": [
                "white-on-gray",
                "white-on-white",
                "gray-tint-on-white",
                "blue-tint-on-white",
                "dark-mode",
            ],
        },
        "models": models_output,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecards", nargs="+", help="Explicit scorecard JSON files")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = build_structured_benchmark(args.scorecards)
    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Summarized {len(summary['models'])} models to {out_file} ({len(summary['warnings'])} warnings).")


if __name__ == "__main__":
    main()
