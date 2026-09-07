import type { BorderSpecimenConfig, BorderSides, StrokeStyle, StrokeWidth, CornerRadius, CornerUniformity, Elevation, BackgroundTheme } from "./types.ts";

export const SPECIMENS: BorderSpecimenConfig[] = [];

// Helper to add specimen
function addSpecimen(cfg: Omit<BorderSpecimenConfig, "id"> & { id?: string }) {
  const index = SPECIMENS.length + 1;
  const id = cfg.id || `borderbench-${String(index).padStart(3, "0")}`;
  SPECIMENS.push({ ...cfg, id });
}

// 1. Core Curvature Sweep (holding 1px solid, all-4, flat, white-on-gray)
const curvatures: { class: CornerRadius; px: number }[] = [
  { class: "sharp", px: 0 },
  { class: "subtle", px: 3 },
  { class: "medium", px: 8 },
  { class: "large", px: 18 },
  { class: "pill", px: 9999 },
];

for (const c of curvatures) {
  addSpecimen({
    has_border: true,
    border_sides: "all-4",
    stroke_style: "solid",
    stroke_width: "1px",
    stroke_width_px: 1,
    corner_radius: c.class,
    corner_radius_px: c.px,
    corner_uniformity: "all-corners",
    elevation: "none",
    theme: "white-on-gray",
    title: `${c.class.toUpperCase()} Border Radius`,
    subtitle: `Curvature token test: ${c.class} (${c.px}px)`,
    tag: "Curvature",
  });
}

// 2. Stroke Width Sweep (holding medium 8px, solid, all-4, flat, white-on-gray)
const strokeWidths: { class: StrokeWidth; px: number; has: boolean; style: StrokeStyle }[] = [
  { class: "0px", px: 0, has: false, style: "none" },
  { class: "1px", px: 1, has: true, style: "solid" },
  { class: "2px", px: 2, has: true, style: "solid" },
  { class: "4px", px: 4, has: true, style: "solid" },
  { class: "8px", px: 8, has: true, style: "solid" },
];

for (const sw of strokeWidths) {
  addSpecimen({
    has_border: sw.has,
    border_sides: sw.has ? "all-4" : "none",
    stroke_style: sw.style,
    stroke_width: sw.class,
    stroke_width_px: sw.px,
    corner_radius: "medium",
    corner_radius_px: 8,
    corner_uniformity: "all-corners",
    elevation: "none",
    theme: "white-on-gray",
    title: `Stroke Width ${sw.class}`,
    subtitle: `Thickness token test: ${sw.class} (${sw.px}px)`,
    tag: "Thickness",
  });
}

// 3. Stroke Style Sweep (holding medium 8px, 2px stroke, all-4, flat, white-on-gray)
const strokeStyles: { style: StrokeStyle; width: StrokeWidth; px: number }[] = [
  { style: "solid", width: "2px", px: 2 },
  { style: "dashed", width: "2px", px: 2 },
  { style: "dotted", width: "2px", px: 2 },
  { style: "double", width: "4px", px: 4 }, // double requires >= 3-4px to render cleanly
];

for (const ss of strokeStyles) {
  addSpecimen({
    has_border: true,
    border_sides: "all-4",
    stroke_style: ss.style,
    stroke_width: ss.width,
    stroke_width_px: ss.px,
    corner_radius: "medium",
    corner_radius_px: 8,
    corner_uniformity: "all-corners",
    elevation: "none",
    theme: "white-on-gray",
    title: `${ss.style.toUpperCase()} Stroke Pattern`,
    subtitle: `Border style test: ${ss.style}`,
    tag: "Pattern",
  });
}

// 4. Edge Selectivity / Asymmetric Sides
const sideConfigs: { sides: BorderSides; width: StrokeWidth; px: number }[] = [
  { sides: "all-4", width: "1px", px: 1 },
  { sides: "bottom-only", width: "1px", px: 1 },
  { sides: "left-only", width: "4px", px: 4 },
  { sides: "top-only", width: "2px", px: 2 },
  { sides: "none", width: "0px", px: 0 },
];

for (const sc of sideConfigs) {
  const has = sc.sides !== "none";
  addSpecimen({
    has_border: has,
    border_sides: sc.sides,
    stroke_style: has ? "solid" : "none",
    stroke_width: sc.width,
    stroke_width_px: sc.px,
    corner_radius: "sharp",
    corner_radius_px: 0,
    corner_uniformity: "all-corners",
    elevation: "none",
    theme: "white-on-gray",
    title: `Side Config: ${sc.sides}`,
    subtitle: `Edge selectivity test: ${sc.sides}`,
    tag: "Sides",
  });
}

