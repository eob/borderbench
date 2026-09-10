import type { BorderSpecimenConfig, BorderSides, StrokeStyle, StrokeWidth, CornerRadius, CornerUniformity, Elevation, BackgroundTheme } from "./types.ts";

export const SPECIMENS: BorderSpecimenConfig[] = [];

// Fixed neutral card copy. Identical on every specimen: models must judge
// border, corner, and shadow pixels, never rendered text.
const TITLE = "Container Specimen";
const SUBTITLE = "Surface and edge sample";
const TAG = "Sample";

const RADII: { class: CornerRadius; px: number }[] = [
  { class: "sharp", px: 0 },
  { class: "subtle", px: 3 },
  { class: "medium", px: 8 },
  { class: "large", px: 18 },
  { class: "pill", px: 9999 },
];

const WIDTHS: { class: StrokeWidth; px: number }[] = [
  { class: "0px", px: 0 },
  { class: "1px", px: 1 },
  { class: "2px", px: 2 },
  { class: "4px", px: 4 },
  { class: "8px", px: 8 },
];

const SIDES: BorderSides[] = ["all-4", "bottom-only", "left-only", "top-only", "none"];
const THEMES: BackgroundTheme[] = ["white-on-gray", "white-on-white", "gray-tint-on-white", "blue-tint-on-white", "dark-mode"];
const ROUND_RADII: CornerRadius[] = ["subtle", "medium", "large"];

function radiusPx(radius: CornerRadius, uniformity: CornerUniformity): number | [number, number, number, number] {
  const px = RADII.find((r) => r.class === radius)!.px;
  if (uniformity === "top-only") return [px, px, 0, 0];
  if (uniformity === "asymmetric") return [px, px, px, 2];
  return px;
}

function addSpecimen(cfg: Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag">) {
  const index = SPECIMENS.length + 1;
  SPECIMENS.push({ ...cfg, id: `borderbench-v1-${String(index).padStart(3, "0")}`, title: TITLE, subtitle: SUBTITLE, tag: TAG });
}

function bordered(sides: BorderSides, width: StrokeWidth, style: StrokeStyle, elevation: Elevation) {
  const px = WIDTHS.find((w) => w.class === width)!.px;
  const has = sides !== "none";
  if (!has && (width !== "0px" || style !== "none")) throw new Error("borderless specimens need 0px/none stroke");
  if (has && (width === "0px" || style === "none")) throw new Error("bordered specimens need a visible stroke");
  if (style === "double" && px < 4) throw new Error("double needs at least 4px");
  if (elevation === "stroke+shadow" && !has) throw new Error("stroke+shadow needs a border");
  if ((elevation === "subtle-drop" || elevation === "floating-drop" || elevation === "ring-only") && has) {
    throw new Error(`${elevation} is borderless by design; use stroke+shadow to combine`);
  }
  return { has_border: has, stroke_width_px: px };
}

// 1. Curvature sweep: 1px solid all-4, flat, white-on-gray.
for (const r of RADII) {
  const b = bordered("all-4", "1px", "solid", "none");
  addSpecimen({
    has_border: b.has_border, border_sides: "all-4", stroke_style: "solid", stroke_width: "1px",
    stroke_width_px: b.stroke_width_px, corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: "none", theme: "white-on-gray",
  });
}

// 2. Width sweep: medium radius, solid all-4, flat, blue-tint (theme separates it from sweep 1).
for (const w of WIDTHS) {
  const has = w.px > 0;
  const b = bordered(has ? "all-4" : "none", w.class, has ? "solid" : "none", "none");
  addSpecimen({
    has_border: b.has_border, border_sides: has ? "all-4" : "none", stroke_style: has ? "solid" : "none",
    stroke_width: w.class, stroke_width_px: b.stroke_width_px, corner_radius: "medium", corner_radius_px: 8,
    corner_uniformity: "all-corners", elevation: "none", theme: "blue-tint-on-white",
  });
}

