"""Independent dataset release gate: every image and label checked offline."""

import hashlib
import io
import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from baseline.validate_dataset import validate_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]

CANVAS_W, CANVAS_H = 560, 360
CARD_W, CARD_H = 400, 240
DPR = 2


def _card_image(border_px: int = 1, radius_px: int = 12, variant: int = 0) -> bytes:
    canvas = Image.new("RGB", (CANVAS_W * DPR, CANVAS_H * DPR), (241, 245, 249))
    left = (CANVAS_W - CARD_W) // 2 * DPR
    top = (CANVAS_H - CARD_H) // 2 * DPR
    right = left + CARD_W * DPR - 1
    bottom = top + CARD_H * DPR - 1
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((left, top, right, bottom), radius=radius_px * DPR, fill=(203, 213, 225))
    inset = border_px * DPR
    draw.rounded_rectangle((left + inset, top + inset, right - inset, bottom - inset), radius=max(0, radius_px * DPR - inset), fill=(255, 255, 255))
    font = ImageFont.truetype(str(REPO_ROOT / "src/assets/DejaVuSans.ttf"), 32)
    for y in (264, 312, 360):
        draw.text((340, y), "Reference text", font=font, fill=(51, 65, 85))
    draw.rectangle((496, 432, 623, 435), fill=(51, 65, 85))
    canvas.putpixel((400, 300), (variant, 0, 0))
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()


def _write_corpus(root: Path, images: dict[str, bytes], ground_truth: dict | None = None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    prompt = (REPO_ROOT / "baseline" / "prompt.txt").read_text(encoding="utf-8")
    font_path = root / "fonts/DejaVuSans.ttf"
    font_path.parent.mkdir(exist_ok=True)
    font_path.write_bytes((REPO_ROOT / "src/assets/DejaVuSans.ttf").read_bytes())
    font_hash = hashlib.sha256(font_path.read_bytes()).hexdigest()
    tasks = []
    for task_id, raw in images.items():
        (root / f"{task_id}.png").write_bytes(raw)
        tasks.append(
            {
                "taskId": task_id,
                "imageFilename": f"{task_id}.png",
                "imagePath": f"{task_id}.png",
                "groundTruth": ground_truth
                or {
                    "has_border": True,
                    "border_sides": "all-4",
                    "stroke_style": "solid",
                    "stroke_width": "1px",
                    "stroke_width_px": 1,
                    "corner_radius": "medium",
                    "corner_radius_px": 12,
                    "corner_uniformity": "all-corners",
                    "elevation": "none",
                    "theme": "white-on-gray",
                },
                "prompt": prompt,
                "imageSha256": hashlib.sha256(raw).hexdigest(),
                "rendered": {
                    "browser": "chromium-test",
                    "platform": "linux",
                    "reference": {"fontFamily": "BorderBench Reference", "fontSizePx": 16, "lineHeightPx": 24, "ruleWidthPx": 64},
                    "font": {"path": "fonts/DejaVuSans.ttf", "sha256": font_hash, "family": "DejaVu Sans", "platformFonts": [{"familyName": "DejaVu Sans", "isCustomFont": True, "glyphCount": 20}]},
                    "shadowReference": {"imageFilename": f"{task_id}.png", "imageSha256": hashlib.sha256(raw).hexdigest()},
                    "viewport": {"width": 560, "height": 360, "deviceScaleFactor": 2},
                    "card": {"x": 80, "y": 60, "width": 400, "height": 240},
                    "computed": {
                        "borderTopWidth": "1px",
                        "borderRightWidth": "1px",
                        "borderBottomWidth": "1px",
                        "borderLeftWidth": "1px",
                        "borderTopStyle": "solid",
                        "borderRightStyle": "solid",
                        "borderBottomStyle": "solid",
                        "borderLeftStyle": "solid",
                        "borderTopLeftRadius": "12px",
                        "borderTopRightRadius": "12px",
                        "borderBottomRightRadius": "12px",
                        "borderBottomLeftRadius": "12px",
                        "boxShadow": "none",
                    },
                },
            }
        )
    catalog = {"schema_version": 1, "tasks": [{key: row.get(key) for key in ("taskId", "groundTruth", "design")} for row in tasks],
               "referenceFont": {"path": "fonts/DejaVuSans.ttf", "sha256": font_hash}, "prompt": prompt.strip()}
    (root / "catalog.json").write_text(json.dumps(catalog))
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps({"tasks": tasks, "total_tasks": len(tasks), "canonical_canvas": {"width_px": 560, "height_px": 360, "card_width_px": 400, "card_height_px": 240, "dpr": 2}}, indent=2), encoding="utf-8")
    return manifest


