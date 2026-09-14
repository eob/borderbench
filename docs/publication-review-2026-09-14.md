# Publication review — September 14, 2026

**Decision: publish V1.2.0 as a sealed, partial comparison.** The reviewed
benchmark and archived answers support the reported descriptive scores. This
review found no dataset, answer-leakage, or scoring defect that requires a new
release or another paid campaign. It repaired missing interpretation and data
links in the generated standalone report, then regenerated that report from
archived predictions.

Review base: `07ee683`. Dataset commit:
`b8c3a6b84bc250b3a22739bfec5e4fed47bbcffc`. Reviewed campaign:
[`2026-09-12-first-campaign`](../results/runs/1.2.0/2026-09-12-first-campaign/README.md).
The independent [replay script](../tickets/evidence/publication-review-2026-09-14.py)
imports no benchmark evaluator, parser, or statistics code. Its
[machine-readable evidence](../tickets/evidence/publication-review-2026-09-14.json)
records the reproduced counts and costs.

## Dataset, rendering, and labels

- Regenerated all **477 images** into the separate candidate directory. All
  477 PNG files and decoded pixel arrays match the frozen corpus byte for byte;
  prompts, ground truth, and matched-block membership also match. No frozen
  dataset, release descriptor, or source run was modified.
- The design contains **53 distinct geometries × 3 themes × 3 shadows**. Each
  geometry appears exactly once in every theme/shadow combination. This removes
  theme-to-label and shadow-to-geometry shortcuts in the full release.
- All 477 decoded images are distinct. PNG files carry no metadata fields.
  The inner reference crop is byte-identical for all 159 images within each
  theme. Browser regression tests independently check geometry, fixed content,
  font use, stroke tokens, and controlled comparisons.
- Reviewed the 53-geometry contact sheet and renderer/validator paths for
  widths, styles, partial edges, capsule clamping, nonuniform corners, shadow
  controls, and scale references. The all-image gate checks the computed CSS,
  pixel evidence, canonical labels, contrast and paired shadows, image and font
  hashes, declared class coverage, and recipe catalog.
- Provider construction sends the same prompt and image bytes for every task.
  It does not send task IDs, filenames, manifest ground truth, or recipe text.
  BorderBench has no multiple-choice candidate array whose sorting could reveal
  an answer; category enums and definitions are constant across all requests.

## Sampling, scoring, and provenance

The independent audit reparsed every raw model answer, compared it directly with
the frozen manifest, and reproduced all **1,664 responses**. Every exact-match
flag and every attribute flag agrees with the publication. It also recomputed
all class recalls, confusion matrices, observed-class balanced accuracies,
majority baselines, border-present diagnostics, all group breakdowns, and all
matched-block diagnostics. All agree, including empty-group nulls.

All 13 configurations observed the same **128 task IDs**. They exactly match the
first 128 IDs after sorting the full corpus and applying `random.Random(0)`.
There are no duplicate model/task observations, malformed final answers,
infrastructure failures, hidden retries, or unmetered attempts in this campaign.
Each published result matches its source attempt. The finalizer independently
passes SQLite integrity, ledger/export equivalence, release identity, raw-answer
grading, chronology, committed-source checks, and publication hashes.

Decimal arithmetic reproduces the dated token-rate estimate exactly:
**$21.27932190**. This is recorded usage multiplied by catalog prices, not an
invoice or a promise of current pricing. The live runner's reservations and
shared spending guard, final-answer retention, resume isolation, interruption
handling, and strict schema enforcement remain covered by the existing suite.

The generated site reproduces the seal's shared cohort and every published
metric, diagnostic, and matched block for all 13 configurations. It reports
zero excluded runs and zero warnings. An offline three-image smoke run and
resume produce three attempts total across two invocations, without repeating
already final answers or contacting a provider.

## Interpretation that must remain visible

The sample is **128/477 images**, with 52/53 geometry recipes. It has seven 1px
examples and eight top-only corner examples. Only two complete shadow blocks
and two complete style blocks are present; other controlled dimensions have no
complete blocks. Full-corpus independence does not imply exact balance in this
random subset. Category frequencies, conditional scores, and missing coverage
must accompany aggregate accuracy.

GPT-6 Astra's 128/128 exact matches establish an observed ceiling on this sample.
They do not establish perfect performance on the remaining 349 images. Muse
Spark 1.3 chose half the correct width in all 25 width mistakes. Claude Fable
5.1 labeled 30/43 subtle shadows as absent. Haiku always predicted uniform
corners: 107/128 aggregate accuracy, but 0/21 on nonuniform corners. These are
descriptive error patterns; the data do not establish their causes.

Human category agreement remains unmeasured. The corpus is synthetic and fixes
layout, text, font, browser, and device pixel ratio; it omits dark themes,
right-only and two-edge borders, double borders, and inset or colored shadows.
Three theme repeats are correlated geometry observations. The design is not a
full factorial and remaining geometry correlations limit isolated causal
interpretation. No population interval or significance claim follows from
these fixed-corpus scores.

The campaign records requested model identifiers, provider settings, raw answer
text, usage, timestamps, and source code identity. It does not preserve a
provider-signed identity attestation or complete HTTP response envelope.
Provider defaults, image processing, and mutable model aliases limit remote
reproducibility; the comparison measures each recorded configuration's complete
vision-and-response pipeline.

## Reporting repair

Before the change, inspection of `site/index.html` produced:

```text
structured results link: FAIL (absent from generated report)
human agreement limitation: FAIL (absent from generated report)
synthetic scope limitation: FAIL (absent from generated report)
```

The report now explains exact match, dependent absence labels, invalid answers,
shared sample coverage, class imbalance, repeated geometries, and synthetic and
human-agreement limits. It links structured diagnostics, methodology, dataset
and reproduction instructions, and the available sealed results and seal.
These reporting changes do not alter the frozen protocol or any scores.

## Validation gates

All gates ran on `07ee683` plus the reporting and review changes unless stated.

| Gate | Outcome |
| --- | --- |
| Baseline and final `bun run test` | 194 Python tests; 21 TypeScript/browser tests; 5,631 assertions; typecheck passed |
| `bun run validate:release` | All 477 frozen inputs valid |
| `bun run render`, all-image comparison, `bun run validate:candidate` | All 477 candidate PNGs identical; candidate gate valid |
| Independent replay script | All 1,664 responses, all subgroup diagnostics and blocks, all costs agree |
| `python -m baseline.finalize --run-dir results/runs/1.2.0/2026-09-12-first-campaign --verify` | Publication seal and committed sources verified |
| `bun run build:page --release 1.2.0` and seal comparison | 13 configurations, 128 shared images, no excluded runs or warnings, identical published metrics |
| Chromium at 360px and 1280px | No horizontal page overflow, broken images, or JavaScript errors; data/seal links and human-agreement limitation present |
| Offline smoke/resume | Three final attempts across two invocations, $0 |
| `python scripts/check_frozen_artifacts.py --base origin/main` | Six prior frozen descriptor/dataset paths unchanged |
| `python -m pip wheel . --no-deps` | V1.2.0 wheel built |
| `git diff --check` | Passed |

The simplification and comment-hygiene pass retained a small reporting change
and kept independent audit logic in review evidence. The historical scores and
earlier invalid answer-leaking prototype remain explicitly distinguished from
V1.2.0. No paid measurements were repeated because the stimulus and scoring
contracts passed this review unchanged.
