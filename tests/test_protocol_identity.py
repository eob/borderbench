"""Protocol identity, scorecard completeness, and resume correctness."""

import io
import json
import re
import sqlite3
from pathlib import Path

import pytest
from PIL import Image

from baseline.evaluator import BaselineEvaluator
from baseline.runner import dataset_fingerprint, run_benchmark
from baseline.run_state import RunStore

REPO_ROOT = Path(__file__).resolve().parents[1]


def _tiny_png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (255, 255, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


def _mock_result(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "has_border_gt": True,
        "border_sides_gt": "all-4",
        "stroke_style_gt": "solid",
        "stroke_width_gt": "1px",
        "corner_radius_gt": "medium",
        "corner_uniformity_gt": "all-corners",
        "elevation_gt": "none",
        "theme": "white-on-gray",
        "image_path": f"{task_id}.png",
        "raw_prediction": "{}",
        "predicted_has_border": True,
        "predicted_border_sides": "all-4",
        "predicted_stroke_style": "solid",
        "predicted_stroke_width": "1px",
        "predicted_corner_radius": "medium",
        "predicted_corner_uniformity": "all-corners",
        "predicted_elevation": "none",
        "has_border_correct": True,
        "border_sides_correct": True,
        "stroke_style_correct": True,
        "stroke_width_correct": True,
        "corner_radius_correct": True,
        "corner_uniformity_correct": True,
        "elevation_correct": True,
        "all_correct": True,
        "latency_sec": 0.01,
        "model_name": "mock",
        "provider": "google",
        "cost_usd": 0.0,
    }


def _write_manifest(path: Path, task_ids: list[str]) -> None:
    for task_id in task_ids:
        (path.parent / f"{task_id}.png").write_bytes(_tiny_png())
    tasks = [
        {
            "taskId": task_id,
            "imagePath": str(path.parent / f"{task_id}.png"),
            "imageFilename": f"{task_id}.png",
            "groundTruth": {
                "has_border": True,
                "border_sides": "all-4",
                "stroke_style": "solid",
                "stroke_width": "1px",
                "corner_radius": "medium",
                "corner_radius_px": 8,
                "corner_uniformity": "all-corners",
                "elevation": "none",
                "theme": "white-on-gray",
            },
            "prompt": "prompt",
        }
        for task_id in task_ids
    ]
    path.write_text(json.dumps({"tasks": tasks}, indent=2), encoding="utf-8")


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "verified_at": "2026-09-10",
                "models": [
                    {
                        "id": "mock-model",
                        "provider": "google",
                        "model": "mock-model",
                        "display_name": "Mock",
                        "api_key_env": "GEMINI_API_KEY",
                        "source_url": "https://example.com/model",
                        "input_per_m": 1.0,
                        "output_per_m": 1.0,
                        "max_output_tokens": 16,
                        "enabled": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_shared_prompt_file_exists():
    prompt = REPO_ROOT / "baseline" / "prompt.txt"
    assert prompt.is_file(), "baseline/prompt.txt must freeze the shared grading prompt"
    assert "7 design attributes" in prompt.read_text(encoding="utf-8")


def test_grading_version_bumped():
    from baseline.evaluator import GRADING_VERSION

    assert GRADING_VERSION != "1"


def test_protocol_fingerprint_format_and_stability():
    from baseline.evaluator import evaluation_protocol_fingerprint

    first = evaluation_protocol_fingerprint()
    assert re.fullmatch(r"[0-9a-f]{64}", first), first
    assert evaluation_protocol_fingerprint() == first


def test_scorecard_partial_status_cohort_and_invalid_count():
    evaluator = BaselineEvaluator(mock=True)
    item = {
        "taskId": "t1",
        "imagePath": "t1.png",
        "groundTruth": {
            "has_border": True,
            "border_sides": "all-4",
            "stroke_style": "solid",
            "stroke_width": "1px",
            "corner_radius": "medium",
            "corner_uniformity": "all-corners",
            "elevation": "none",
            "theme": "white-on-gray",
        },
    }
    result = evaluator._eval_single_task(item, "prompt")
    card = evaluator.score_results([result], expected_task_count=3)
    assert card.status == "partial"
    assert re.fullmatch(r"[0-9a-f]{64}", card.cohort_sha256)
    assert card.invalid_responses == 0


def test_scorecard_complete_status():
    evaluator = BaselineEvaluator(mock=True)
    item = {
        "taskId": "t1",
        "imagePath": "t1.png",
        "groundTruth": {
            "has_border": True,
            "border_sides": "all-4",
            "stroke_style": "solid",
            "stroke_width": "1px",
            "corner_radius": "medium",
            "corner_uniformity": "all-corners",
            "elevation": "none",
            "theme": "white-on-gray",
        },
    }
    result = evaluator._eval_single_task(item, "prompt")
    card = evaluator.score_results([result], expected_task_count=1)
    assert card.status == "complete"


def test_foreign_checkpoint_tasks_rejected(tmp_path):
    from baseline.evaluator import evaluation_protocol_fingerprint, load_manifest
    from baseline.model_config import load_model_config

    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["t1"])
    config = tmp_path / "models.json"
    _write_config(config)
    (model_config,) = load_model_config(config)
    fingerprint = dataset_fingerprint(load_manifest(str(manifest)))
    output = tmp_path / "runs"
    directory = output / "mock-resume"
    directory.mkdir(parents=True)
    with RunStore(directory / "state.sqlite3") as store:
        store.register_run(
            "resume", fingerprint,
            {"mock": True, "evaluation_protocol": evaluation_protocol_fingerprint()},
        )
        store.register_model("resume", "mock-model", model_config)
        store.save_result("resume", "mock-model", "foreign-task", _mock_result("foreign-task"))
    with pytest.raises(ValueError, match="[Cc]heckpoint|[Ff]oreign|[Uu]nknown task"):
        run_benchmark(
            manifest_path=manifest,
            config_path=config,
            output_dir=output,
            run_id="resume",
            budget_usd=None,
            mock=True,
        )


def test_legacy_run_without_protocol_rejected(tmp_path):
    from baseline.evaluator import load_manifest

    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["t1"])
    config = tmp_path / "models.json"
    _write_config(config)
    fingerprint = dataset_fingerprint(load_manifest(str(manifest)))
    output = tmp_path / "runs"
    directory = output / "mock-legacy"
    directory.mkdir(parents=True)
    with RunStore(directory / "state.sqlite3") as store:
        store.register_run("legacy", fingerprint, {"mock": True})
        store.register_model("legacy", "mock-model", {"id": "mock-model"})
    (directory / "run.json").write_text(
        json.dumps(
            {
                "release": None,
                "dataset_git_commit": None,
                "dataset_fingerprint": fingerprint,
                "manifest_path": str(manifest.resolve()),
                "mock": True,
                "expected_task_count": 1,
                "created_at": "2026-09-10T00:00:00+00:00",
                "invocations": [],
                "model_configs": {},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="[Dd]isagrees"):
        run_benchmark(
            manifest_path=manifest,
            config_path=config,
            output_dir=output,
            run_id="legacy",
            budget_usd=None,
            mock=True,
        )


def test_protocol_change_rejected_on_resume(tmp_path):
    from baseline.evaluator import evaluation_protocol_fingerprint, load_manifest

    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["t1"])
    config = tmp_path / "models.json"
    _write_config(config)
    output = tmp_path / "runs"
    run_benchmark(
        manifest_path=manifest,
        config_path=config,
        output_dir=output,
        run_id="proto",
        budget_usd=None,
        mock=True,
    )
    assert evaluation_protocol_fingerprint()
    assert load_manifest(str(manifest))
    connection = sqlite3.connect(output / "mock-proto" / "state.sqlite3")
    try:
        row = connection.execute(
            "SELECT metadata_json FROM runs WHERE run_id = ?", ("proto",)
        ).fetchone()
        metadata = json.loads(row[0])
        assert "evaluation_protocol" in metadata, "run metadata must record the grading protocol"
        metadata["evaluation_protocol"] = "0" * 64
        connection.execute(
            "UPDATE runs SET metadata_json = ? WHERE run_id = ?",
            (json.dumps(metadata, sort_keys=True), "proto"),
        )
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(ValueError, match="[Pp]rotocol"):
        run_benchmark(
            manifest_path=manifest,
            config_path=config,
            output_dir=output,
            run_id="proto",
            budget_usd=None,
            mock=True,
        )