def test_valid_mini_corpus_passes(tmp_path):
    manifest = _write_corpus(
        tmp_path, {"t1": _card_image(1), "t2": _card_image(1, variant=1)}
    )
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is True, report["errors"]
    assert report["sample_count"] == 2


def test_corrupt_png_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    (tmp_path / "t1.png").write_bytes(b"not a png")
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("png" in e["code"] or "hash" in e["code"] or "decode" in e["code"] for e in report["errors"])


def test_duplicate_pixels_rejected(tmp_path):
    raw = _card_image()
    manifest = _write_corpus(tmp_path, {"t1": raw, "t2": raw})
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("duplicate" in e["code"] for e in report["errors"])


def test_hash_mismatch_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    (tmp_path / "t1.png").write_bytes(_card_image(6))
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("hash" in e["code"] for e in report["errors"])


def test_enum_violation_rejected(tmp_path):
    gt = {
        "has_border": True,
        "border_sides": "all-4",
        "stroke_style": "solid",
        "stroke_width": "3px",
        "stroke_width_px": 3,
        "corner_radius": "medium",
        "corner_radius_px": 12,
        "corner_uniformity": "all-corners",
        "elevation": "none",
        "theme": "white-on-gray",
    }
    manifest = _write_corpus(tmp_path, {"t1": _card_image()}, ground_truth=gt)
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("label" in e["code"] or "enum" in e["code"] for e in report["errors"])


def test_absolute_image_path_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["tasks"][0]["imagePath"] = "/tmp/elsewhere/t1.png"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("path" in e["code"] for e in report["errors"])


def test_invisible_boundary_rejected(tmp_path):
    gt = {
        "has_border": False,
        "border_sides": "none",
        "stroke_style": "none",
        "stroke_width": "0px",
        "stroke_width_px": 0,
        "corner_radius": "medium",
        "corner_radius_px": 12,
        "corner_uniformity": "all-corners",
        "elevation": "none",
        "theme": "white-on-white",
    }
    blank = Image.new("RGB", (CANVAS_W * DPR, CANVAS_H * DPR), (255, 255, 255))
    buffer = io.BytesIO()
    blank.save(buffer, format="PNG")
    manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()}, ground_truth=gt)
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("visib" in e["code"] or "contrast" in e["code"] for e in report["errors"])


def test_quota_violation_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image(1), "t2": _card_image(1, variant=1)})
    report = validate_dataset(manifest, min_per_label=8)
    assert report["valid"] is False
    assert any("quota" in e["code"] or "coverage" in e["code"] for e in report["errors"])


def test_prompt_mismatch_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["tasks"][0]["prompt"] = "a different prompt"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert report["valid"] is False
    assert any("prompt" in e["code"] for e in report["errors"])


def test_historical_manifest_rejected():
    report = validate_dataset(REPO_ROOT / "dataset" / "borderbench-1" / "manifest.json")
    assert report["valid"] is False
    assert report["errors"], "the invalid prototype set must fail the release gate"


