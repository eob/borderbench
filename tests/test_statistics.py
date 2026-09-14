import importlib


def test_class_balance_diagnostics_expose_majority_predictors_and_absence_shortcuts():
    stats = importlib.import_module("baseline.statistics")
    tasks = []
    for i in range(10):
        gt = dict(has_border=i == 0, border_sides="all-4" if i == 0 else "none",
                  stroke_width="1px" if i == 0 else "0px", stroke_style="solid" if i == 0 else "none",
                  corner_radius="sharp", corner_uniformity="all-corners", elevation="none")
        prediction = {**gt, "stroke_width": "0px"}
        tasks.append({**{key + "_gt": value for key, value in gt.items()},
                      **{"predicted_" + key: value for key, value in prediction.items()},
                      **{key + "_correct": prediction[key] == value for key, value in gt.items()}})
    report = stats.diagnostic_metrics(tasks)
    width = report["attributes"]["stroke_width"]
    assert width["accuracy"] == .9
    assert width["balanced_accuracy_observed_classes"] == .5
    assert width["majority_baseline"] == .9
    assert width["class_recall"]["1px"] == 0
    assert width["class_recall"]["8px"] is None
    assert width["confusion"]["1px"]["0px"] == 1
    assert report["border_present"]["stroke_width"]["accuracy"] == 0


def test_empty_diagnostic_cohort_is_unknown_not_zero():
    stats = importlib.import_module("baseline.statistics")
    width = stats.diagnostic_metrics([])["attributes"]["stroke_width"]
    assert width["count"] == 0
    assert width["accuracy"] is None
    assert width["balanced_accuracy_observed_classes"] is None


def test_matched_blocks_require_complete_level_sets():
    from baseline.statistics import matched_block_metrics
    items = [dict(taskId=str(i), groundTruth=dict(theme="light", elevation="none"),
                  design=dict(matchedBlocks=[dict(id="width", axis="stroke_width", level=str(i))]))
             for i in range(3)]
    tasks = [dict(task_id=str(i), stroke_width_correct=i != 2) for i in range(3)]
    full = matched_block_metrics(tasks, items)["stroke_width"]
    assert full["complete_blocks"] == 1
    assert full["all_levels_correct_rate"] == 0
    assert full["both_levels_correct_pair_rate"] == 1 / 3
    partial = matched_block_metrics(tasks[:2], items)["stroke_width"]
    assert partial["complete_blocks"] == 0
    assert partial["both_levels_correct_pair_rate"] is None
