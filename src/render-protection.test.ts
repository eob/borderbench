import { describe, expect, test } from "bun:test";
import { refuseProtectedDir } from "./render.ts";

describe("render protection", () => {
  test("refuses historical and registered release directories", () => {
    expect(() => refuseProtectedDir("dataset/rendered", [])).toThrow(/historical/);
    expect(() => refuseProtectedDir("dataset/borderbench-1", [])).toThrow(/historical/);
    expect(() => refuseProtectedDir("dataset/borderbench-v1", ["dataset/borderbench-v1"])).toThrow(/release/);
  });

  test("allows candidate and unregistered directories", () => {
    expect(() => refuseProtectedDir("dataset/candidate-rendered", ["dataset/borderbench-v1"])).not.toThrow();
    expect(() => refuseProtectedDir("dataset/borderbench-v1", [])).not.toThrow();
  });
});
