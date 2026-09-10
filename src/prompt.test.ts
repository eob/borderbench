import { describe, expect, test } from "bun:test";
import { PROMPT_TEXT } from "./prompt.ts";
import * as fs from "node:fs";
import * as path from "node:path";

describe("shared prompt", () => {
  test("prompt matches the frozen baseline text and names seven attributes", () => {
    const frozen = fs.readFileSync(path.resolve("baseline/prompt.txt"), "utf-8").trim();
    expect(PROMPT_TEXT.trim()).toBe(frozen);
    expect(PROMPT_TEXT).toContain("7 design attributes");
  });
});