// 3. Style sweep: medium radius, all-4, flat, gray-tint.
for (const [style, width] of [["solid", "2px"], ["dashed", "2px"], ["dotted", "2px"], ["double", "4px"]] as [StrokeStyle, StrokeWidth][]) {
  const b = bordered("all-4", width, style, "none");
  addSpecimen({
    has_border: b.has_border, border_sides: "all-4", stroke_style: style, stroke_width: width,
    stroke_width_px: b.stroke_width_px, corner_radius: "medium", corner_radius_px: 8,
    corner_uniformity: "all-corners", elevation: "none", theme: "gray-tint-on-white",
  });
}

// 4. Sides sweep: sharp corners, solid, flat, dark-mode.
for (const [sides, width] of [["all-4", "1px"], ["bottom-only", "1px"], ["left-only", "4px"], ["top-only", "2px"], ["none", "0px"]] as [BorderSides, StrokeWidth][]) {
  const has = sides !== "none";
  const b = bordered(sides, width, has ? "solid" : "none", "none");
  addSpecimen({
    has_border: b.has_border, border_sides: sides, stroke_style: has ? "solid" : "none",
    stroke_width: width, stroke_width_px: b.stroke_width_px, corner_radius: "sharp", corner_radius_px: 0,
    corner_uniformity: "all-corners", elevation: "none", theme: "dark-mode",
  });
}

// 5. Uniformity sweep: 1px solid all-4, flat, white-on-white (bordered, so the boundary stays visible).
for (const [radius, uniformity] of [["medium", "all-corners"], ["large", "top-only"], ["large", "asymmetric"]] as [CornerRadius, CornerUniformity][]) {
  const b = bordered("all-4", "1px", "solid", "none");
  addSpecimen({
    has_border: b.has_border, border_sides: "all-4", stroke_style: "solid", stroke_width: "1px",
    stroke_width_px: b.stroke_width_px, corner_radius: radius, corner_radius_px: radiusPx(radius, uniformity),
    corner_uniformity: uniformity, elevation: "none", theme: "white-on-white",
  });
}

// 6. Elevation sweep: medium radius, all-corners, gray-tint.
for (const [elevation, sides, width] of [
  ["none", "all-4", "1px"],
  ["subtle-drop", "none", "0px"],
  ["floating-drop", "none", "0px"],
  ["ring-only", "none", "0px"],
  ["stroke+shadow", "all-4", "1px"],
] as [Elevation, BorderSides, StrokeWidth][]) {
  const has = sides !== "none";
  const b = bordered(sides, width, has ? "solid" : "none", elevation);
  addSpecimen({
    has_border: b.has_border, border_sides: sides, stroke_style: has ? "solid" : "none",
    stroke_width: width, stroke_width_px: b.stroke_width_px, corner_radius: "medium", corner_radius_px: 8,
    corner_uniformity: "all-corners", elevation, theme: "gray-tint-on-white",
  });
}

// 7. Contrast pairs: large radius, 2px when bordered. The two pale themes get a
// shadow instead of a flat borderless card, which would be invisible.
for (const theme of THEMES) {
  const pale = theme === "white-on-white" || theme === "gray-tint-on-white";
  for (const has of [true, false]) {
    const elevation: Elevation = !has && pale ? "subtle-drop" : "none";
    const b = bordered(has ? "all-4" : "none", has ? "2px" : "0px", has ? "solid" : "none", elevation);
    addSpecimen({
      has_border: b.has_border, border_sides: has ? "all-4" : "none", stroke_style: has ? "solid" : "none",
      stroke_width: has ? "2px" : "0px", stroke_width_px: b.stroke_width_px, corner_radius: "large",
      corner_radius_px: 18, corner_uniformity: "all-corners", elevation, theme,
    });
  }
}

