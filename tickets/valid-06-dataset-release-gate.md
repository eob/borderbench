# valid-06-dataset-release-gate: Refuse unvalidated benchmark inputs

- **Status**: Completed
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

A read-only gate that checks every image and label and refuses live model
spend on anything unvalidated. No validator exists at base.

## Findings (base `bd5523a`)

| # | Finding | Evidence |
| --- | --- | --- |
| G1 | No dataset validator | `baseline/validate_dataset.py` absent; runner accepts any manifest whose labels parse and files exist |
| G2 | No CI | No `.github/workflows/`; nothing enforces tests, typecheck, or gates |
| G3 | Historical set would fail | Absolute paths (R4), answer text (R1), invisible cards (D2), single-sample classes (D1) — a gate must reject it while preserving it as history |

## Plan

1. Red: missing module, corrupt/blank/duplicate PNGs, hash mismatch, enum violation, prompt-hash mismatch, invisible boundary, quota violation, stale-managed-file drift.
2. Build `baseline/validate_dataset.py` (CLI + API): decode every PNG with Pillow; verify dimensions, hashes, duplicates, edge-contrast observability, computed-style evidence consistency, prompt hash, per-label quotas, manifest/managed-file accounting; emit complete JSON report with failing exit status.
3. Require the gate before nonmock clients/requests; show gate status on the page (release-02); keep mock/offline fixtures working.
4. Add CI: pinned Bun 1.3.14, Playwright Chromium, pytest, Bun tests, typecheck, `validate:release`.
5. Independent review hardening: erased-region, alpha-mode, malformed-manifest, and forged-evidence regressions with pre-fix reversion.

## Acceptance

- Frozen corpus: valid, 120 unique decoded images, zero errors.
- Historical manifest: rejected with actionable errors.
- Guard tests prove rejected data causes zero clients/requests.

## Completion

Independent Pillow validator (11 finding codes) with CLI; live runs gated; CI runs tests, typecheck, dataset and release gates.
