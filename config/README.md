# Model catalogs

The default [`models.all.json`](models.all.json) combines the same **13 enabled
models** as FontBench: four Claude, four GPT, three Gemini, and Muse Spark 1.2
and 1.3. The disabled Gemini 2.5 Flash-Lite entry remains historical metadata.

[`models.json`](models.json) and [`models.meta.json`](models.meta.json) preserve
FontBench's source catalog bytes at commit
[`14b09c3ad89e5b587c19abee5b66978968252f85`](https://github.com/eob/fontbench/commit/14b09c3ad89e5b587c19abee5b66978968252f85).
The combined file concatenates their entries without changing IDs, output
caps, endpoints, prices, or model-default reasoning settings. Its verification
date is the older source date; current readiness checks are recorded separately
in the [model preparation evidence](../tickets/evidence/feat-08-model-readiness.json).

| Catalog | Enabled models | Credentials |
| --- | --- | --- |
| `models.all.json` | All 13 | All four variables below |
| `models.json` | 11 Claude / GPT / Gemini | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` |
| `models.meta.json` | Muse Spark 1.2 and 1.3 | `MODEL_API_KEY` |

One run shares the cumulative spending guard and task order across all models:

```bash
bun run benchmark --release 1.2.0 --run-id first-campaign --budget-usd 25 --max-tasks 24
```

Repeat the same command to resume, or increase `--max-tasks` to extend the same
campaign. `--config config/models.meta.json` selects only the Meta catalog;
`--models muse-spark-1.3` selects one model from the default combined catalog.
Use `--mock` for offline checks.

Muse uses the existing OpenAI-compatible Responses transport at
`https://api.meta.ai/v1`, a 16,384-token output cap, and a 300-second transport
timeout. FontBench observed reasoning exceed both the smaller output cap and
the usual 60-second wait. Other endpoints retain their 60-second timeout.
Timeouts are recorded per model in invocation history.

An Anthropic key spanning workspaces can use `ANTHROPIC_WORKSPACE_ID`; its
`wrkspc_...` value is sent only as Anthropic account routing and recorded in the
invocation. Workspace-scoped keys can omit it. API keys are never copied into
run records. Authentication, rate, and credit failures pause only models sharing
the same provider, endpoint, and credential variable, so Meta failures do not
pause native OpenAI models. The catalog guard permits at most five enabled
models per provider endpoint.

The corpus, provider request bodies, response schema, grading, and frozen
protocol remain unchanged. Read-only model listing verifies account visibility;
it does not establish inference funding or remaining quota.
