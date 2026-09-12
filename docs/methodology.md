# BorderBench V1.2.0 methodology

## Intended inference

This benchmark measures whether a vision-language model can assign coarse,
explicitly defined web design categories to a rendered card. It measures joint
visual recognition, scale interpretation, and adherence to a JSON response
contract. It does not recover arbitrary CSS source or establish perception
independently of language knowledge.

The source baseline for this audit is BorderBench `077578b` and FontBench
`14b09c3ad89e5b587c19abee5b66978968252f85` (2026-09-12). The implemented repairs and
checks are recorded in [valid-07](../tickets/valid-07-perceptual-rigor.md).

## Quantization and reference frame

The target categories are sampled prototypes, not bins inferred from arbitrary
continuous values. There are no hidden midpoint decisions: every width and
radius is rendered at its stated anchor. Tailwind **3.4.17** is pinned because
utility naming and defaults can change between versions. Numeric radius values
assume a 16px root font size. The 0/4/12/24/full radius set avoids crowded 2/3/4px
or 16/18px distinctions. Widths double from 1px through 8px.

The official [border width](https://v3.tailwindcss.com/docs/border-width),
[border radius](https://v3.tailwindcss.com/docs/border-radius), and
[box shadow](https://v3.tailwindcss.com/docs/box-shadow) references were checked
2026-09-12. The renderer stores literal CSS values and uses no remote stylesheet.
This is a category reference, not a dependency on a live Tailwind installation.

The model receives the same prompt for every input and provider. Fixed 16px/24px
DejaVu Sans text and a 64px horizontal guide establish scale. The bundled font,
its SHA-256, and actual browser font-use evidence remove system-font fallback
ambiguity. Image resizing preserves the relative scale of the references and
the boundary. No task-specific answer text, recipe ID, or image filename is sent
as prompt content.

A stroke is a visible line pattern along the boundary; shadow is diffuse cast
shading. Shadow level is independent of stroke presence. Ring-only and
stroke-plus-shadow categories were removed because they mixed implementation
provenance or border presence into the shadow answer. Capsule rounding names the
CSS-clamped capsule shape, not a literally measurable 9999px arc.

## Experimental design

The corpus contains 53 distinct geometry recipes. Their union includes matched
width, style-at-each-width, edge-selection, radius in three contexts, and
uniformity at 12px/24px comparison sets, plus mixed heavy/partial cases. Duplicate
recipes shared by several sets appear once with multiple block memberships.
Each geometry is fully crossed with three light themes and three shadow levels,
yielding 477 images. [specimens.ts](../src/specimens.ts) is the complete recipe
construction; the frozen catalog records membership explicitly.

This arrangement removes theme-to-label shortcuts and makes shadow level
independent of the other labels. Matched blocks hold nuisance properties fixed.
Removing a stroke necessarily changes presence, sides, style, and width together;
those are logically dependent labels. Three theme repeats are correlated
measurements of one geometry, not three independent geometry samples.

The design is deliberately not a full factorial of all borders, corners, and
sides. Some geometry correlations remain. Class counts are published, and raw
accuracy is accompanied by per-class recall and balanced accuracy. Borderless
examples are retained for absence detection; conditional border-present results
prevent easy absence cases from concealing poor width or pattern recognition.

Dark backgrounds and same-color invisible surfaces are outside this release.
The old dark-theme 10%-black shadows were too weak for a fair distinction. Other
explicit limits are no right-only or two-edge borders, no double borders or inset/colored
shadows, one font/content/layout/browser/DPR, and synthetic card surfaces. Do not
generalize results to arbitrary screenshots, components, sizes, or accessibility.

## Validation and evidence

The all-image gate checks label consistency, complete enum coverage and quotas,
prompt identity, image dimensions and hashes, duplicate decoded pixels, finite
canonical geometry, exact computed border/radius/shadow values, recipe catalog,
font/scale evidence, and visible pixel differences. Every shadow has the same
recipe and theme rendered flat as its control. Contrast in a card edge alone
cannot establish shadow visibility. Browser tests independently pin constant
inner pixels across border widths, sides, patterns, shadows, and capsules.

Frozen descriptors bind manifest bytes to a Git commit and bind the corpus and
evaluation protocol to fingerprints. The runner invokes the gate before creating
clients. Renderer output guards resolve symlinks and reject overlapping frozen
paths. CI checks every descriptor that existed on the base revision, including
its entire dataset directory.

Automated contrast and pair checks establish machine-observable differences.
They do **not** establish human label agreement or a perceptual difficulty
threshold. Visual inspection catches obvious construction errors; a blinded
human pilot is still needed to measure whether designers reliably agree on every
category. That remains an empirical limitation, not a claim filled in by tests.

## Scoring and publication

Each valid JSON answer is compared across seven dimensions. Duplicate JSON keys,
extra/missing fields, wrong types, and invalid enum values invalidate the whole
answer. Case and surrounding whitespace in label strings are normalized; boolean
presence is strictly a JSON boolean. Invalid model answers score zero and are not
retried for a better score. Infrastructure failures remain outside accuracy
until resolved and remain in the attempt and cost records.

Exact match requires every dimension correct. Seven separate attribute scores
show error location. Because presence/sides/style/width share absence semantics,
these seven scores are not seven independent measures. No mean-of-seven
headline score is used. Class-balanced accuracy averages recall over observed
classes and reports both observed and defined class counts; missing classes are
null. Majority baselines use the same cohort. Confusion matrices preserve errors
between neighboring width/radius anchors.

The sealed export also includes complete matched-block diagnostics: all levels
correct, and both labels correct for each pair of levels. An incomplete block is
excluded and its absence appears in coverage, rather than silently shrinking the
comparison. Blocks overlap and share theme repeats, so these are descriptive
scores, not independent trials for a binomial confidence interval. No population
confidence interval or model significance claim is made from this fixed corpus.

Partial accuracy divides by final observed answers; coverage is a separate
quantity. Cross-model rankings and group breakdowns use the intersection of
observed task IDs. Saved target labels and correctness flags are independently
checked against the frozen image's ground truth and reparsed raw answer.
Chronology and recorded model configurations are verified. Temperature, seed,
and reasoning settings use provider defaults; those defaults can change remotely. Across runs, the
first final observation wins, even if a resumed older run answers later.

Finalization freezes a roster and cohort, checks the SQLite ledger against every
export, replays grading, verifies source artifacts against committed bytes, and
hashes the complete publication. Its lock excludes an active runner. A sealed
run cannot resume; further measurements use another run ID. Billing summaries
retain retries and distinguish metered costs from unmetered reservations.

## Before the first measured batch

Run the full offline checks, inspect the frozen corpus, and execute a mock
smoke/resume cycle. Select the model roster and any partial sample size before
looking at model scores. Verify the dated catalog's availability and pricing.
Use one frozen release, the same selected task set, and recorded provider
settings. Run complete coverage when affordable; otherwise publish the exact
shared sample and class coverage. Commit the source run, seal, verify, and then
publish. Human agreement and a larger diverse screenshot corpus are follow-up
experiments; model data from this release cannot substitute for them.
