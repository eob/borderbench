# release-04-v1-1-rosetta: Tailwind Rosetta Stone and realistic style set

- **Status**: In Progress
- **Branch**: `release-04-v1-1-rosetta`
- **Base**: `ee30b61`
- **Machine**: `eob-dev2`
- **Harness**: muse
- **Session ID**: `01a08932-89e6-7782-b859-de207f01941f`
- **PR**: Pending
- **Assignee**: Edward Benson

## Goal

Ground every BorderBench label in Tailwind design tokens (the Rosetta
Stone), declare the fixed rendering context in the prompt, and drop the
unrealistic `double` stroke style. Ship as release 1.1.0 (new corpus,
prompt, and enum; same 7-field schema).

## Versioning rule (adopted)

- Minor (1.x): corpus, prompt-text, enum-value, or stack refinements.
  Scores stay incomparable across versions; the shape is stable.
- Major (x.0): schema field added or removed (e.g. dropping
  `has_border`, deferred to a future 2.0.0).

## Rosetta mapping (Tailwind v3 tokens, verified against published scales)

| BorderBench label | Tailwind equivalent |
| --- | --- |
| `0px` / `1px` / `2px` / `4px` / `8px` | `border-0` / `border` / `border-2` / `border-4` / `border-8` |
| `solid` / `dashed` / `dotted` / `none` | `border-solid` / `border-dashed` / `border-dotted` / `border-none` |
| `all-4` / `bottom-only` / `left-only` / `top-only` / `none` | `border` / `border-b` / `border-l` / `border-t` / `border-0` |
| `sharp` 0 / `subtle` 3 / `medium` 8 / `large` 18 / `pill` 9999 | `rounded-none` / between `rounded-sm` 2 and `rounded` 4 / `rounded-lg` 8 / near `rounded-2xl` 16 / `rounded-full` |
| `all-corners` / `top-only` / `asymmetric` | uniform rounding / `rounded-t-*` modal sheet / brand accent |
| `none` | flat, no shadow |
| `subtle-drop` | `shadow` (v3 default stack, exact) |
| `floating-drop` | `shadow-lg` (exact after 0.12 to 0.1 alpha alignment) |
| `ring-only` | near `ring-1` in neutral (our stack stays neutral, not Tailwind blue) |
| `stroke+shadow` | `border` + `shadow-md` (exact) |

Fixed prompt context (new): system font stack, title 16px semibold,
subtitle 12px, body 13px, meta 11px; 40px pill avatar, 6px badge/button
radii. Inner content is identical on every image and carries no signal.

## Double-border evidence and decision

Keep: `double` is a CSS keyword and Tailwind core utility
(`border-double`); it renders distinctly at 4px+.

Drop (accepted): double borders are vanishingly rare in contemporary UI
cards (print certificates, formal tables); the style forces a
style-width correlation (>= 4px); at 4px its lines duplicate the
hairline test. A UI-understanding benchmark should spend its 9 samples
on realistic patterns. The 9 V1.0.0 specimens redistribute to
dashed/dotted/solid heavies. Revisit only with real-world UI frequency
evidence.

## Plan

1. Red: prompt Tailwind/fixed-context content, `double` rejection at
   schema and specimen levels, exact shadow-stack rendering, rosetta doc
   coverage of every label.
2. Implement: prompt rewrite, `StrokeStyle`/`BorderPrediction` without
   `double`, specimen redistribution, `shadow-lg`-exact floating stack,
   export/page/taxonomy updates.
3. Regenerate corpus to `dataset/borderbench-v1.1/`, validate with zero
   errors (contrast gate is the empirical check on aligned stacks).
4. Release `1.1.0`: descriptor, changelog, README mapping, rebuilt site.
5. Full gates, isolated base reversions, simplify/hygiene, PR.

## Acceptance

- `bun run test`, `validate:dataset`, `validate:release --release 1.1.0`
  green; V1.0.0 gate still passes untouched.
- No `double` anywhere in taxonomy, corpus, prompt, or exports.
- Prompt names Tailwind equivalents and fixed text sizes.

## Handoff & Takeover Log

- `2026-09-10`: Started by `muse` on `eob-dev2` (Session `01a08932-89e6-7782-b859-de207f01941f`).
