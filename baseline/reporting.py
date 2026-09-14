"""Shared scorecard integrity checks for report consumers."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
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


def scorecard_tasks(card: dict, *, dataset_fingerprint: str | None = None, complete: bool = False) -> list[dict]:
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
            or not isinstance(card.get("dataset_fingerprint"), str)
            or dataset_fingerprint is not None and card.get("dataset_fingerprint") != dataset_fingerprint
            or card.get("cohort_sha256") != cohort_fingerprint(ids)
            or not isinstance(card.get("mock"), bool)):
        raise ValueError("Incompatible dataset, protocol, or mock provenance")
    if card.get("status") not in ("complete", "partial") or (
            card["status"] == "complete" and len(tasks) != card["expected_task_count"]):
        raise ValueError("Inconsistent completion status")
    if complete and (card["status"] != "complete" or not tasks or card["mock"]):
        raise ValueError("Only complete live runs are eligible")
    for task in tasks:
        if type(task.get("all_correct")) is not bool or any(
                type(task.get(f"{key}_correct")) is not bool for key in DIMENSIONS):
            raise ValueError("Invalid grading flags")
        if task["all_correct"] != all(task[f"{key}_correct"] for key in DIMENSIONS):
            raise ValueError("Inconsistent exact grading flags")
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


def finite_nonnegative(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def _ledger_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Missing ledger timestamp")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Malformed ledger timestamp") from error
    if timestamp.tzinfo is None:
        raise ValueError("Ledger timestamp requires a timezone")
    return timestamp.astimezone(timezone.utc)


def _code_identity(record: dict) -> tuple:
    if "runner_git_commit" not in record or "runner_git_dirty" not in record:
        raise ValueError("Missing runner Git provenance")
    commit, dirty = record["runner_git_commit"], record["runner_git_dirty"]
    if commit is None and dirty is None:
        return None, None
    if not isinstance(commit, str) or re.fullmatch("[0-9a-f]{40}", commit) is None or type(dirty) is not bool:
        raise ValueError("Invalid runner Git provenance")
    return commit, dirty


def validate_task_result(task: dict, item: dict, model: dict) -> None:
    """Replay grading against frozen labels without contacting a provider."""
    from baseline.evaluator import grade_border_prediction
    from baseline.providers import parse_prediction
    targets = {f"{key}_gt": item["groundTruth"][key] for key in DIMENSIONS}
    targets.update(task_id=item["taskId"], theme=item["groundTruth"]["theme"],
                   model_name=model["model"], provider=model["provider"])
    if any(type(task.get(key)) is not type(value) or task.get(key) != value for key, value in targets.items()):
        raise ValueError("Task targets or model identity disagree with the frozen dataset")
    if not isinstance(task.get("raw_prediction"), str):
        raise ValueError("Task has no raw prediction")
    try:
        parsed = parse_prediction(task["raw_prediction"])
    except ValueError:
        parsed = None
    invalid = task.get("error_kind") == "invalid_response"
    if task.get("error_kind") not in (None, "invalid_response") or task.get("error") and not invalid:
        raise ValueError("Infrastructure failures are not completed observations")
    if parsed is not None and invalid:
        raise ValueError("Parseable answer was mislabeled invalid_response")
    if parsed is None and not invalid:
        raise ValueError("Malformed raw prediction was not graded invalid")
    flags = ({f"{key}_correct": False for key in DIMENSIONS} | {"all_correct": False}) if invalid else grade_border_prediction(parsed, item["groundTruth"])
    if any(type(task.get(key)) is not bool or task[key] != value for key, value in flags.items()):
        raise ValueError("Task grades disagree with raw prediction replay")
    if not invalid and any(task.get(f"predicted_{key}") != parsed[key] for key in DIMENSIONS):
        raise ValueError("Stored prediction disagrees with raw prediction")
    if task.get("latency_sec") is not None and not finite_nonnegative(task["latency_sec"]):
        raise ValueError("Invalid observation latency")
    if task.get("cost_usd") is not None and not finite_nonnegative(task["cost_usd"]):
        raise ValueError("Invalid observation cost")
    _ledger_time(task.get("recorded_at"))


def aggregate_release_runs(release: dict, items: list[dict], results_root: str | Path, *, root=None) -> dict:
    """Verify run ledgers and keep the earliest final answer per config and task."""
    from baseline.model_config import _ModelConfig
    from baseline.releases import model_config_fingerprint

    identity = {
        "release": release["benchmark_version"], "dataset_git_commit": release.get("dataset_git_commit"),
        "dataset_fingerprint": release["dataset_fingerprint"],
        "evaluation_protocol": release["evaluation_protocol_fingerprint"],
        "expected_task_count": release.get("expected_task_count", len(items)), "grading_version": GRADING_VERSION,
        "schema_version": 1, "mock": False,
    }
    by_id = {item["taskId"]: item for item in items}
    directory = Path(results_root) / release["benchmark_version"]
    candidates, configs, runs, warnings, excluded = [], {}, [], [], []
    for run_dir in sorted(directory.iterdir()) if directory.is_dir() else []:
        if not run_dir.is_dir() or run_dir.name.startswith("mock-"):
            continue
        try:
            if any((run_dir / name).exists() for name in ("finalization.json", "final_results.json")):
                from baseline.finalize import verify_finalization
                verify_finalization(run_dir, root=root)
            metadata = read_report_json(run_dir / "run.json", warnings)
            summary = read_report_json(run_dir / "summary.json", warnings)
            if any(record.get(key) != value for record in (metadata, summary) for key, value in identity.items()):
                raise ValueError("Incompatible release, dataset, protocol, or mock provenance")
            if any(record.get("run_id") != run_dir.name for record in (metadata, summary)):
                raise ValueError("Run ID disagrees with its directory")
            created, updated = _ledger_time(metadata.get("created_at")), _ledger_time(summary.get("updated_at"))
            if _ledger_time(summary.get("created_at")) != created or updated < created:
                raise ValueError("Inconsistent run chronology")
            invocations = metadata.get("invocations")
            if not isinstance(invocations, list) or not invocations:
                raise ValueError("Missing invocation history")
            code_ids = set()
            for invocation in invocations:
                if not isinstance(invocation, dict) or not isinstance(invocation.get("models"), list) or not invocation["models"]:
                    raise ValueError("Malformed invocation history")
                code_ids.add(_code_identity(invocation))
                if not created <= _ledger_time(invocation.get("started_at")) <= _ledger_time(invocation.get("updated_at")) <= updated:
                    raise ValueError("Invalid invocation chronology")
                if "finished_at" in invocation and not created <= _ledger_time(invocation["finished_at"]) <= updated:
                    raise ValueError("Invalid invocation finish time")
            if _code_identity(summary) != _code_identity(invocations[-1]):
                raise ValueError("Summary runner provenance disagrees with its invocation")
            if not isinstance(summary.get("models"), dict) or not isinstance(metadata.get("model_configs"), dict):
                raise ValueError("Missing model configuration roster")
            if set(summary["models"]) != set(metadata["model_configs"]):
                raise ValueError("Summary and metadata model rosters disagree")
            ledger = [json.loads(line) for line in (run_dir / "attempts.jsonl").read_text().splitlines()]
            final_rows, seen_attempts, cost_by_model, errors_by_model = {}, set(), {}, {}
            for attempt in ledger:
                if not isinstance(attempt, dict) or not isinstance(attempt.get("result"), dict):
                    raise ValueError("Malformed attempt ledger")
                attempt_id, model_id, task_id = (attempt.get(key) for key in ("attempt_id", "model_id", "task_id"))
                if not isinstance(attempt_id, str) or attempt_id in seen_attempts:
                    raise ValueError("Duplicate or missing attempt identity")
                seen_attempts.add(attempt_id)
                if model_id not in metadata["model_configs"] or task_id not in by_id:
                    raise ValueError("Unknown attempt model or dataset task")
                if not created <= _ledger_time(attempt.get("created_at")) <= updated:
                    raise ValueError("Attempt falls outside run chronology")
                result = attempt["result"]
                if result.get("task_id") != task_id:
                    raise ValueError("Attempt task identity disagrees with its result")
                cost = result.get("cost_usd")
                if cost is not None and not finite_nonnegative(cost):
                    raise ValueError("Invalid attempt cost")
                if not finite_nonnegative(attempt.get("cost_usd")) or not math.isclose(attempt["cost_usd"], cost or 0, abs_tol=1e-12):
                    raise ValueError("Attempt billed cost disagrees with its result")
                costs = cost_by_model.setdefault(model_id, [])
                costs.append(cost)
                key = (model_id, task_id)
                if key in final_rows:
                    raise ValueError("Attempt follows an already final answer")
                if not result.get("error") or result.get("error_kind") == "invalid_response":
                    final_rows[key] = result
                else:
                    errors_by_model[model_id] = errors_by_model.get(model_id, 0) + 1
            if not finite_nonnegative(summary.get("spent_cost_usd")) or not math.isclose(
                summary["spent_cost_usd"], sum(cost or 0 for costs in cost_by_model.values() for cost in costs), abs_tol=1e-9
            ):
                raise ValueError("Summary cost disagrees with attempt history")
            if summary.get("cost_incomplete") is not any(cost is None for costs in cost_by_model.values() for cost in costs):
                raise ValueError("Unknown cost provenance disagrees with attempt history")
        except (ValueError, TypeError, KeyError, OSError, AttributeError) as error:
            warnings.append(f"Excluded {run_dir.name}: {error}")
            excluded.append({"path": run_dir.name, "reason": str(error)})
            continue
        run_record = {"run_id": run_dir.name, "created_at": created.isoformat(), "updated_at": updated.isoformat(),
                      "spent_cost_usd": summary["spent_cost_usd"], "cost_incomplete": summary["cost_incomplete"],
                      "runner_git_commit": summary["runner_git_commit"], "runner_git_dirty": summary["runner_git_dirty"],
                      "invocations": invocations}
        runs.append(run_record)
        for path in sorted(run_dir.glob("scorecard_*.json")):
            try:
                card = read_report_json(path, warnings)
                tasks = scorecard_tasks(card, dataset_fingerprint=identity["dataset_fingerprint"])
                if any(card.get(key) != value for key, value in identity.items()) or card.get("run_id") != run_dir.name:
                    raise ValueError("Scorecard release identity disagrees with its ledger")
                config = _ModelConfig.model_validate_json(json.dumps(card.get("model_config"))).model_dump(mode="json")
                model_id = config["id"]
                config_id = model_config_fingerprint(config)
                state = summary["models"].get(model_id)
                if (path.name != f"scorecard_{model_id}.json" or card.get("model_id") != model_id
                        or card.get("model_name") != config["model"] or card.get("provider") != config["provider"]
                        or card.get("max_output_tokens") != config["max_output_tokens"]
                        or card.get("model_config_fingerprint") != config_id
                        or metadata["model_configs"].get(model_id) != config or not isinstance(state, dict)
                        or state.get("model_config") != config or state.get("model_config_fingerprint") != config_id
                        or type(state.get("completed")) is not int or state.get("completed") != len(tasks) or _code_identity(card) not in code_ids
                        or not any(config in invocation["models"] for invocation in invocations)):
                    raise ValueError("Inconsistent recorded model configuration")
                card_updated = _ledger_time(card.get("updated_at"))
                if _ledger_time(card.get("created_at")) != created or not created <= card_updated <= updated:
                    raise ValueError("Scorecard chronology disagrees with its ledger")
                expected_rows = {task_id: result for (m_id, task_id), result in final_rows.items() if m_id == model_id}
                if {task["task_id"]: task for task in tasks} != expected_rows:
                    raise ValueError("Scorecard rows disagree with final attempt records")
                model_costs = cost_by_model.get(model_id, [])
                model_cost = None if any(cost is None for cost in model_costs) else sum(model_costs)
                state_cost = state.get("cost_usd")
                if ((model_cost is None and state_cost is not None)
                        or (model_cost is not None and (not finite_nonnegative(state_cost)
                            or not math.isclose(state_cost, model_cost, rel_tol=0, abs_tol=1e-12)))):
                    raise ValueError("Model cost disagrees with its attempt ledger")
                for task in tasks:
                    item = by_id.get(task["task_id"])
                    if item is None:
                        raise ValueError("Unknown release task")
                    validate_task_result(task, item, config)
                    recorded = _ledger_time(task["recorded_at"])
                    if not created <= recorded <= card_updated or not any(
                        _ledger_time(invocation["started_at"]) <= recorded <= _ledger_time(invocation["updated_at"])
                        for invocation in invocations if config in invocation["models"]
                    ):
                        raise ValueError("Observation falls outside an invocation of its model configuration")
            except (ValueError, TypeError, KeyError, AttributeError) as error:
                warnings.append(f"Excluded {run_dir.name}/{path.name}: {error}")
                excluded.append({"path": f"{run_dir.name}/{path.name}", "reason": str(error)})
                continue
            entry = configs.setdefault(config_id, {
                "id": config_id, "model_id": model_id, "display_name": config["display_name"],
                "provider": config["provider"], "model": config["model"],
                "max_output_tokens": config["max_output_tokens"], "model_config": config,
                "runs": [], "origins": [], "repeat_observations": 0, "repeat_cost_usd": 0.0,
                "total_cost_usd": 0.0, "infrastructure_errors": 0,
            })
            if run_dir.name not in entry["runs"]:
                entry["runs"].append(run_dir.name)
            entry["origins"].append({**run_record, "model_id": model_id, "model_config": config,
                                     "task_count": len(tasks), "cost_usd": model_cost})
            entry["total_cost_usd"] = None if model_cost is None or entry["total_cost_usd"] is None else entry["total_cost_usd"] + model_cost
            entry["infrastructure_errors"] += errors_by_model.get(model_id, 0)
            candidates.extend((_ledger_time(task["recorded_at"]), run_dir.name, model_id, config_id, task) for task in tasks)
    observations = {}
    for recorded, run_id, model_id, config_id, task in sorted(candidates, key=lambda row: row[:3]):
        key = (config_id, task["task_id"])
        if key in observations:
            configs[config_id]["repeat_observations"] += 1
            cost = task.get("cost_usd")
            prior_cost = configs[config_id]["repeat_cost_usd"]
            configs[config_id]["repeat_cost_usd"] = None if cost is None or prior_cost is None else prior_cost + cost
        else:
            observations[key] = {"recorded_at": recorded.isoformat(), "run": run_id, "model_id": model_id, "task": task}
    for entry in configs.values():
        entry["runs"].sort()
    return {"observations": observations, "configs": configs, "runs": runs, "warnings": warnings,
            "excluded_runs": excluded, "duplicate_policy": "First recorded final answer; ties use run ID, then model ID."}
