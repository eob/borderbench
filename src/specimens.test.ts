import { describe, expect, test } from "bun:test";
import { SPECIMENS } from "./specimens.ts";

describe("BorderBench Specimens", () => {
  test("generates exactly 120 specimens", () => {
    expect(SPECIMENS.length).toBe(120);
  });

  test("unique specimen IDs", () => {
    const ids = new Set(SPECIMENS.map((s) => s.id));
    expect(ids.size).toBe(120);
  });

  test("valid attributes across all specimens", () => {
    for (const s of SPECIMENS) {
      expect(typeof s.has_border).toBe("boolean");
      expect(["all-4", "bottom-only", "left-only", "top-only", "none"]).toContain(s.border_sides);
      expect(["solid", "dashed", "dotted", "double", "none"]).toContain(s.stroke_style);
      expect(["0px", "1px", "2px", "4px", "8px"]).toContain(s.stroke_width);
      expect(["sharp", "subtle", "medium", "large", "pill"]).toContain(s.corner_radius);
      expect(["all-corners", "top-only", "asymmetric"]).toContain(s.corner_uniformity);
      expect(["none", "subtle-drop", "floating-drop", "ring-only", "stroke+shadow"]).toContain(s.elevation);
    }
  });
});
