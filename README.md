# BorderBench V1.2.0

BorderBench measures recognition of visible card borders, corner geometry, and
cast shadows. V1.2.0 contains **477 images: 53 shape recipes × 3 themes × 3 shadow
levels**, with a fixed visual scale and controlled comparisons. It is ready for
an initial model campaign; it does not yet have V1.2.0 model results or a measured
human agreement baseline.

The [methodology](docs/methodology.md) explains the design, scoring, validation,
and remaining limits. The [audit ticket](tickets/valid-07-perceptual-rigor.md)
compares the implementation with FontBench and retains regression evidence.

## Setup and validate

Requires Bun 1.3.14, Python 3.10+, Git history containing the dataset commit, and
Chromium for browser checks and rendering.

```bash
bun install --frozen-lockfile
bunx playwright install chromium
python3 -m venv .venv
.venv/bin/python -m pip install -e .
bun run test
bun run validate:release
```

On Linux, `bunx playwright install --with-deps chromium` installs browser system
dependencies. Validation is offline. Frozen live runs run the complete dataset
gate before creating provider clients.

## What the model sees and answers

Each image shows a 400×240 CSS px card on a 560×360 canvas at 2× DPR. The same
bundled DejaVu Sans text appears at 16px with 24px line height, with a 64px
scale guide. This supplies both a familiar typographic reference and an explicit
scale even when a provider resizes the image. Inner content stays in the same
position and cannot shift with border width or edge selection.

The shared [prompt](baseline/prompt.txt) defines exact anchors from **Tailwind
CSS 3.4.17 with a 16px root size**. Nearby intermediate classes are omitted.

| Attribute | Answer categories |
| --- | --- |
| Presence | `has_border`: visible stroke on any edge |
| Sides | `all-4`, `bottom-only`, `left-only`, `top-only`, `none` |
| Style | `solid`, `dashed`, `dotted`, `none` |
| Width | `0px`, `1px`, `2px`, `4px`, `8px`: `border-0`, `border`, `border-2`, `border-4`, `border-8` |
| Radius | `sharp` 0px, `subtle` 4px, `medium` 12px, `large` 24px, `pill`: `rounded-none`, `rounded`, `rounded-xl`, `rounded-3xl`, `rounded-full` |
| Uniformity | `all-corners`, `top-only`, `asymmetric` (only bottom-left sharp) |
| Shadow | `none`, `subtle-drop`, `floating-drop`: `shadow-none`, `shadow`, `shadow-lg` |

Every shadow level appears with every shape and theme. The task does not ask the
model to infer invisible CSS implementation details such as ring versus border.
Nonuniform corners use 12px or 24px rounding against a sharp corner. Themes are
unscored and repeat identically across all geometry/shadow combinations.

## Run a campaign

First exercise the pipeline without provider requests:

```bash
bun run benchmark --release 1.2.0 --mock --run-id smoke --max-tasks 3
```

Choose explicit model IDs from [config/models.json](config/models.json), or pass
`--config path/to/models.json`. The catalog records dated model IDs and prices;
verify them against provider documentation before a paid campaign. Set the API
key environment variable named by each selected configuration.

```bash
bun run benchmark --release 1.2.0 --run-id first-batch \
  --models YOUR_MODEL_ID --budget-usd 25
```

The live command makes paid requests. The budget uses configured prices and
conservative reservations; it is an estimate, not a provider-enforced spending
limit. Unknown usage is identified explicitly rather than priced as zero.

Repeat the same command to resume. A deterministic shuffled `--max-tasks N`
subset can be extended later. Changed inference settings require a different
run ID. Lost checkpoints and sealed publications refuse resume. Valid responses
and malformed model answers are final observations; malformed answers score
zero, while infrastructure failures remain retryable.

Runs are saved under `results/runs/1.2.0/<run-id>/`, including SQLite checkpoint,
every attempt, raw answers, recorded usage, configuration and code identity,
summary, and scorecards. No provider requests are needed to replay grading.

```bash
bun run build:page --release 1.2.0 --results-dir results/runs --output-dir site
python3 -m http.server 8000 --directory site
```

All ranked models and breakdowns use the same shared image cohort. Complementary
runs can contribute observations; repeats retain the earliest final answer by
observation time. Costs retain all attempts, including retries. The structured
export includes class recalls, confusion matrices, majority baselines, balanced
accuracies, and stroke scores conditional on a border being present.

Before publishing a measured comparison, commit its source run and freeze its
roster/cohort using the [finalization workflow](releases/FINALIZATION.md):

```bash
.venv/bin/python -m baseline.finalize \
  --run-dir results/runs/1.2.0/first-batch --scope full
.venv/bin/python -m baseline.finalize \
  --run-dir results/runs/1.2.0/first-batch --verify
```

Use `--scope common` for a deliberately partial comparison. Sealing independently
checks raw-response grades, checkpoint, exports, chronology, and committed bytes.

## Regenerate and inspect

```bash
bun run render
bun run validate:candidate
```

Generation writes `dataset/candidate-rendered`; it refuses paths overlapping
frozen releases and historical inputs. Candidates retain the font and license,
recipe catalog, image hashes, computed styles, browser and font evidence, scale
geometry, and paired flat controls. A new dataset or protocol needs a new release.

V1.0.0 and V1.1.0 inputs and trial results remain unchanged and incomparable with
V1.2.0. Their compatible tooling is available at the corresponding Git tags.
The earlier answer-leaking prototype remains explicitly invalid. See the
[dataset guide](dataset/README.md), [releases](releases/README.md), and
[results guide](results/README.md). Code is MIT licensed; the bundled font retains
its [license](src/assets/DejaVuSans.LICENSE).
