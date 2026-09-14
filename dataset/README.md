# BorderBench datasets

## V1.2.0: calibrated perceptual corpus

`borderbench-v1.2` contains 477 images: 53 unique shape recipes crossed with three
light themes and three independent shadow levels. The [methodology](../docs/methodology.md)
documents matched comparisons and interpretation limits. The
[shared prompt](../baseline/prompt.txt) is the complete response contract.

### Tailwind Rosetta Stone

Exact Tailwind CSS **3.4.17**, 16px root-size anchors:

| BorderBench | Tailwind reference |
| --- | --- |
| Width `0px`, `1px`, `2px`, `4px`, `8px` | `border-0`, `border`, `border-2`, `border-4`, `border-8` |
| Style `solid`, `dashed`, `dotted`, `none` | `border-solid`, `border-dashed`, `border-dotted`, `border-none` |
| Sides `all-4`, `bottom-only`, `left-only`, `top-only`, `none` | `border`, `border-b`, `border-l`, `border-t`, `border-0` |
| Radius `sharp` 0, `subtle` 4, `medium` 12, `large` 24, `pill` 9999px | `rounded-none`, `rounded`, `rounded-xl`, `rounded-3xl`, `rounded-full` |
| Uniformity `all-corners`, `top-only`, `asymmetric` | equal radii, rounded top pair, three rounded corners with bottom-left sharp |
| Shadow `none`, `subtle-drop`, `floating-drop` | `shadow-none`, `shadow`, `shadow-lg` |

Nonuniform corners use only 12px/24px versus 0. Exact shadow stacks are in the
prompt and renderer. Border presence and shadow are independent. No question
asks whether a visible outline originated from `ring-1` or a CSS border.

Every image uses the same bundled DejaVu Sans text at 16px/24px and 64px scale guide.
The foreground text/ruler pixels remain fixed even when borders are thicker,
partial, patterned, or capsule-shaped. Font license and binary travel with the
corpus. The frozen manifest retains browser-computed styles, actual font-use and
scale evidence, recipe membership, hashes, and paired flat-shadow controls.

### Generation and validation

```bash
bun run render
bun run validate:candidate
bun run validate:dataset
bun run validate:release
```

The default renderer writes to ignored `candidate-rendered/`, and refuses
symlink aliases or parent/child overlaps with any frozen or historical dataset.
Keep manifest, catalog, fonts, and PNGs together. The committed pixels define the
benchmark; other browser versions may rasterize differently. New pixels,
prompts, taxonomy, or scoring require a separate release descriptor.

Validation checks every image, complete label coverage, exact geometry/styles,
font/reference evidence, contrast and paired shadow differences. A nonempty
border edge is not sufficient proof of visible corners or shadows. Automated
pixel checks are not a human agreement study.

## V1.1.0 and V1.0.0: preserved releases

`borderbench-v1.1` and `borderbench-v1` each retain 120 images, their original
prompts, evidence, descriptors, and trial results unchanged. Use tags `v1.1.0`
and `v1.0.0` for their compatible tooling. Scores cannot transfer to V1.2.0.

V1.1 used radius values 0/3/8/18/full (including `rounded-lg`8px), approximate
Tailwind radius descriptions, `ring-only` near `ring-1`, and `stroke+shadow`
using `shadow-md`. Its system-font inner layout shifted with borders, and some
dark shadows and asymmetric corners were poorly separated. These limitations
are recorded in [the audit](../tickets/valid-07-perceptual-rigor.md). Preserving
those records is not a claim of parity with the revised perceptual design.

## Historical prototype: invalid

`borderbench-1/manifest.json` and `rendered/` are the original 120-image prototype.
Card text reveals answers, rare classes have single examples, and the manifest
uses absolute image paths. It is invalid for perception evaluation and remains
only as historical audit evidence. The renderer refuses to overwrite it.
