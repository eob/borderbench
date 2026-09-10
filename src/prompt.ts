import * as fs from "node:fs";
import * as path from "node:path";

export const PROMPT_TEXT: string = fs
  .readFileSync(path.resolve("baseline/prompt.txt"), "utf-8")
  .trim();
