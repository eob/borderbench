import { chromium } from "playwright";
import { SPECIMENS } from "./specimens.ts";
import { PROMPT_TEXT } from "./prompt.ts";
import type { BorderSpecimenConfig, BorderBenchmarkManifestItem } from "./types.ts";
import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";

const MANAGED_PREFIX = "borderbench-";
const HISTORICAL_DIRS = ["dataset/borderbench-1", "dataset/rendered"];

export function releaseDatasetPaths(repository = path.resolve(import.meta.dir, "..")): string[] {
  const releasesDir = path.join(repository, "releases");
  const registered: string[] = [];
  for (const file of fs.readdirSync(releasesDir)) {
    if (!file.endsWith(".json")) continue;
    const descriptor = JSON.parse(fs.readFileSync(path.join(releasesDir, file), "utf-8"));
    for (const key of ["dataset_path", "dataset_manifest"]) {
      const value = descriptor?.[key];
      if (typeof value !== "string" || !value || path.isAbsolute(value) || value.includes("\\")
          || value.split("/").some(part => !part || part === "." || part === "..")) {
        throw new Error(`Invalid ${key} in release registry ${file}`);
      }
    }
    if (descriptor.dataset_manifest !== `${descriptor.dataset_path}/manifest.json`) {
      throw new Error(`Invalid dataset manifest in release registry ${file}`);
    }
    registered.push(path.join(repository, descriptor.dataset_path));
  }
  return registered;
}

function physicalPath(filename: string): string {
  let existing = path.resolve(filename);
  const suffix: string[] = [];
  while (!fs.existsSync(existing)) {
    if (fs.lstatSync(existing, { throwIfNoEntry: false })?.isSymbolicLink()) {
      throw new Error(`Cannot resolve output symlink: ${existing}`);
    }
    suffix.unshift(path.basename(existing));
    existing = path.dirname(existing);
  }
  return path.join(fs.realpathSync(existing), ...suffix);
}

export function refuseProtectedDir(chosen: string, registered: string[]): void {
  const resolved = physicalPath(chosen);
  const historical = HISTORICAL_DIRS.map(directory => path.resolve(import.meta.dir, "..", directory));
  for (const directory of [...historical, ...registered]) {
    const protectedDir = physicalPath(directory);
    if (resolved === protectedDir || resolved.startsWith(protectedDir + path.sep)
        || protectedDir.startsWith(resolved.endsWith(path.sep) ? resolved : resolved + path.sep)) {
      const kind = historical.includes(directory) ? "historical" : "registered release";
      throw new Error(`Refusing to overwrite ${kind} dataset: ${chosen}. Render a separate candidate instead.`);
    }
  }
}

function resolveOutputDir(): string {
  const flag = process.argv.indexOf("--output-dir");
  const chosen = flag >= 0 && process.argv[flag + 1] ? process.argv[flag + 1] : "dataset/candidate-rendered";
  refuseProtectedDir(chosen, releaseDatasetPaths());
  return path.resolve(chosen);
}

export const REFERENCE_FONT_PATH = new URL("./assets/DejaVuSans.ttf", import.meta.url);
const FONT_BYTES = fs.readFileSync(REFERENCE_FONT_PATH);
export const REFERENCE_FONT_SHA256 = crypto.createHash("sha256").update(FONT_BYTES).digest("hex");
const FONT_DATA = FONT_BYTES.toString("base64");
export const SHADOWS = {
  none: "none",
  "subtle-drop": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
  "floating-drop": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
} as const;

