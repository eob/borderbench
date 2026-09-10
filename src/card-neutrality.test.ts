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

  test("footer carries no divider border", () => {
    const html = generateCardHtml(SPECIMENS[0]);
    const css = html.slice(0, html.indexOf("</style>"));
    expect(css).not.toContain("border-top: 1px solid");
  });

  test("inner chrome geometry is constant across specimens", () => {
    const first = generateCardHtml(SPECIMENS[0]);
    const last = generateCardHtml(SPECIMENS[SPECIMENS.length - 1]);
    const chrome = (html: string) => {
      const css = html.slice(0, html.indexOf("</style>"));
      return [...css.matchAll(/\.(avatar|badge|btn|status-dot)\s*\{[^}]*\}/g)].map((m) => m[0]).join("\n");
    };
    expect(chrome(first)).toBe(chrome(last));
  });
});
