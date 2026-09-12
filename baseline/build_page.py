"""Build the versioned benchmark page from accumulated compatible runs."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from baseline.evaluator import load_manifest
from baseline.releases import (
    DEFAULT_RELEASE,
    REPO_ROOT,
    load_release,
    model_config_fingerprint,
    release_manifest_path,
    validate_release,
)
from baseline.reporting import DIMENSIONS, metrics, read_report_json, scorecard_tasks
from baseline.validate_dataset import validate_dataset

METRIC_LABELS = {
    "exact": "All seven correct",
    "has_border": "Border presence",
    "border_sides": "Edge selectivity",
    "stroke_style": "Stroke style",
    "stroke_width": "Stroke width",
    "corner_radius": "Corner radius",
    "corner_uniformity": "Corner uniformity",
    "elevation": "Elevation",
}

AXES = [
    ("border_sides", "Edge selectivity", "Which card edges carry a stroke."),
    ("stroke_style", "Stroke style", "Solid, dashed, dotted, or no stroke pattern."),
    ("stroke_width", "Stroke width", "Hairline 1px through heavy 8px strokes."),
    ("corner_radius", "Corner radius", "Sharp corners through full pill capsules."),
    ("corner_uniformity", "Corner uniformity", "Equal, top-only, or asymmetric corner curvature."),
    ("elevation", "Elevation", "Flat cards and two coarse Tailwind drop-shadow levels, independent of the border."),
]

DEFAULT_SITE_URL = "https://edwardbenson.com/benchmarks/borderbench/"


def _select_samples(items: list[dict], key: str, count: int) -> list[dict]:
    remaining = sorted(items, key=lambda item: item["taskId"])
    selected: list[dict] = []
    seen: Counter = Counter()
    while remaining and len(selected) < count:
        sample = max(remaining, key=lambda item: 1 / (1 + seen[item["groundTruth"][key]]))
        selected.append(sample)
        remaining.remove(sample)
        seen[sample["groundTruth"][key]] += 1
    return selected


def _montage(samples: list[dict], title: str, columns: int, key: str) -> str:
    cell_w, cell_h, gap = 280, 220, 12
    columns = min(columns, len(samples))
    rows = math.ceil(len(samples) / columns)
    width = columns * cell_w + (columns + 1) * gap
    height = rows * cell_h + (rows + 1) * gap
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="#f1f5f9"/>',
    ]
    for index, sample in enumerate(samples):
        x = gap + index % columns * (cell_w + gap)
        y = gap + index // columns * (cell_h + gap)
        label = sample["groundTruth"][key]
        detail = f"{sample['groundTruth']['stroke_width']} {sample['groundTruth']['stroke_style']}"
        parts.extend([
            f"<g>",
            f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="8" fill="#fff"/>',
            f"<image x=\"{x + 8}\" y=\"{y + 8}\" width=\"{cell_w - 16}\" height=\"150\" preserveAspectRatio=\"xMidYMid meet\" href=\"inputs/{escape(sample['imageFilename'])}\"/>",
            f"<text x=\"{x + 12}\" y=\"{y + 181}\" font-family=\"Arial,sans-serif\" font-size=\"15\" font-weight=\"700\" fill=\"#0f172a\">{escape(str(label))}</text>",
            f"<text x=\"{x + 12}\" y=\"{y + 202}\" font-family=\"Arial,sans-serif\" font-size=\"11\" fill=\"#64748b\">{escape(detail)}</text>",
            "</g>",
        ])
    return "\n".join(parts + ["</svg>"])


def _percent(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def collect_observations(release: dict, results_dir: Path, items: list[dict] | None = None) -> tuple[dict, list[str]]:
    from baseline.reporting import aggregate_release_runs
    if items is None:
        items = load_manifest(str(release_manifest_path(release))) if "dataset_manifest" in release else []
    history = aggregate_release_runs(release, items, results_dir)
    return history, history["warnings"]


def _breakdown_table(section: dict, models: list[dict]) -> str:
    headings = "".join(f"<th scope=\"col\">{escape(model['display_name'])}</th>" for model in models)
    rows = []
    for group in section["groups"]:
        cells = []
        for model in models:
            value = group["models"][model["id"]]
            score = value["metrics"]["exact"]
            cells.append(f"<td>{_percent(score)}<small>n={value['count']}</small></td>")
        rows.append(f"<tr><th scope=\"row\">{escape(group['label'])}<small>{group['available']} inputs</small></th>{''.join(cells)}</tr>")
    return f"<div class=\"table-scroll\"><table><thead><tr><th scope=\"col\">Input group<small>All seven correct</small></th>{headings}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument("--results-dir", default="results/runs")
    parser.add_argument("--output-dir", default="site")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="Public URL where the generated site and assets will be served")
    args = parser.parse_args()
    benchmark = build_page(args.release, args.results_dir, args.output_dir, site_url=args.site_url)
    print(f"Built page for release {args.release}: {len(benchmark['configs'])} configurations, {benchmark['shared_task_count']} shared inputs.")


def build_page(
    release_version: str = DEFAULT_RELEASE,
    results_dir: str | Path = "results/runs",
    output_dir: str | Path = "site",
    *,
    site_url: str = DEFAULT_SITE_URL,
) -> dict:
    address = urlsplit(site_url)
    if address.scheme not in ("http", "https") or not address.netloc or address.query or address.fragment:
        raise ValueError("site_url must be an absolute HTTP(S) directory URL without a query or fragment")
    site_url = site_url.rstrip("/") + "/"
    release = load_release(release_version)
    manifest_path = release_manifest_path(release)
    validity = validate_dataset(manifest_path)
    if not validity["valid"]:
        raise ValueError(f"Release corpus failed validation with {len(validity['errors'])} errors")
    items = validate_release(release)
    if not items:
        raise ValueError("A benchmark page needs at least one rendered input")

    collected, warnings = collect_observations(release, Path(results_dir), items)
    observations = collected["observations"]
    configs = collected["configs"]

    per_config_tasks: dict[str, list[dict]] = {cid: [] for cid in configs}
    for (config_id, _task_id), obs in observations.items():
        per_config_tasks[config_id].append(obs["task"])
    shared_ids = set.intersection(*[set(t["task_id"] for t in tasks) for tasks in per_config_tasks.values() if tasks]) if any(per_config_tasks.values()) else set()

    from baseline.statistics import diagnostic_metrics, matched_block_metrics

    leaderboard = []
    for config_id, config in sorted(configs.items(), key=lambda kv: kv[1]["display_name"]):
        tasks = sorted(per_config_tasks[config_id], key=lambda t: t["task_id"])
        shared = [t for t in tasks if t["task_id"] in shared_ids]
        leaderboard.append({
            **config,
            "completed": len(tasks),
            "expected": release["expected_task_count"],
            "metrics": metrics(tasks),
            "shared_metrics": metrics(shared),
            "diagnostics": diagnostic_metrics(tasks),
            "shared_diagnostics": diagnostic_metrics(shared),
            "shared_matched_blocks": matched_block_metrics(shared, items),
            "status": "complete" if len(tasks) == len(items) else "partial" if tasks else "pending",
            "invalid_responses": sum(task.get("error_kind") == "invalid_response" for task in tasks),
            "avg_latency_sec": round(sum(t["latency_sec"] for t in tasks) / len(tasks), 3) if tasks and all(t.get("latency_sec") is not None for t in tasks) else None,
        })
    leaderboard.sort(key=lambda row: (-(row["shared_metrics"]["exact"] if row["shared_metrics"]["exact"] is not None else -1), row["display_name"]))

    breakdowns = []
    for key, title, blurb in AXES:
        groups = []
        for value in sorted(validity["distributions"].get(key, {})):
            available = {item["taskId"] for item in items if item["groundTruth"][key] == value}
            per_model = {}
            for row in leaderboard:
                config_id = row["id"]
                measured = [t for t in per_config_tasks[config_id] if t["task_id"] in available & shared_ids]
                per_model[config_id] = {"count": len(measured), "metrics": metrics(measured)}
            groups.append({"label": value, "available": len(available), "models": per_model})
        breakdowns.append({"key": key, "title": title, "blurb": blurb, "groups": groups})

    output = Path(output_dir)
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("borderbench-logo.svg", "borderbench-share.png"):
        shutil.copyfile(REPO_ROOT / "branding" / name, assets / name)
    inputs_dir = output / "inputs"
    if inputs_dir.exists():
        shutil.rmtree(inputs_dir)
    inputs_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        shutil.copyfile(item["imagePath"], inputs_dir / item["imageFilename"])

    run_links = []
    for run in collected["runs"]:
        source = Path(results_dir) / release_version / run["run_id"]
        destination = output / "runs" / run["run_id"]
        if not source.is_dir():
            continue
        destination.mkdir(parents=True, exist_ok=True)
        names = ["run.json", "summary.json", "attempts.jsonl", "finalization.json", "final_results.json"]
        names.extend(path.name for path in source.glob("scorecard_*.json"))
        for name in names:
            if (source / name).is_file():
                shutil.copyfile(source / name, destination / name)
        run_links.append(f'<li><a href="runs/{escape(run["run_id"], quote=True)}/run.json">{escape(run["run_id"])}</a> · <a href="runs/{escape(run["run_id"], quote=True)}/attempts.jsonl">attempt ledger</a></li>')
    run_history = "<h2>Recorded runs</h2><ul>" + "".join(run_links) + "</ul>" if run_links else ""

    sections = []
    for key, title, blurb in AXES:
        samples = _select_samples(items, key, 8)
        sections.append(
            f"<section><h2>{escape(title)}</h2><p>{escape(blurb)}</p>{_montage(samples, title, 4, key)}"
            + _breakdown_table(
                {"groups": next(b["groups"] for b in breakdowns if b["key"] == key)},
                leaderboard,
            )
            + "</section>"
        )

    rows = []
    for row in leaderboard:
        cells = "".join(f"<td>{_percent(row['shared_metrics'][m])}</td>" for m in ("exact", *DIMENSIONS))
        rows.append(
            f"<tr><th scope=\"row\">{escape(row['display_name'])}<small>{escape(row['provider'])} · {row['completed']}/{row['expected']} · {len(row['runs'])} run(s)</small></th>{cells}</tr>"
        )
    leaderboard_html = (
        "<div class=\"table-scroll\"><table><thead><tr><th scope=\"col\">Model</th>"
        + "".join(f"<th scope=\"col\">{label}</th>" for label in METRIC_LABELS.values())
        + "</tr></thead><tbody>"
        + ("".join(rows) if rows else "<tr><td colspan=\"9\">No measurements yet.</td></tr>")
        + "</tbody></table></div>"
    )
    warnings_html = "".join(f"<li>{escape(w)}</li>" for w in warnings)
    warnings_block = ""
    if warnings:
        warnings_block = '<div class="warnings"><ul>' + warnings_html + "</ul></div>"
    sections_html = "".join(sections)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BorderBench — Can a model see the edge?</title>
<meta name="description" content="A visual benchmark for how language models perceive borders, corners, and shadows. Seven attributes. A fixed scale. Reproducible comparisons.">
<link rel="canonical" href="{escape(site_url, quote=True)}">
<link rel="icon" type="image/svg+xml" href="assets/borderbench-logo.svg">
<meta property="og:type" content="website">
<meta property="og:url" content="{escape(site_url, quote=True)}">
<meta property="og:title" content="BorderBench — Can a model see the edge?">
<meta property="og:description" content="Measuring how language models perceive borders, corners, and shadows.">
<meta property="og:image" content="{escape(site_url, quote=True)}assets/borderbench-share.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="BorderBench. Can a model see the edge? A study of border patterns, widths, corners, and shadows.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="BorderBench — Can a model see the edge?">
<meta name="twitter:description" content="Measuring how language models perceive borders, corners, and shadows.">
<meta name="twitter:image" content="{escape(site_url, quote=True)}assets/borderbench-share.png">
<meta name="twitter:image:alt" content="BorderBench. Can a model see the edge? A study of border patterns, widths, corners, and shadows.">
<style>
body {{ font-family: Arial, sans-serif; margin: 0 auto; max-width: 1200px; padding: 24px; color: #0f172a; }}
small {{ display: block; color: #64748b; font-weight: 400; }}
.table-scroll {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; font-size: 14px; }}
thead th {{ background: #f1f5f9; }}
section {{ margin-top: 32px; }}
svg {{ max-width: 100%; height: auto; }}
.warnings {{ background: #fef9c3; border: 1px solid #eab308; padding: 8px 16px; }}
code {{ font-size: 12px; }}
.brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 20px; margin-bottom: 24px; }}
.brand img {{ width: 40px; height: 40px; }}
.share-card {{ display: block; width: 100%; height: auto; border-radius: 16px; }}
h1 {{ font-size: clamp(28px, 4vw, 44px); letter-spacing: -0.035em; margin-bottom: 12px; }}
.intro {{ max-width: 760px; font-size: 18px; line-height: 1.5; }}
</style>
</head>
<body>
<header>
<div class="brand"><img src="assets/borderbench-logo.svg" alt="" width="40" height="40">BorderBench <small>V{escape(release_version)}</small></div>
<img class="share-card" src="assets/borderbench-share.png" alt="BorderBench — Can a model see the edge?" width="1200" height="630">
<h1>Can a model see the edge?</h1>
<p class="intro">A visual benchmark for how language models perceive borders, corners, and shadows. Seven attributes, coarse Tailwind categories, and a fixed visual scale.</p>
</header>
<p>{len(items)} inputs · dataset <code>{release["dataset_fingerprint"][:12]}</code> · protocol <code>{release["evaluation_protocol_fingerprint"][:12]}</code> · gate passed</p>
<p>Shared cohort: {len(shared_ids)} inputs measured by every configuration with observations. All comparison scores and breakdowns use this same cohort; unmeasured configurations remain unranked. Repeats keep the earliest final observation; total costs include every attempt. Per-model observed scores and confusion matrices are available in the structured export.</p>
{leaderboard_html}
{warnings_block}
{run_history}
{sections_html}
</body>
</html>
"""
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(html, encoding="utf-8")
    benchmark = {
        "release": release_version,
        "dataset_fingerprint": release["dataset_fingerprint"],
        "evaluation_protocol": release["evaluation_protocol_fingerprint"],
        "expected_task_count": release["expected_task_count"],
        "gate": {"valid": True, "sample_count": len(items)},
        "shared_task_count": len(shared_ids),
        "shared_task_ids": sorted(shared_ids),
        "runs": collected["runs"],
        "excluded_runs": collected["excluded_runs"],
        "duplicate_policy": collected["duplicate_policy"],
        "configs": leaderboard,
        "observations": [{"config_id": config_id, "task_id": task_id, **observation}
                         for (config_id, task_id), observation in sorted(observations.items())],
        "breakdowns": breakdowns,
        "warnings": warnings,
    }
    (output / "benchmark.json").write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    return benchmark


if __name__ == "__main__":
    main()
