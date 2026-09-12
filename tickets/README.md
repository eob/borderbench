# BorderBench issue catalog

Authoritative local workfu/ticketfu catalog. Adapted from the FontBench
validity program (`../fontbench/tickets/`): six validity audits plus three
release tickets. BorderBench has no Harbor package, so valid-04 covers card
leakage, export integrity, and reporting instead of Harbor packaging.

| Ticket | Priority | Scope | State |
| --- | --- | --- | --- |
| [valid-01](valid-01-benchmark-audit.md) | Critical | Audit integration, census, regen, final verification | Completed |
| [valid-02](valid-02-rendering.md) | Critical | Neutral card content, verified computed styles, portable manifest | Completed |
| [valid-03](valid-03-evaluation.md) | Critical | Strict prediction schema, protocol identity, resume/cohort correctness | Completed |
| [valid-04](valid-04-packaging-reporting.md) | High | Answer leakage, export integrity, honest shared-cohort reports | Completed |
| [valid-05](valid-05-experimental-design.md) | High | Class balance, observability, definitions and limits | Completed |
| [valid-06](valid-06-dataset-release-gate.md) | Critical | Independent image/label validation and mandatory release checks | Completed |
| [release-01](release-01-versioned-runs.md) | High | V1.0.0 identity, Git anchor, resumable dated runs and attempt logs | Completed |
| [release-02](release-02-aggregate-run-history.md) | High | Aggregate compatible model runs across time and publish origins | Completed |
| [release-03](release-03-protect-frozen-artifacts.md) | High | Protect frozen directories and isolate candidate generation | Completed |
| [valid-07](valid-07-perceptual-rigor.md) | Critical | FontBench parity, calibrated perceptual design, sealed publication | In progress |

The original 120-image prototype and its published scores are **invalid historical
prototypes**: card text reveals the answers, rare classes have single samples,
and grading is permissive. They are preserved in Git history and labeled in
[results](../results/README.md); no scores carry forward into V1.0.0.
