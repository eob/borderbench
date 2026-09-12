import json
from dataclasses import replace

import pytest

from baseline.evaluator import BaselineEvaluator, DEFAULT_PROMPT
from baseline.providers import parse_prediction


TARGET = dict(has_border=True, border_sides="all-4", stroke_style="solid",
              stroke_width="1px", corner_radius="medium",
              corner_uniformity="all-corners", elevation="none")


@pytest.mark.parametrize("elevation", ["ring-only", "stroke+shadow"])
def test_hidden_css_provenance_is_not_an_answer_category(elevation):
    with pytest.raises(ValueError, match="Invalid"):
        parse_prediction(json.dumps({**TARGET, "elevation": elevation}))


def test_prompt_defines_exact_coarse_versioned_anchors():
    for token in ("3.4.17", "rounded-xl", "rounded-3xl", "12px", "24px", "DejaVu Sans"):
        assert token in DEFAULT_PROMPT


def test_partial_accuracy_uses_observed_final_answers_and_reports_coverage():
    evaluator = BaselineEvaluator(mock=True)
    result = evaluator._eval_single_task(dict(taskId="sample", imagePath="unused.png",
        groundTruth={**TARGET, "theme": "white-on-gray"}), DEFAULT_PROMPT)
    infrastructure = replace(result, task_id="unavailable", error="timeout", error_kind="unavailable")
    card = evaluator.score_results([result, infrastructure], expected_task_count=10)
    assert card.total_tasks == 1
    assert card.overall_exact_match == 100
    assert card.expected_task_count == 10
    assert card.status == "partial"


def test_grading_purely_compares_perceptual_dimensions():
    from baseline.evaluator import grade_border_prediction
    assert grade_border_prediction(TARGET, TARGET)["all_correct"] is True
    flags = grade_border_prediction({**TARGET, "stroke_width": "2px"}, TARGET)
    assert not flags["all_correct"] and not flags["stroke_width_correct"]
    assert flags["elevation_correct"]
