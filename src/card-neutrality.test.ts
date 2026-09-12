import { describe, expect, test } from "bun:test";
import { generateCardHtml } from "./render.ts";
import { SPECIMENS } from "./specimens.ts";

const LABEL_TOKENS = [
  "all-4", "bottom-only", "left-only", "top-only",
  "solid", "dashed", "dotted", "double",
  "0px", "1px", "2px", "4px", "8px",
  "sharp", "subtle", "medium", "large", "pill",
  "all-corners", "top-only", "asymmetric",
  "subtle-drop", "floating-drop", "ring-only", "stroke+shadow",
  "white-on-gray", "white-on-white", "gray-tint-on-white", "blue-tint-on-white", "dark-mode",
];

describe("card neutrality", () => {
  test("rendered card text reveals no labels, tokens, or themes", () => {
    const leaked: string[] = [];
    for (const specimen of SPECIMENS) {
      const html = generateCardHtml(specimen);
      const body = html.slice(html.indexOf("<body>"));
      const text = body.replace(/<[^>]*>/g, " ").toLowerCase();
      for (const token of LABEL_TOKENS) {
        if (token === "none") continue;
        if (text.includes(token)) leaked.push(`${specimen.id}: ${token}`);
      }
      if (text.includes(specimen.id)) leaked.push(`${specimen.id}: specimen id in card text`);
    }
    expect(leaked).toEqual([]);
  });

  test("reference text and markup are identical on every specimen", () => {
    const body = (html: string) => html.slice(html.indexOf("<body>"));
    const expected = body(generateCardHtml(SPECIMENS[0]));
    for (const specimen of SPECIMENS) expect(body(generateCardHtml(specimen))).toBe(expected);
  });
});
