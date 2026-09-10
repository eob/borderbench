# release-03-protect-frozen-artifacts: Freeze the corpus, isolate candidates

- **Status**: Planned
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Make the frozen V1.0.0 corpus overwrite-proof and direct all future
generation to isolated candidate directories. Mirrors FontBench release-03.

## Findings (base `bd5523a`)

- `bun run render` writes directly into the live dataset paths with no
  release check; a re-render silently moves the benchmark under old runs.
- No candidate/output separation; no guard against overlapping release dirs.

## Plan

1. Red: render into a registered release dir refuses; candidate render lands
   in `dataset/candidate-rendered` with its own manifest; overlap refused.
2. Registry of release dataset paths from `releases/*.json`; renderer and
   validator resolve through it; generation commands default to candidate
   paths and require explicit flags for anything else.
3. Document the candidate → validate → freeze → new-release workflow in
   `dataset/README.md`.

## Acceptance

- Attempted in-place re-render of the frozen corpus exits nonzero with no
  bytes changed (verified by pre/post tree hash).
- Candidate generation + validation works end to end offline.
