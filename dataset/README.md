# BorderBench datasets

## Current release: `borderbench-v1` (120 images)

The V1.0.0 corpus. Every card carries fixed neutral text; models must judge
border, corner, and shadow pixels only. Each manifest task records the image
SHA-256, the Chromium computed styles that were verified at render time
(border widths/styles, corner radii, box-shadow), the card box, and the
browser version.

```bash
bun run validate:dataset
```

The gate decodes every PNG with Pillow and checks dimensions, hashes,
duplicates, label/enum conformance, prompt identity, evidence consistency,
per-label quotas (minimum 8 samples per graded value), and a measurable
card boundary on every image. Re-rendering reproduces byte-identical PNGs
on the same browser and platform; system font rendering may differ
elsewhere, so the committed bytes are the benchmark, not the generator.

Validate a development candidate the same way:

```bash
bun run render
bun run validate:candidate
```

`bun run render` writes to `dataset/candidate-rendered/` (gitignored) and
refuses registered release directories and historical paths. Freezing a
candidate as a new release means validating it, moving it to a new
`dataset/` directory, and registering a new descriptor under `releases/`.

## Historical prototype (invalid, preserved)

`dataset/borderbench-1/manifest.json` + `dataset/rendered/` (120 images) is
the September 2026 prototype. Its card text reveals the answers ("Stroke
Width 8px", "Theme: dark-mode"), rare classes have single samples
(`asymmetric=1`, `floating-drop=1`), and its manifest carries absolute
image paths. It fails the release gate and must not be compared with
V1.0.0. The files stay in Git history and in the worktree as audit
evidence; the renderer refuses to overwrite them.