// 5. Corner Uniformity / Asymmetric Radii
addSpecimen({
  has_border: true,
  border_sides: "all-4",
  stroke_style: "solid",
  stroke_width: "1px",
  stroke_width_px: 1,
  corner_radius: "medium",
  corner_radius_px: 8,
  corner_uniformity: "all-corners",
  elevation: "none",
  theme: "white-on-gray",
  title: "Uniform Corners (8px)",
  subtitle: "Symmetry test: all 4 corners equal",
  tag: "Uniformity",
});

addSpecimen({
  has_border: true,
  border_sides: "all-4",
  stroke_style: "solid",
  stroke_width: "1px",
  stroke_width_px: 1,
  corner_radius: "large",
  corner_radius_px: [16, 16, 0, 0],
  corner_uniformity: "top-only",
  elevation: "none",
  theme: "white-on-gray",
  title: "Top-Rounded Modal Header",
  subtitle: "Symmetry test: top corners rounded (16px), bottom sharp (0px)",
  tag: "Uniformity",
});

addSpecimen({
  has_border: true,
  border_sides: "all-4",
  stroke_style: "solid",
  stroke_width: "1px",
  stroke_width_px: 1,
  corner_radius: "large",
  corner_radius_px: [16, 16, 16, 2],
  corner_uniformity: "asymmetric",
  elevation: "none",
  theme: "white-on-gray",
  title: "Asymmetric Chat Bubble",
  subtitle: "Symmetry test: 3 rounded corners (16px), 1 acute corner (2px)",
  tag: "Uniformity",
});

// 6. Elevation & Shadow vs Border Space
const elevations: { elevation: Elevation; has_border: boolean; width: StrokeWidth; px: number; title: string; subtitle: string }[] = [
  { elevation: "none", has_border: true, width: "1px", px: 1, title: "Flat Border Only", subtitle: "1px border, 0px shadow" },
  { elevation: "subtle-drop", has_border: false, width: "0px", px: 0, title: "Pure Subtle Shadow", subtitle: "0px border, shadow-sm" },
  { elevation: "floating-drop", has_border: false, width: "0px", px: 0, title: "Pure Floating Shadow", subtitle: "0px border, shadow-lg" },
  { elevation: "ring-only", has_border: false, width: "0px", px: 0, title: "Ring Pseudo-Border", subtitle: "0px border, 1px box-shadow ring" },
  { elevation: "stroke+shadow", has_border: true, width: "1px", px: 1, title: "Border Plus Shadow", subtitle: "1px border and shadow-md" },
];

for (const el of elevations) {
  addSpecimen({
    has_border: el.has_border,
    border_sides: el.has_border ? "all-4" : "none",
    stroke_style: el.has_border ? "solid" : "none",
    stroke_width: el.width,
    stroke_width_px: el.px,
    corner_radius: "medium",
    corner_radius_px: 8,
    corner_uniformity: "all-corners",
    elevation: el.elevation,
    theme: "white-on-gray",
    title: el.title,
    subtitle: el.subtitle,
    tag: "Elevation",
  });
}

// 7. Background Tint & Optical Step Illusion Matrix
const opticalPairs: { theme: BackgroundTheme; has_border: boolean; width: StrokeWidth; px: number; title: string; subtitle: string }[] = [
  { theme: "white-on-gray", has_border: true, width: "1px", px: 1, title: "White Card on Light Gray (Bordered)", subtitle: "Standard card with 1px border" },
  { theme: "white-on-gray", has_border: false, width: "0px", px: 0, title: "White Card on Light Gray (Unbordered)", subtitle: "Contrast boundary without border" },
  { theme: "white-on-white", has_border: true, width: "1px", px: 1, title: "White Card on White Canvas (Bordered)", subtitle: "Border is only visual boundary" },
  { theme: "white-on-white", has_border: false, width: "0px", px: 0, title: "White Card on White Canvas (Unbordered)", subtitle: "Flush boundary without border" },
  { theme: "gray-tint-on-white", has_border: true, width: "1px", px: 1, title: "Gray Tint on White (Bordered)", subtitle: "Tinted container with 1px border" },
  { theme: "gray-tint-on-white", has_border: false, width: "0px", px: 0, title: "Gray Tint on White (Optical Step)", subtitle: "Subtle background step without stroke" },
  { theme: "blue-tint-on-white", has_border: true, width: "1px", px: 1, title: "Blue Tint on White (Bordered)", subtitle: "Tinted container with 1px border" },
  { theme: "blue-tint-on-white", has_border: false, width: "0px", px: 0, title: "Blue Tint on White (Unbordered)", subtitle: "Tinted container with 0px border" },
  { theme: "dark-mode", has_border: true, width: "1px", px: 1, title: "Dark Mode Card (Bordered)", subtitle: "Slate-800 card with subtle white/10 border" },
  { theme: "dark-mode", has_border: false, width: "0px", px: 0, title: "Dark Mode Card (Unbordered)", subtitle: "Slate-800 card without border" },
];

