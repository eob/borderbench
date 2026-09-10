# BorderBench issue catalog

Authoritative local workfu/ticketfu catalog. Adapted from the FontBench
validity program (`../fontbench/tickets/`): six validity audits plus three
release tickets. BorderBench has no Harbor package, so valid-04 covers card
leakage, export integrity, and reporting instead of Harbor packaging.

| Ticket | Priority | Scope | State |
| --- | --- | --- | --- |
| [valid-01](valid-01-benchmark-audit.md) | Critical | Audit integration, census, regen, final verification | In Progress |
| [valid-02](valid-02-rendering.md) | Critical | Neutral card content, verified computed styles, portable manifest | Planned |
| [valid-03](valid-03-evaluation.md) | Critical | Strict prediction schema, protocol identity, resume/cohort correctness | Planned |
| [valid-04](valid-04-packaging-reporting.md) | High | Answer leakage, export integrity, honest shared-cohort reports | Planned |
| [valid-05](valid-05-experimental-design.md) | High | Class balance, observability, definitions and limits | Planned |
| [valid-06](valid-06-dataset-release-gate.md) | Critical | Independent image/label validation and mandatory release checks | Planned |
| [release-01](release-01-versioned-runs.md) | High | V1.0.0 identity, Git anchor, resumable dated runs and attempt logs | Planned |
| [release-02](release-02-aggregate-run-history.md) | High | Aggregate compatible model runs across time and publish origins | Planned |
| [release-03](release-03-protect-frozen-artifacts.md) | High | Protect frozen directories and isolate candidate generation | Planned |

The current 120-image set and its published scores are **invalid historical
prototypes**: card text reveals the answers, rare classes have single samples,
and grading is permissive. They are preserved in Git history and labeled in
[results](../results/README.md); no scores carry forward into V1.0.0.
