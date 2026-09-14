"""Offline release gate for rendered pixels, labels, and rendering evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageChops
from pydantic import ValidationError

from baseline.evaluator import DEFAULT_PROMPT
from baseline.providers import BorderPrediction

WIDTH_PX = {"0px": 0, "1px": 1, "2px": 2, "4px": 4, "8px": 8}
RADIUS_PX = {"sharp": 0, "subtle": 4, "medium": 12, "large": 24, "pill": 9999}
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


def _edge_contrast(gray: Image.Image) -> float:
    """Strongest luminance step across the four card edges (midpoints)."""
    left = CARD_CSS["x"] * DPR
    top = CARD_CSS["y"] * DPR
    right = left + CARD_CSS["width"] * DPR
    bottom = top + CARD_CSS["height"] * DPR
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


SHADOWS = {
    "none": "none",
    "subtle-drop": "rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px",
    "floating-drop": "rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px",
}
CANONICAL_CANVAS = {"width_px": 560, "height_px": 360, "card_width_px": 400, "card_height_px": 240, "dpr": 2}
VIEWPORT = {"width": 560, "height": 360, "deviceScaleFactor": 2}


def _number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _check_labels(gt: object, task_id: str, fail) -> bool:
    if not isinstance(gt, dict):
        fail("label_enum", "Missing groundTruth object", task_id)
        return False
    keys = ("has_border", *AXES)
    targets = {key: gt.get(key) for key in keys}
    try:
        BorderPrediction.model_validate(targets, strict=True)
    except ValidationError as error:
        fail("label_enum", f"Invalid border labels: {error}", task_id)
        return False
    if gt.get("theme") not in tuple(PALETTES):
        fail("label_theme", f"Unknown theme: {gt.get('theme')!r}", task_id)
    absent = [gt["border_sides"] == "none", gt["stroke_style"] == "none", gt["stroke_width"] == "0px"]
    if any(value != (not gt["has_border"]) for value in absent):
        fail("label_consistency", "Border presence, sides, style and width must agree", task_id)
    width = gt.get("stroke_width_px")
    if not _number(width) or width != WIDTH_PX[gt["stroke_width"]]:
        fail("label_px", "stroke_width_px disagrees with stroke_width", task_id)
    radius = RADIUS_PX[gt["corner_radius"]]
    labeled = gt.get("corner_radius_px")
    uniformity = gt["corner_uniformity"]
    expected = radius
    if uniformity != "all-corners":
        if gt["corner_radius"] not in ("medium", "large"):
            fail("label_uniformity", "Non-uniform corners require medium or large radius", task_id)
        expected = [radius, radius, 0, 0] if uniformity == "top-only" else [radius, radius, radius, 0]
    values = labeled if isinstance(labeled, list) else [labeled]
    if not all(_number(value) for value in values) or labeled != expected:
        fail("label_px", "corner_radius_px disagrees with radius and uniformity", task_id)
    return True


def _check_evidence(item: dict, fail) -> None:
    task_id, gt = item["taskId"], item["groundTruth"]
    rendered = item.get("rendered")
    if not isinstance(rendered, dict):
        fail("evidence_shape", "Missing rendered evidence object", task_id)
        return
    for key in ("browser", "platform"):
        if not isinstance(rendered.get(key), str) or not rendered[key].strip():
            fail("evidence_shape", f"Rendered evidence must record {key}", task_id)
    if rendered.get("viewport") != VIEWPORT:
        fail("evidence_geometry", "Viewport must be 560x360 CSS pixels at DPR 2", task_id)
    card = rendered.get("card")
    if not isinstance(card, dict) or any(not _number(card.get(key)) for key in CARD_CSS):
        fail("evidence_shape", "Card box must hold finite numbers for x, y, width and height", task_id)
    elif any(abs(card[key] - expected) > 0.01 for key, expected in CARD_CSS.items()):
        fail("evidence_geometry", "Card geometry differs from its canonical box", task_id)
    computed = rendered.get("computed")
    if not isinstance(computed, dict):
        fail("evidence_shape", "Missing computed styles", task_id)
        return
    for side in ("Top", "Right", "Bottom", "Left"):
        present = gt["has_border"] and (gt["border_sides"] == "all-4" or gt["border_sides"] == side.lower() + "-only")
        width = f"{WIDTH_PX[gt['stroke_width']]}px" if present else "0px"
        style = gt["stroke_style"] if present else "none"
        for suffix, expected, code in (("Width", width, "evidence_width"), ("Style", style, "evidence_style")):
            key = f"border{side}{suffix}"
            if computed.get(key) != expected:
                fail(code, f"Computed {key} {computed.get(key)!r} != labeled {expected!r}", task_id)
    labeled = gt.get("corner_radius_px")
    corners = labeled if isinstance(labeled, list) else [labeled] * 4
    for key, wanted in zip(("borderTopLeftRadius", "borderTopRightRadius", "borderBottomRightRadius", "borderBottomLeftRadius"), corners):
        value = computed.get(key)
        if not isinstance(value, str) or re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?px", value) is None:
            fail("evidence_shape", f"Computed {key} must be a finite nonnegative pixel value", task_id)
        elif not _number(wanted) or abs(float(value[:-2]) - wanted) > 0.01:
            fail("evidence_radius", f"Computed {key} differs from labeled radius", task_id)
    if computed.get("boxShadow") != SHADOWS.get(gt["elevation"]):
        fail("evidence_shadow", "Computed box-shadow differs from the exact frozen Tailwind stack", task_id)


REFERENCE_FONT_SHA256 = "abdc775b21b1bc470d50c97e790d276f2054b7504e56e5bd3e64f48d68582322"
REFERENCE = {"fontFamily": "BorderBench Reference", "fontSizePx": 16, "lineHeightPx": 24, "ruleWidthPx": 64}
PALETTES = {
    "white-on-gray": ((241, 245, 249), (255, 255, 255), (203, 213, 225)),
    "gray-tint-on-white": ((255, 255, 255), (226, 232, 240), (148, 163, 184)),
    "blue-tint-on-white": ((255, 255, 255), (239, 246, 255), (147, 197, 253)),
}


def _check_pixels(item: dict, image: Image.Image, flat: Image.Image, fail) -> dict:
    """Measure the actual perimeter; flat controls isolate shadows from surface tones."""
    task_id, gt = item["taskId"], item["groundTruth"]
    palette = PALETTES.get(gt.get("theme"))
    if palette is None:
        return {}
    canvas, _, border = palette
    px = flat.load()
    left, top, right, bottom = 160, 120, 960, 600
    # The center of each side remains straight for all supported radii, including pills.
    coordinates = {
        "top": lambda along, depth: (560 + along, top + depth),
        "bottom": lambda along, depth: (560 + along, bottom - 1 - depth),
        "left": lambda along, depth: (left + depth, 360 + along),
        "right": lambda along, depth: (right - 1 - depth, 360 + along),
    }
    widths = {}
    for side, coordinate in coordinates.items():
        present = gt["has_border"] and (gt["border_sides"] == "all-4" or gt["border_sides"] == side + "-only")
        expected = WIDTH_PX[gt["stroke_width"]] * DPR if present else 0
        span = 1 if gt["corner_radius"] == "pill" and side in ("left", "right") else 64
        columns = [[max(abs(channel - target) for channel, target in zip(px[coordinate(along, depth)], border)) <= 12
                    for depth in range(20)] for along in range(-span, span + 1)]
        measured = max(sum(column) for column in columns)
        widths[side] = measured
        if abs(measured - expected) > (1 if expected else 0):
            fail("pixel_width", f"{side} border measures {measured} physical pixels; label requires {expected}", task_id)
        if present and span > 1:
            ink = [any(column) for column in columns]
            fraction = sum(ink) / len(ink)
            if gt["stroke_style"] == "solid" and fraction < 0.98:
                fail("pixel_style", f"Solid {side} border has gaps", task_id)
            elif gt["stroke_style"] in ("dashed", "dotted") and not 0.1 < fraction < 0.95:
                fail("pixel_style", f"Broken {side} border lacks visible repeated gaps", task_id)
            longest = current = 0
            for marked in ink:
                current = current + 1 if marked else 0
                longest = max(longest, current)
            if (gt["stroke_style"] == "dotted" and longest > expected + 2) or (gt["stroke_style"] == "dashed" and longest < expected * 1.7):
                fail("pixel_style", f"{side} segment length disagrees with dashed/dotted category", task_id)
    radii = gt["corner_radius_px"]
    radii = radii if isinstance(radii, list) else [radii] * 4
    for index, radius in enumerate(radii):
        if not _number(radius):
            continue
        radius = min(radius, CARD_CSS["height"] / 2) * DPR
        # Points well away from the antialiased arc distinguish every retained radius.
        for offset in (1, 3, 8, 18, 48, 100):
            x = left + offset if index in (0, 3) else right - 1 - offset
            y = top + offset if index in (0, 1) else bottom - 1 - offset
            expected_surface = offset + 0.5 >= radius * (1 - 2 ** -0.5)
            distance = max(abs(channel - background) for channel, background in zip(px[x, y], canvas))
            if expected_surface != (distance > 0):
                fail("pixel_radius", f"Corner {index} silhouette disagrees with labeled radius at inset {offset} physical pixels", task_id)
                break
    difference = ImageChops.difference(image, flat)
    interior = difference.crop((left, top, right, bottom))
    # Outer shadow may occupy rounded-away corners but cannot alter the fixed reference.
    if difference.crop((320, 264, 800, 456)).getbbox() is not None:
        fail("pixel_reference", "Shadow pairing changes the fixed reference region", task_id)
    difference.paste((0, 0, 0), (left, top, right, bottom))
    histogram = difference.convert("L").histogram()
    changed = sum(histogram[2:])
    max_delta = max(maxima for _, maxima in difference.getextrema())
    bounds = difference.convert("L").point(lambda value: 255 if value >= 2 else 0).getbbox()
    extent = max(left - bounds[0], top - bounds[1], bounds[2] - right, bounds[3] - bottom) if bounds else 0
    if gt["elevation"] == "none":
        if changed or interior.getbbox() is not None:
            fail("pixel_shadow", "Flat control differs from the flat sample", task_id)
    elif changed < 100 or max_delta < 3:
        fail("pixel_shadow", "Labeled shadow lacks measurable exterior contrast against its matched flat control", task_id)
    elif (gt["elevation"] == "subtle-drop" and extent > 12) or (gt["elevation"] == "floating-drop" and extent < 20):
        fail("pixel_shadow_scale", "Shadow spread disagrees with the coarse Tailwind shadow category", task_id)
    return {"border_widths_physical_px": widths, "shadow_changed_pixels": changed,
            "shadow_max_channel_delta": max_delta, "shadow_extent_physical_px": extent}


def _check_reference(item: dict, image: Image.Image, root: Path, checked_fonts: set[Path], fail) -> None:
    task_id = item["taskId"]
    rendered = item.get("rendered", {})
    if not isinstance(rendered, dict):
        return
    if rendered.get("reference") != REFERENCE:
        fail("reference_scale", "Reference must use fixed 16px/24px text and a 64px rule", task_id)
    try:
        font = rendered["font"]
        source = _local_file(root, font["path"])
        if source not in checked_fonts:
            if hashlib.sha256(source.read_bytes()).hexdigest() != REFERENCE_FONT_SHA256:
                raise ValueError("Reference font binary differs from the pinned DejaVu Sans asset")
            checked_fonts.add(source)
        if font["sha256"] != REFERENCE_FONT_SHA256 or font["family"] != "DejaVu Sans":
            raise ValueError("Reference font identity differs from the pinned font")
        faces = font["platformFonts"]
        if not isinstance(faces, list) or not faces or any(
            not isinstance(face, dict) or face.get("familyName") != "DejaVu Sans"
            or face.get("isCustomFont") is not True or not _number(face.get("glyphCount")) or face["glyphCount"] <= 0
            for face in faces
        ):
            raise ValueError("All reference glyphs must use the pinned custom font")
    except (OSError, KeyError, TypeError, ValueError) as error:
        fail("reference_font", str(error), task_id)
    rule = image.crop((496, 432, 624, 436))
    if rule.getextrema() != ((51, 51), (65, 65), (85, 85)):
        fail("reference_pixels", "The 64px scale rule is missing, clipped or altered", task_id)
    for top in (264, 312, 360):
        line = image.crop((320, top, 800, top + 48)).convert("L")
        if line.getextrema()[0] > 100:
            fail("reference_pixels", "A reference text line has no visible dark ink", task_id)


def validate_dataset(manifest_path: str | Path, *, min_per_label: int = 8, require_complete: bool = True) -> dict:
    """Return a complete audit report; invalid inputs fail without changing files."""
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    report: dict = {
        "validation_version": 2,
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
    if not isinstance(data, dict) or type(data.get("total_tasks")) is not int or data["total_tasks"] != len(items):
        fail("manifest_count", "total_tasks must equal the task array length")
    if not isinstance(data, dict) or data.get("canonical_canvas") != CANONICAL_CANVAS:
        fail("manifest_geometry", "Missing or noncanonical canvas specification")
    if type(min_per_label) is not int or min_per_label < 1:
        fail("quota", "min_per_label must be a positive integer")
        return report
    report["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    try:
        catalog = json.loads((root / "catalog.json").read_text())
        expected_tasks = catalog["tasks"]
        if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1 or not isinstance(expected_tasks, list):
            raise ValueError("Unsupported catalog schema")
        expected = {row["taskId"]: row for row in expected_tasks}
        actual = {row["taskId"]: {key: row.get(key) for key in ("taskId", "groundTruth", "design")} for row in items}
        if len(expected) != len(expected_tasks) or expected != actual:
            raise ValueError("Manifest does not match the frozen catalog's complete task census and labels")
        if catalog.get("prompt") != DEFAULT_PROMPT or catalog.get("referenceFont") != {"path": "fonts/DejaVuSans.ttf", "sha256": REFERENCE_FONT_SHA256}:
            raise ValueError("Catalog prompt or reference font identity differs from the protocol")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        fail("catalog", str(error))
    by_filename = {row.get("imageFilename"): row for row in items if isinstance(row, dict) and isinstance(row.get("imageFilename"), str)}
    checked_fonts: set[Path] = set()
    report["pixel_evidence"] = {}
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
        labels_valid = _check_labels(gt, task_id, fail)

        if not isinstance(item.get("prompt"), str) or item["prompt"].strip() != DEFAULT_PROMPT:
            fail("prompt", "Task prompt differs from baseline/prompt.txt", task_id)

        try:
            image_file = _local_file(root, item.get("imageFilename"))
            if _local_file(root, item.get("imagePath")) != image_file:
                raise ValueError("imagePath and imageFilename must identify the same artifact")
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
                image = image.convert("RGBA")
                if image.getchannel("A").getextrema() != (255, 255):
                    fail("png_alpha", "Image has transparent pixels", task_id)
                    continue
                rgb = image.convert("RGB")
                pixels = rgb.tobytes()
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
        if labels_valid:
            _check_evidence(item, fail)
            _check_reference(item, rgb, root, checked_fonts, fail)
            try:
                reference = item["rendered"]["shadowReference"]
                other = by_filename[reference["imageFilename"]]
                if other["groundTruth"]["elevation"] != "none" or reference["imageSha256"] != other["imageSha256"]:
                    raise ValueError("Shadow reference must identify a hashed flat sample")
                expected_gt = {**gt, "elevation": "none"}
                if other["groundTruth"] != expected_gt or other.get("design", {}).get("recipeId") != item.get("design", {}).get("recipeId"):
                    raise ValueError("Shadow control must hold every non-shadow design property constant")
                reference_path = _local_file(root, reference["imageFilename"])
                if hashlib.sha256(reference_path.read_bytes()).hexdigest() != reference["imageSha256"]:
                    raise ValueError("Shadow reference image hash mismatch")
                with Image.open(reference_path) as flat_image:
                    flat = flat_image.convert("RGB")
                if flat.size != CANVAS_PX:
                    raise ValueError("Shadow reference dimensions differ")
                report["pixel_evidence"][task_id] = _check_pixels(item, rgb, flat, fail)
            except (OSError, KeyError, TypeError, ValueError, AttributeError) as error:
                fail("shadow_reference", str(error), task_id)

    report["distributions"] = {
        axis: dict(sorted(Counter(
            str(item["groundTruth"].get(axis, "<missing>")) for item in items if isinstance(item, dict) and isinstance(item.get("groundTruth"), dict)
        ).items()))
        for axis in ("has_border", *AXES, "theme")
    }
    for axis in ("has_border", *AXES, "theme"):
        counts = Counter(
            str(item["groundTruth"][axis]) for item in items
            if isinstance(item, dict) and isinstance(item.get("groundTruth"), dict) and item["groundTruth"].get(axis) is not None
        )
        if require_complete:
            expected = ({"True", "False"} if axis == "has_border" else set(PALETTES) if axis == "theme"
                        else set(BorderPrediction.model_json_schema()["properties"][axis]["enum"]))
            missing = expected - set(counts)
            if missing:
                fail("coverage", f"{axis} lacks required labels: {sorted(missing)}")
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

    report["font_asset_count"] = len(checked_fonts)
    report["unique_pixel_count"] = len(decoded)
    report["error_counts"] = dict(Counter(error["code"] for error in report["errors"]))
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
    print(json.dumps({k: v for k, v in report.items() if k not in ("errors", "pixel_evidence")}, indent=2))
    for error in report["errors"]:
        print(f"[{error['code']}] {error['taskId']}: {error['detail']}")
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
