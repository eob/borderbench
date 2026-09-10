import { describe, expect, test } from "bun:test";
import { generateCardHtml } from "./render.ts";
import type { BackgroundTheme, BorderSpecimenConfig, Elevation } from "./types.ts";

function specimen(elevation: Elevation): BorderSpecimenConfig {
  const bordered = elevation === "none" || elevation === "stroke+shadow";
  return {
    id: "probe",
    has_border: bordered,
    border_sides: bordered ? "all-4" : "none",
    stroke_style: bordered ? "solid" : "none",
    stroke_width: bordered ? "1px" : "0px",
    stroke_width_px: bordered ? 1 : 0,
    corner_radius: "medium",
    corner_radius_px: 8,
    corner_uniformity: "all-corners",
    elevation,
    theme: "white-on-gray" as BackgroundTheme,
    title: "Container Specimen",
    subtitle: "Surface and edge sample",
    tag: "Sample",
  };
}

describe("elevation shadow tokens", () => {
  const stacks: [Elevation, string][] = [
    ["none", "box-shadow: none"],
    ["subtle-drop", "box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"],
    ["floating-drop", "box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"],
    ["ring-only", "box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.12)"],
    ["stroke+shadow", "box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"],
  ];
  for (const [elevation, stack] of stacks) {
    test(`${elevation} renders its frozen token stack`, () => {
      expect(generateCardHtml(specimen(elevation))).toContain(stack);
    });
  }
});
