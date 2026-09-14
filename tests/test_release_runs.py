"""Versioned runs: identities, ledgers, and first-wins aggregation."""

import io
import json
from pathlib import Path

import pytest
from PIL import Image

from baseline.build_page import collect_observations
from baseline.evaluator import GRADING_VERSION, cohort_fingerprint, evaluation_protocol_fingerprint
from baseline.releases import load_release
from baseline.runner import run_benchmark

PROTOCOL = evaluation_protocol_fingerprint()
FINGERPRINT = "f" * 64


def _tiny_png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (255, 255, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


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


def _items() -> list[dict]:
    return [{"taskId": task_id, "groundTruth": {
        "has_border": True, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px",
        "corner_radius": "medium", "corner_uniformity": "all-corners", "elevation": "none",
        "theme": "white-on-gray",
    }} for task_id in ("t1", "t2")]


def _row(task_id: str, correct: bool) -> dict:
    from baseline.evaluator import grade_border_prediction
    target = _items()[0]["groundTruth"]
    parsed = {key: value for key, value in target.items() if key != "theme"} if correct else {
        "has_border": False, "border_sides": "none", "stroke_style": "none", "stroke_width": "0px",
        "corner_radius": "sharp", "corner_uniformity": "top-only", "elevation": "subtle-drop",
    }
    return {
        "task_id": task_id, **grade_border_prediction(parsed, target),
        **{f"{key}_gt": value for key, value in target.items() if key != "theme"},
        **{f"predicted_{key}": value for key, value in parsed.items()},
        "theme": target["theme"], "raw_prediction": json.dumps(parsed),
        "model_name": "mock-model", "provider": "google",
        "latency_sec": 1.0, "cost_usd": 0.01, "error": None, "error_kind": None,
    }


def _write_run(root: Path, name: str, rows: list[dict], created: str, *, protocol: str = PROTOCOL,
               fingerprint: str = FINGERPRINT, mock: bool = False) -> None:
    from datetime import datetime, timedelta
    from baseline.model_config import _ModelConfig
    from baseline.releases import model_config_fingerprint
    run_dir = root / name
    run_dir.mkdir(parents=True)
    config = _ModelConfig.model_validate_json(json.dumps({
        "id": "mock-model", "provider": "google", "model": "mock-model", "display_name": "Mock",
        "api_key_env": "GEMINI_API_KEY", "source_url": "https://example.com/model", "max_output_tokens": 16,
    })).model_dump(mode="json")
    try:
        updated = (datetime.fromisoformat(created) + timedelta(seconds=1)).isoformat()
    except ValueError:
        updated = created
    for row in rows:
        row.setdefault("recorded_at", updated)
    updated = max([updated, *[row["recorded_at"] for row in rows]])
    provenance = {
        "schema_version": 1, "run_id": name, "release": "9.9.9", "dataset_git_commit": "a" * 40,
        "dataset_fingerprint": fingerprint, "evaluation_protocol": protocol, "grading_version": GRADING_VERSION,
        "mock": mock, "expected_task_count": 2, "created_at": created, "updated_at": updated,
        "runner_git_commit": None, "runner_git_dirty": None,
    }
    invocation = {"started_at": created, "updated_at": updated, "finished_at": updated,
                  "models": [config], "runner_git_commit": None, "runner_git_dirty": None}
    (run_dir / "run.json").write_text(json.dumps({**provenance, "invocations": [invocation],
                                                  "model_configs": {"mock-model": config}}))
    costs = [row["cost_usd"] for row in rows]
    total_cost = sum(costs)
    state = {"model_config": config, "model_config_fingerprint": model_config_fingerprint(config),
             "completed": len(rows), "cost_usd": total_cost}
    (run_dir / "summary.json").write_text(json.dumps({**provenance, "spent_cost_usd": total_cost,
        "cost_incomplete": False, "models": {"mock-model": state}}))
    (run_dir / "attempts.jsonl").write_text("".join(json.dumps({
        "sequence": index + 1, "run_id": name, "attempt_id": str(index), "model_id": "mock-model",
        "task_id": row["task_id"], "created_at": row["recorded_at"], "result": row, "cost_usd": row["cost_usd"],
    }) + "\n" for index, row in enumerate(rows)))
    (run_dir / "scorecard_mock-model.json").write_text(json.dumps({
        **provenance, "model_id": "mock-model", "model_name": "mock-model", "display_name": "Mock",
        "provider": "google", "model_config": config, "model_config_fingerprint": model_config_fingerprint(config),
        "max_output_tokens": 16, "total_tasks": len(rows), "status": "complete" if len(rows) == 2 else "partial",
        "cohort_sha256": cohort_fingerprint([row["task_id"] for row in rows]), "tasks": rows,
    }))


def _release() -> dict:
    return {"benchmark_version": "9.9.9", "dataset_fingerprint": FINGERPRINT,
            "evaluation_protocol_fingerprint": PROTOCOL, "dataset_git_commit": "a" * 40, "expected_task_count": 2}


def test_unknown_release_rejected(tmp_path):
    (tmp_path / "releases").mkdir()
    with pytest.raises(ValueError, match="[Rr]elease"):
        load_release("9.9.9", root=tmp_path)


def test_mock_release_run_writes_ledgers_and_resumes(tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["t1", "t2"])
    config = tmp_path / "models.json"
    _write_config(config)
    output = tmp_path / "runs"
    first = run_benchmark(
        manifest_path=manifest, config_path=config, output_dir=output,
        run_id="ledger", budget_usd=None, max_tasks=1, mock=True,
    )
    run_dir = output / "mock-ledger"
    run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert run_meta["evaluation_protocol"] == PROTOCOL
    assert len(run_meta["invocations"]) == 1
    assert (run_dir / "attempts.jsonl").read_text(encoding="utf-8").count("\n") == 1
    assert first["status"] == "partial"
    second = run_benchmark(
        manifest_path=manifest, config_path=config, output_dir=output,
        run_id="ledger", budget_usd=None, mock=True,
    )
    run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert len(run_meta["invocations"]) == 2
    assert (run_dir / "attempts.jsonl").read_text(encoding="utf-8").count("\n") == 2
    assert second["status"] == "complete"


def test_release_and_manifest_are_mutually_exclusive(tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["t1"])
    config = tmp_path / "models.json"
    _write_config(config)
    with pytest.raises(ValueError, match="[Rr]elease"):
        run_benchmark(
            manifest_path=manifest, config_path=config, output_dir=tmp_path / "runs",
            run_id="x", release="1.0.0", mock=True,
        )


def test_first_observation_wins_repeats(tmp_path):
    root = tmp_path / "runs" / "9.9.9"
    root.mkdir(parents=True)
    _write_run(root, "run-a", [_row("t1", True), _row("t2", True)], "2026-09-10T01:00:00+00:00")
    _write_run(root, "run-b", [_row("t1", False), _row("t2", True)], "2026-09-10T02:00:00+00:00")
    collected, warnings = collect_observations(_release(), tmp_path / "runs", _items())
    assert warnings == []
    (config,) = collected["configs"].values()
    assert config["repeat_observations"] == 2
    assert config["repeat_cost_usd"] == pytest.approx(0.02)
    kept = {task_id: obs["task"] for (_, task_id), obs in collected["observations"].items()}
    assert kept["t1"]["all_correct"] is True
    assert kept["t1"]["cost_usd"] == pytest.approx(0.01)
    assert all(obs["run"] == "run-a" for obs in collected["observations"].values())


def test_incompatible_and_mock_runs_excluded(tmp_path):
    root = tmp_path / "runs" / "9.9.9"
    root.mkdir(parents=True)
    _write_run(root, "good", [_row("t1", True)], "2026-09-10T01:00:00+00:00")
    _write_run(root, "bad-protocol", [_row("t1", True)], "2026-09-10T02:00:00+00:00", protocol="0" * 64)
    _write_run(root, "mock-run", [_row("t1", True)], "2026-09-10T03:00:00+00:00", mock=True)
    collected, warnings = collect_observations(_release(), tmp_path / "runs", _items())
    assert len(collected["observations"]) == 1
    assert any("bad-protocol" in warning for warning in warnings)
