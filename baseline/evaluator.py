"""BorderBench Multi-Attribute Evaluator and Task Grader."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError

from baseline.providers import PredictionClient, PredictionResponse, BorderPrediction, PREDICTION_KEYS, parse_prediction


GRADING_VERSION = "3"
DEFAULT_PROMPT = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8").strip()

THEMES = (
    "white-on-gray",
    "white-on-white",
    "gray-tint-on-white",
    "blue-tint-on-white",
    "dark-mode",
)


def evaluation_protocol_fingerprint() -> str:
    """Pin request construction, answer schema, grading, and the fallback prompt."""
    digest = hashlib.sha256(json.dumps({
        "grading_version": GRADING_VERSION, "default_prompt": DEFAULT_PROMPT,
        "schema": BorderPrediction.model_json_schema(),
    }, sort_keys=True).encode())
    for name in ("evaluator.py", "providers.py"):
        digest.update(Path(__file__).with_name(name).read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def _canonical_ground_truth(item: dict, index: int) -> dict:
    gt = item.get("groundTruth")
    if not isinstance(gt, dict):
        raise ValueError(f"Manifest task {index} must carry a groundTruth object")
    targets = {
        "has_border": gt.get("has_border"),
        "border_sides": gt.get("border_sides"),
        "stroke_style": gt.get("stroke_style"),
        "stroke_width": gt.get("stroke_width"),
        "corner_radius": gt.get("corner_radius"),
        "corner_uniformity": gt.get("corner_uniformity"),
        "elevation": gt.get("elevation"),
    }
    try:
        if BorderPrediction.model_validate(targets).model_dump() != targets:
            raise ValueError(f"Noncanonical border labels in manifest task {index}")
    except ValidationError as error:
        raise ValueError(f"Invalid border labels in manifest task {index}: {error}") from error
    if gt.get("theme") not in THEMES:
        raise ValueError(f"Manifest task {index} has an unknown theme")
    return targets


def load_manifest(manifest_path: str) -> list[dict]:
    """Load canonically labeled tasks with image paths resolved beside the manifest."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        items = data.get("tasks", [])
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Manifest must be a JSON object with 'tasks' or a JSON array")
    if not isinstance(items, list):
        raise ValueError("Manifest 'tasks' must be a JSON array")
    task_ids = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Manifest task {index} must be a JSON object")
        task_id = item.get("taskId")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"Manifest task {index} must have a non-empty taskId")
        if task_id in task_ids:
            raise ValueError(f"Duplicate manifest taskId: {task_id}")
        task_ids.add(task_id)
        _canonical_ground_truth(item, index)
        if item.get("imageFilename"):
            item["imagePath"] = str(Path(manifest_path).resolve().parent / item["imageFilename"])
    return items


def cohort_fingerprint(task_ids: list[str]) -> str:
    return hashlib.sha256(",".join(sorted(task_ids)).encode()).hexdigest()


def grade_border_prediction(parsed: dict, ground_truth: dict) -> dict[str, bool]:
    """Compare the seven visual attributes; malformed answers score zero."""
    flags = {key + "_correct": key in parsed and parsed[key] == ground_truth[key]
             for key in PREDICTION_KEYS}
    return {**flags, "all_correct": all(flags.values())}


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
    grading_version: str = GRADING_VERSION
    provider: str = "google"
    task_results: List[TaskEvaluationResult] = field(default_factory=list)
    status: str = "partial"
    cohort_sha256: str = ""
    invalid_responses: int = 0


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
        prompt = item.get("prompt", prompt_default) or DEFAULT_PROMPT

        start_t = time.perf_counter()
        response = self.predict_image(image_path, prompt)
        latency = time.perf_counter() - start_t
        raw_pred = response.raw_text
        error = response.error
        error_kind = response.error_kind
        try:
            if error:
                raise ValueError(error)
            parsed_pred = parse_prediction(raw_pred)
        except ValueError as invalid:
            parsed_pred = {}
            if not error:
                error = str(invalid)
                error_kind = "invalid_response"

        pred_has_border = bool(parsed_pred.get("has_border", False))
        pred_sides = str(parsed_pred.get("border_sides", ""))
        pred_style = str(parsed_pred.get("stroke_style", ""))
        pred_width = str(parsed_pred.get("stroke_width", ""))
        pred_radius = str(parsed_pred.get("corner_radius", ""))
        pred_uniformity = str(parsed_pred.get("corner_uniformity", ""))
        pred_elev = str(parsed_pred.get("elevation", ""))

        gt = item.get("groundTruth", {})
        gt_has_border = bool(gt.get("has_border", False))
        gt_sides = str(gt.get("border_sides", "")).strip().lower()
        gt_style = str(gt.get("stroke_style", "")).strip().lower()
        gt_width = str(gt.get("stroke_width", "")).strip().lower()
        gt_radius = str(gt.get("corner_radius", "")).strip().lower()
        gt_uniformity = str(gt.get("corner_uniformity", "")).strip().lower()
        gt_elev = str(gt.get("elevation", "")).strip().lower()
        theme = str(gt.get("theme", "white-on-gray"))

        flags = grade_border_prediction({} if error else parsed_pred, gt)

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
            **flags,
            latency_sec=latency,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            request_attempts=response.request_attempts,
            unmetered_attempts=response.unmetered_attempts,
            error=error,
            error_kind=error_kind,
            model_name=self.model_name,
            provider=self.provider,
        )

    def score_results(self, results: list[TaskEvaluationResult], expected_task_count: int = 0) -> BorderBenchScorecard:
        results = [r for r in results if not r.error or r.error_kind == "invalid_response"]
        if len({r.task_id for r in results}) != len(results):
            raise ValueError("Cannot score duplicate task observations")
        total = len(results)
        if expected_task_count and total > expected_task_count:
            raise ValueError("Observed tasks exceed the expected corpus")
        denom = float(total or 1)

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

        expected = expected_task_count or total
        invalid_responses = sum(1 for r in results if r.error_kind == "invalid_response")
        retryable = any(r.error and r.error_kind != "invalid_response" for r in results)
        status = "complete" if expected > 0 and total == expected and not retryable else "partial"

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
            expected_task_count=expected,
            provider=self.provider,
            task_results=results,
            status=status,
            cohort_sha256=cohort_fingerprint([r.task_id for r in results]),
            invalid_responses=invalid_responses,
        )
