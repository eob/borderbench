import { describe, expect, test } from "bun:test";
import { refuseProtectedDir } from "./render.ts";
import * as renderer from "./render.ts";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

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

test("refuses release ancestors, descendants, and symlink aliases", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "borderbench-protection-"));
  try {
    const frozen = path.join(root, "frozen");
    fs.mkdirSync(frozen);
    fs.symlinkSync(frozen, path.join(root, "alias"));
    fs.symlinkSync(path.join(frozen, "missing"), path.join(root, "dangling"));
    for (const destination of [root, frozen, path.join(frozen, "child"), path.join(root, "alias"), path.join(root, "alias/new"), path.join(root, "dangling/child")]) {
      expect(() => refuseProtectedDir(destination, [frozen])).toThrow();
    }
    expect(() => refuseProtectedDir(path.join(root, "frozen-copy"), [frozen])).not.toThrow();
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("malformed or missing release registry fails closed", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "borderbench-registry-"));
  try {
    expect(() => renderer.releaseDatasetPaths(root)).toThrow();
    fs.mkdirSync(path.join(root, "releases"));
    const file = path.join(root, "releases/1.0.0.json");
    for (const entry of ["{", "{}", '{"dataset_path":"../outside"}', '{"dataset_path":"dataset/frozen"}']) {
      fs.writeFileSync(file, entry);
      expect(() => renderer.releaseDatasetPaths(root)).toThrow();
    }
    fs.writeFileSync(file, JSON.stringify({ dataset_path: "dataset/frozen", dataset_manifest: "dataset/frozen/manifest.json" }));
    expect(renderer.releaseDatasetPaths(root)).toEqual([path.join(root, "dataset/frozen")]);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
