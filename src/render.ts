import { chromium } from "playwright";
import { SPECIMENS } from "./specimens.ts";
import type { BorderSpecimenConfig, BorderBenchmarkManifestItem } from "./types.ts";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = path.resolve("dataset/rendered");
const MANIFEST_DIR = path.resolve("dataset/borderbench-1");
const MANIFEST_PATH = path.join(MANIFEST_DIR, "manifest.json");

fs.mkdirSync(OUTPUT_DIR, { recursive: true });
fs.mkdirSync(MANIFEST_DIR, { recursive: true });

function generateCardHtml(specimen: BorderSpecimenConfig): string {
  // Theme styling
  let canvasBg = "#f1f5f9"; // slate-100
  let cardBg = "#ffffff";
  let textColor = "#0f172a"; // slate-900
  let mutedColor = "#64748b"; // slate-500
  let borderColor = "#cbd5e1"; // slate-300
  let avatarBg = "#e2e8f0";
  let buttonBg = "#0f172a";
  let buttonText = "#ffffff";

  if (specimen.theme === "white-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#ffffff";
    borderColor = "#cbd5e1";
  } else if (specimen.theme === "gray-tint-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#f8fafc"; // slate-50
    borderColor = "#cbd5e1";
  } else if (specimen.theme === "blue-tint-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#eff6ff"; // blue-50
    borderColor = "#93c5fd"; // blue-300
    avatarBg = "#dbeafe";
    buttonBg = "#2563eb";
  } else if (specimen.theme === "dark-mode") {
    canvasBg = "#020617"; // slate-950
    cardBg = "#1e293b"; // slate-800
    textColor = "#f8fafc";
    mutedColor = "#94a3b8";
    borderColor = "rgba(255, 255, 255, 0.16)";
    avatarBg = "#334155";
    buttonBg = "#f8fafc";
    buttonText = "#0f172a";
  }

  // Border CSS construction
  let borderTop = "none";
  let borderRight = "none";
  let borderBottom = "none";
  let borderLeft = "none";

  if (specimen.has_border && specimen.stroke_width_px > 0 && specimen.stroke_style !== "none") {
    const strokeStr = `${specimen.stroke_width_px}px ${specimen.stroke_style} ${borderColor}`;
    if (specimen.border_sides === "all-4") {
      borderTop = borderRight = borderBottom = borderLeft = strokeStr;
    } else if (specimen.border_sides === "bottom-only") {
      borderBottom = strokeStr;
    } else if (specimen.border_sides === "left-only") {
      borderLeft = strokeStr;
    } else if (specimen.border_sides === "top-only") {
      borderTop = strokeStr;
    }
  }

  // Border Radius CSS
  let borderRadiusCss = "0px";
  if (Array.isArray(specimen.corner_radius_px)) {
    const [tl, tr, br, bl] = specimen.corner_radius_px;
    borderRadiusCss = `${tl}px ${tr}px ${br}px ${bl}px`;
  } else {
    borderRadiusCss = `${specimen.corner_radius_px}px`;
  }

  // Shadow CSS
  let boxShadowCss = "none";
  if (specimen.elevation === "subtle-drop") {
    boxShadowCss = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)";
  } else if (specimen.elevation === "floating-drop") {
    boxShadowCss = "0 10px 15px -3px rgba(0, 0, 0, 0.12), 0 4px 6px -4px rgba(0, 0, 0, 0.1)";
  } else if (specimen.elevation === "ring-only") {
    boxShadowCss = "0 0 0 1px rgba(0, 0, 0, 0.12)";
  } else if (specimen.elevation === "stroke+shadow") {
    boxShadowCss = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)";
  }

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 560px;
    height: 360px;
    background: ${canvasBg};
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  .card {
    width: 400px;
    height: 240px;
    background: ${cardBg};
    border-top: ${borderTop};
    border-right: ${borderRight};
    border-bottom: ${borderBottom};
    border-left: ${borderLeft};
    border-radius: ${borderRadiusCss};
    box-shadow: ${boxShadowCss};
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }
  .header {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 9999px;
    background: ${avatarBg};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: ${textColor};
    font-size: 14px;
    flex-shrink: 0;
  }
  .title-group {
    flex: 1;
    min-width: 0;
  }
  .title {
    font-size: 16px;
    font-weight: 600;
    color: ${textColor};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .subtitle {
    font-size: 12px;
    color: ${mutedColor};
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .badge {
    font-size: 11px;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 6px;
    background: ${specimen.theme === "dark-mode" ? "#334155" : "#e2e8f0"};
    color: ${textColor};
  }
  .body {
    font-size: 13px;
    line-height: 1.5;
    color: ${mutedColor};
  }
  .meta-row {
    display: flex;
    gap: 16px;
    margin-top: 6px;
  }
  .meta-item {
    font-size: 11px;
    color: ${mutedColor};
  }
  .meta-item strong {
    color: ${textColor};
  }
  .footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 12px;
    border-top: 1px solid ${specimen.theme === "dark-mode" ? "rgba(255,255,255,0.08)" : "#f1f5f9"};
  }
  .status {
    font-size: 12px;
    font-weight: 500;
    color: ${textColor};
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: #10b981;
  }
  .btn {
    font-size: 12px;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 6px;
    background: ${buttonBg};
    color: ${buttonText};
    border: none;
    cursor: pointer;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="avatar">${specimen.id.slice(-2)}</div>
      <div class="title-group">
        <div class="title">${specimen.title}</div>
        <div class="subtitle">${specimen.subtitle}</div>
      </div>
      <div class="badge">${specimen.tag}</div>
    </div>
    <div class="body">
      Interface container specimen evaluating border presence, stroke pattern, edge selectivity, corner curvature, and elevation properties.
      <div class="meta-row">
        <div class="meta-item">Token: <strong>${specimen.id}</strong></div>
        <div class="meta-item">Theme: <strong>${specimen.theme}</strong></div>
      </div>
    </div>
    <div class="footer">
      <div class="status"><span class="status-dot"></span>Active Specimen</div>
      <button class="btn">Inspect</button>
    </div>
  </div>
</body>
</html>`;
}

const PROMPT_TEXT = `Analyze the visual border and surface properties of the primary UI card container in this image.
The image shows a standardized 400x240 CSS px card rendered on a canvas.

Evaluate these 6 design attributes and respond ONLY with a valid JSON object matching this schema:
{
  "has_border": true | false,
  "border_sides": "all-4" | "bottom-only" | "left-only" | "top-only" | "none",
  "stroke_style": "solid" | "dashed" | "dotted" | "double" | "none",
  "stroke_width": "0px" | "1px" | "2px" | "4px" | "8px",
  "corner_radius": "sharp" | "subtle" | "medium" | "large" | "pill",
  "corner_uniformity": "all-corners" | "top-only" | "asymmetric",
  "elevation": "none" | "subtle-drop" | "floating-drop" | "ring-only" | "stroke+shadow"
}

Definitions:
- has_border: true if the card has an explicit border stroke on any edge, false otherwise.
- border_sides: which edges of the card have a stroke. If has_border is false, this is "none".
- stroke_style: line pattern. If has_border is false, this is "none".
- stroke_width: stroke thickness category: 0px (none), 1px (hairline), 2px (medium), 4px (thick), 8px (heavy).
- corner_radius: corner curvature category: sharp (0px), subtle (2-4px), medium (6-10px), large (14-24px), pill (circular/capsule/9999px).
- corner_uniformity: all-corners (equal curvature on all 4 corners), top-only (only top corners rounded, bottom sharp), asymmetric (different radii).
- elevation: box-shadow appearance: none (flat), subtle-drop (soft shadow-sm/md), floating-drop (diffuse shadow-lg), ring-only (box-shadow outline ring without stroke), stroke+shadow (both stroke and shadow).`;

async function main() {
  console.log(`Starting render of ${SPECIMENS.length} BorderBench specimens...`);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 560, height: 360 },
    deviceScaleFactor: 2, // 2x Retina DPR
  });

  const manifestItems: BorderBenchmarkManifestItem[] = [];

  for (let i = 0; i < SPECIMENS.length; i++) {
    const specimen = SPECIMENS[i];
    const filename = `${specimen.id}.png`;
    const outputPath = path.join(OUTPUT_DIR, filename);
    const html = generateCardHtml(specimen);

    await page.setContent(html);
    await page.screenshot({ path: outputPath, type: "png" });

    manifestItems.push({
      taskId: specimen.id,
      imagePath: outputPath,
      imageFilename: filename,
      groundTruth: {
        has_border: specimen.has_border,
        border_sides: specimen.border_sides,
        stroke_style: specimen.stroke_style,
        stroke_width: specimen.stroke_width,
        stroke_width_px: specimen.stroke_width_px,
        corner_radius: specimen.corner_radius,
        corner_radius_px: specimen.corner_radius_px,
        corner_uniformity: specimen.corner_uniformity,
        elevation: specimen.elevation,
        theme: specimen.theme,
      },
      prompt: PROMPT_TEXT,
    });

    if ((i + 1) % 20 === 0 || i === SPECIMENS.length - 1) {
      console.log(`Rendered ${i + 1}/${SPECIMENS.length} specimens...`);
    }
  }

  await browser.close();

  const manifest = {
    benchmark_id: "borderbench-1",
    name: "BorderBench-1",
    version: "1.0.0",
    description: "Visual border, corner radius, stroke style, and elevation identification benchmark for multimodal vision-language models.",
    total_tasks: manifestItems.length,
    canonical_canvas: {
      width_px: 560,
      height_px: 360,
      card_width_px: 400,
      card_height_px: 240,
      dpr: 2,
    },
    tasks: manifestItems,
  };

  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2));
  console.log(`✅ Finished rendering! Manifest written to ${MANIFEST_PATH}`);
}

main().catch((err) => {
  console.error("Render failed:", err);
  process.exit(1);
});
