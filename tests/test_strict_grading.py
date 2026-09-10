"""Strict whole-answer grading: ambiguous predictions earn zero, not partial credit."""

import json

import pytest

from baseline.evaluator import BaselineEvaluator
from baseline.providers import BorderPrediction, PredictionResponse


VALID = {
    "has_border": True,
    "border_sides": "all-4",
    "stroke_style": "solid",
    "stroke_width": "1px",
    "corner_radius": "medium",
    "corner_uniformity": "all-corners",
    "elevation": "none",
}

ITEM = {
    "taskId": "t1",
    "imagePath": "t1.png",
    "groundTruth": {**VALID, "theme": "white-on-gray"},
}


def _evaluate(monkeypatch, raw: str, parsed: dict):
    evaluator = BaselineEvaluator(mock=True)
    response = PredictionResponse(raw_text=raw, parsed=parsed)
    monkeypatch.setattr(evaluator, "predict_image", lambda image_path, prompt: response)
    return evaluator._eval_single_task(ITEM, "prompt")


def test_valid_prediction_still_passes(monkeypatch):
    raw = json.dumps(VALID)
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is True
    assert result.error_kind is None


def test_extra_key_invalidates_whole_answer(monkeypatch):
    raw = json.dumps({**VALID, "confidence": 0.9})
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"
    assert result.stroke_style_correct is False


def test_duplicate_keys_invalidates_whole_answer(monkeypatch):
    raw = '{"has_border": true, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px", "stroke_width": "8px", "corner_radius": "medium", "corner_uniformity": "all-corners", "elevation": "none"}'
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"


def test_missing_field_invalidates_whole_answer(monkeypatch):
    partial = {k: v for k, v in VALID.items() if k != "elevation"}
    raw = json.dumps(partial)
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"
    assert result.stroke_style_correct is False


def test_blank_value_invalidates_whole_answer(monkeypatch):
    raw = json.dumps({**VALID, "stroke_width": "   "})
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"
    assert result.stroke_style_correct is False


def test_invalid_enum_invalidates_whole_answer(monkeypatch):
    raw = json.dumps({**VALID, "stroke_width": "3px"})
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"


def test_nonstring_value_invalidates_whole_answer(monkeypatch):
    raw = json.dumps({**VALID, "corner_radius": 8})
    result = _evaluate(monkeypatch, raw, json.loads(raw))
    assert result.all_correct is False
    assert result.error_kind == "invalid_response"


def test_schema_forbids_extra_keys():
    with pytest.raises(Exception, match="extra|Extra|additional"):
        BorderPrediction.model_validate({**VALID, "confidence": 0.9})


def test_parse_prediction_valid_normalizes():
    from baseline.providers import parse_prediction

    parsed = parse_prediction(json.dumps({**VALID, "border_sides": " All-4 "}))
    assert parsed == VALID


def test_parse_prediction_rejects_malformed():
    from baseline.providers import parse_prediction

    with pytest.raises(ValueError, match="[Ee]xtra|unknown|Unknown"):
        parse_prediction(json.dumps({**VALID, "confidence": 0.9}))
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        parse_prediction('{"has_border": true, "has_border": false, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px", "corner_radius": "medium", "corner_uniformity": "all-corners", "elevation": "none"}')
    with pytest.raises(ValueError, match="[Mm]issing"):
        parse_prediction(json.dumps({k: v for k, v in VALID.items() if k != "elevation"}))
    with pytest.raises(ValueError, match="[Bb]lank|[Ee]mpty"):
        parse_prediction(json.dumps({**VALID, "stroke_width": "   "}))
    with pytest.raises(ValueError, match="[Ii]nvalid"):
        parse_prediction(json.dumps({**VALID, "stroke_width": "3px"}))
    with pytest.raises(ValueError, match="[Bb]ool"):
        parse_prediction(json.dumps({**VALID, "has_border": "true"}))