// 8. Quota filler: deterministic schedules for rare values, then balanced
// round-robin. Every filler below keeps (labels + theme) unique.
function filler(spec: Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag">) {
  const pale = spec.theme === "white-on-white" || spec.theme === "gray-tint-on-white";
  if (pale && !spec.has_border && spec.elevation === "none") throw new Error("invisible pale borderless flat card");
  if ((spec.corner_uniformity === "top-only" || spec.corner_uniformity === "asymmetric") && !ROUND_RADII.includes(spec.corner_radius)) {
    throw new Error("non-uniform corners need a rounded radius");
  }
  const key = JSON.stringify([spec.border_sides, spec.stroke_style, spec.stroke_width, spec.corner_radius, spec.corner_uniformity, spec.elevation, spec.theme]);
  if (SPECIMENS.some((s) => JSON.stringify([s.border_sides, s.stroke_style, s.stroke_width, s.corner_radius, s.corner_uniformity, s.elevation, s.theme]) === key)) {
    throw new Error(`duplicate graded combination: ${key}`);
  }
  bordered(spec.border_sides, spec.stroke_width, spec.stroke_style, spec.elevation);
  addSpecimen(spec);
}

// 8a. Asymmetric corners x8.
for (let i = 0; i < 8; i++) {
  const radius = ROUND_RADII[i % 3];
  filler({
    has_border: true, border_sides: "all-4", stroke_style: "solid", stroke_width: "1px", stroke_width_px: 1,
    corner_radius: radius, corner_radius_px: radiusPx(radius, "asymmetric"),
    corner_uniformity: "asymmetric", elevation: "none", theme: THEMES[(i + 2) % 5],
  });
}

// 8b. Top-only corners x8.
const TOP_STYLES: StrokeStyle[] = ["solid", "dashed", "dotted"];
for (let i = 0; i < 8; i++) {
  const radius = ROUND_RADII[(i + 1) % 3];
  filler({
    has_border: true, border_sides: "all-4", stroke_style: TOP_STYLES[i % 3], stroke_width: "2px", stroke_width_px: 2,
    corner_radius: radius, corner_radius_px: radiusPx(radius, "top-only"),
    corner_uniformity: "top-only", elevation: "none", theme: THEMES[(i + 3) % 5],
  });
}

// 8c. Floating drop x8 (borderless, shadow keeps pale themes visible).
take(8, (i): Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag"> => {
  const r = RADII[Math.floor(i / 2) % 5];
  return {
    has_border: false, border_sides: "none", stroke_style: "none", stroke_width: "0px", stroke_width_px: 0,
    corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: "floating-drop", theme: THEMES[(2 * i + 1) % 5],
  };
});

// 8d. Ring-only x8.
take(8, (i): Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag"> => {
  const r = RADII[(Math.floor(i / 2) + 2) % 5];
  return {
    has_border: false, border_sides: "none", stroke_style: "none", stroke_width: "0px", stroke_width_px: 0,
    corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: "ring-only", theme: THEMES[(2 * i + 3) % 5],
  };
});

function take(count: number, candidate: (i: number) => Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag">) {
  let added = 0;
  for (let i = 0; added < count && i < 200; i++) {
    try {
      filler(candidate(i));
      added++;
    } catch {
      continue;
    }
  }
  if (added < count) throw new Error("quota schedule exhausted without filling its quota");
}

// 8e. Double stroke x8 across sides; two carry stroke+shadow.
const DOUBLE_SIDES: BorderSides[] = ["all-4", "bottom-only", "left-only", "top-only"];
for (let i = 0; i < 8; i++) {
  const width: StrokeWidth = i % 2 === 0 ? "4px" : "8px";
  const r = RADII[i % 5];
  filler({
    has_border: true, border_sides: DOUBLE_SIDES[i % 4], stroke_style: "double", stroke_width: width,
    stroke_width_px: width === "4px" ? 4 : 8, corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: i >= 6 ? "stroke+shadow" : "none", theme: THEMES[(i + 4) % 5],
  });
}

// 8f. Heavy 8px non-double x4.
for (let i = 0; i < 4; i++) {
  const r = RADII[(i + 1) % 5];
  filler({
    has_border: true, border_sides: DOUBLE_SIDES[(i + 1) % 4], stroke_style: i % 2 === 0 ? "solid" : "dashed",
    stroke_width: "8px", stroke_width_px: 8, corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: "none", theme: THEMES[(i + 2) % 5],
  });
}

