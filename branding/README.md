# BorderBench identity

- `borderbench-logo.svg`: scalable mark and favicon.
- `borderbench-share.png`: 1200×630 PNG, suitable for Twitter/X's large image card.
- `social-card.html`: editable source artwork with vector borders and shadows.

Rebuild with `bun run build:branding` after installing Chromium. The card uses the
repository's bundled DejaVu Sans font; its license is in
[`src/assets/DejaVuSans.LICENSE`](../src/assets/DejaVuSans.LICENSE). No network
fonts or image-generation service are needed. This is new BorderBench artwork;
no custom FontBench logo was available in the inspected repository or live site.

`bun run build:page` copies both display assets into `site/assets/` and writes
Open Graph and Twitter metadata. Its default public URL is
`https://edwardbenson.com/benchmarks/borderbench/`; set `--site-url` to the actual
hosting directory when deploying elsewhere. Serve the generated HTML and its
assets together. Generating this directory does not deploy it or update the
separate edwardbenson.com application. The PNG can also be uploaded directly as
a social post or repository social preview.
