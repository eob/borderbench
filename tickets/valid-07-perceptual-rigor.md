# valid-07-perceptual-rigor: Calibrated perceptual benchmark and FontBench parity

- **Status**: Implemented; PR review pending
- **Branch**: `valid-07-perceptual-rigor`
- **Base**: BorderBench `077578b`; FontBench `14b09c3ad89e5b587c19abee5b66978968252f85`
- **Machine**: `/mnt/disks/data/borderbench`
- **Harness**: codex
- **Session ID**: not exposed
- **PR**: https://github.com/eob/borderbench/pull/3
- **Assignee**: Edward Benson

## Research brief

Determine whether every scored distinction can be inferred fairly from the image,
whether rendering and dataset evidence enforce that contract, and whether model
comparisons faithfully represent the recorded answers on an identical cohort.
The decision is readiness for a new paid campaign. Existing releases and trial
data are historical evidence and must remain byte-identical.

Hypotheses: inherited FontBench infrastructure may already suffice; alternatively,
CSS provenance labels, weak perceptual separation, renderer side channels, or
reporting trust gaps may invalidate conclusions. Test each against source and
controlled counterexamples. This pass does not claim human agreement or empirical
model performance without observations.

## Plan and gates

1. Compare design, evaluation, and integrity independently; preserve baseline logs.
2. Reproduce defects with adversarial tests and controlled render ablations.
3. Prepare a new version with exact, coarsely spaced Tailwind anchors, independent
   border/shadow labels, fixed visual scale, matched interventions and theme balance.
4. Harden dataset validation, run preflight, scoring, and publication against the
   FontBench baseline; keep regression evidence here.
5. Render and inspect all-image diagnostics, run complete offline tests and mock
   campaign/resume/export checks, freeze the accepted dataset and protocol.
6. Simplification review, final evidence matrix, methodology and campaign instructions.

## Baseline evidence

`bun run test` at `077578b`: 83 Python tests passed; 18 Bun tests passed; TypeScript
typecheck passed. Passing tests do not establish perceptual validity.

## Decisions and durable findings

The final findings, decisions, evidence, and remaining limits follow below.

## Findings and implemented response

| Finding at the pinned baseline | Consequence | Repair and evidence |
| --- | --- | --- |
| V1.1 inner header moves 8px and shrinks 16px across width sweep | Layout reveals border width without inspecting the stroke | Absolute fixed reference; byte-equal central crops across widths, sides, patterns, capsules and shadows; [perception evidence](evidence/valid-07-perception.md) |
| Subtle asymmetric corners differ in 20 physical pixels; dark shadows differ at most 2–3/255 | Scored categories can be practically imperceptible | Exact 0/4/12/24/full radii; nonuniform corners 12/24 versus 0; light themes and all 318 elevated inputs paired to flat controls |
| Ring-only asks for CSS provenance; shadow classes encode border presence | Joint source guessing confounds recognition | Three independent shadow labels, every geometry×theme×shadow combination present |
| Radius tokens only approximately match Tailwind; system font varies | Reference scale and categories can drift | Tailwind 3.4.17 exact anchors, bundled hashed font, 16px/24px text and 64px guide; actual Chromium font check |
| Validator accepts arbitrary shadow values, nonfinite geometry, malformed coupled labels, omitted categories; normal release runs bypass pixel gate | Invalid data can reach paid runs despite a nominal release | Complete catalog, strict finite schema, pixel width/pattern/corner/shadow tests, mandatory preflight; [integrity evidence](evidence/valid-07-integrity.md) |
| Ranking uses different per-model cohorts, saved flags are trusted, old run creation beats earlier observations | Scores and repeat selection can misrepresent actual answers | Frozen-target raw replay, identical shared cohorts, recorded-at order and full ledger checks; [evaluation evidence](evidence/valid-07-evaluation.md) |
| Missing checkpoint can recreate measurements; rejected configuration changes poison metadata; unmetered calls cost zero | Resumes can bias measurements or budgets | Fail-closed state/config validation, conservative cost reservation and explicit unknowns |
| BorderBench lacks FontBench publication sealing | Published roster/cohort and source observations can change | Offline finalize/verify, SQLite/export/raw replay/commit binding; 34 finalizer tests |
| Both inherited invalid-response replay logic and finalizer metadata checks were incomplete | Consistent evidence forgery could be sealed | Require invalid text actually fail parsing; verify model-config census and unknown-cost marker; [adversarial red](evidence/valid-07-finalization-adversarial-red.txt) |

