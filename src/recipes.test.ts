import { describe, expect, test } from "bun:test";
import { SPECIMENS } from "./specimens.ts";

const MIN_PER_LABEL = 8;

function counts(key: (s: (typeof SPECIMENS)[number]) => string): Map<string, number> {
  const map = new Map<string, number>();
  for (const s of SPECIMENS) {
    const value = key(s);
    map.set(value, (map.get(value) ?? 0) + 1);
  }
  return map;
}

describe("BorderBench recipes", () => {
  test("every graded label value meets the minimum sample quota", () => {
    const axes = {
      border_sides: counts((s) => s.border_sides),
      stroke_style: counts((s) => s.stroke_style),
      stroke_width: counts((s) => s.stroke_width),
      corner_radius: counts((s) => s.corner_radius),
      corner_uniformity: counts((s) => s.corner_uniformity),
      elevation: counts((s) => s.elevation),
    };
    for (const [axis, axisCounts] of Object.entries(axes)) {
      for (const [value, count] of axisCounts) {
        expect(`${axis}=${value}: ${count}`).toBe(`${axis}=${value}: ${count >= MIN_PER_LABEL ? count : `ONLY ${count}, need ${MIN_PER_LABEL}`}`);
      }
    }
  });

  test("no invisible-boundary combinations", () => {
    // A borderless flat card on white-on-white has no visible boundary at all.
    // ring-only is a rendered 1px outline and stays visible; the pixel-contrast
    // gate verifies every boundary independently.
    const invisible = SPECIMENS.filter(
      (s) => s.theme === "white-on-white" && !s.has_border && s.elevation === "none",
    );
    expect(invisible.map((s) => s.id)).toEqual([]);
  });

  test("large radius maps to one pixel value", () => {
    for (const s of SPECIMENS.filter((s) => s.corner_radius === "large")) {
      if (!Array.isArray(s.corner_radius_px)) {
        expect(s.corner_radius_px).toBe(24);
      } else if (s.corner_uniformity === "asymmetric") {
        // Three rounded corners carry the label; the accent corner is sharp by design.
        expect([...s.corner_radius_px].sort((a, b) => a - b)).toEqual([0, 24, 24, 24]);
      } else {
        expect(s.corner_radius_px.filter((v) => v > 0).every((v) => v === 24)).toBe(true);
      }
    }
  });

  test("card copy carries no label text", () => {
    const labels = new Set([
      "all-4", "bottom-only", "left-only", "top-only", "none",
      "solid", "dashed", "dotted", "double",
      "0px", "1px", "2px", "4px", "8px",
      "sharp", "subtle", "medium", "large", "pill",
      "all-corners", "asymmetric",
      "subtle-drop", "floating-drop", "ring-only", "stroke+shadow",
      "white-on-gray", "white-on-white", "gray-tint-on-white", "blue-tint-on-white", "dark-mode",
      "curvature", "thickness", "pattern", "sides", "uniformity", "elevation", "contrast", "composite",
      "border", "radius", "shadow", "stroke",
    ]);
    const leaked: string[] = [];
    for (const s of SPECIMENS) {
      const tokens = `${s.title} ${s.subtitle} ${s.tag}`.toLowerCase().split(/[^a-z0-9+.-]+/);
      for (const token of tokens) {
        if (labels.has(token)) leaked.push(`${s.id}: ${token}`);
      }
    }
    expect(leaked).toEqual([]);
  });
});
