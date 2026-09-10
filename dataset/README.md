# BorderBench datasets

## Tailwind Rosetta Stone

Every graded label maps to Tailwind CSS utilities (v3 scale). Names stay
benchmark-local; the utilities are the external reference designers know.

| BorderBench label | Tailwind equivalent |
| --- | --- |
| `0px` / `1px` / `2px` / `4px` / `8px` | `border-0` / `border` / `border-2` / `border-4` / `border-8` |
| `solid` / `dashed` / `dotted` / `none` | `border-solid` / `border-dashed` / `border-dotted` / `border-none` |
| `all-4` / `bottom-only` / `left-only` / `top-only` / `none` | `border` / `border-b` / `border-l` / `border-t` / `border-0` |
| `sharp` 0 / `subtle` 3 / `medium` 8 / `large` 18 / `pill` 9999 | `rounded-none` / between `rounded-sm` 2 and `rounded` 4 / `rounded-lg` 8 / near `rounded-2xl` 16 / `rounded-full` |
| `all-corners` / `top-only` / `asymmetric` | uniform rounding / `rounded-t-*` modal sheet / brand accent |
| `none` | flat, no shadow |
| `subtle-drop` | `shadow` (v3 default stack, exact) |
| `floating-drop` | `shadow-lg` (exact) |
| `ring-only` | near `ring-1` in neutral (our stack stays neutral gray) |
| `stroke+shadow` | `border` + `shadow-md` (exact) |

Frozen elevation stacks (`rgba` spells Tailwind's `rgb(0 0 0 / ...)`):

- `subtle-drop`: `0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)`
- `floating-drop`: `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)`
- `ring-only`: `0 0 0 1px rgba(0, 0, 0, 0.12)`
- `stroke+shadow`: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)`

Fixed context on every image: system font stack, title 16px semibold,
subtitle 12px, body 13px, meta 11px; 40px pill avatar, 6px badge and
button corners, 6px status dot. Inner content is identical and carries
no signal.

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
