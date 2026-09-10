import { chromium } from "playwright";
import { SPECIMENS } from "./specimens.ts";
import { PROMPT_TEXT } from "./prompt.ts";
import type { BorderSpecimenConfig, BorderBenchmarkManifestItem } from "./types.ts";
import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = path.resolve("dataset/borderbench-v1");
const MANAGED_PREFIX = "borderbench-v1-";

export function generateCardHtml(specimen: BorderSpecimenConfig): string {
  let canvasBg = "#f1f5f9";
  let cardBg = "#ffffff";
  let textColor = "#0f172a";
  let mutedColor = "#64748b";
  let borderColor = "#cbd5e1";

  if (specimen.theme === "white-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#ffffff";
    borderColor = "#cbd5e1";
  } else if (specimen.theme === "gray-tint-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#f8fafc";
    borderColor = "#cbd5e1";
  } else if (specimen.theme === "blue-tint-on-white") {
    canvasBg = "#ffffff";
    cardBg = "#eff6ff";
    borderColor = "#93c5fd";
  } else if (specimen.theme === "dark-mode") {
    canvasBg = "#020617";
    cardBg = "#1e293b";
    textColor = "#f8fafc";
    mutedColor = "#94a3b8";
    borderColor = "rgba(255, 255, 255, 0.16)";
  }

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

  let borderRadiusCss = "0px";
  if (Array.isArray(specimen.corner_radius_px)) {
    const [tl, tr, br, bl] = specimen.corner_radius_px;
    borderRadiusCss = `${tl}px ${tr}px ${br}px ${bl}px`;
  } else {
    borderRadiusCss = `${specimen.corner_radius_px}px`;
  }

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
    background: #64748b;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #ffffff;
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
    background: #64748b;
    color: #ffffff;
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
    background: #334155;
    color: #ffffff;
    border: none;
    cursor: pointer;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="avatar">S</div>
      <div class="title-group">
        <div class="title">${specimen.title}</div>
        <div class="subtitle">${specimen.subtitle}</div>
      </div>
      <div class="badge">${specimen.tag}</div>
    </div>
    <div class="body">
      A neutral interface surface used to compare container edges across images.
      <div class="meta-row">
        <div class="meta-item">Section: <strong>Overview</strong></div>
        <div class="meta-item">State: <strong>Active</strong></div>
      </div>
    </div>
    <div class="footer">
      <div class="status"><span class="status-dot"></span>Active</div>
      <button class="btn">Inspect</button>
    </div>
  </div>
</body>
</html>`;
}

interface ComputedEvidence {
  borderTopWidth: string;
  borderRightWidth: string;
  borderBottomWidth: string;
  borderLeftWidth: string;
  borderTopStyle: string;
  borderRightStyle: string;
  borderBottomStyle: string;
  borderLeftStyle: string;
  borderTopLeftRadius: string;
  borderTopRightRadius: string;
  borderBottomRightRadius: string;
  borderBottomLeftRadius: string;
  boxShadow: string;
  cardX: number;
  cardY: number;
  cardWidth: number;
  cardHeight: number;
}

function expectedWidths(specimen: BorderSpecimenConfig): [string, string, string, string] {
  const px = `${specimen.stroke_width_px}px`;
  const zero = "0px";
  if (!specimen.has_border || specimen.stroke_width_px === 0) return [zero, zero, zero, zero];
  switch (specimen.border_sides) {
    case "all-4": return [px, px, px, px];
    case "top-only": return [px, zero, zero, zero];
    case "bottom-only": return [zero, zero, px, zero];
    case "left-only": return [zero, zero, zero, px];
    default: return [zero, zero, zero, zero];
  }
}

function expectedRadii(specimen: BorderSpecimenConfig): [number, number, number, number] {
  if (Array.isArray(specimen.corner_radius_px)) return specimen.corner_radius_px;
  return [specimen.corner_radius_px, specimen.corner_radius_px, specimen.corner_radius_px, specimen.corner_radius_px];
}

function verifyComputed(specimen: BorderSpecimenConfig, computed: ComputedEvidence): void {
  const [et, er, eb, el] = expectedWidths(specimen);
  const actual = [computed.borderTopWidth, computed.borderRightWidth, computed.borderBottomWidth, computed.borderLeftWidth];
  const sides = [et, er, eb, el];
  for (let i = 0; i < 4; i++) {
    if (actual[i] !== sides[i]) {
      throw new Error(`${specimen.id}: border width mismatch on side ${i}: expected ${sides[i]}, got ${actual[i]}`);
    }
  }
  const styles = [computed.borderTopStyle, computed.borderRightStyle, computed.borderBottomStyle, computed.borderLeftStyle];
  for (let i = 0; i < 4; i++) {
    const want = sides[i] === "0px" ? "none" : specimen.stroke_style;
    if (styles[i] !== want) {
      throw new Error(`${specimen.id}: border style mismatch on side ${i}: expected ${want}, got ${styles[i]}`);
    }
  }
  const radii = [computed.borderTopLeftRadius, computed.borderTopRightRadius, computed.borderBottomRightRadius, computed.borderBottomLeftRadius];
  const expected = expectedRadii(specimen);
  for (let i = 0; i < 4; i++) {
    if (Math.abs(parseFloat(radii[i]) - expected[i]) > 0.5) {
      throw new Error(`${specimen.id}: corner radius mismatch on corner ${i}: expected ${expected[i]}, got ${radii[i]}`);
    }
  }
  if (specimen.elevation === "none" && computed.boxShadow !== "none") {
    throw new Error(`${specimen.id}: expected flat box-shadow none, got ${computed.boxShadow}`);
  }
  if (specimen.elevation !== "none" && computed.boxShadow === "none") {
    throw new Error(`${specimen.id}: expected a rendered box-shadow for ${specimen.elevation}, got none`);
  }
  for (const [name, got, want] of [["x", computed.cardX, 80], ["y", computed.cardY, 60], ["width", computed.cardWidth, 400], ["height", computed.cardHeight, 240]] as const) {
    if (Math.abs(got - want) > 2) {
      throw new Error(`${specimen.id}: card geometry ${name} expected ${want}, got ${got}`);
    }
  }
}

async function main() {
  const staging = `${OUTPUT_DIR}.staging-${process.pid}`;
  fs.rmSync(staging, { recursive: true, force: true });
  fs.mkdirSync(staging, { recursive: true });
  console.log(`Starting render of ${SPECIMENS.length} BorderBench specimens...`);
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({
      viewport: { width: 560, height: 360 },
      deviceScaleFactor: 2,
    });
    const browserVersion = browser.version();
    const manifestItems: BorderBenchmarkManifestItem[] = [];

    for (let i = 0; i < SPECIMENS.length; i++) {
      const specimen = SPECIMENS[i];
      const filename = `${specimen.id}.png`;
      const outputPath = path.join(staging, filename);
      await page.setContent(generateCardHtml(specimen));
      const computed = await page.evaluate((): ComputedEvidence => {
        const card = document.querySelector(".card") as HTMLElement;
        const style = getComputedStyle(card);
        const rect = card.getBoundingClientRect();
        return {
          borderTopWidth: style.borderTopWidth,
          borderRightWidth: style.borderRightWidth,
          borderBottomWidth: style.borderBottomWidth,
          borderLeftWidth: style.borderLeftWidth,
          borderTopStyle: style.borderTopStyle,
          borderRightStyle: style.borderRightStyle,
          borderBottomStyle: style.borderBottomStyle,
          borderLeftStyle: style.borderLeftStyle,
          borderTopLeftRadius: style.borderTopLeftRadius,
          borderTopRightRadius: style.borderTopRightRadius,
          borderBottomRightRadius: style.borderBottomRightRadius,
          borderBottomLeftRadius: style.borderBottomLeftRadius,
          boxShadow: style.boxShadow,
          cardX: rect.x,
          cardY: rect.y,
          cardWidth: rect.width,
          cardHeight: rect.height,
        };
      });
      verifyComputed(specimen, computed);
      await page.screenshot({ path: outputPath, type: "png" });
      const bytes = fs.readFileSync(outputPath);

      manifestItems.push({
        taskId: specimen.id,
        imagePath: filename,
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
        imageSha256: crypto.createHash("sha256").update(bytes).digest("hex"),
        rendered: {
          browser: browserVersion,
          platform: process.platform,
          viewport: { width: 560, height: 360, deviceScaleFactor: 2 },
          card: { x: computed.cardX, y: computed.cardY, width: computed.cardWidth, height: computed.cardHeight },
          computed: {
            borderTopWidth: computed.borderTopWidth,
            borderRightWidth: computed.borderRightWidth,
            borderBottomWidth: computed.borderBottomWidth,
            borderLeftWidth: computed.borderLeftWidth,
            borderTopStyle: computed.borderTopStyle,
            borderRightStyle: computed.borderRightStyle,
            borderBottomStyle: computed.borderBottomStyle,
            borderLeftStyle: computed.borderLeftStyle,
            borderTopLeftRadius: computed.borderTopLeftRadius,
            borderTopRightRadius: computed.borderTopRightRadius,
            borderBottomRightRadius: computed.borderBottomRightRadius,
            borderBottomLeftRadius: computed.borderBottomLeftRadius,
            boxShadow: computed.boxShadow,
          },
        },
      });

      if ((i + 1) % 20 === 0 || i === SPECIMENS.length - 1) {
        console.log(`Rendered ${i + 1}/${SPECIMENS.length} specimens...`);
      }
    }

    const manifest = {
      benchmark_id: "borderbench-v1",
      name: "BorderBench V1",
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
    fs.writeFileSync(path.join(staging, "manifest.json"), JSON.stringify(manifest, null, 2));

    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    for (const file of fs.readdirSync(OUTPUT_DIR)) {
      if (file.startsWith(MANAGED_PREFIX) && file.endsWith(".png") && !manifestItems.some((m) => m.imageFilename === file)) {
        fs.rmSync(path.join(OUTPUT_DIR, file));
      }
    }
    for (const file of fs.readdirSync(staging)) {
      fs.renameSync(path.join(staging, file), path.join(OUTPUT_DIR, file));
    }
    console.log(`Finished rendering! Manifest written to ${path.join(OUTPUT_DIR, "manifest.json")}`);
  } finally {
    await browser.close();
    fs.rmSync(staging, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error("Render failed:", err);
  process.exit(1);
});
