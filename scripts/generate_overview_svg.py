"""Generate a high-fidelity SVG contact sheet of representative BorderBench cards."""

from __future__ import annotations

import base64
import json
from pathlib import Path


def generate_overview_svg(manifest_path: str, output_path: str, selected_ids: list[str]):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    task_map = {t["taskId"]: t for t in manifest.get("tasks", [])}

    cols = 4
    rows = (len(selected_ids) + cols - 1) // cols
    card_w = 440
    card_h = 300
    gap = 20
    pad = 24

    total_w = pad * 2 + cols * card_w + (cols - 1) * gap
    total_h = pad * 2 + rows * card_h + (rows - 1) * gap

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img">',
        f'<title>BorderBench Representative Specimens</title>',
        f'<rect width="100%" height="100%" fill="#f8fafc"/>',
    ]

    for idx, t_id in enumerate(selected_ids):
        task = task_map.get(t_id)
        if not task:
            continue
        gt = task["groundTruth"]
        img_p = Path(task["imagePath"])
        if not img_p.exists():
            continue
        b64_data = base64.b64encode(img_p.read_bytes()).decode("ascii")

        col = idx % cols
        row = idx // cols
        x = pad + col * (card_w + gap)
        y = pad + row * (card_h + gap)

        title = f"{t_id}: {gt['stroke_width']} {gt['stroke_style']} ({gt['corner_radius']})"
        label_line = f"Radius: {gt['corner_radius']} ({gt['corner_radius_px']}px) · Shadow: {gt['elevation']}"
        theme_label = f"sides: {gt['border_sides']} | uniformity: {gt['corner_uniformity']} | theme: {gt['theme']}"

        svg_parts.append(f'<g data-task-id="{t_id}">')
        svg_parts.append(f'  <rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>')
        # Render image inside card
        img_w = card_w - 24
        img_h = 200
        svg_parts.append(f'  <image x="{x + 12}" y="{y + 12}" width="{img_w}" height="{img_h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64_data}"/>')
        # Text details
        svg_parts.append(f'  <text x="{x + 16}" y="{y + 242}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="600" fill="#0f172a">{title}</text>')
        svg_parts.append(f'  <text x="{x + 16}" y="{y + 264}" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="500" fill="#475569">{label_line}</text>')
        svg_parts.append(f'  <text x="{x + 16}" y="{y + 282}" font-family="ui-monospace, monospace" font-size="11" fill="#94a3b8">{theme_label}</text>')
        svg_parts.append(f'</g>')

    svg_parts.append('</svg>')
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(svg_parts), encoding="utf-8")
    print(f"Generated {out_file} ({total_w}x{total_h}, {len(selected_ids)} specimens)")


if __name__ == "__main__":
    specimens = [
        "borderbench-001",
        "borderbench-005",
        "borderbench-008",
        "borderbench-012",
        "borderbench-015",
        "borderbench-019",
        "borderbench-023",
        "borderbench-025",
        "borderbench-030",
        "borderbench-034",
        "borderbench-037",
        "borderbench-043",
        "borderbench-046",
        "borderbench-052",
        "borderbench-058",
        "borderbench-065",
    ]
    generate_overview_svg(
        "dataset/borderbench-1/manifest.json",
        "site/assets/overview.svg",
        specimens
    )
    # Also write to kaya-web
    generate_overview_svg(
        "dataset/borderbench-1/manifest.json",
        "/mnt/disks/data/kaya-web/main/apps/edwardbenson/public/images/benchmarks/borderbench/overview.svg",
        specimens
    )
