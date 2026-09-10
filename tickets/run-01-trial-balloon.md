# run-01-trial-balloon: First V1.1.0 measurements (Gemini + Claude)

- **Status**: In Progress
- **Branch**: `main` (PR #2 merged as `fc7bbec` before the campaign; results commit directly)
- **Base**: `fc7bbec`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **Assignee**: Edward Benson

## Goal

First paid measurement campaign on release 1.1.0 (all enabled Gemini
and Claude models), adversarial pre-flight, run history, rebuilt
leaderboard, and an unlinked trial-balloon page on edwardbenson.com.

## Adversarial pre-flight (all pass, 2026-09-10)

| Probe | Result |
| --- | --- |
| A1 re-render determinism | 120/120 PNGs byte-identical |
| A2a flipped image byte | `image_hash` + `png_decode`, corpus invalid |
| A2b forged evidence widths | `evidence_width`, corpus invalid |
| A3 title-glyph identity | 1 hash per (theme, left px, top px) group, 42/42; residual variance is standard CSS border-box content shift from the visible border itself, not a leak |
| A4 single-field shortcuts | Only known structural predictors (`sides` to presence 1.000, `has_border` to elevation 0.717 by the borderless-elevation taxonomy); theme predicts nothing above 0.375 |
| A5 cross-version | New code refuses 1.0.0 closed; 1.0.0 validates under `v1.0.0` |

## Campaigns

| Run ID | Models | Budget | Estimate |
| --- | --- | --- | --- |
| `gemini-sep10` | gemini-3.1-pro-preview, gemini-3.8-flash, gemini-3.5-flash-lite | $10 | ~$0.90 |
| `claude-sep10` | claude-fable-5-1, claude-opus-5, claude-sonnet-5, claude-haiku-4-5-20251001 | $15 | ~$4.85 |

Per-request reserve enforcement active; invalid answers are final;
infra failures retry with backoff. GPT models explicitly out of scope
for this balloon.
