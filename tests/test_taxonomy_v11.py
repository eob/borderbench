"""V1.1 taxonomy: Tailwind Rosetta Stone, fixed context, no double borders."""

import json
from pathlib import Path

import pytest

from baseline.providers import BorderPrediction, parse_prediction

REPO_ROOT = Path(__file__).resolve().parents[1]
VALID = {
    "has_border": True,
    "border_sides": "all-4",
    "stroke_style": "solid",
    "stroke_width": "1px",
    "corner_radius": "medium",
    "corner_uniformity": "all-corners",
    "elevation": "none",
}


def test_prompt_is_tailwind_rosetta_with_fixed_context():
    prompt = (REPO_ROOT / "baseline" / "prompt.txt").read_text(encoding="utf-8")
    for token in ("Tailwind", "border-8", "rounded-full", "shadow-lg", "DejaVu Sans", "16px"):
        assert token in prompt, f"prompt must declare {token}"
    assert '"double"' not in prompt, "double borders left the taxonomy in 1.1.0"


def test_double_rejected_at_schema_boundary():
    with pytest.raises(ValueError, match="[Ii]nvalid"):
        parse_prediction(json.dumps({**VALID, "stroke_style": "double"}))
    with pytest.raises(Exception):
        BorderPrediction.model_validate({**VALID, "stroke_style": "double"})


def test_rosetta_doc_covers_every_label():
    guide = (REPO_ROOT / "dataset" / "README.md").read_text(encoding="utf-8")
    assert "Tailwind" in guide
    for token in (
        "border-0", "border-2", "border-4", "border-8",
        "border-solid", "border-dashed", "border-dotted",
        "rounded-none", "rounded-lg", "rounded-full",
        "shadow-md", "shadow-lg", "ring-1",
    ):
        assert token in guide, f"rosetta must map {token}"


def test_exports_list_no_double_style():
    from baseline.export_structured import build_structured_benchmark  # noqa: F401
    import baseline.export_structured as export_module
    import inspect

    assert '"double"' not in inspect.getsource(export_module), "export taxonomy must drop double"
