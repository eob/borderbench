# First BorderBench V1.2.0 measurements

**13 model configurations × 128 identical images = 1,664 scored responses.**
The campaign retained 1,664 attempts and
0 infrastructure failures. Total recorded
metered cost: **$21.279322**, within the shared
$25 spending guard. These estimates use the recorded
provider token usage and dated catalog rates; they are not invoice amounts.

This is a sealed, partial comparison: **128/477 release images** per model.
The cohort is the first 128 task IDs after sorting and shuffling with
Python's `random.Random(0)`. It was selected using cost and corpus coverage; model scores
did not determine the sample size or membership. All models received the same images and frozen prompt;
no final answer was retried or replaced to improve its score.

| Model | All seven | Presence | Sides | Style | Width | Radius | Corners | Shadow | API cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6 Astra | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | $3.088 |
| GPT-5.6 Sol | 79.7% | 100.0% | 98.4% | 100.0% | 98.4% | 89.1% | 95.3% | 97.7% | $1.594 |
| GPT-5.6 Luna | 76.6% | 97.7% | 93.8% | 96.1% | 94.5% | 90.6% | 93.0% | 99.2% | $0.096 |
| Gemini 3.1 Pro Preview | 76.6% | 98.4% | 97.7% | 98.4% | 94.5% | 96.9% | 97.7% | 84.4% | $2.379 |
| GPT-5.6 Terra | 70.3% | 99.2% | 98.4% | 97.7% | 93.8% | 87.5% | 89.8% | 97.7% | $0.831 |
| Muse Spark 1.2 | 68.0% | 99.2% | 98.4% | 99.2% | 96.1% | 93.8% | 92.2% | 83.6% | $2.096 |
| Muse Spark 1.3 | 53.9% | 100.0% | 99.2% | 100.0% | 80.5% | 97.7% | 100.0% | 68.8% | $1.874 |
| Gemini 3.8 Flash | 53.1% | 98.4% | 98.4% | 98.4% | 85.9% | 75.8% | 98.4% | 84.4% | $0.822 |
| Claude Fable 5.1 | 51.6% | 98.4% | 98.4% | 98.4% | 93.0% | 93.0% | 97.7% | 60.9% | $4.380 |
| Claude Opus 5 | 23.4% | 98.4% | 97.7% | 98.4% | 88.3% | 64.1% | 94.5% | 50.0% | $2.744 |
| Gemini 3.5 Flash-Lite | 22.7% | 83.6% | 75.8% | 80.5% | 53.1% | 82.8% | 87.5% | 67.2% | $0.099 |
| Claude Haiku 4.5 | 10.2% | 90.6% | 83.6% | 84.4% | 40.6% | 68.0% | 83.6% | 53.1% | $0.366 |
| Claude Sonnet 5 | 7.8% | 94.5% | 85.9% | 94.5% | 44.5% | 62.5% | 85.9% | 43.8% | $0.910 |

Astra reached the observed ceiling on this sample (128/128 all-seven matches);
that does not establish perfect performance on the full release. Errors in other
models separate the visual dimensions: Muse 1.3 halved the correct width anchor
in all 25 of its width errors, and Fable missed 30/43 subtle shadows as “none.”
These patterns do not establish their causes.

Haiku answered “all-corners” on every image: 107/128 overall, but 0/13 asymmetric
and 0/8 top-only cases. The class-balanced diagnostics make this majority-category
behavior visible alongside aggregate accuracy.

Scores are proportions of the same 128 images. “All seven” requires every
attribute to be correct on an image. Full class recalls, confusion matrices,
conditional stroke scores, majority baselines and coverage accompany the
[sealed structured results](final_results.json). The generated
[benchmark page](../../../../site/index.html) shows all attributes and input groups.

The sample covers all answer categories and 52 of 53 shape recipes. It includes
only seven 1px examples and eight top-only corner examples. It has two complete
shadow intervention blocks and two style blocks, with no complete blocks for the
other controlled comparisons. The bordered medium-radius asymmetric recipe is
absent. Theme/category independence is approximate in this random prefix.
Consequently these are descriptive sample scores, with limited subgroup and
matched-comparison evidence. Human category agreement is unmeasured. Do not
interpret small ranking differences as established population differences.

The [campaign ticket](../../../../tickets/feat-08-models-branding.md) records
model readiness, the preselected cohort counts, execution changes, and gates.

## Reproduce and verify

- [Release descriptor](../../../../releases/1.2.0.json),
  [methodology](../../../../docs/methodology.md), and
  [model catalogs](../../../../config/README.md).
- [Run metadata](run.json), [attempt ledger](attempts.jsonl),
  [checkpoint](state.sqlite3), [summary](summary.json), and
  [publication seal](finalization.json).
- Source checkpoint commit: `8e6b751d9210bdf480a77bee1f2e9d9100f815ad`.
- Cohort fingerprint: `4b8399796335fd11f290ae4fc9c1c47c4328ab1668b46607866fe70b2a233ed6`.

```sh
.venv/bin/python -m baseline.finalize \
  --run-dir results/runs/1.2.0/2026-09-12-first-campaign --verify
```

This verification makes no provider requests. The sealed run cannot resume;
subsequent measurements must use a new run ID.