## Final design and interpretation

V1.2.0 freezes 477 images, 53 distinct geometry recipes, three light themes and
three independently crossed shadow levels. Corpus commit:
`b8c3a6b84bc250b3a22739bfec5e4fed47bbcffc`.
Dataset fingerprint: `85a9c8d4d23a6b2f9d7a3c15bcc8bc1031980139595d2dcb45df1262478c7451`.
The [descriptor](../releases/1.2.0.json) pins the exact evaluation protocol.

Class imbalance remains visible in the frozen [validation report](../dataset/borderbench-v1.2/validation.json),
including 405 uniform, 36 top-only, 36 asymmetric examples. Reports publish class
recalls/confusions, balanced accuracy with missing-class coverage, majority
baselines, and border-present-only stroke metrics. Complete matched blocks score
all-level and pair recognition. These are descriptive finite-corpus statistics,
not independent trials or population confidence estimates.

The renderer and dataset gate are substantially stricter than the inspected
FontBench baseline where relevant; the equivalent runner, provenance, cohort,
release, and finalization capabilities are now present. Font-specific binary
family/weight checks and Harbor packaging are domain-specific and not copied.
No blanket claim of 100% scientific validity follows from engineering parity.

Human category agreement remains **unknown**. Only machine-observable contrast
and selected visual inspection were established. Provider-default sampling and
reasoning settings are not fixed by the benchmark. Arbitrary screenshots, dark
surfaces, other layouts/fonts/scales, right-only/two-edge borders, double borders,
and inset/colored shadows are outside this release. See the
[methodology](../docs/methodology.md) for the intended inference and limits.

## Validation gate matrix

Tests ran on this branch against base BorderBench `077578b` and dataset commit
`b8c3a6b`; implementation commit `00b322812e39d167f379a5c97b5ea191678aee0a` contains the verified code.

| Gate | Result |
| --- | --- |
| `bun run test` | 173 Python tests passed; 21 Bun tests passed (5,631 assertions); TypeScript clean |
| `bun run validate:release` | 477 inputs; 477 unique decoded images; 1 pinned font; zero findings; all dataset bytes match frozen Git tree |
| Matched render controls | 318 visible shadows with correct spread; every width/style/corner probe passes; one identical reference crop per theme |
| Pure protocol/statistics isolated reversion | 8 failures recur under original baseline; [output](evidence/valid-07-protocol-reversion.txt) |
| Rendering isolated reversion | 3 original failures recur; [output](evidence/valid-07-perception-reversion.txt) |
| Runner/reporting isolated reversion | 12 original failures recur; [output](evidence/valid-07-evaluation-reversion.log) |
| Integrity isolated reversion | 9 original failures recur; [evidence](evidence/valid-07-integrity.md) |
| Mock partial→full→resume | 7 then 477 inputs; 3 invocations; 477 final attempts; 477 distinct tasks; zero duplicates; cost $0 |
| `bun run build:page --release 1.2.0` |New release page; zero live configurations; mocks excluded |
| Local page Chromium at 1280px and 360px | 48 images, 7 tables, zero JS errors, zero horizontal overflow |
| `pip wheel . --no-deps` |`borderbench-1.2.0-py3-none-any.whl` built |
| `git diff --check` |Clean |

Paid inference was not started. The mock checkpoint is ignored and cannot enter
the leaderboard. Earlier frozen datasets/descriptors and all paid source runs
are preserved unchanged.

## Delivery

Implementation, documentation, corpus, and regenerated local release page are committed and pushed on `valid-07-perceptual-rigor`. PR #3 is the review boundary; no merge or paid inference was performed. The existing brain project note links this audit and distinguishes earlier result snapshots from V1.2.0.

## Remote CI follow-up

The first remote run failed two finalizer/aggregation checks: a per-model cost
used exact floating-point equality even though the whole-run check used a
numeric tolerance. The same ledger values accumulated using ordinary sum versus
compensated sum differ by one unit in the last place. A controlled regression
reproduced the model exclusion; a $0.000001 corruption control remained rejected.
The collector now allows at most $0.000000000001 absolute rounding difference
and still requires finite nonnegative costs and matching unknown-cost markers.
Reporting/finalizer checks: 52 passed, including both new controls. Isolated
reversion: 1 failed/1 passed, as expected. See the
[CI log](evidence/valid-07-ci-first-run.log) and
[rounding evidence](evidence/valid-07-evaluation.md#ci-cost-accumulation-follow-up).
