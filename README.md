# BorderBench V1.0.0

BorderBench measures recognition of seven container properties from an
image: border presence, edge selectivity, stroke style, stroke width,
corner radius, corner uniformity, and elevation. **V1.0.0 freezes 120
images** with fixed neutral card text, verified rendering evidence, and
zero validation errors.

The [release descriptor](releases/1.0.0.json) binds this version to
dataset Git commit
[`11adacb`](https://github.com/eob/borderbench/commit/11adacbfebcf92fac4c8680c1a2541d3fed546bc),
the dataset fingerprint, and the evaluation protocol fingerprint.
[CHANGELOG.md](CHANGELOG.md) records the release; Git tag `v1.0.0`
identifies its compatible tooling.

The original 120-image set and its published scores are **invalid
historical prototypes**: card text revealed the answers. Their inputs,
paid checkpoint, and reports are preserved and labeled in the [dataset
guide](dataset/README.md) and [historical result
catalog](results/historical.json). The [ticket
catalog](tickets/README.md) records the defects, repairs, and regression
evidence.

## Setup and validate the release

Requires Bun 1.3.14, Python 3.10+, Git history containing the dataset
commit, and Chromium for rendering.

```bash
bun install --frozen-lockfile
bunx playwright install chromium
python3 -m venv .venv
.venv/bin/python -m pip install -e .
bun run validate:release
```

On Linux, `bunx playwright install --with-deps chromium` can install
browser system dependencies. The release validator runs offline: it
verifies the committed manifest bytes, dataset and protocol fingerprints,
and the independent all-image gate. Live runs require this gate before
contacting a model.

## Run any supported vision model, now or later

Run an offline smoke check first:

```bash
bun run benchmark --release 1.0.0 --mock --run-id smoke --max-tasks 3
```

Select models from [`config/models.json`](config/models.json), or provide
your own catalog with `--config path/to/models.json`. Native adapters
support OpenAI Responses, Anthropic Messages, and Google generateContent;
an OpenAI-compatible endpoint can use `base_url`. Set the API key
environment variable specified by each configuration. Catalog IDs and
prices are dated records; verify availability and rates when scheduling a
new campaign.

Separate runs can contribute to the same release:

```bash
# Example: GPT in one campaign.
bun run benchmark --release 1.0.0 --run-id gpt-september \
  --models gpt-6-astra --budget-usd 25

# Example: Gemini in a later campaign.
bun run benchmark --release 1.0.0 --run-id gemini-later \
  --models gemini-3.1-pro-preview --budget-usd 25

# Rebuild the website from all compatible recorded runs.
bun run build:page --release 1.0.0 --results-dir results/runs --output-dir site
python3 -m http.server 8000 --directory site
```

These live commands make paid requests. The budget is a cumulative
estimate for that run based on configured rates and conservative
reservations, not a provider invoice or provider-enforced limit.

Each run writes to `results/runs/1.0.0/<run-id>/`. Its `run.json` records
the release, full dataset Git hash, data/protocol fingerprints, model
configurations, timestamps, and executing code commit/dirty state.
`state.sqlite3` is the resumable checkpoint; `attempts.jsonl` retains
every attempt; summaries and scorecards expose the scored observations.
Commit a completed run directory to contribute it to this repository. The
runner does not commit or push automatically. See the [run log
guide](results/README.md) for the artifact layout and contribution
workflow.

Repeat the same command to resume. `--max-tasks N` selects a reproducible
subset that can be extended later; `--concurrency N` controls simultaneous
requests. Omitting `--run-id` creates a unique run. New model IDs can be
added in separate runs at any time. Changed inference settings need a new
run ID and remain separate configurations on the website. Explicit
`--manifest` runs are unversioned experiments and do not enter the release
leaderboard.

The website combines complementary observations for the same
provider/model/endpoint/output limit, keeps the earliest final observation
for each input, and retains all contributing run records and attempt
costs. Repeating a task cannot replace a lower score with a higher one.
Mocks, incompatible releases, and malformed reports are excluded. Rankings
use shared task cohorts; partial coverage is displayed explicitly.

Completed answers and malformed model outputs are final datapoints.
Malformed outputs receive zero; infrastructure failures remain retryable
and appear in error counts. The report leads with exact match: all seven
fields must be correct. It also shows the seven individual attribute
accuracies. Extra fields, duplicate JSON keys, missing fields, and invalid
enum values invalidate the whole prediction.

## What the benchmark measures

Every input shows the same neutral card (400×240 CSS px at 2× DPR) with
identical text and inner chrome. Only the outer boundary, corners,
shadow, and theme colors vary. The [shared
prompt](baseline/prompt.txt) defines the labels:

| Dimension | Labels and definition |
| --- | --- |
| Presence | `has_border`: a stroke exists on any edge |
| Sides | `all-4`, `bottom-only`, `left-only`, `top-only`, `none` |
| Style | `solid`, `dashed`, `dotted`, `double` (needs ≥4px), `none` |
| Width | `0px`, `1px` (hairline), `2px`, `4px`, `8px` (heavy) |
| Radius | `sharp` (0px), `subtle` (3px), `medium` (8px), `large` (18px), `pill` (9999px) |
| Uniformity | `all-corners`, `top-only` (bottom sharp), `asymmetric` (2px acute corner) |
| Elevation | `none`, `subtle-drop`, `floating-drop`, `ring-only`, `stroke+shadow` |

`theme` (card/canvas colors) is an unscored condition, not a graded
field: it varies the contrast the boundary must survive. A visible
boundary may come from a stroke, a shadow, or a tonal step; every image
passes a measured boundary-contrast gate. Theme carries no label
shortcut: theme-conditioned lookups match majority-class accuracy on
every axis.

Accepted design limits: presence is encoded across four coordinated
fields (`has_border`, sides, style, width), so exact match weighs it
more than a single field; `stroke+shadow` implies a border;
`top-only`/`asymmetric` apply only to rounded radii; shadow-only pale
cards expose corners through the shadow silhouette. The 120-image corpus
favors cheap full reruns over exhaustive combinations; per-value counts
are published in the frozen validation report. Inspect per-group results
and contact sheets alongside aggregate scores.

## Candidate generation

The release inputs are already checked in. Generation commands create
development candidates; they refuse to overwrite registered release or
historical directories.

```bash
bun run render
# renders to dataset/candidate-rendered, then:
bun run validate:candidate
```

The renderer verifies the computed border widths, styles, radii, and
shadows Chromium actually used, and records image hashes, card geometry,
and browser provenance. Initial rendering needs a local Chromium; no
network font or API access is used.

## Development checks

```bash
bun run test
bun run validate:release
```

The checks cover Python, TypeScript, local Chromium page checks, and
frozen release integrity. No provider access or API keys are needed.
Repository code is MIT licensed. See [LICENSE](LICENSE).
