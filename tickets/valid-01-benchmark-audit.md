# valid-01-benchmark-audit: Validate BorderBench before final runs

- **Status**: Completed
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **PR**: https://github.com/eob/borderbench/pull/1
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

## Findings and repaired behavior

| Area | Original evidence | Accepted correction |
| --- | --- | --- |
| Pixel/label validity | Card titles, subtitles, tags, token IDs, and theme labels rendered inside the judged image (e.g. `Stroke Width 8px`); inner footer divider border | Fixed neutral copy and chrome on all 120 images; divider removed; computed border/corner/shadow styles verified per specimen |
| Identity/portability | Absolute `/mnt/disks/data/...` image paths; no hashes, no browser provenance | Relative paths resolved beside the manifest; SHA-256 per image; browser/platform/card geometry recorded |
| Experimental design | `asymmetric=1`, `floating-drop=1`, `double=4`, `8px=4`; invisible white-on-white flat cards; `large` mapped to 18px and 16px | Every graded value sampled 9+ times; invisible combinations forbidden by a measured boundary-contrast gate (4x margin); unified mappings |
| Evaluation | Extra keys ignored, duplicate keys resolved, missing/blank/invalid enums earn partial credit; hardcoded grading marker; no protocol identity | Strict whole-answer schema at provider and evaluator boundaries; shared frozen prompt; protocol fingerprint with resume guards |
| Checkpoints | Foreign task IDs completable by count; protocol changes mix silently; no status/cohort/invalid accounting | Foreign IDs rejected; protocol mismatch rejected; scorecards carry status, cohort hash, invalid counts |
| Reporting | Export guessed costs from fixed tokens, hardcoded totals, latest-mtime score shopping; README showed 4 of 7 dims | Export derives metered metrics from explicit task rows with warnings; page aggregates first-wins observations with shared cohorts |
| Release process | Unversioned `default` run, gitignored checkpoint, no descriptor, no CI | `releases/1.0.0.json` with Git anchor, versioned run ledgers, frozen-dir protection, candidate isolation, CI gate |

## Release artifacts

- `dataset/borderbench-v1/manifest.json`: 120 accepted inputs, relative paths, shared prompt, image hashes, rendering evidence.
- `dataset/borderbench-v1/validation.json`: complete gate report; zero errors, 120 unique decoded images, quotas met, theme carries no shortcut.
- `releases/1.0.0.json` + `CHANGELOG.md`: version identity, dataset commit `11adacb`, content/protocol fingerprints.
- `results/historical-2026-09-07-default/`: preserved paid pilot ($2.01, 600 obs) with checkpoint; classified invalid in `results/historical.json`.
- `site/index.html` + `site/benchmark.json`: validated empty leaderboard with six breakdowns and contact sheets; no inherited scores.

## Validation gate matrix

Base `bd5523a`; implementation on `valid-01-benchmark-audit`.

| Gate | Result |
| --- | --- |
| Baseline suites before changes | 43 Python, 3 Bun passed; existing tests did not detect the validity defects |
| Red evidence | 19 Python + 6 Bun failures, 3 missing-module errors ([python](evidence/red-python.log), [bun](evidence/red-bun.log)) |
| Final Python suite | 79 passed |
| Final Bun suite + typecheck | 13 passed; `tsc --noEmit` clean |
| Frozen dataset gate | 120 inputs, 120 unique pixels, zero errors; historical manifest rejected |
| Offline release run + resume | 3 then 117 attempts, zero duplicates, $0 spend; SQLite integrity ok; 2 invocations |
| Page build + Chromium desktop/mobile | 0 JS errors, 0 overflow, 48 montage images, 7 tables on both layouts |
| Wheel build | `borderbench-1.0.0` wheel contains prompt, validator, releases, builder, reporting |
| Isolated base-code reversions | Python: 20 failed + 1 control passed + validator import error; Bun: 6 failed + 2 errors ([python](evidence/reversion-python.log), [bun](evidence/reversion-bun.log)) |
| Render protection | Registered release and historical dirs refused with zero bytes changed; candidate flow renders + validates |
| Historical preservation | `git diff --quiet bd5523a -- dataset/borderbench-1 dataset/rendered results/scorecard_gemini-3.1-pro-preview.json` passed |

## Review and limitations

Theme is an unscored contrast condition; presence spans four coordinated
fields; uniformity variants and shadow-only pale cards are documented
special cases. The corpus favors cheap full reruns over exhaustive
coverage. No paid model inference or publication was performed.

Merged to main as `64c5ca6` via PR #1 (merge commit; dataset commit
`11adacb` is an ancestor of main). Release tooling tagged `v1.0.0`.
