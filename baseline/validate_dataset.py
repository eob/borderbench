"""Offline release gate for rendered pixels, labels, and rendering evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image
from pydantic import ValidationError

from baseline.evaluator import DEFAULT_PROMPT, THEMES
from baseline.providers import BorderPrediction

WIDTH_PX = {"0px": 0, "1px": 1, "2px": 2, "4px": 4, "8px": 8}
RADIUS_PX = {"sharp": 0, "subtle": 3, "medium": 8, "large": 18, "pill": 9999}
AXES = (
    "border_sides",
    "stroke_style",
    "stroke_width",
    "corner_radius",
    "corner_uniformity",
    "elevation",
)

CANVAS_PX = (1120, 720)
CARD_CSS = {"x": 80, "y": 60, "width": 400, "height": 240}
DPR = 2
MIN_EDGE_CONTRAST = 2.5


def _card_edges_px() -> tuple[int, int, int, int]:
    left = CARD_CSS["x"] * DPR
    top = CARD_CSS["y"] * DPR
    return left, top, left + CARD_CSS["width"] * DPR, top + CARD_CSS["height"] * DPR


def _edge_contrast(gray: Image.Image) -> float:
    """Strongest luminance step across the four card edges (midpoints)."""
    left, top, right, bottom = _card_edges_px()
    width, height = gray.size
    px = gray.load()
    assert px is not None

    def strip_mean(x0: int, y0: int, x1: int, y1: int) -> float:
        total = 0
        count = 0
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                total += px[x, y]
                count += 1
        return total / count if count else 0.0

    def band_spread(x0: int, y0: int, x1: int, y1: int) -> float:
        values = [
            px[x, y]
            for y in range(max(0, y0), min(height, y1))
            for x in range(max(0, x0), min(width, x1))
        ]
        return float(max(values) - min(values)) if values else 0.0

    mid_x = (left + right) // 2
    mid_y = (top + bottom) // 2
    third = (right - left) // 3
    vthird = (bottom - top) // 3
    edges = [
        (mid_x - third, top - 10, mid_x + third, top - 3, mid_x - third, top + 3, mid_x + third, top + 10,
         mid_x - third, top - 2, mid_x + third, top + 3),
        (mid_x - third, bottom - 10, mid_x + third, bottom - 3, mid_x - third, bottom + 3, mid_x + third, bottom + 10,
         mid_x - third, bottom - 2, mid_x + third, bottom + 3),
        (left - 10, mid_y - vthird, left - 3, mid_y + vthird, left + 3, mid_y - vthird, left + 10, mid_y + vthird,
         left - 2, mid_y - vthird, left + 3, mid_y + vthird),
        (right - 10, mid_y - vthird, right - 3, mid_y + vthird, right + 3, mid_y - vthird, right + 10, mid_y + vthird,
         right - 2, mid_y - vthird, right + 3, mid_y + vthird),
    ]
    best = 0.0
    for x0, y0, x1, y1, x2, y2, x3, y3, bx0, by0, bx1, by1 in edges:
        step = abs(strip_mean(x0, y0, x1, y1) - strip_mean(x2, y2, x3, y3))
        best = max(best, step, band_spread(bx0, by0, bx1, by1))
    return best


def _local_file(root: Path, filename: object) -> Path:
    if not isinstance(filename, str) or not filename or Path(filename).is_absolute():
        raise ValueError("Expected a relative artifact path")
    file = (root / filename).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        raise ValueError(f"Missing artifact or path outside dataset: {filename}")
    return file


def _check_evidence(item: dict, fail) -> None:
    task_id = item.get("taskId")
    gt = item.get("groundTruth", {})
    rendered = item.get("rendered")
    if not isinstance(rendered, dict):
        fail("evidence_shape", "Missing rendered evidence object", task_id)
        return
    if not isinstance(rendered.get("browser"), str) or not rendered["browser"].strip():
        fail("evidence_shape", "Rendered evidence must record the browser version", task_id)
    card = rendered.get("card")
    if not isinstance(card, dict):
        fail("evidence_shape", "Rendered evidence must record the card box", task_id)
        return
    try:
        for key in ("x", "y", "width", "height"):
            if abs(float(card[key]) - CARD_CSS[key]) > 2:
                fail("evidence_geometry", f"Card {key} {card[key]} differs from canonical {CARD_CSS[key]}", task_id)
    except (TypeError, ValueError):
        fail("evidence_shape", "Card box must hold finite numbers", task_id)
        return
    computed = rendered.get("computed")
    if not isinstance(computed, dict):
        fail("evidence_shape", "Rendered evidence must record computed styles", task_id)
        return
    width_px = WIDTH_PX.get(gt.get("stroke_width"), None)
    sides = gt.get("border_sides")
    if width_px is None or not isinstance(sides, str):
        return
    want = {
        "borderTopWidth": "0px",
        "borderRightWidth": "0px",
        "borderBottomWidth": "0px",
        "borderLeftWidth": "0px",
    }
    if gt.get("has_border") and width_px > 0:
        stroke = f"{width_px}px"
        if sides == "all-4":
            want = dict.fromkeys(want, stroke)
        elif sides == "top-only":
            want["borderTopWidth"] = stroke
        elif sides == "bottom-only":
            want["borderBottomWidth"] = stroke
        elif sides == "left-only":
            want["borderLeftWidth"] = stroke
    for key, expected in want.items():
        if computed.get(key) != expected:
            fail("evidence_width", f"Computed {key} {computed.get(key)!r} != labeled {expected!r}", task_id)
    styles = {
        "borderTopStyle": want["borderTopWidth"],
        "borderRightStyle": want["borderRightWidth"],
        "borderBottomStyle": want["borderBottomWidth"],
        "borderLeftStyle": want["borderLeftWidth"],
    }
    for key, labeled_width in styles.items():
        expected = "none" if labeled_width == "0px" else gt.get("stroke_style")
        if computed.get(key) != expected:
            fail("evidence_style", f"Computed {key} {computed.get(key)!r} != labeled {expected!r}", task_id)
    radii = {
        "borderTopLeftRadius": 0,
        "borderTopRightRadius": 1,
        "borderBottomRightRadius": 2,
        "borderBottomLeftRadius": 3,
    }
    labeled = gt.get("corner_radius_px")
    corners = labeled if isinstance(labeled, list) else [labeled] * 4
    for key, index in radii.items():
        try:
            actual = float(str(computed.get(key, "")).strip().removesuffix("px").split()[0])
        except (ValueError, IndexError):
            fail("evidence_shape", f"Computed {key} is not a pixel value", task_id)
            continue
        if (
            index < len(corners)
            and isinstance(corners[index], (int, float))
            and abs(actual - corners[index]) > 0.5
        ):
            fail("evidence_radius", f"Computed {key} {actual} != labeled {corners[index]}", task_id)
    shadow = computed.get("boxShadow")
    if gt.get("elevation") == "none" and shadow != "none":
        fail("evidence_shadow", f"Flat card must compute box-shadow none, got {shadow!r}", task_id)
    if gt.get("elevation") != "none" and shadow == "none":
        fail("evidence_shadow", f"Elevated card {gt.get('elevation')!r} must compute a box-shadow", task_id)


def validate_dataset(manifest_path: str | Path, *, min_per_label: int = 8) -> dict:
    """Return a complete audit report; invalid inputs fail without changing files."""
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    report: dict = {
        "validation_version": 1,
        "valid": False,
        "sample_count": 0,
        "errors": [],
        "distributions": {},
        "shortcut_accuracy": {},
    }

    def fail(code: str, detail: str, task_id: object = None) -> None:
        report["errors"].append({"code": code, "taskId": task_id, "detail": detail})

    try:
        data = json.loads(manifest_path.read_bytes())
    except (OSError, ValueError) as error:
        fail("manifest", f"Cannot read manifest: {error}")
        return report
    items = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        fail("manifest", "Dataset is empty or has no task array")
        return report
    report["sample_count"] = len(items)
    report["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    seen_ids: set[str] = set()
    decoded: dict[str, str] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail("manifest", f"Task {index} must be a JSON object")
            continue
        task_id = item.get("taskId")
        if not isinstance(task_id, str) or not task_id.strip():
            fail("task_id", f"Task {index} must have a non-empty taskId")
            continue
        if task_id in seen_ids:
            fail("task_id", f"Duplicate taskId: {task_id}", task_id)
        seen_ids.add(task_id)

        gt = item.get("groundTruth")
        targets = None
        if isinstance(gt, dict):
            targets = {key: gt.get(key) for key in (
                "has_border", "border_sides", "stroke_style", "stroke_width",
                "corner_radius", "corner_uniformity", "elevation",
            )}
            try:
                if BorderPrediction.model_validate(targets).model_dump() != targets:
                    fail("label_enum", "Noncanonical border labels", task_id)
            except ValidationError as error:
                fail("label_enum", f"Invalid border labels: {error}", task_id)
            if gt.get("theme") not in THEMES:
                fail("label_theme", f"Unknown theme: {gt.get('theme')!r}", task_id)
            if gt.get("stroke_width_px") != WIDTH_PX.get(gt.get("stroke_width")):
                fail("label_px", "stroke_width_px disagrees with stroke_width", task_id)
            expected_radius = RADIUS_PX.get(gt.get("corner_radius"))
            labeled_radius = gt.get("corner_radius_px")
            uniformity = gt.get("corner_uniformity")
            if isinstance(labeled_radius, list):
                if uniformity not in ("top-only", "asymmetric") or len(labeled_radius) != 4:
                    fail("label_uniformity", "Corner arrays need top-only/asymmetric with four values", task_id)
                elif gt.get("corner_radius") not in ("subtle", "medium", "large"):
                    fail("label_uniformity", "Non-uniform corners need a rounded radius", task_id)
                elif uniformity == "top-only" and labeled_radius[2:] != [0, 0]:
                    fail("label_px", "top-only corners need sharp bottom corners", task_id)
                elif uniformity == "asymmetric" and sorted(labeled_radius) != sorted([expected_radius] * 3 + [2]):
                    fail("label_px", "asymmetric corners need three labeled radii plus the 2px acute corner", task_id)
            elif labeled_radius != expected_radius:
                fail("label_px", "corner_radius_px disagrees with corner_radius", task_id)
        else:
            fail("label_enum", "Missing groundTruth object", task_id)

        if not isinstance(item.get("prompt"), str) or item["prompt"].strip() != DEFAULT_PROMPT:
            fail("prompt", "Task prompt differs from baseline/prompt.txt", task_id)

        try:
            image_file = _local_file(root, item.get("imageFilename"))
            _local_file(root, item.get("imagePath"))
        except ValueError as error:
            fail("image_path", str(error), task_id)
            continue
        try:
            raw = image_file.read_bytes()
        except OSError as error:
            fail("image_path", f"Cannot read image: {error}", task_id)
            continue
        if raw[:8] != b"\x89PNG\r\n\x1a\n":
            fail("png_signature", "Image is not a PNG", task_id)
            continue
        if item.get("imageSha256") != hashlib.sha256(raw).hexdigest():
            fail("image_hash", "Image bytes differ from the recorded SHA-256", task_id)
        try:
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                if image.size != CANVAS_PX:
                    fail("png_dimensions", f"Image is {image.size[0]}x{image.size[1]}, want 1120x720", task_id)
                    continue
                if image.mode == "P":
                    image = image.convert("RGBA")
                if "A" in image.getbands():
                    alpha = image.getchannel("A")
                    if alpha.getextrema() != (255, 255):
                        fail("png_alpha", "Image has transparent pixels", task_id)
                        continue
                pixels = image.convert("RGB").tobytes()
                gray = image.convert("L")
        except Exception as error:
            fail("png_decode", f"Cannot decode PNG: {error}", task_id)
            continue
        digest = hashlib.sha256(pixels).hexdigest()
        if digest in decoded:
            fail("duplicate_pixels", f"Decoded pixels duplicate {decoded[digest]}", task_id)
        else:
            decoded[digest] = task_id
        if _edge_contrast(gray) < MIN_EDGE_CONTRAST:
            fail("visible_boundary", "No detectable card boundary (border, shadow, or tonal step)", task_id)
        _check_evidence(item, fail)

    report["distributions"] = {
        axis: dict(sorted(Counter(
            str(item.get("groundTruth", {}).get(axis, "<missing>")) for item in items if isinstance(item, dict)
        ).items()))
        for axis in (*AXES, "theme")
    }
    for axis in AXES:
        counts = Counter(
            item["groundTruth"][axis] for item in items
            if isinstance(item, dict) and isinstance(item.get("groundTruth"), dict) and item["groundTruth"].get(axis) is not None
        )
        for value, count in sorted(counts.items()):
            if count < min_per_label:
                fail("quota", f"{axis}={value} has {count} samples, need {min_per_label}")
        majority = max(counts.values()) / len(items) if counts else 0.0
        groups: dict[str, Counter] = defaultdict(Counter)
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("groundTruth"), dict):
                continue
            groups[str(item["groundTruth"].get("theme"))][str(item["groundTruth"].get(axis))] += 1
        themed = sum(max(group.values()) for group in groups.values()) / len(items) if groups else 0.0
        report["shortcut_accuracy"][axis] = {
            "majority_class": round(majority, 4),
            "theme_lookup": round(themed, 4),
        }

    listed = {
        str(item.get("imageFilename")) for item in items
        if isinstance(item, dict) and isinstance(item.get("imageFilename"), str)
    }
    for extra in sorted(root.glob("borderbench*.png")):
        if extra.name not in listed:
            fail("stale_file", f"Unlisted managed image: {extra.name}")

    report["valid"] = not report["errors"]
    return report


def require_valid_dataset(manifest_path: str | Path, *, min_per_label: int = 8) -> dict:
    """Raise ValueError unless the corpus passes the release gate."""
    report = validate_dataset(manifest_path, min_per_label=min_per_label)
    if not report["valid"]:
        first = report["errors"][0]
        raise ValueError(
            f"Dataset {manifest_path} failed validation with {len(report['errors'])} errors; "
            f"first: [{first['code']}] {first['taskId']}: {first['detail']}"
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--min-per-label", type=int, default=8)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    report = validate_dataset(args.manifest, min_per_label=args.min_per_label)
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "errors"}, indent=2))
    for error in report["errors"]:
        print(f"[{error['code']}] {error['taskId']}: {error['detail']}")
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
