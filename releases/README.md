# BorderBench releases

Each file pins one frozen benchmark version: the dataset manifest path, the
Git commit holding its exact bytes, the dataset and evaluation-protocol
fingerprints, and the expected task count.

| Release | Corpus | Status |
| --- | --- | --- |
| [1.0.0](1.0.0.json) | `dataset/borderbench-v1` (120 images) | Current |

Validate a release offline before any live run:

```bash
bun run validate:release
```

The gate refuses changed manifest bytes, a changed dataset fingerprint, a
changed evaluation protocol, or a wrong task count. Changes to released
inputs or evaluation behavior require a new release descriptor and version;
never edit a published descriptor in place.
