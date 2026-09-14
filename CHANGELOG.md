# BorderBench changelog


## 1.2.0 — 2026-09-12

- Replaces the corpus with 477 calibrated inputs: 53 geometry recipes crossed
  with three light themes and three independent shadow levels.
- Uses exact coarse Tailwind 3.4.17 radius anchors (0/4/12/24/full), visible
  nonuniform corners, and fixed 16px DejaVu Sans text plus a 64px scale guide.
- Removes ring-only and stroke+shadow provenance categories; border and shadow
  are scored independently. Prevents border-induced inner layout shifts.
- Adds catalog, pinned font evidence, pixel width/style/corner checks, matched
  shadow controls, and mandatory live preflight. Protects every frozen dataset.
- Verifies raw answers and attempt chronology before aggregation; uses shared
  image cohorts for rankings and reports conditional/macro/confusion diagnostics.
- Adds offline result sealing and independent verification against committed
  source checkpoints, immutable final answers, and complete cost histories.
- Preserves all earlier releases/results unchanged. Old scores do not transfer.

## V1.1.0 — 2026-09-10

Tailwind Rosetta Stone release. Every label maps to Tailwind CSS
utilities (see the [rosetta table](dataset/README.md)), the prompt
declares the fixed text sizes and inner chrome, elevation stacks align
exactly to Tailwind `shadow` / `shadow-lg` / `shadow-md`, and the
unrealistic `double` style is removed (its 9 specimens redistribute to
dashed/dotted heavies). Same 7-field schema; scores are incomparable
with V1.0.0.

| Identity | Frozen value |
| --- | --- |
| Version | `1.1.0` |
| Release descriptor | [releases/1.1.0.json](releases/1.1.0.json) |
| Dataset Git commit | [`ec1dc04`](https://github.com/eob/borderbench/commit/ec1dc044f39b45be7c4b6fea018026722640b947) |
| Dataset fingerprint | `506b7372566e3dab8022311df478ba78d608b0584d7eaabd1435b9f9f8b0764c` |
| Evaluation protocol fingerprint | `36f674d3004f400d7bdc10eded7df6a8f1e0bfef9a2e203fb390146b916bcd5d` |
| Grading version | `2` |
| Compatible release checkout | Git tag `v1.1.0` |

V1.0.0 remains valid and immutable under tag `v1.0.0`; no scores
transfer between releases.

## V1.0.0 — 2026-09-10

First named, frozen benchmark release. The accepted corpus contains
**120 images with fixed neutral card text**, every graded label value
sampled at least 9 times, Chromium computed-style evidence per image, and
zero validation errors.

| Identity | Frozen value |
| --- | --- |
| Version | `1.0.0` |
| Release descriptor | [releases/1.0.0.json](releases/1.0.0.json) |
| Dataset Git commit | [`11adacbfebcf92fac4c8680c1a2541d3fed546bc`](https://github.com/eob/borderbench/commit/11adacbfebcf92fac4c8680c1a2541d3fed546bc) |
| Dataset fingerprint | `dcbff0b1c76a788e9516dfafd13ab0a345743ee94783d7e226a02efb8886d64d` |
| Evaluation protocol fingerprint | `154aa49f7a90b1f35c4f97db5f4b70e129e9e8310992d3affbd0a75a7b1a0ed8` |
| Grading version | `2` |
| Compatible release checkout | Git tag `v1.0.0` |

The dataset commit predates this release naming and records the exact
frozen inputs. The release tag records the version-aware tooling and
run-log workflow.

This release fixes answer-bearing card text, the inner footer divider,
unverified rendering, permissive answer grading, single-sample classes,
invisible-boundary cards, invented export costs, and unversioned runs. It
retains image hashes, computed-style evidence, and browser provenance, and
rejects mismatched release data before live requests. Full details and
causal regression evidence are in the [ticket catalog](tickets/README.md).

Runs record the release label, dataset Git commit and fingerprint,
evaluation protocol, model configuration, code checkout, timestamps, and
every attempt. Runs made at different times can contribute to the same
website; repeated model/configuration–input pairs are resolved by first
recorded observation, without choosing the highest score. Changed
inference configurations remain distinct.

The 120-image scale is intentional: cheap full reruns with per-label
quotas instead of exhaustive factorial coverage. Presence is weighed
across four coordinated fields, uniformity variants are special cases,
and theme is an unscored condition; see the README for the documented
limits.

## Unversioned prototype — historical, invalid for V1.0.0 comparisons

- The original 120-image set renders titles, subtitles, tags, token IDs,
  and theme labels inside the judged card, has single-sample classes
  (`asymmetric=1`, `floating-drop=1`), and carries absolute image paths.
  Its paid responses and checkpoint are preserved as historical records.
- Code and measurements at `bd5523a` and earlier are pre-release
  prototypes. They must not be relabeled as V1.0.0 or combined with its
  measurements.

See [historical classifications](results/historical.json) and the
[results guide](results/README.md). No historical scores were carried
into V1.0.0.
