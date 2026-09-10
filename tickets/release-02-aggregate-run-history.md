# release-02-aggregate-run-history: Combine compatible runs honestly

- **Status**: Completed
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Build the benchmark page from accumulated versioned runs with explicit
cohorts and origins. Retire the unversioned exporter's implicit overwrite.
Mirrors FontBench release-02.

## Findings (base `bd5523a`)

- `baseline/export_structured.py` globs all scorecards, picks latest-mtime per
  model (score shopping), and requires no matching dataset/protocol/cohort.
- No page builder; `site/` holds one SVG with no provenance, completeness, or
  shared-cohort accounting.

## Plan

1. Red: mixed-protocol exclusion, mock exclusion, duplicate observation
   first-wins (no score replacement), partial-coverage display, malformed-row
   warnings preserving peers.
2. Add `baseline/build_page.py`: discover `results/runs/1.0.0/*/`, require
   matching release/dataset/protocol, first-recorded-observation wins with
   deterministic ties, retain repeat costs; emit `site/index.html` +
   `site/benchmark.json` with release identity, gate status, per-model
   completion, shared-cohort tables, all 7 dims + exact match.
3. CLI-ify legacy exporter as explicitly unversioned (explicit in/out paths).
4. Desktop + mobile Chromium checks: loads, no JS errors, no overflow.

## Acceptance

- Rebuilt page over zero V1.0.0 runs shows the corpus with empty leaderboard.
- Aggregation regressions fail on base exporter behavior, pass on builder.

## Completion

Page builder aggregates compatible runs first-wins with deterministic ties, shared cohorts, breakdowns, contact sheets.
