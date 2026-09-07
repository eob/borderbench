from baseline.evaluator import BaselineEvaluator, TaskEvaluationResult, BorderBenchScorecard
from baseline.providers import BorderPrediction


def test_border_prediction_schema():
    valid = {
        "has_border": True,
        "border_sides": "all-4",
        "stroke_style": "solid",
        "stroke_width": "1px",
        "corner_radius": "medium",
        "corner_uniformity": "all-corners",
        "elevation": "none",
    }
    pred = BorderPrediction.model_validate(valid)
    assert pred.has_border is True
    assert pred.border_sides == "all-4"
    assert pred.stroke_width == "1px"


def test_evaluator_scoring():
    evaluator = BaselineEvaluator(mock=True)
    item = {
        "taskId": "test-1",
        "imagePath": "test.png",
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
    assert result.all_correct is True
    assert result.has_border_correct is True
    assert result.border_sides_correct is True

    scorecard = evaluator.score_results([result], expected_task_count=1)
    assert scorecard.overall_exact_match == 100.0
    assert scorecard.has_border_accuracy == 100.0
    assert scorecard.total_tasks == 1