@pytest.mark.parametrize("mutation", [
    lambda row: row["rendered"]["card"].update(x=float("nan")),
    lambda row: row["rendered"]["computed"].update(borderTopLeftRadius="NaNpx"),
    lambda row: row["rendered"]["card"].pop("x"),
    lambda row: row.update(groundTruth="broken"),
    lambda row: row["groundTruth"].update(has_border=1),
    lambda row: row["groundTruth"].update(corner_uniformity="top-only"),
    lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].pop("boxShadow")),
    lambda row: (row["groundTruth"].update(elevation="subtle-drop"), row["rendered"]["computed"].update(boxShadow="rgb(0, 0, 0) 0px 100px 100px 100px")),
])
def test_malformed_or_forged_evidence_fails_closed(tmp_path, mutation):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text())
    mutation(data["tasks"][0])
    manifest.write_text(json.dumps(data))
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert not report["valid"], "Malformed evidence must fail with findings, without crashing"


def test_incorrect_declared_task_count_is_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text())
    data["total_tasks"] = 999
    manifest.write_text(json.dumps(data))
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert any(error["code"] == "manifest_count" for error in report["errors"])


def test_release_gate_requires_every_label(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    report = validate_dataset(manifest)
    assert any(error["code"] == "coverage" for error in report["errors"]), "Absent classes need explicit coverage findings"


def test_pixels_cannot_claim_a_different_border_width(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image(8)})
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert any(error["code"] == "pixel_width" for error in report["errors"])


def test_pixels_cannot_claim_a_different_radius(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image(1, radius_px=24)})
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert any(error["code"] == "pixel_radius" for error in report["errors"])


def test_dots_cannot_be_labeled_as_dashes():
    from baseline.validate_dataset import _check_pixels

    image = Image.open(io.BytesIO(_card_image())).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((490, 120, 630, 121), fill="white")
    for x in range(490, 630, 4):
        draw.rectangle((x, 120, x + 1, 121), fill=(203, 213, 225))
    item = {"taskId": "t1", "groundTruth": {
        "has_border": True, "border_sides": "all-4", "stroke_style": "dashed", "stroke_width": "1px",
        "corner_radius": "medium", "corner_radius_px": 12, "elevation": "none", "theme": "white-on-gray",
    }}
    findings = []
    _check_pixels(item, image, image.copy(), lambda code, detail, *_: findings.append((code, detail)))
    assert any(code == "pixel_style" and "segment length" in detail for code, detail in findings)


def test_missing_reference_text_and_rule_fail_even_with_updated_hashes(tmp_path):
    image = Image.open(io.BytesIO(_card_image())).convert("RGB")
    ImageDraw.Draw(image).rectangle((320, 264, 799, 455), fill="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()})
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert any(error["code"] == "reference_pixels" for error in report["errors"])


def test_missing_shadow_pixels_fail_independently_of_correct_css_evidence():
    from baseline.validate_dataset import _check_pixels

    image = Image.open(io.BytesIO(_card_image())).convert("RGB")
    item = {"taskId": "t1", "groundTruth": {
        "has_border": True, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px",
        "corner_radius": "medium", "corner_radius_px": 12, "elevation": "subtle-drop", "theme": "white-on-gray",
    }}
    findings = []
    _check_pixels(item, image, image.copy(), lambda code, *args: findings.append(code))
    assert "pixel_shadow" in findings


def test_shadow_pixels_must_match_the_coarse_spread_category():
    from baseline.validate_dataset import _check_pixels

    flat = Image.open(io.BytesIO(_card_image())).convert("RGB")
    image = flat.copy()
    ImageDraw.Draw(image).rectangle((200, 610, 919, 634), fill=(225, 229, 233))
    item = {"taskId": "t1", "groundTruth": {
        "has_border": True, "border_sides": "all-4", "stroke_style": "solid", "stroke_width": "1px",
        "corner_radius": "medium", "corner_radius_px": 12, "elevation": "subtle-drop", "theme": "white-on-gray",
    }}
    findings = []
    _check_pixels(item, image, flat, lambda code, *args: findings.append(code))
    assert "pixel_shadow_scale" in findings


def test_rgb_transparency_chunk_is_rejected(tmp_path):
    image = Image.open(io.BytesIO(_card_image())).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", transparency=(255, 255, 255))
    manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()})
    report = validate_dataset(manifest, min_per_label=1, require_complete=False)
    assert any(error["code"] == "png_alpha" for error in report["errors"])
