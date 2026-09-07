"""BorderBench Structured Summary Aggregator.

Consolidates model scorecards into a structured, lightweight benchmark dataset
for visualization on edwardbenson.com.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


MODEL_METADATA = {
    "claude-fable-5-1": {"display_name": "Claude Fable 5.1", "family": "Claude", "provider": "anthropic"},
    "claude-opus-5": {"display_name": "Claude Opus 5", "family": "Claude", "provider": "anthropic"},
    "claude-sonnet-5": {"display_name": "Claude Sonnet 5", "family": "Claude", "provider": "anthropic"},
    "claude-haiku-4-5-20251001": {"display_name": "Claude Haiku 4.5", "family": "Claude", "provider": "anthropic"},
    "gpt-6-astra": {"display_name": "GPT-6 Astra", "family": "GPT", "provider": "openai"},
    "gpt-5.6-sol": {"display_name": "GPT-5.6 Sol", "family": "GPT", "provider": "openai"},
    "gpt-5.6-terra": {"display_name": "GPT-5.6 Terra", "family": "GPT", "provider": "openai"},
    "gpt-5.6-luna": {"display_name": "GPT-5.6 Luna", "family": "GPT", "provider": "openai"},
    "gemini-3.1-pro-preview": {"display_name": "Gemini 3.1 Pro Preview", "family": "Gemini", "provider": "google"},
    "gemini-3.8-flash": {"display_name": "Gemini 3.8 Flash", "family": "Gemini", "provider": "google"},
    "gemini-3.5-flash-lite": {"display_name": "Gemini 3.5 Flash-Lite", "family": "Gemini", "provider": "google"},
    "gemini-2.5-flash": {"display_name": "Gemini 2.5 Flash", "family": "Gemini", "provider": "google"},
    "gemini-2.5-pro": {"display_name": "Gemini 2.5 Pro", "family": "Gemini", "provider": "google"},
}


def build_structured_benchmark(results_dir: str | Path = "results") -> Dict[str, Any]:
    results_path = Path(results_dir)
    scorecards = list(results_path.glob("**/scorecard_*.json"))
    
    # Group by model_id, selecting the latest scorecard
    latest_scorecards: Dict[str, Path] = {}
    for p in scorecards:
        m_id = p.stem.removeprefix("scorecard_")
        if m_id not in latest_scorecards or p.stat().st_mtime > latest_scorecards[m_id].stat().st_mtime:
            latest_scorecards[m_id] = p

    models_output = []
    for model_id, path in latest_scorecards.items():
        with open(path, "r", encoding="utf-8") as f:
            sc = json.load(f)

        meta = MODEL_METADATA.get(model_id, {
            "display_name": sc.get("display_name", model_id),
            "family": "Other",
            "provider": sc.get("provider", "other"),
        })

        total_tasks = sc.get("total_tasks", 120)
        pricing = sc.get("pricing", {})
        input_price = pricing.get("input_per_m") or 0.0
        output_price = pricing.get("output_per_m") or 0.0

        # Estimate average cost per task based on 600 input tokens and 60 output tokens
        avg_cost_usd = ((600 * input_price) + (60 * output_price)) / 1_000_000

        entry = {
            "model_id": model_id,
            "display_name": meta["display_name"],
            "provider": sc.get("provider", meta["provider"]),
            "family": meta["family"],
            "total_tasks": total_tasks,
            "evaluated_at": sc.get("timestamp"),
            "all_correct_accuracy": round(sc.get("overall_exact_match", 0.0), 1),
            "has_border_accuracy": round(sc.get("has_border_accuracy", 0.0), 1),
            "border_sides_accuracy": round(sc.get("border_sides_accuracy", 0.0), 1),
            "stroke_style_accuracy": round(sc.get("stroke_style_accuracy", 0.0), 1),
            "stroke_width_accuracy": round(sc.get("stroke_width_accuracy", 0.0), 1),
            "corner_radius_accuracy": round(sc.get("corner_radius_accuracy", 0.0), 1),
            "corner_uniformity_accuracy": round(sc.get("corner_uniformity_accuracy", 0.0), 1),
            "elevation_accuracy": round(sc.get("elevation_accuracy", 0.0), 1),
            "avg_latency_sec": round(sc.get("avg_latency_sec", 0.0), 2),
            "avg_cost_usd": round(avg_cost_usd, 6),
            "pricing": {
                "input_per_m": input_price,
                "output_per_m": output_price,
            },
            "by_theme": sc.get("accuracy_by_theme", {}),
            "by_curvature": sc.get("accuracy_by_curvature", {}),
            "by_thickness": sc.get("accuracy_by_thickness", {}),
            "by_sides": sc.get("accuracy_by_sides", {}),
            "by_elevation": sc.get("accuracy_by_elevation", {}),
        }
        models_output.append(entry)

    # Sort descending by all_correct_accuracy
    models_output.sort(key=lambda m: (m["all_correct_accuracy"], -m["avg_latency_sec"]), reverse=True)

    summary = {
        "benchmark_id": "borderbench-1",
        "name": "BorderBench-1",
        "version": "1.0.0",
        "description": "Visual border, corner radius, stroke style, and elevation identification benchmark for multimodal vision-language models.",
        "eval_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tasks_per_model": 120,
        "taxonomies": {
            "attributes": [
                "all_correct",
                "has_border",
                "border_sides",
                "stroke_style",
                "stroke_width",
                "corner_radius",
                "corner_uniformity",
                "elevation",
            ],
            "border_sides": ["all-4", "bottom-only", "left-only", "top-only", "none"],
            "stroke_styles": ["solid", "dashed", "dotted", "double", "none"],
            "stroke_widths": ["0px", "1px", "2px", "4px", "8px"],
            "corner_radii": ["sharp", "subtle", "medium", "large", "pill"],
            "corner_uniformity": ["all-corners", "top-only", "asymmetric"],
            "elevations": ["none", "subtle-drop", "floating-drop", "ring-only", "stroke+shadow"],
            "themes": [
                "white-on-gray",
                "white-on-white",
                "gray-tint-on-white",
                "blue-tint-on-white",
                "dark-mode",
            ],
        },
        "models": models_output,
    }
    return summary


def main():
    summary = build_structured_benchmark("results")
    out_file = Path("results/borderbench_summary.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Generated structured benchmark summary at {out_file} with {len(summary['models'])} models.")


if __name__ == "__main__":
    main()
