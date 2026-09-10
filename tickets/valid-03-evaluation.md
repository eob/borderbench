# valid-03-evaluation: Strict answers and reproducible evaluation

- **Status**: Planned
- **Branch**: `valid-01-benchmark-audit`
- **Base**: `bd5523a`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

Reject ambiguous malformed answers, pin evaluation protocol identity, and make
completion and compared cohorts auditable before new runs. Offline only.

## Findings (base `bd5523a`)

| # | Finding | Evidence |
| --- | --- | --- |
| E1 | Permissive grading admits ambiguous answers | `BorderPrediction` allows extra keys; `json.loads` resolves duplicate keys; evaluator `.get()` defaults for missing fields; blank/invalid enums earn partial credit |
| E2 | No protocol identity | `dataset_fingerprint` uses hardcoded `borderbench-grading-1` marker; prompt text duplicated in `src/render.ts`, not shared/frozen; code changes mix silently into resumed runs |
| E3 | Scorecards hide completeness | No `status`, cohort hash, or invalid-response count; partial runs divide by expected count with no visible flag |
| E4 | Resume rules unverified | Foreign task IDs, model-config mutation, fingerprint mismatch paths lack regression pins |

## Plan

1. Red: extra/duplicate/missing/blank/invalid-enum answers, protocol-change resume, foreign checkpoint IDs, partial-cohort status.
2. Strict whole-answer schema (`extra="forbid"`, duplicate-key detection, normalized case/whitespace, blank rejection); invalid answers are final zero-credit with usage preserved.
3. Single `baseline/prompt.txt`; `evaluation_protocol_fingerprint()` over prompt + schema + grading version + request/grading sources; run identity binds dataset + protocol hashes.
4. Scorecards carry sorted-task cohort hash, partial/complete status, invalid count; invalid responses stay in the denominator; infra failures stay retryable.
5. Resume must match task IDs, model identity, labels; nonmock runs pass the valid-06 gate before any client/request; isolated base-source reversions.

## Acceptance

- All Red cases fail on `bd5523a` sources and pass after the fix.
- Complete Python suite green; no transport/policy abstraction bloat.
