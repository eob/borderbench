# feat-08: FontBench model parity, branding, and first measurements

- **Status**: In Progress
- **Branch**: `valid-07-perceptual-rigor` (continuation of the unmerged release PR)
- **Base**: `6bcc695ab2833deed36ad25da410c518c4bcab4e`
- **FontBench reference**: `14b09c3ad89e5b587c19abee5b66978968252f85`
- **Harness / machine**: codex / eob-dev2
- **Session**: not exposed
- **PR**: https://github.com/eob/borderbench/pull/3

## Authorized work

Commit and push the completed validity work, configure the same models as
FontBench, create a coordinated BorderBench logo/share card, then run every
configured model against V1.2.0 to begin collecting measured data. Use the
repository's $25 total campaign guard and the same shuffled task sequence.

## Plan

1. Verify prior commits are pushed; inspect base and Meta catalogs and provider wiring.
2. Add missing model configurations, retaining dated pricing and explicit endpoints.
3. Locate and inspect FontBench's actual visual identity; create and integrate
   BorderBench logo and a social share image with preview metadata.
4. Verify model loading, request shape, metadata/assets, and unchanged release identity.
5. Commit/push preparation, start measured inference, verify/resume safely, and
   retain attempted/completed observations and costs without hiding provider failures.
6. Publish honest shared-cohort results and commit/push the source measurement records.

## Evidence and decisions

Initial base catalogs are identical (11 enabled Anthropic/OpenAI/Google models,
one disabled historical Gemini model). FontBench also has a separate two-model
Meta Muse Spark catalog, which BorderBench is missing. Prior validity work is
already pushed at `6bcc695`; working tree was clean at task start.


## Model parity implementation and validation

The default `config/models.all.json` now includes 13 enabled models: 4 Anthropic,
4 native OpenAI, 3 Google, and 2 Meta. Both `models.json` and `models.meta.json`
preserve the exact source bytes from FontBench commit
`14b09c3ad89e5b587c19abee5b66978968252f85`; the combined catalog preserves every
record, including the disabled historical Gemini entry. Source hashes are pinned
in `tests/test_model_parity.py` without requiring a sibling checkout in CI.

Runner changes port FontBench's 300-second Meta transport timeout and optional
Anthropic workspace header. Both settings are recorded in invocation history;
all output caps and model-default reasoning settings are unchanged. The catalog
bound is five enabled models per provider endpoint. Authentication, credit, and
rate failures pause only the same provider/endpoint/credential group, preserving
independence between Meta and OpenAI even though both use the Responses adapter.
No frozen provider/evaluator source or V1.2.0 release input was changed.

The initial regression gate failed 10 tests for missing catalogs, endpoint limits,
workspace routing, timeout/provenance, and cross-provider pause contamination;
7 controls passed. [Verbatim red](evidence/feat-08-model-parity-red.log). Restoring
only baseline runner/model loading code in a temporary source copy reproduced
10 failures with 9 controls passing. [Reversion](evidence/feat-08-model-parity-reversion.log).

| Gate | Base | Result |
| --- | --- | --- |
| Model parity, model configuration, execution rigor, and finalization tests | `6bcc695ab2833deed36ad25da410c518c4bcab4e` + preparation changes | 85 passed in 6.02s |
| All 13 model request/response paths over local HTTP mock transport | Same | 13 correctly configured requests and 13 final scored observations; zero live inference |
| `.venv/bin/python -m baseline.releases --release 1.2.0` | Same | Passed: 477 inputs, dataset `85a9c8d4d23a6b2f9d7a3c15bcc8bc1031980139595d2dcb45df1262478c7451`, protocol `d22d04185da1464fe0902cb563bc020c9d3f836d02cdf864062d28db88702be4` |
| `git diff --check` | Same | Clean |

Read-only authenticated `GET /models` checks returned HTTP 200 from all four
endpoints and listed every requested model ID. Credential values were neither
printed nor retained. All four required credential variables are present;
`ANTHROPIC_WORKSPACE_ID` is absent. [Sanitized readiness evidence](evidence/feat-08-model-readiness.json).
Listing access does not prove inference quota, funding, or whether the current
Anthropic credential requires workspace routing for Messages. FontBench's
historical campaign recorded billing and workspace issues, then successful
responses after account configuration; those failures are not assumed current.

Pricing checks on 2026-09-12 confirmed the 11 primary models' recorded standard
rates against [official OpenAI pricing](https://developers.openai.com/api/docs/pricing),
[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), and
[Google pricing](https://ai.google.dev/gemini-api/docs/pricing). The
[Meta pricing page](https://dev.meta.ai/docs/pricing-rate-limits) returned a
JavaScript shell; Meta's $1.25/$4.25 per-million rates remain attributed to the
September 10 FontBench snapshot. Source catalog verification dates were preserved.

## Durable model decisions

One default catalog supplies a single cumulative budget and task sequence for all
13 models. Runtime timeouts and authentication routing are execution provenance;
the response schema, prompt, inference body, grading, and model configuration
fingerprints remain the frozen V1.2.0 protocol. A final simplification review kept
changes at the runner initialization boundary and reused the existing Responses
transport. Paid inference remains the campaign owner's next step after preparing
and committing the combined model and branding changes.

## Branding and preparation gate

Created an editable SVG mark, HTML/vector share artwork, and 1200×630 PNG in
`branding/`. The design uses solid/dashed/dotted strokes, coarse corner changes,
and a visible cast shadow. Typography uses the bundled font. A deterministic
Playwright command (`bun run build:branding`) regenerates the PNG offline.
Inspected the rendered image at full size. No custom FontBench logo was found
in the inspected repository, website assets, or live social metadata; this is
new BorderBench artwork, coordinated with the benchmark's visual subject.

The page builder copies both assets and emits Open Graph/Twitter large-image
metadata with absolute URLs and dimensions. `--site-url` sets the deployment
location; local generation does not publish to the separate website. The
integration regression initially failed for the missing public URL/metadata
support ([red output](evidence/feat-08-branding-red.txt)), then passed while
retaining the same shared-cohort ranking assertions.

Full preparation suite: 194 Python tests, 21 Bun tests (5,631 assertions), and
TypeScript checking passed. The generated V1.2.0 page passes the complete frozen
dataset gate and currently contains zero live observations. Simplification
review kept rendering in one small script and transport changes at the existing
runner boundary; no new provider abstraction or evaluation protocol was added.
