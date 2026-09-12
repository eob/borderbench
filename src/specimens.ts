import type { BorderSpecimenConfig, BorderSides, StrokeStyle, StrokeWidth, CornerRadius, CornerUniformity, Elevation, BackgroundTheme, MatchedBlock } from "./types.ts";

export const RADII = { sharp: 0, subtle: 4, medium: 12, large: 24, pill: 9999 } as const;
export const WIDTHS: StrokeWidth[] = ["0px", "1px", "2px", "4px", "8px"];
export const THEMES: BackgroundTheme[] = ["white-on-gray", "gray-tint-on-white", "blue-tint-on-white"];
export const ELEVATIONS: Elevation[] = ["none", "subtle-drop", "floating-drop"];
const SIDES: BorderSides[] = ["all-4", "bottom-only", "left-only", "top-only", "none"];
const STYLES: StrokeStyle[] = ["solid", "dashed", "dotted"];
const UNIFORMITIES: CornerUniformity[] = ["all-corners", "top-only", "asymmetric"];

type Geometry = Pick<BorderSpecimenConfig, "border_sides" | "stroke_style" | "stroke_width" | "corner_radius" | "corner_uniformity">;
const BASE: Geometry = { border_sides: "all-4", stroke_style: "solid", stroke_width: "2px", corner_radius: "medium", corner_uniformity: "all-corners" };
const recipes = new Map<string, { geometry: Geometry; blocks: MatchedBlock[] }>();

function add(overrides: Partial<Geometry>, block: MatchedBlock): void {
  const geometry = { ...BASE, ...overrides };
  if (geometry.border_sides === "none" || geometry.stroke_width === "0px") {
    geometry.border_sides = "none";
    geometry.stroke_style = "none";
    geometry.stroke_width = "0px";
  }
  const key = JSON.stringify(geometry);
  const existing = recipes.get(key);
  if (existing) existing.blocks.push(block);
  else recipes.set(key, { geometry, blocks: [block] });
}

// Each block holds all independent properties fixed. The zero-width/no-side
// conditions also update their logically dependent presence/style/width labels.
for (const width of WIDTHS) add({ stroke_width: width }, { id: "width", axis: "stroke_width", level: width });
for (const width of WIDTHS.filter(w => w !== "0px")) {
  for (const style of STYLES) add({ stroke_width: width, stroke_style: style }, { id: `style-${width}`, axis: "stroke_style", level: style });
}
for (const style of STYLES) {
  for (const sides of SIDES) add({ stroke_style: style, border_sides: sides }, { id: `sides-${style}`, axis: "border_sides", level: sides });
}
const contexts: Partial<Geometry>[] = [
  { border_sides: "none" },
  {},
  { stroke_style: "dashed", stroke_width: "4px" },
];
for (const [index, context] of contexts.entries()) {
  for (const radius of Object.keys(RADII) as CornerRadius[]) {
    add({ ...context, corner_radius: radius }, { id: `radius-${index}`, axis: "corner_radius", level: radius });
  }
}
for (const radius of ["medium", "large"] as const) {
  for (const [index, context] of contexts.slice(0, 2).entries()) {
    for (const uniformity of UNIFORMITIES) {
      add({ ...context, corner_radius: radius, corner_uniformity: uniformity }, { id: `uniformity-${radius}-${index}`, axis: "corner_uniformity", level: uniformity });
    }
  }
}
// Mixed cases extend the sweeps to heavy partial edges and rounded patterns.
for (const [sideIndex, sides] of SIDES.slice(0, 4).entries()) {
  for (const [styleIndex, style] of STYLES.entries()) {
    add({ border_sides: sides, stroke_style: style, stroke_width: styleIndex === 0 ? "8px" : "4px",
      corner_radius: (["sharp", "subtle", "large", "pill"] as const)[(sideIndex + styleIndex) % 4] },
    { id: "mixed", axis: "mixed", level: `${sides}-${style}` });
  }
}

export const SPECIMENS: BorderSpecimenConfig[] = [];
for (const [recipeIndex, recipe] of [...recipes.values()].entries()) {
  const recipeId = `recipe-${String(recipeIndex + 1).padStart(3, "0")}`;
  for (const theme of THEMES) {
    for (const elevation of ELEVATIONS) {
      const geometry = recipe.geometry;
      const px = RADII[geometry.corner_radius];
      let radius: number | [number, number, number, number] = px;
      if (geometry.corner_uniformity === "top-only") radius = [px, px, 0, 0];
      if (geometry.corner_uniformity === "asymmetric") radius = [px, px, px, 0];
      SPECIMENS.push({ ...geometry, id: `borderbench-${String(SPECIMENS.length + 1).padStart(3, "0")}`,
        has_border: geometry.border_sides !== "none", stroke_width_px: Number.parseInt(geometry.stroke_width),
        corner_radius_px: radius, theme, elevation,
        title: "Sample interface", subtitle: "Aa Bb Cc 0123456789", tag: "16 px type · 64 px guide",
        design: { recipeId, matchedBlocks: [...recipe.blocks, { id: `elevation-${recipeId}`, axis: "elevation", level: elevation }] },
      });
    }
  }
}

// Check every declared enum, including absent values, rather than only counting
// whichever classes happened to be emitted by the recipes.
const ENUMS = { border_sides: SIDES, stroke_style: [...STYLES, "none"], stroke_width: WIDTHS,
  corner_radius: Object.keys(RADII), corner_uniformity: UNIFORMITIES, elevation: ELEVATIONS };
for (const [axis, values] of Object.entries(ENUMS)) {
  for (const value of values) {
    const count = SPECIMENS.filter(s => s[axis as keyof typeof ENUMS] === value).length;
    if (count < 8) throw new Error(`quota violated: ${axis}=${value} has ${count}, need 8`);
  }
}
