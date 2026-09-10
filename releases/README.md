# BorderBench releases

Each file pins one frozen benchmark version: the dataset manifest path, the
Git commit holding its exact bytes, the dataset and evaluation-protocol
fingerprints, and the expected task count.

| Release | Corpus | Status |
| --- | --- | --- |
| [1.1.0](1.1.0.json) | `dataset/borderbench-v1.1` (120 images) | Current |
| [1.0.0](1.0.0.json) | `dataset/borderbench-v1` (120 images) | Superseded but valid; incomparable scores |

Scores never transfer across releases. The 1.0.0 corpus, descriptor,
and tag stay immutable; use the `v1.0.0` checkout for 1.0.0 runs.

Validate a release offline before any live run:

```bash
bun run validate:release
```

Superseded releases validate only under their compatible checkout (for
example, `validate:release-1.0` at tag `v1.0.0`); newer code refuses
them closed with a protocol mismatch instead of mixing versions.

The gate refuses changed manifest bytes, a changed dataset fingerprint, a
changed evaluation protocol, or a wrong task count. Changes to released
inputs or evaluation behavior require a new release descriptor and version;
never edit a published descriptor in place.
