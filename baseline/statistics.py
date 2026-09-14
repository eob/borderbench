"""Descriptive class diagnostics for a fixed, explicitly selected task cohort."""

from collections import Counter, defaultdict
from itertools import combinations

from baseline.providers import BorderPrediction, PREDICTION_KEYS


def diagnostic_metrics(tasks: list[dict]) -> dict:
    """Expose label imbalance and exclude trivial absence cases in stroke diagnostics."""
    schema = BorderPrediction.model_json_schema()["properties"]

    def attribute(rows: list[dict], axis: str) -> dict:
        labels = [False, True] if axis == "has_border" else schema[axis]["enum"]
        counts = Counter(row[axis + "_gt"] for row in rows)
        correct = Counter(row[axis + "_gt"] for row in rows if row[axis + "_correct"])
        label_key = lambda label: str(label).lower() if isinstance(label, bool) else label
        confusion = {label_key(label): {} for label in labels}
        for row in rows:
            predicted = "invalid" if row.get("error_kind") == "invalid_response" else label_key(row.get("predicted_" + axis, "invalid"))
            cell = confusion[label_key(row[axis + "_gt"])]
            cell[predicted] = cell.get(predicted, 0) + 1
        recall = {label_key(label): correct[label] / counts[label] if counts[label] else None for label in labels}
        observed = [value for value in recall.values() if value is not None]
        return dict(count=len(rows), accuracy=sum(correct.values()) / len(rows) if rows else None,
                    balanced_accuracy_observed_classes=sum(observed) / len(observed) if observed else None,
                    observed_class_count=len(observed), defined_class_count=len(labels),
                    majority_baseline=max(counts.values()) / len(rows) if rows else None,
                    class_count={label_key(label): counts[label] for label in labels},
                    class_recall=recall, confusion=confusion)

    present = [row for row in tasks if row["has_border_gt"]]
    return dict(attributes={axis: attribute(tasks, axis) for axis in PREDICTION_KEYS},
                border_present={axis: attribute(present, axis) for axis in ("border_sides", "stroke_style", "stroke_width")},
                interpretation="Descriptive metrics on the selected finite cohort. Missing classes have null recall. Theme repeats are not independent samples; no population confidence claim is made.")


def matched_block_metrics(tasks: list[dict], items: list[dict]) -> dict:
    """Score complete intervention blocks, preserving identical nuisance conditions."""
    blocks = defaultdict(list)
    observed = {task["task_id"]: task for task in tasks}
    for item in items:
        gt = item["groundTruth"]
        for block in item.get("design", {}).get("matchedBlocks", []):
            axis = block["axis"]
            if axis not in PREDICTION_KEYS:
                continue
            condition = None if axis == "elevation" else gt["elevation"]
            blocks[(axis, block["id"], gt["theme"], condition)].append(item["taskId"])
    by_axis = defaultdict(lambda: dict(expected_blocks=0, complete_blocks=0, correct_blocks=0,
                                     level_pairs=0, correct_pairs=0))
    for (axis, *_), task_ids in blocks.items():
        if len(task_ids) < 2:
            continue
        out = by_axis[axis]
        out["expected_blocks"] += 1
        if not all(task_id in observed for task_id in task_ids):
            continue
        flags = [observed[task_id][axis + "_correct"] for task_id in task_ids]
        out["complete_blocks"] += 1
        out["correct_blocks"] += all(flags)
        for first, second in combinations(flags, 2):
            out["level_pairs"] += 1
            out["correct_pairs"] += first and second
    return {axis: {**out,
                   "all_levels_correct_rate": out["correct_blocks"] / out["complete_blocks"] if out["complete_blocks"] else None,
                   "both_levels_correct_pair_rate": out["correct_pairs"] / out["level_pairs"] if out["level_pairs"] else None}
            for axis, out in sorted(by_axis.items())}
