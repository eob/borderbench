# release-01-versioned-runs: V1.0.0 identity and resumable dated runs

- **Status**: Planned
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Name the accepted corpus V1.0.0 with a Git-anchored identity, and make every
future measurement a resumable, attributable run. Mirrors FontBench
release-01; no paid inference here.

## Findings (base `bd5523a`)

- No release descriptor, CHANGELOG, or tag; manifest claims `version 1.0.0`
  for the invalid prototype set.
- Unversioned `run_id "default"`; no `run.json`/`attempts.jsonl`; run records
  model config but not code commit, timestamps, or protocol identity.
- `.gitignore` excludes all of `results/runs/`; measurements cannot be shared.

## Plan

1. Red: release resolution (`--release 1.0.0` selects frozen manifest; unknown release fails closed); run provenance (commit/dirty, timestamps, configs); stale-resume rejection.
2. Add `releases/1.0.0.json` (manifest path, dataset Git commit + fingerprint, protocol fingerprint, task count), `releases/README.md`, `CHANGELOG.md`, tag `v1.0.0`.
3. Runner writes `results/runs/1.0.0/<run-id>/` with `run.json`, `state.sqlite3`, `attempts.jsonl`, summaries, scorecards; records release, dataset commit/fingerprint, protocol, configs, code commit/dirty, timestamps.
4. Track versioned runs in Git; keep mocks, locks, WAL/SHM excluded.
5. Offline CLI + resume smoke: same command resumes with zero new attempts and zero spend.

## Acceptance

- `bun run benchmark --release 1.0.0 --mock --run-id smoke --max-tasks 3` passes offline.
- Versioned mock + resume gates green; historical data untouched and excluded.
