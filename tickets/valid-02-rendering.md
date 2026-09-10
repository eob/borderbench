# valid-02-rendering: Neutral cards and verified rendered styles

- **Status**: Completed
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Every graded label must be judged from border/corner/shadow pixels only, and
every image must carry measured evidence that the declared CSS actually
rendered. Preserve historical runs as audit evidence.

## Findings (base `bd5523a`, all reproduced)

| # | Finding | Evidence |
| --- | --- | --- |
| R1 | Card text reveals answers inside the image | `src/render.ts` renders title/subtitle/tag/token/theme/id, e.g. `Stroke Width 8px`, `Theme: dark-mode`, `Token: borderbench-001`; avatar shows id digits |
| R2 | Inner footer divider is a distractor border | `.footer { border-top: 1px solid ... }` varies by theme inside the judged card |
| R3 | Declared CSS never verified | No computed-style readback; `double` at 4px, `dashed`/`dotted`, `ring-only` vs 1px border never checked; no browser version recorded |
| R4 | Manifest carries absolute paths | `imagePath: /mnt/disks/data/borderbench/...` breaks every other checkout |
| R5 | Render overwrites in place | No staging, no stale-PNG cleanup, no image hashes, failure leaves mixed output |

## Plan

1. Red: tests asserting neutral card HTML (no label/token/theme text), computed-style verification, relative paths, staged writes.
2. Replace card copy with fixed neutral content; remove footer divider border; keep inner badge/button/avatar geometry constant across specimens.
3. Read back computed border widths/styles/radii/shadows and card bounds per specimen; record image SHA-256, browser version, geometry in manifest.
4. Relative `imagePath`; atomic staged replacement with stale managed-PNG removal.
5. Base-code reversion controls; offline re-render determinism check.

## Acceptance

- No specimen string in `src/specimens.ts` labels appears in its card HTML.
- Manifest validates with zero errors under the valid-06 gate.
- Re-render reproduces all PNG hashes byte-identically (same browser).

## Completion

Neutral fixed card copy/chrome, footer divider removed, computed-style verification, image hashes, relative paths, staged atomic writes.
