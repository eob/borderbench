"""BorderBench Multi-Attribute Evaluator and Task Grader."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from baseline.providers import PredictionClient, PredictionResponse, BorderPrediction


def load_manifest(manifest_path: str) -> list[dict]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("tasks", [])
    if isinstance(data, list):
        return data
    raise ValueError("Manifest must be a JSON object with 'tasks' or a JSON array")


@dataclass
class TaskEvaluationResult:
    task_id: str
    has_border_gt: bool
    border_sides_gt: str
    stroke_style_gt: str
    stroke_width_gt: str
    corner_radius_gt: str
    corner_uniformity_gt: str
    elevation_gt: str
    theme: str
    image_path: str
    raw_prediction: str
    predicted_has_border: bool
    predicted_border_sides: str
    predicted_stroke_style: str
    predicted_stroke_width: str
    predicted_corner_radius: str
    predicted_corner_uniformity: str
    predicted_elevation: str
    has_border_correct: bool
    border_sides_correct: bool
    stroke_style_correct: bool
    stroke_width_correct: bool
    corner_radius_correct: bool
    corner_uniformity_correct: bool
    elevation_correct: bool
    all_correct: bool
    latency_sec: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    request_attempts: int | None = None
    unmetered_attempts: int | None = None
    error: str | None = None
    error_kind: str | None = None
    model_name: str = ""
    provider: str = ""


@dataclass
class BorderBenchScorecard:
    total_tasks: int
    overall_exact_match: float
    has_border_accuracy: float
    border_sides_accuracy: float
    stroke_style_accuracy: float
    stroke_width_accuracy: float
    corner_radius_accuracy: float
    corner_uniformity_accuracy: float
    elevation_accuracy: float
    avg_latency_sec: float
    accuracy_by_theme: Dict[str, Dict[str, float]]
    accuracy_by_curvature: Dict[str, Dict[str, float]]
    accuracy_by_thickness: Dict[str, Dict[str, float]]
    accuracy_by_sides: Dict[str, Dict[str, float]]
    accuracy_by_elevation: Dict[str, Dict[str, float]]
    model_name: str
    timestamp: str
    expected_task_count: int = 0
    grading_version: str = "1"
    provider: str = "google"
    task_results: List[TaskEvaluationResult] = field(default_factory=list)


class BaselineEvaluator:
    def __init__(
        self,
        model_name: str = "gemini-3.5-flash",
        mock: bool = False,
        provider: str = "google",
        api_key_env: str | None = None,
        base_url: str | None = None,
        max_output_tokens: int = 1024,
    ):
        self.model_name = model_name
        self.provider = provider
        self.mock = mock
        self._client = None if mock else PredictionClient(
            provider, model_name, api_key_env=api_key_env,
            base_url=base_url, max_output_tokens=max_output_tokens,
        )

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def predict_image(self, image_path: str, prompt: str) -> PredictionResponse:
        if self.mock:
            prediction = {
                "has_border": True,
                "border_sides": "all-4",
                "stroke_style": "solid",
                "stroke_width": "1px",
                "corner_radius": "medium",
                "corner_uniformity": "all-corners",
                "elevation": "none",
            }
            return PredictionResponse(json.dumps(prediction), prediction, input_tokens=0, output_tokens=0)
        return self._client.predict(image_path, prompt)

    def _eval_single_task(self, item: dict, prompt_default: str) -> TaskEvaluationResult:
        image_path = item["imagePath"]
        prompt = item.get("prompt", prompt_default)

        start_t = time.perf_counter()
        response = self.predict_image(image_path, prompt)
        latency = time.perf_counter() - start_t
        raw_pred = response.raw_text
        parsed_pred = response.parsed if not response.error else {}

        pred_has_border = bool(parsed_pred.get("has_border", False))
        pred_sides = str(parsed_pred.get("border_sides", "")).strip().lower()
        pred_style = str(parsed_pred.get("stroke_style", "")).strip().lower()
        pred_width = str(parsed_pred.get("stroke_width", "")).strip().lower()
        pred_radius = str(parsed_pred.get("corner_radius", "")).strip().lower()
        pred_uniformity = str(parsed_pred.get("corner_uniformity", "")).strip().lower()
        pred_elev = str(parsed_pred.get("elevation", "")).strip().lower()

        gt = item.get("groundTruth", {})
        gt_has_border = bool(gt.get("has_border", False))
        gt_sides = str(gt.get("border_sides", "")).strip().lower()
        gt_style = str(gt.get("stroke_style", "")).strip().lower()
        gt_width = str(gt.get("stroke_width", "")).strip().lower()
        gt_radius = str(gt.get("corner_radius", "")).strip().lower()
        gt_uniformity = str(gt.get("corner_uniformity", "")).strip().lower()
        gt_elev = str(gt.get("elevation", "")).strip().lower()
        theme = str(gt.get("theme", "white-on-gray"))

        has_border_correct = pred_has_border == gt_has_border
        border_sides_correct = pred_sides == gt_sides
        stroke_style_correct = pred_style == gt_style
        stroke_width_correct = pred_width == gt_width
        corner_radius_correct = pred_radius == gt_radius
        corner_uniformity_correct = pred_uniformity == gt_uniformity
        elevation_correct = pred_elev == gt_elev

        all_correct = (
            not response.error
            and has_border_correct
            and border_sides_correct
            and stroke_style_correct
            and stroke_width_correct
            and corner_radius_correct
            and corner_uniformity_correct
            and elevation_correct
        )

        return TaskEvaluationResult(
            task_id=item["taskId"],
            has_border_gt=gt_has_border,
            border_sides_gt=gt_sides,
            stroke_style_gt=gt_style,
            stroke_width_gt=gt_width,
            corner_radius_gt=gt_radius,
            corner_uniformity_gt=gt_uniformity,
            elevation_gt=gt_elev,
            theme=theme,
            image_path=image_path,
            raw_prediction=raw_pred,
            predicted_has_border=pred_has_border,
            predicted_border_sides=pred_sides,
            predicted_stroke_style=pred_style,
            predicted_stroke_width=pred_width,
            predicted_corner_radius=pred_radius,
            predicted_corner_uniformity=pred_uniformity,
            predicted_elevation=pred_elev,
            has_border_correct=has_border_correct,
            border_sides_correct=border_sides_correct,
            stroke_style_correct=stroke_style_correct,
            stroke_width_correct=stroke_width_correct,
            corner_radius_correct=corner_radius_correct,
            corner_uniformity_correct=corner_uniformity_correct,
            elevation_correct=elevation_correct,
            all_correct=all_correct,
            latency_sec=latency,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            request_attempts=response.request_attempts,
            unmetered_attempts=response.unmetered_attempts,
            error=response.error,
            error_kind=response.error_kind,
            model_name=self.model_name,
            provider=self.provider,
        )

    def score_results(self, results: list[TaskEvaluationResult], expected_task_count: int = 0) -> BorderBenchScorecard:
        total = len(results)
        denom = float(expected_task_count) if expected_task_count > 0 else float(total or 1)

        exact_matches = sum(1 for r in results if r.all_correct)
        has_border_matches = sum(1 for r in results if r.has_border_correct)
        sides_matches = sum(1 for r in results if r.border_sides_correct)
        style_matches = sum(1 for r in results if r.stroke_style_correct)
        width_matches = sum(1 for r in results if r.stroke_width_correct)
        radius_matches = sum(1 for r in results if r.corner_radius_correct)
        uniformity_matches = sum(1 for r in results if r.corner_uniformity_correct)
        elevation_matches = sum(1 for r in results if r.elevation_correct)

        avg_latency = (sum(r.latency_sec for r in results) / total) if total > 0 else 0.0

        def build_slice(key_fn) -> Dict[str, Dict[str, float]]:
            buckets: Dict[str, Dict[str, int]] = {}
            for r in results:
                k = key_fn(r)
                if k not in buckets:
                    buckets[k] = {"total": 0, "exact": 0, "presence": 0}
                buckets[k]["total"] += 1
                if r.all_correct:
                    buckets[k]["exact"] += 1
                if r.has_border_correct:
                    buckets[k]["presence"] += 1
            out = {}
            for k, b in buckets.items():
                tot = b["total"]
                out[k] = {
                    "total": tot,
                    "exact_accuracy": round((b["exact"] / tot) * 100, 1) if tot > 0 else 0.0,
                    "presence_accuracy": round((b["presence"] / tot) * 100, 1) if tot > 0 else 0.0,
                }
            return out

        by_theme = build_slice(lambda r: r.theme)
        by_curvature = build_slice(lambda r: r.corner_radius_gt)
        by_thickness = build_slice(lambda r: r.stroke_width_gt)
        by_sides = build_slice(lambda r: r.border_sides_gt)
        by_elevation = build_slice(lambda r: r.elevation_gt)

        return BorderBenchScorecard(
            total_tasks=total,
            overall_exact_match=round((exact_matches / denom) * 100, 2),
            has_border_accuracy=round((has_border_matches / denom) * 100, 2),
            border_sides_accuracy=round((sides_matches / denom) * 100, 2),
            stroke_style_accuracy=round((style_matches / denom) * 100, 2),
            stroke_width_accuracy=round((width_matches / denom) * 100, 2),
            corner_radius_accuracy=round((radius_matches / denom) * 100, 2),
            corner_uniformity_accuracy=round((uniformity_matches / denom) * 100, 2),
            elevation_accuracy=round((elevation_matches / denom) * 100, 2),
            avg_latency_sec=round(avg_latency, 3),
            accuracy_by_theme=by_theme,
            accuracy_by_curvature=by_curvature,
            accuracy_by_thickness=by_thickness,
            accuracy_by_sides=by_sides,
            accuracy_by_elevation=by_elevation,
            model_name=self.model_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            expected_task_count=expected_task_count or total,
            provider=self.provider,
            task_results=results,
        )
