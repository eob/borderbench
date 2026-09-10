# valid-05-experimental-design: Balanced coverage and disclosed limits

- **Status**: Planned
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Every reported accuracy must rest on enough samples, every graded label must
be observable in pixels, and every design limit must be documented. Keep the
120-image scale; fix balance with quotas, not growth.

## Findings (base `bd5523a`, 120 tasks)

| # | Finding | Evidence |
| --- | --- | --- |
| D1 | Single-sample classes | `asymmetric=1`, `floating-drop=1`, `double=4`, `8px=4`, `ring-only=4`, `top-only` uniformity=10; `has_border` 92/28; `elevation=none` 78/120 |
| D2 | Unobservable labels | `white-on-white` + borderless + flat = invisible card, yet `corner_radius`/`corner_uniformity` still graded; no observability requirement (FontBench single-line analog) |
| D3 | Inconsistent px mapping | `large` renders 18px but uniformity variants use 16px; prompt ranges documented but mapping undisclosed |
| D4 | Label dependencies undisclosed | `has_border` ⟺ sides ⟺ style ⟺ width (presence weighed 4× in exact match); `stroke+shadow` ⟹ `has_border`; uniformity degenerate for `sharp`/`pill` |
| D5 | Schema/docs mismatch | Prompt says "6 design attributes" for 7 fields; README lists 6 dims then 7 items; `theme` in groundTruth but unscored and unexplained |
| D6 | No shortcut baselines | Tag/title text predicts labels ~100% (R1 leak); no majority-class or theme-only baseline reported |
| D7 | Ad-hoc random composites | Seed-42 sampling with no recipe catalog, quotas, or skipped census |

## Plan

1. Red: per-label minimum counts, observability (edge-contrast) gate, mapping consistency, shortcut-baseline report.
2. Quota-driven recipes: every graded value ≥8 samples with crossed factors; forbid invisible combinations (require visible boundary: border, shadow, or tonal step above threshold).
3. Unify `large`→18px (uniformity variants `[18,18,0,0]`, `[18,18,18,2]`); freeze mapping table in README + prompt.
4. Document dependencies, unscored `theme` condition, fixed inner distractors; correct counts to 7 fields.
5. Publish majority-class and theme-only shortcut baselines from the frozen corpus.

## Acceptance

- Frozen corpus: all graded values ≥8; zero invisible-boundary images; baselines disclosed.
- Conditional correlations that remain are documented as accepted limits.