export function generateCardHtml(specimen: BorderSpecimenConfig): string {
  const palette = {
    "white-on-gray": ["#f1f5f9", "#ffffff", "#cbd5e1"],
    "gray-tint-on-white": ["#ffffff", "#e2e8f0", "#94a3b8"],
    "blue-tint-on-white": ["#ffffff", "#eff6ff", "#93c5fd"],
  };
  const colors = palette[specimen.theme as keyof typeof palette];
  if (!colors) throw new Error(`Unsupported candidate theme: ${specimen.theme}`);
  const [canvasBg, cardBg, borderColor] = colors;
  const stroke = `${specimen.stroke_width_px}px ${specimen.stroke_style} ${borderColor}`;
  const side = (name: string) => specimen.has_border && (specimen.border_sides === "all-4" || specimen.border_sides === `${name}-only`) ? stroke : "none";
  const radius = Array.isArray(specimen.corner_radius_px)
    ? specimen.corner_radius_px.map(px => `${px}px`).join(" ") : `${specimen.corner_radius_px}px`;
  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  @font-face { font-family: "BorderBench Reference"; src: url(data:font/ttf;base64,${FONT_DATA}) format("truetype"); font-style: normal; font-weight: 400; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { position: relative; width: 560px; height: 360px; background: ${canvasBg}; }
  .card { position: absolute; left: 80px; top: 60px; width: 400px; height: 240px;
    background: ${cardBg}; border-top: ${side("top")}; border-right: ${side("right")};
    border-bottom: ${side("bottom")}; border-left: ${side("left")};
    border-radius: ${radius}; box-shadow: ${SHADOWS[specimen.elevation]}; }
  .reference { position: absolute; left: 160px; top: 132px; width: 240px; height: 96px;
    color: #334155; font-family: "BorderBench Reference"; font-synthesis: none;
    font-size: 16px; line-height: 24px; font-weight: 400; text-align: center; }
  .reference p { white-space: nowrap; }
  .scale-rule { width: 64px; height: 2px; margin: 12px auto 0; background: #334155; }
</style></head><body>
  <div class="card"></div>
  <div class="reference"><p>${specimen.title}</p><p>${specimen.subtitle}</p><p>${specimen.tag}</p><div class="scale-rule"></div></div>
</body></html>`;
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
  referenceFontFamily: string;
  referenceFontSize: string;
  referenceLineHeight: string;
  ruleWidth: number;
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
  if (computed.referenceFontFamily !== "BorderBench Reference" || computed.referenceFontSize !== "16px"
      || computed.referenceLineHeight !== "24px" || computed.ruleWidth !== 64) {
    throw new Error(`${specimen.id}: reference scale differs from 16px/24px text and 64px rule`);
  }
  for (const [name, got, want] of [["x", computed.cardX, 80], ["y", computed.cardY, 60], ["width", computed.cardWidth, 400], ["height", computed.cardHeight, 240]] as const) {
    if (Math.abs(got - want) > 2) {
      throw new Error(`${specimen.id}: card geometry ${name} expected ${want}, got ${got}`);
    }
  }
}

async function main() {
  const OUTPUT_DIR = resolveOutputDir();
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
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("DOM.enable");
    await cdp.send("CSS.enable");
    fs.mkdirSync(path.join(staging, "fonts"));
    fs.copyFileSync(REFERENCE_FONT_PATH, path.join(staging, "fonts/DejaVuSans.ttf"));
    fs.copyFileSync(new URL("./assets/DejaVuSans.LICENSE", import.meta.url), path.join(staging, "fonts/DejaVuSans.LICENSE"));
    const manifestItems: BorderBenchmarkManifestItem[] = [];

    for (let i = 0; i < SPECIMENS.length; i++) {
      const specimen = SPECIMENS[i];
      const filename = `${specimen.id}.png`;
      const outputPath = path.join(staging, filename);
      await page.setContent(generateCardHtml(specimen));
      await page.evaluate(() => document.fonts.ready);
      const computed = await page.evaluate((): ComputedEvidence => {
        const card = document.querySelector(".card") as HTMLElement;
        const style = getComputedStyle(card);
        const rect = card.getBoundingClientRect();
        const referenceStyle = getComputedStyle(document.querySelector(".reference")!);
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
          referenceFontFamily: referenceStyle.fontFamily.replaceAll('"', ""),
          referenceFontSize: referenceStyle.fontSize,
          referenceLineHeight: referenceStyle.lineHeight,
          ruleWidth: document.querySelector(".scale-rule")!.getBoundingClientRect().width,
        };
      });
      verifyComputed(specimen, computed);
      const documentRoot = await cdp.send("DOM.getDocument");
      const referenceNode = await cdp.send("DOM.querySelector", { nodeId: documentRoot.root.nodeId, selector: ".reference" });
      const { fonts } = await cdp.send("CSS.getPlatformFontsForNode", { nodeId: referenceNode.nodeId });
      if (!fonts.length || fonts.some(font => font.familyName !== "DejaVu Sans" || !font.isCustomFont || font.glyphCount <= 0)) {
        throw new Error(`${specimen.id}: reference text used unexpected font: ${JSON.stringify(fonts)}`);
      }
      await page.screenshot({ path: outputPath, type: "png" });
      const bytes = fs.readFileSync(outputPath);

      manifestItems.push({
        taskId: specimen.id,
        design: specimen.design,
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
          font: { path: "fonts/DejaVuSans.ttf", sha256: REFERENCE_FONT_SHA256, family: "DejaVu Sans", platformFonts: fonts },
          reference: { fontFamily: computed.referenceFontFamily, fontSizePx: Number.parseFloat(computed.referenceFontSize), lineHeightPx: Number.parseFloat(computed.referenceLineHeight), ruleWidthPx: computed.ruleWidth },
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

    for (const item of manifestItems) {
      const reference = manifestItems.find(other => other.design?.recipeId === item.design?.recipeId
        && other.groundTruth.theme === item.groundTruth.theme && other.groundTruth.elevation === "none");
      if (!reference?.imageSha256) throw new Error(`Missing flat control for ${item.taskId}`);
      item.rendered!.shadowReference = { imageFilename: reference.imageFilename, imageSha256: reference.imageSha256 };
    }
    fs.writeFileSync(path.join(staging, "catalog.json"), JSON.stringify({
      schema_version: 1, tasks: manifestItems.map(item => ({ taskId: item.taskId, groundTruth: item.groundTruth, design: item.design })),
      referenceFont: { path: "fonts/DejaVuSans.ttf", sha256: REFERENCE_FONT_SHA256 }, prompt: PROMPT_TEXT,
    }, null, 2) + "\n");
    const manifest = {
      benchmark_id: "borderbench-candidate",
      name: "BorderBench candidate",
      version: "0.0.0-candidate",
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
      fs.cpSync(path.join(staging, file), path.join(OUTPUT_DIR, file), { recursive: true, force: true });
    }
    console.log(`Finished rendering! Manifest written to ${path.join(OUTPUT_DIR, "manifest.json")}`);
  } finally {
    await browser.close();
    fs.rmSync(staging, { recursive: true, force: true });
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.error("Render failed:", err);
    process.exit(1);
  });
}
