# valid-07-perceptual-rigor: Calibrated perceptual benchmark and FontBench parity

- **Status**: In Progress
- **Branch**: `valid-07-perceptual-rigor`
- **Base**: BorderBench `077578b`; FontBench `14b09c3ad89e5b587c19abee5b66978968252f85`
- **Machine**: `/mnt/disks/data/borderbench`
- **Harness**: codex
- **Session ID**: not exposed
- **PR**: local review pending
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

Pending controlled checks and integration.
