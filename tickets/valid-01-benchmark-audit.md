# valid-01-benchmark-audit: Validate BorderBench before final runs

- **Status**: In Progress
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **PR**: Pending
- **Assignee**: Edward Benson

## Goal

Audit rendered pixels, label observability, experimental design, grading,
provenance, and reporting against the FontBench validity program. Repair
proven defects and freeze a reproducibly validated dataset before any new
paid evaluation. No live model inference in this audit.

## Context & Requirements

- FontBench reference: `../fontbench/tickets/` (valid-01..06, release-01..03),
  whose repairs (multiline observability, native-face verification, strict
  grading, opaque Harbor tasks, frozen releases) are the standard.
- BorderBench base `bd5523a`: 120 images, 5 paid models ($2.01), permissive
  grading, answer-bearing card text, no validator, no release identity.
- Preserve paid history: committed root scorecards stay in Git; the gitignored
  `results/runs/default/` checkpoint ($2.01, 600 observations) is copied to a
  tracked historical directory before any regeneration.

## Plan and ownership

1. Establish baseline gates (43 Python + 3 Bun tests green at `bd5523a`).
2. Record Red evidence per defect class with isolated base-code controls.
3. Repair rendering (valid-02), design (valid-05), evaluation (valid-03),
   reporting (valid-04), and gate (valid-06); regenerate candidates.
4. Freeze the accepted corpus, add versioned runs (release-01..03), CI gate.
5. Combined verification: full suites, offline resume, page build, gate matrix.

## Handoff & Takeover Log

- `2026-09-10`: Started by `muse` on `eob-dev2` (Session `01a08932-89e6-7782-b859-de207f01941f`).

## Decisions and durable findings

- Card text is the critical leak: titles, subtitles, tags, token IDs, and
  theme labels are rendered inside the judged image. Neutral fixed content.
- Old scores are invalid and stay historical; V1.0.0 starts with zero
  measurements. Changed pixels/labels/prompts/grading require a new release.
- 120-image scale is kept (cheap reruns); balance is fixed by quotas, not
  growth. Minimum 8 samples per graded label value.

## Validation gate matrix

Pending. Target: full Python + Bun suites, TypeScript typecheck, frozen
validator exit 0, offline mock run + resume with zero spend, page build with
desktop/mobile checks, base-code reversion evidence per ticket.
