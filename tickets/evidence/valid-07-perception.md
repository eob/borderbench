# Perceptual design evidence (2026-09-12)

Baseline: existing V1.1 corpus and working tree before the V1.2 implementation.
Controlled browser: Chromium 153.0.8010.12, Linux, 560×360 CSS viewport,
DPR 2. Fifteen controlled baseline renders matched the frozen PNG pixels exactly.

The width sweep moved the inner header from x=104,y=84 CSS px at width 0 to
x=112,y=92 at width 8; its width changed from 352 to 336 CSS px. This made
inner layout a side channel for border width and active edges. The new renderer
positions a fixed reference independently of the border box, with a byte-equal
PNG crop test covering 1→8 px, partial sides, dotted style, capsule corners,
and floating shadow.

The three subtle asymmetric examples (038, 041, 044) used radii [3,3,3,2].
Changing them to [3,3,3,3] affected only 20 physical pixels inside a 6×6 box.
New asymmetric examples use three 12px or 24px corners and one sharp corner.

Dark-mode examples 058, 065, 091, 096, 100, 118 had maximum luminance differences
of only 2–3/255 when their shadows were disabled. The old strongest-boundary
contrast check did not test shadow visibility. New candidates use three light
themes and link every shadow image to its matched flat input for independent
pixel validation of the actual shadow signal.

## Red evidence

Command: `bun test src/perception-design.test.ts` before implementation.

```text
error: expect(received).toBe(expected)
Expected: 4
Received: 3
(fail) perceptually identifiable design > radii use coarse exact Tailwind tokens and nonuniform corners differ visibly

error: expect(received).toEqual(expected)
Expected: nine theme/elevation combinations per geometry
Received: ["dark-mode:none", "white-on-gray:none"]
(fail) perceptually identifiable design > every geometry has all shadow levels in every light theme

error: expect(received).toBe(expected)
Expected: true
Received: false
(fail) perceptually identifiable design > inner reference pixels remain fixed across widths, sides, styles, radii, shadows

0 pass
3 fail
4 expect() calls
Ran 3 tests across 1 file.
```

## Decisions and durable findings

The candidate has 53 unique border/corner geometries, each crossed with all
three shadow levels and all three themes: 477 inputs. Recipe metadata retains
controlled width, style, sides, radius, uniformity, and elevation blocks;
mixed cases broaden the conditions. This is a matched design, not an exhaustive
factorial of every boundary property. Presence is redundant with three other
fields and score interpretation must acknowledge that dependence. Class counts
are unequal, so macro and conditional metrics should accompany exact match.

Radius labels map to frozen Tailwind v3 tokens 0,4,12,24,9999 CSS px. Shadows
use exact default `shadow` and `shadow-lg` stacks independent of stroke presence.
The ambiguous source-implementation `ring-only` and composite `stroke+shadow`
labels are removed from the current protocol. Historical release bytes remain
preserved.

The reference uses unmodified DejaVu Sans with its redistribution notice.
SHA-256: `abdc775b21b1bc470d50c97e790d276f2054b7504e56e5bd3e64f48d68582322`.
The renderer embeds the binary, waits for fonts, verifies Chromium's actual
custom font with CDP, and records 16px font size,24px line height,64px rule.

Controlled ablations and raw geometry from the initial audit are available
locally in `/tmp/borderbench-perception-audit/`; the regression tests and
frozen candidate evidence are the durable checks.

## Green, reversion, and image review

Base Git commit: `077578b121561fb657cb7fc58fd1940b9a0e7b57`.

| Gate | Result |
| --- | --- |
| `bun run test:ts` | 21 passed, 0 failed; 5,631 assertions, including Chromium reference-crop invariance and matched block controls |
| `bun run typecheck` | passed |
| Isolated original-source reversion | all three original failures reproduced, including the same 4-vs-3 radius and false-vs-true PNG equality signatures; full output in `valid-07-perception-reversion.txt` |
| `bun run render` | 477/477; successful second render into an existing candidate directory |

Across all 477 first-candidate PNGs, shadow-versus-flat exterior differences had
maximum luminance deltas 26–27/255 for subtle and 32/255 for floating. At least
3,525 and 17,564 exterior physical pixels, respectively, differed by at least
3 levels. Flat controls had zero difference. The central 240×96 CSS reference
crop had exactly three unique pixel patterns across the entire corpus, one per
theme, confirming the absence of border/corner/shadow content-layout cues.

The final gray-tint palette was strengthened to card `#e2e8f0`, border
`#94a3b8`, white canvas, avoiding the previous pale 5/255 surface step. Every
image was rerendered after this change. Final candidate manifest SHA-256:
`0399662ed2091d71dd6ef66a60a7cd79f6abd9b336591db88110c8633c35bb78`.
The image content and labels were visually inspected for a heavy dotted full
stroke, borderless capsule, borderless asymmetric shadow, and heavy partial
left stroke; reference text remains fully visible and unclipped.
