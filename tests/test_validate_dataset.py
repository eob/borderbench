"""Independent dataset release gate: every image and label checked offline."""

import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from baseline.validate_dataset import validate_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]

CANVAS_W, CANVAS_H = 560, 360
CARD_W, CARD_H = 400, 240
DPR = 2


def _card_image(border_px: int = 2, radius_px: int = 8) -> bytes:
    canvas = Image.new("RGB", (CANVAS_W * DPR, CANVAS_H * DPR), (241, 245, 249))
    pixels = canvas.load()
    left = (CANVAS_W - CARD_W) // 2 * DPR
    top = (CANVAS_H - CARD_H) // 2 * DPR
    right = left + CARD_W * DPR
    bottom = top + CARD_H * DPR
    for y in range(top, bottom):
        for x in range(left, right):
            edge = min(x - left, right - 1 - x, y - top, bottom - 1 - y)
            pixels[x, y] = (203, 213, 225) if edge < border_px * DPR else (255, 255, 255)
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()


def _write_corpus(root: Path, images: dict[str, bytes], ground_truth: dict | None = None) -> Path:
    from baseline.evaluator import load_manifest  # noqa: F401  (pins loader availability)

    root.mkdir(parents=True, exist_ok=True)
    prompt = (REPO_ROOT / "baseline" / "prompt.txt").read_text(encoding="utf-8")
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
                    "corner_radius_px": 8,
                    "corner_uniformity": "all-corners",
                    "elevation": "none",
                    "theme": "white-on-gray",
                },
                "prompt": prompt,
                "imageSha256": hashlib.sha256(raw).hexdigest(),
                "rendered": {
                    "browser": "chromium-test",
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
                        "borderTopLeftRadius": "8px",
                        "borderTopRightRadius": "8px",
                        "borderBottomRightRadius": "8px",
                        "borderBottomLeftRadius": "8px",
                        "boxShadow": "none",
                    },
                },
            }
        )
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps({"tasks": tasks}, indent=2), encoding="utf-8")
    return manifest


def test_valid_mini_corpus_passes(tmp_path):
    manifest = _write_corpus(
        tmp_path, {"t1": _card_image(2), "t2": _card_image(4)}
    )
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is True, report["errors"]
    assert report["sample_count"] == 2


def test_corrupt_png_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    (tmp_path / "t1.png").write_bytes(b"not a png")
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is False
    assert any("png" in e["code"] or "hash" in e["code"] or "decode" in e["code"] for e in report["errors"])


def test_duplicate_pixels_rejected(tmp_path):
    raw = _card_image()
    manifest = _write_corpus(tmp_path, {"t1": raw, "t2": raw})
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is False
    assert any("duplicate" in e["code"] for e in report["errors"])


def test_hash_mismatch_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    (tmp_path / "t1.png").write_bytes(_card_image(6))
    report = validate_dataset(manifest, min_per_label=1)
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
        "corner_radius_px": 8,
        "corner_uniformity": "all-corners",
        "elevation": "none",
        "theme": "white-on-gray",
    }
    manifest = _write_corpus(tmp_path, {"t1": _card_image()}, ground_truth=gt)
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is False
    assert any("label" in e["code"] or "enum" in e["code"] for e in report["errors"])


def test_absolute_image_path_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["tasks"][0]["imagePath"] = "/tmp/elsewhere/t1.png"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    report = validate_dataset(manifest, min_per_label=1)
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
        "corner_radius_px": 8,
        "corner_uniformity": "all-corners",
        "elevation": "none",
        "theme": "white-on-white",
    }
    blank = Image.new("RGB", (CANVAS_W * DPR, CANVAS_H * DPR), (255, 255, 255))
    buffer = io.BytesIO()
    blank.save(buffer, format="PNG")
    manifest = _write_corpus(tmp_path, {"t1": buffer.getvalue()}, ground_truth=gt)
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is False
    assert any("visib" in e["code"] or "contrast" in e["code"] for e in report["errors"])


def test_quota_violation_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image(2), "t2": _card_image(4)})
    report = validate_dataset(manifest, min_per_label=8)
    assert report["valid"] is False
    assert any("quota" in e["code"] or "coverage" in e["code"] for e in report["errors"])


def test_prompt_mismatch_rejected(tmp_path):
    manifest = _write_corpus(tmp_path, {"t1": _card_image()})
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["tasks"][0]["prompt"] = "a different prompt"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    report = validate_dataset(manifest, min_per_label=1)
    assert report["valid"] is False
    assert any("prompt" in e["code"] for e in report["errors"])


def test_historical_manifest_rejected():
    report = validate_dataset(REPO_ROOT / "dataset" / "borderbench-1" / "manifest.json")
    assert report["valid"] is False
    assert report["errors"], "the invalid prototype set must fail the release gate"
