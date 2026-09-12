# Evaluation, execution, and reporting rigor

Baseline: `077578b121561fb657cb7fc58fd1940b9a0e7b57`; audit and validation date: 2026-09-12 UTC.

## Proven defects and fixes

- A finished partial run retained `running` status; final statuses now describe the completed invocation, while previously registered models remain in summary completeness.
- Deleting SQLite silently repeated completed requests. Existing reports without their checkpoint now refuse resume, and a finalization artifact blocks all resume.
- Rejected inference configuration edits overwrote run metadata before validation. Checkpoint/model/history checks now precede report writes.
- Provider calls without usage became free. Conservative per-attempt estimates remain billed in the ledger; unknown prices require an unbudgeted run and unknown historical cost prevents budgeted resume.
- Attempt ordering used timestamps plus random UUIDs. The ledger now exports SQLite commit sequence and run identity in insertion order.
- Records lacked observation time and immutable model configuration provenance. Each row carries `recorded_at`; each report pins complete config/hash, run identity, code provenance, and invocation times.
- The website trusted target/grade flags and arbitrary task IDs and selected repeats by run creation. Reporting checks the frozen corpus, configuration, chronology, full JSONL final-attempt equality, and replays raw-answer grading. Earliest final observation wins, even across resumed campaigns.
- Retry infrastructure charges disappeared from website costs. The complete ledger now supplies model and run totals and explicit infrastructure counts; unknown costs stay null.
- A shared cohort was computed but the page ranked and displayed unequal observed cohorts. Rankings, comparison cells, and group tables now use the same shared task IDs. Observed metrics, class diagnostics, confusion matrices, matched-block diagnostics, and coverage remain explicit in JSON.
- The legacy export called unknown costs zero and accepted duplicate rows. It is explicitly unversioned, preserves unknown costs, and excludes an entire corrupt scorecard rather than dropping selected rows from its denominator.

## Red evidence

The regression suite was written before implementation. Initial seven execution tests, two report validation tests, and two export tests failed for their intended causal reasons. The equal-timestamp attempt order regression was added and failed before its fix.

- [Execution red](valid-07-evaluation-red.log)
- [Reporting red](valid-07-reporting-red.log)
- [Export red](valid-07-export-red.log)

Representative verbatim evidence:

```text
E       AssertionError: assert 'running' == 'partial'
E       Failed: DID NOT RAISE ValueError
E       assert 0.0 == 0.005016 ± 5.0e-09
E       assert 0.0 is None
```

## Reversion and validation

An isolated temporary checkout copy restored only the five owned implementation files from the baseline commit, retaining current regression tests and current schema. Twelve causally focused regressions failed again, without modifying the shared workspace. [Full reversion output](valid-07-evaluation-reversion.log).

| Gate | Base commit | Result |
| --- | --- | --- |
| Isolated implementation reversion | `077578b121561fb657cb7fc58fd1940b9a0e7b57` | 12 failed for original guard/status/cost/order/grade defects |
| `.venv/bin/python -m pytest tests/test_execution_rigor.py tests/test_reporting_rigor.py tests/test_release_runs.py tests/test_protocol_identity.py tests/test_run_state.py tests/test_export_integrity.py -q` | `077578b121561fb657cb7fc58fd1940b9a0e7b57` plus current work | 59 passed, 0 failed (1.04s) |

All provider paths in these tests use local fake evaluators or HTTP transports. No paid requests were made. The finalizer and corpus/release gates are validated separately by their owning lanes.

## Decisions and durable findings

Completed malformed answers remain final zero-credit observations; infrastructure errors remain retryable and retain all costs. Missing classes/cohorts are shown as null rather than invented zero accuracy. Repeats cannot replace a poorer answer with a later better answer. Comparison scores describe this fixed corpus and shared cohort; repeated themes are not independent evidence for population confidence claims. Historical records and released corpus files were not rewritten by this lane. A final simplification pass removed duplicated summary identity state and dead aggregation code.

Independent review added symmetric guards for parseable answers falsely labeled invalid, and preservation of unknown latency (null rather than an invented zero or partial mean). Both new cases were recorded red before correction; see [invalid replay red](valid-07-invalid-replay-red.log) and [unknown latency red](valid-07-unknown-latency-red.log). An earlier invalid final answer remains zero after a later correct repeat and both costs remain counted. The page copies validated run ledgers and scorecards and exports selected raw observations with source run and recorded time.


## CI cost accumulation follow-up

Base commit: `41afb754c0df2678f76a4aacebe8d76dd0322f99`. CI passed 171 tests but rejected model A in two sealed-run aggregation tests ([initial CI log](valid-07-ci-first-run.log)). Inspection isolated a strict equality comparison between SQLite's accumulated model cost and Python's re-summed JSONL costs. No chronology checks were relaxed.

A controlled fixture retains identical per-attempt costs `[0.014096, 0.0004, 0.0004]` but records their compensated sum in the summary. Ordinary Python summation yields `0.014895999999999998`; compensated summation yields `0.014896`. Before the fix this one-ulp difference produced:

```text
E       AssertionError: ['Excluded retry-costs/scorecard_mock-model.json: Model cost disagrees with its attempt ledger']
1 failed, 1 passed in 0.16s
```

[Full red evidence](valid-07-cost-roundoff-red.log). The symmetric control adds $0.000001 to the model summary and remains rejected. The fix requires finite nonnegative values and accepts only absolute floating point roundoff up to $0.000000000001, with zero relative tolerance; null costs must still agree. The experiment proves the exact-equality defect. Different SQLite accumulation implementations are the leading explanation for the CI/local difference; CI's actual SQLite library version was not recorded in the failing log.

| Gate | Result |
| --- | --- |
| Compensated-sum regression and material-corruption control | 2 passed in 0.13s |
| Reporting plus finalization suites | 52 passed in 10.59s |
| Restore baseline reporting.py in isolated temporary source copy | Same compensated-sum failure; material-corruption control still passes |
| `git diff --check` | Clean |

[Reversion evidence](valid-07-cost-roundoff-reversion.log). All checks were offline; source report and dataset identities are unchanged.
