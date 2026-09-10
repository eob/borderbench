# BorderBench changelog

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