// 8g. Partial sides x12 with varied widths, styles, and shadows.
const PARTIAL: BorderSides[] = ["bottom-only", "left-only", "top-only"];
const PARTIAL_WIDTHS: StrokeWidth[] = ["1px", "2px", "4px"];
const PARTIAL_STYLES: StrokeStyle[] = ["solid", "dashed", "dotted"];
for (let i = 0; i < 12; i++) {
  const width = PARTIAL_WIDTHS[i % 3];
  const r = RADII[(i + 4) % 5];
  filler({
    has_border: true, border_sides: PARTIAL[i % 3], stroke_style: PARTIAL_STYLES[(i + 1) % 3],
    stroke_width: width, stroke_width_px: WIDTHS.find((w) => w.class === width)!.px,
    corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: i >= 7 ? "stroke+shadow" : "none", theme: THEMES[i % 5],
  });
}

// 8h. Subtle drop x8.
take(8, (i): Omit<BorderSpecimenConfig, "id" | "title" | "subtitle" | "tag"> => {
  const r = RADII[(Math.floor(i / 2) + 4) % 5];
  return {
    has_border: false, border_sides: "none", stroke_style: "none", stroke_width: "0px", stroke_width_px: 0,
    corner_radius: r.class, corner_radius_px: r.px,
    corner_uniformity: "all-corners", elevation: "subtle-drop", theme: THEMES[(2 * i) % 5],
  };
});

// 8i. Balanced remainder to exactly 120.
const REM_STYLES: StrokeStyle[] = ["solid", "solid", "dashed", "dotted"];
outer: for (let i = 0; SPECIMENS.length < 120; i++) {
  for (const sides of SIDES) {
    if (SPECIMENS.length >= 120) break outer;
    const has = sides !== "none";
    const width = has ? PARTIAL_WIDTHS[(i + SIDES.indexOf(sides)) % 3] : "0px";
    const style = has ? REM_STYLES[(i + SIDES.indexOf(sides)) % 4] : "none";
    const r = RADII[(i + SIDES.indexOf(sides) * 2) % 5];
    const theme = THEMES[(i * 2 + SIDES.indexOf(sides)) % 5];
    const pale = theme === "white-on-white" || theme === "gray-tint-on-white";
    const elevation: Elevation = !has && pale ? "subtle-drop" : has && (i + SIDES.indexOf(sides)) % 7 === 6 ? "stroke+shadow" : "none";
    if (!has && style !== "none") continue;
    try {
      filler({
        has_border: has, border_sides: sides, stroke_style: style,
        stroke_width: width, stroke_width_px: WIDTHS.find((w) => w.class === width)!.px,
        corner_radius: r.class, corner_radius_px: r.px,
        corner_uniformity: "all-corners", elevation, theme,
      });
    } catch {
      continue;
    }
  }
  if (i > 200) throw new Error("filler failed to reach 120 unique combinations");
}

function assertQuotas() {
  const axes: [string, (s: BorderSpecimenConfig) => string][] = [
    ["border_sides", (s) => s.border_sides],
    ["stroke_style", (s) => s.stroke_style],
    ["stroke_width", (s) => s.stroke_width],
    ["corner_radius", (s) => s.corner_radius],
    ["corner_uniformity", (s) => s.corner_uniformity],
    ["elevation", (s) => s.elevation],
  ];
  for (const [name, key] of axes) {
    const counts = new Map<string, number>();
    for (const s of SPECIMENS) counts.set(key(s), (counts.get(key(s)) ?? 0) + 1);
    for (const [value, count] of counts) {
      if (count < 8) throw new Error(`quota violated: ${name}=${value} has ${count}, need 8`);
    }
  }
  if (SPECIMENS.length !== 120) throw new Error(`expected 120 specimens, got ${SPECIMENS.length}`);
}

assertQuotas();
