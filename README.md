# BorderBench

**BorderBench** is a vision-language benchmark evaluating multimodal AI models on container borders, edge selectivity, stroke width, stroke pattern, corner radius curvature, and elevation/drop shadows.

## Dimensions Evaluated

BorderBench subjects multimodal models to a standardized 400×240px UI card container rendered on high-resolution Retina canvases (2× DPR) across 6 core design dimensions:

1. **Border Presence & Edge Selectivity** (`border_sides`):
   - `all-4`, `bottom-only`, `left-only` (callout bar), `top-only`, `none`
2. **Stroke Style** (`stroke_style`):
   - `solid`, `dashed`, `dotted`, `double`, `none`
3. **Stroke Width / Thickness** (`stroke_width`):
   - `0px` (none), `1px` (hairline), `2px` (medium), `4px` (thick), `8px` (heavy)
4. **Corner Radius / Curvature** (`corner_radius`):
   - `sharp` (0px), `subtle` (3px), `medium` (8px), `large` (18px), `pill` (full circular/capsule)
5. **Corner Uniformity** (`corner_uniformity`):
   - `all-corners` (equal curvature), `top-only` (modal header/tab), `asymmetric` (speech bubble)
6. **Elevation & Shadow Interaction** (`elevation`):
   - `none` (flat), `subtle-drop` (shadow-sm), `floating-drop` (shadow-lg), `ring-only` (1px box-shadow outline without stroke), `stroke+shadow` (visible border + drop shadow)
7. **Optical Step & Contrast Boundaries**:
   - `white-on-gray`, `white-on-white`, `gray-tint-on-white`, `blue-tint-on-white`, `dark-mode`

## Quick Start

### 1. Installation

```bash
bun install
python3 -m venv .venv
.venv/bin/pip install -e .
```

### 2. Render Benchmark Dataset

```bash
bun run render
```

### 3. Run Benchmark Baseline

```bash
# Run mock test
bun run benchmark:mock

# Run real evaluation against enabled models
.venv/bin/python -m baseline.runner --models gemini-2.5-flash gemini-3.5-flash-lite
```

### 4. Export Structured Summary

```bash
bun run export
```

## License

MIT © Edward Benson
