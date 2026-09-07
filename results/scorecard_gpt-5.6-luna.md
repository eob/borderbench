# BorderBench Scorecard: `gpt-5.6-luna`

- **Total Tasks**: 120
- **All-Correct (Exact Match)**: **47.5%**
- **Border Presence Accuracy**: **97.5%**
- **Average Latency**: 3.12s / task
- **Total Cost**: $0.0000

## 1. Dimension Accuracy Breakdown

| Dimension | Accuracy | Description |
|---|---|---|
| **Border Presence** | **97.5%** | Binary detection of container border |
| **Edge Selectivity** | **97.5%** | All-4, top, bottom, left callout bar, none |
| **Stroke Style** | **97.5%** | solid, dashed, dotted, double, none |
| **Stroke Width** | **85.8%** | hairline (1px), medium (2px), thick (4px), heavy (8px), none |
| **Corner Curvature** | **63.3%** | sharp, subtle (3px), medium (8px), large (18px), pill |
| **Corner Uniformity** | **95.8%** | all-corners, top-only, asymmetric |
| **Elevation & Shadow** | **85.8%** | flat, subtle-drop, floating-drop, ring-only, stroke+shadow |

## 2. Accuracy by Surface Theme

| Theme | Tasks | Exact Match | Presence Acc |
|---|---|---|---|
| `white-on-gray` | 43 | 39.5% | 97.7% |
| `white-on-white` | 16 | 75.0% | 100.0% |
| `gray-tint-on-white` | 25 | 64.0% | 92.0% |
| `blue-tint-on-white` | 13 | 30.8% | 100.0% |
| `dark-mode` | 23 | 34.8% | 100.0% |

## 3. Accuracy by Corner Curvature

| Curvature | Tasks | Radius Acc | Exact Match |
|---|---|---|---|
| `sharp` | 21 | 0.0% | 76.2% |
| `subtle` | 21 | 0.0% | 33.3% |
| `medium` | 43 | 0.0% | 23.3% |
| `large` | 14 | 0.0% | 57.1% |
| `pill` | 21 | 0.0% | 76.2% |

## 4. Accuracy by Stroke Thickness

| Thickness | Tasks | Width Acc | Exact Match |
|---|---|---|---|
| `1px` | 50 | 0.0% | 42.0% |
| `0px` | 28 | 0.0% | 39.3% |
| `2px` | 24 | 0.0% | 66.7% |
| `4px` | 14 | 0.0% | 35.7% |
| `8px` | 4 | 0.0% | 100.0% |
