# valid-04-packaging-reporting: Honest measurements and reports

- **Status**: Completed
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Publish scores only with consistent dataset, grading, and cohort provenance.
BorderBench has no Harbor package (explicit non-goal for V1.0.0); this ticket
covers leakage removal verification, export integrity, and reporting honesty.

## Findings (base `bd5523a`)

| # | Finding | Evidence |
| --- | --- | --- |
| P1 | Published scores measured leaked answers | R1 card text; root `results/scorecard_*.json` + README table present them as valid |
| P2 | Paid checkpoint is gitignored and stranded | `.gitignore` excludes `results/runs/`; `state.sqlite3` ($2.01, 600 obs) unresumable from a fresh checkout |
| P3 | Export invents costs and shops scorecards | `build_structured_benchmark` estimates cost from fixed 600/60 tokens, hardcodes totals, trusts aggregate fields, picks latest-mtime scorecard per model |
| P4 | Selective reporting | README table shows 4 of 7 graded dims; 5-of-11 model coverage undisclosed; no shared-cohort counts |
| P5 | No report builder or malformed-shape guards | `site/` is one SVG; corrupt/unhashable persisted shapes can crash consumers (FontBench valid-04 analog) |

## Plan

1. Red: export cost/trust/mtime-selection, malformed metadata/state crashes, partial-cohort intersection.
2. Preserve history: copy `results/runs/default/` to tracked `results/historical-2026-09-07-default/`; add `results/README.md` + `results/historical.json` classification; keep root scorecards read-only.
3. Derive export metrics, latency, taxonomy, and metered costs from task rows; require matching dataset/protocol/cohort for comparisons; validate shapes with warnings preserving valid peers.
4. Report all 7 dims + exact match; expose completion and shared-cohort counts.
5. Base-code reversion controls; page checks deferred to release-02 builder.

## Acceptance

- Export of the historical run shows metered (not guessed) costs.
- Malformed-shape regressions fail on base, pass after fix.
- No historical score appears in V1.0.0 outputs.

## Completion

History preserved and classified; export derives metered metrics from explicit rows with malformed-row warnings.