for (const op of opticalPairs) {
  addSpecimen({
    has_border: op.has_border,
    border_sides: op.has_border ? "all-4" : "none",
    stroke_style: op.has_border ? "solid" : "none",
    stroke_width: op.width,
    stroke_width_px: op.px,
    corner_radius: "medium",
    corner_radius_px: 8,
    corner_uniformity: "all-corners",
    elevation: "none",
    theme: op.theme,
    title: op.title,
    subtitle: op.subtitle,
    tag: "Contrast",
  });
}

// 8. Balanced Combinatorial Cross-Product (to reach 120 total diverse specimens)
// We systematically cross curvature, stroke width, styles, sides, elevations, and themes
const comboThemes: BackgroundTheme[] = ["white-on-gray", "gray-tint-on-white", "blue-tint-on-white", "dark-mode", "white-on-white"];
const comboCurvatures: { class: CornerRadius; px: number }[] = [
  { class: "sharp", px: 0 },
  { class: "subtle", px: 3 },
  { class: "medium", px: 8 },
  { class: "large", px: 18 },
  { class: "pill", px: 9999 },
];
const comboStyles: StrokeStyle[] = ["solid", "dashed", "dotted", "double"];
const comboElevations: Elevation[] = ["none", "subtle-drop", "floating-drop", "ring-only", "stroke+shadow"];
const comboSides: BorderSides[] = ["all-4", "bottom-only", "left-only", "top-only", "none"];

let seed = 42;
function pseudoRandom() {
  seed = (seed * 9301 + 49297) % 233280;
  return seed / 233280;
}

while (SPECIMENS.length < 120) {
  const cIdx = Math.floor(pseudoRandom() * comboCurvatures.length);
  const curv = comboCurvatures[cIdx];
  const themeIdx = Math.floor(pseudoRandom() * comboThemes.length);
  const theme = comboThemes[themeIdx];
  const sideIdx = Math.floor(pseudoRandom() * comboSides.length);
  const sides = comboSides[sideIdx];
  const has = sides !== "none";
  
  let widthClass: StrokeWidth = "1px";
  let widthPx = 1;
  let style: StrokeStyle = "solid";
  let elev: Elevation = "none";
  
  if (!has) {
    widthClass = "0px";
    widthPx = 0;
    style = "none";
    elev = pseudoRandom() > 0.5 ? "subtle-drop" : (pseudoRandom() > 0.5 ? "ring-only" : "none");
  } else {
    const wRand = pseudoRandom();
    if (wRand < 0.35) {
      widthClass = "1px";
      widthPx = 1;
    } else if (wRand < 0.65) {
      widthClass = "2px";
      widthPx = 2;
    } else if (wRand < 0.85) {
      widthClass = "4px";
      widthPx = 4;
    } else {
      widthClass = "8px";
      widthPx = 8;
    }
    
    if (widthPx >= 4 && pseudoRandom() > 0.7) {
      style = "double";
    } else {
      const sRand = pseudoRandom();
      if (sRand < 0.55) style = "solid";
      else if (sRand < 0.8) style = "dashed";
      else style = "dotted";
    }
    
    const eRand = pseudoRandom();
    if (eRand < 0.6) elev = "none";
    else if (eRand < 0.8) elev = "subtle-drop";
    else elev = "stroke+shadow";
  }

  const uniformity: CornerUniformity = 
    curv.class === "sharp" || curv.class === "pill" 
      ? "all-corners" 
      : (pseudoRandom() > 0.85 ? "top-only" : "all-corners");

  const cornerPx = uniformity === "top-only" 
    ? [curv.px, curv.px, 0, 0] as [number, number, number, number]
    : curv.px;

  addSpecimen({
    has_border: has,
    border_sides: sides,
    stroke_style: style,
    stroke_width: widthClass,
    stroke_width_px: widthPx,
    corner_radius: curv.class,
    corner_radius_px: cornerPx,
    corner_uniformity: uniformity,
    elevation: elev,
    theme: theme,
    title: `UI Card Specimen #${SPECIMENS.length + 1}`,
    subtitle: `${curv.class} • ${widthClass} ${style} • ${sides}`,
    tag: "Composite",
  });
}
