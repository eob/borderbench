import { describe, expect, test } from "bun:test";
import { chromium } from "playwright";
import { SPECIMENS } from "./specimens.ts";
import { generateCardHtml } from "./render.ts";

describe("perceptually identifiable design", () => {
  test("radii use coarse exact Tailwind tokens and nonuniform corners differ visibly", () => {
    const px = { sharp: 0, subtle: 4, medium: 12, large: 24, pill: 9999 };
    for (const s of SPECIMENS) {
      if (s.corner_uniformity === "all-corners") expect(s.corner_radius_px).toBe(px[s.corner_radius]);
      else {
        expect(["medium", "large"]).toContain(s.corner_radius);
        expect(s.corner_radius_px).toEqual(s.corner_uniformity === "top-only"
          ? [px[s.corner_radius], px[s.corner_radius], 0, 0]
          : [px[s.corner_radius], px[s.corner_radius], px[s.corner_radius], 0]);
      }
    }
  });

  test("every geometry has all shadow levels in every light theme", () => {
    const groups = new Map<string, Set<string>>();
    for (const s of SPECIMENS) {
      const key = JSON.stringify([s.border_sides, s.stroke_style, s.stroke_width, s.corner_radius, s.corner_uniformity]);
      if (!groups.has(key)) groups.set(key, new Set());
      groups.get(key)!.add(`${s.theme}:${s.elevation}`);
    }
    const expected = ["white-on-gray", "gray-tint-on-white", "blue-tint-on-white"].flatMap(t =>
      ["none", "subtle-drop", "floating-drop"].map(e => `${t}:${e}`)).sort();
    for (const levels of groups.values()) expect([...levels].sort()).toEqual(expected);
  });

  test("matched blocks change only their declared perceptual dimension", () => {
    const groups = new Map<string, typeof SPECIMENS>();
    for (const s of SPECIMENS) {
      expect(s.design?.matchedBlocks.length).toBeGreaterThan(0);
      for (const block of s.design!.matchedBlocks) {
        if (block.axis === "mixed") continue;
        const key = `${block.id}:${s.theme}:${block.axis === "elevation" ? "" : s.elevation}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key)!.push(s);
      }
    }
    for (const specimens of groups.values()) {
      expect(specimens.length).toBeGreaterThan(1);
      const axes = ["border_sides", "stroke_style", "stroke_width", "corner_radius", "corner_uniformity", "elevation"] as const;
      const changed = axes.filter(axis => new Set(specimens.map(s => s[axis])).size > 1);
      const includes = (axis: string) => specimens.every(s => s.design!.matchedBlocks.some(b => b.axis === axis));
      if (changed.includes("corner_radius")) expect(changed).toEqual(["corner_radius"]);
      else if (changed.includes("corner_uniformity")) expect(changed).toEqual(["corner_uniformity"]);
      else if (changed.includes("elevation")) expect(changed).toEqual(["elevation"]);
      else if (changed.includes("border_sides")) expect(includes("stroke_width") || includes("border_sides")).toBe(true);
      else expect(changed).toEqual(["stroke_style"]);
    }
  });

  test("inner reference pixels remain fixed across widths, sides, styles, radii, shadows", async () => {
    const browser = await chromium.launch({ headless: true });
    try {
      const page = await browser.newPage({ viewport: { width: 560, height: 360 }, deviceScaleFactor: 2 });
      const base = SPECIMENS.find(s => s.theme === "white-on-gray" && s.corner_radius === "medium" && s.stroke_width === "1px")!;
      const variants = [base,
        { ...base, stroke_width: "8px" as const, stroke_width_px: 8 },
        { ...base, border_sides: "bottom-only" as const },
        { ...base, stroke_style: "dotted" as const },
        { ...base, corner_radius: "pill" as const, corner_radius_px: 9999 },
        { ...base, elevation: "floating-drop" as const }];
      const crops: Buffer[] = [];
      for (const specimen of variants) {
        await page.setContent(generateCardHtml(specimen));
        await page.evaluate(() => document.fonts.ready);
        crops.push(await page.screenshot({ clip: { x: 160, y: 132, width: 240, height: 96 } }));
      }
      for (const crop of crops.slice(1)) expect(crop.equals(crops[0])).toBe(true);
    } finally { await browser.close(); }
  });
});
