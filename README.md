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

## Benchmark Results (120 Tasks / 600 Evaluations)

Interactive results and Pareto frontier are published at [edwardbenson.com/benchmarks/borderbench](https://edwardbenson.com/benchmarks/borderbench).

| Model | All Correct (Exact Match) | Border Presence | Stroke Width | Corner Radius | Edge Selectivity | Latency / Task | Cost / Task |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gemini 3.1 Pro Preview** | **68.33%** | 95.83% | 75.83% | 85.83% | 85.83% | 4.28s | $0.0068 |
| **Gemini 3.8 Flash** | **61.67%** | 98.33% | 70.83% | 84.17% | 83.33% | 4.17s | $0.0042 |
| **GPT-5.6 Luna** | **47.50%** | 97.50% | 55.83% | 81.67% | 80.83% | 3.12s | $0.00055 |
| **GPT-5.6 Terra** | **45.00%** | 97.50% | 53.33% | 75.83% | 84.17% | 1.98s | $0.0044 |
| **Gemini 3.5 Flash-Lite** | **38.33%** | 94.17% | 48.33% | 75.00% | 73.33% | 0.94s | $0.00066 |

### Key Findings

1. **High Presence Discrimination, Low Stroke Precision**: Models reliably detect whether a container has a border (94%–98%), but classifying exact stroke width (`hairline` 1px vs `regular` 2px vs `thick` 4px) is the primary failure mode (sub-50% on lighter models).
2. **Frontier Champion**: **Gemini 3.1 Pro** achieves highest overall fidelity (**68.33%**), closely followed by **Gemini 3.8 Flash** (**61.67%**).
3. **Cost Efficiency**: **GPT-5.6 Luna** offers the best Pareto efficiency ($0.00055/task for 47.5% all-correct accuracy).

## License

MIT © Edward Benson
