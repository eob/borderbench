"""Build the versioned benchmark page from accumulated compatible runs."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from collections import Counter
from html import escape
from pathlib import Path

from baseline.evaluator import load_manifest
from baseline.releases import (
    DEFAULT_RELEASE,
    load_release,
    model_config_fingerprint,
    release_manifest_path,
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
    ("elevation", "Elevation", "Flat cards, drop shadows, rings, and combined borders."),
]


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


def collect_observations(release: dict, results_dir: Path) -> tuple[dict, list[str]]:
    """Aggregate first-recorded observations per inference configuration."""
    warnings: list[str] = []
    fingerprint = release["dataset_fingerprint"]
    runs_root = results_dir / release["benchmark_version"]
    observations: dict[tuple[str, str], dict] = {}
    configs: dict[str, dict] = {}
    if runs_root.is_dir():
        run_dirs = sorted([d for d in runs_root.iterdir() if d.is_dir() and not d.name.startswith("mock-")])
    else:
        run_dirs = []
    for run_dir in run_dirs:
        run_meta = read_report_json(run_dir / "run.json", warnings)
        if not run_meta:
            warnings.append(f"{run_dir.name}: missing run.json; skipped")
            continue
        if (
            run_meta.get("release") != release["benchmark_version"]
            or run_meta.get("dataset_fingerprint") != fingerprint
            or run_meta.get("evaluation_protocol") != release["evaluation_protocol_fingerprint"]
            or run_meta.get("mock") is not False
        ):
            warnings.append(f"{run_dir.name}: incompatible release, dataset, protocol, or mock run; skipped")
            continue
        created = run_meta.get("created_at", "")
        for scorecard_path in sorted(run_dir.glob("scorecard_*.json")):
            card = read_report_json(scorecard_path, warnings)
            if not card:
                continue
            if card.get("mock") is not False:
                continue
            try:
                tasks = scorecard_tasks(card, dataset_fingerprint=fingerprint)
            except ValueError as error:
                warnings.append(f"{run_dir.name}/{scorecard_path.name}: {error}; skipped")
                continue
            model_id = card.get("model_id") or card.get("model_name")
            full_config = (run_meta.get("model_configs") or {}).get(model_id)
            if not isinstance(full_config, dict) or "provider" not in full_config or "model" not in full_config:
                warnings.append(f"{run_dir.name}/{scorecard_path.name}: missing run configuration; skipped")
                continue
            config_id = model_config_fingerprint(full_config)
            configs.setdefault(config_id, {
                "id": config_id,
                "model_id": model_id,
                "display_name": card.get("display_name") or model_id,
                "provider": full_config["provider"],
                "model": full_config["model"],
                "max_output_tokens": full_config.get("max_output_tokens", 1024),
                "runs": [],
                "repeat_observations": 0,
                "repeat_cost_usd": 0.0,
                "total_cost_usd": 0.0,
            })
            if run_dir.name not in configs[config_id]["runs"]:
                configs[config_id]["runs"].append(run_dir.name)
            for task in tasks:
                key = (config_id, task["task_id"])
                cost = task.get("cost_usd") or 0.0
                configs[config_id]["total_cost_usd"] += cost
                candidate = (str(created), run_dir.name, task)
                if key not in observations:
                    observations[key] = {"created": str(created), "run": run_dir.name, "task": task}
                else:
                    prior = observations[key]
                    configs[config_id]["repeat_observations"] += 1
                    configs[config_id]["repeat_cost_usd"] += cost
                    if (str(created), run_dir.name) < (prior["created"], prior["run"]):
                        observations[key] = {"created": str(created), "run": run_dir.name, "task": task}
    for config in configs.values():
        config["runs"].sort()
        config["total_cost_usd"] = round(config["total_cost_usd"], 6)
        config["repeat_cost_usd"] = round(config["repeat_cost_usd"], 6)
    return {"observations": observations, "configs": configs}, warnings


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
    args = parser.parse_args()
    benchmark = build_page(args.release, args.results_dir, args.output_dir)
    print(f"Built page for release {args.release}: {len(benchmark['configs'])} configurations, {benchmark['shared_task_count']} shared inputs.")


def build_page(
    release_version: str = DEFAULT_RELEASE,
    results_dir: str | Path = "results/runs",
    output_dir: str | Path = "site",
) -> dict:
    release = load_release(release_version)
    manifest_path = release_manifest_path(release)
    validity = validate_dataset(manifest_path)
    if not validity["valid"]:
        raise ValueError(f"Release corpus failed validation with {len(validity['errors'])} errors")
    items = load_manifest(str(manifest_path))
    if not items:
        raise ValueError("A benchmark page needs at least one rendered input")
    by_id = {item["taskId"]: item for item in items}

    collected, warnings = collect_observations(release, Path(results_dir))
    observations = collected["observations"]
    configs = collected["configs"]

    per_config_tasks: dict[str, list[dict]] = {cid: [] for cid in configs}
    for (config_id, _task_id), obs in observations.items():
        per_config_tasks[config_id].append(obs["task"])
    shared_ids = set.intersection(*[set(t["task_id"] for t in tasks) for tasks in per_config_tasks.values()]) if per_config_tasks else set()

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
            "avg_latency_sec": round(sum(float(t.get("latency_sec", 0.0)) for t in tasks) / len(tasks), 3) if tasks else None,
        })
    leaderboard.sort(key=lambda row: (-(row["metrics"]["exact"] or -1), row["display_name"]))

    breakdowns = []
    for key, title, blurb in AXES:
        groups = []
        for value in sorted(validity["distributions"].get(key, {})):
            available = {item["taskId"] for item in items if item["groundTruth"][key] == value}
            per_model = {}
            for row in leaderboard:
                config_id = row["id"]
                measured = [t for t in per_config_tasks[config_id] if t["task_id"] in available]
                per_model[config_id] = {"count": len(measured), "metrics": metrics(measured)}
            groups.append({"label": value, "available": len(available), "models": per_model})
        breakdowns.append({"key": key, "title": title, "blurb": blurb, "groups": groups})

    output = Path(output_dir)
    inputs_dir = output / "inputs"
    if inputs_dir.exists():
        shutil.rmtree(inputs_dir)
    inputs_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        shutil.copyfile(item["imagePath"], inputs_dir / item["imageFilename"])

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
        cells = "".join(f"<td>{_percent(row['metrics'][m])}</td>" for m in ("exact", *DIMENSIONS))
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
<title>BorderBench {escape(release_version)}</title>
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
</style>
</head>
<body>
<h1>BorderBench {escape(release_version)}</h1>
<p>{len(items)} inputs · dataset <code>{release["dataset_fingerprint"][:12]}</code> · protocol <code>{release["evaluation_protocol_fingerprint"][:12]}</code> · gate passed</p>
<p>Shared cohort: {len(shared_ids)} inputs measured by every listed configuration. Repeats keep the earliest observation; repeat costs stay in the ledger.</p>
{leaderboard_html}
{warnings_block}
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
        "configs": leaderboard,
        "breakdowns": breakdowns,
        "warnings": warnings,
    }
    (output / "benchmark.json").write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    return benchmark


if __name__ == "__main__":
    main()
