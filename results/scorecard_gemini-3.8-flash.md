# BorderBench Scorecard: `gemini-3.8-flash`

- **Total Tasks**: 120
- **All-Correct (Exact Match)**: **61.7%**
- **Border Presence Accuracy**: **98.3%**
- **Average Latency**: 4.17s / task
- **Total Cost**: $0.0000

## 1. Dimension Accuracy Breakdown

| Dimension | Accuracy | Description |
|---|---|---|
| **Border Presence** | **98.3%** | Binary detection of container border |
| **Edge Selectivity** | **98.3%** | All-4, top, bottom, left callout bar, none |
| **Stroke Style** | **98.3%** | solid, dashed, dotted, double, none |
| **Stroke Width** | **97.5%** | hairline (1px), medium (2px), thick (4px), heavy (8px), none |
| **Corner Curvature** | **87.5%** | sharp, subtle (3px), medium (8px), large (18px), pill |
| **Corner Uniformity** | **95.8%** | all-corners, top-only, asymmetric |
| **Elevation & Shadow** | **77.5%** | flat, subtle-drop, floating-drop, ring-only, stroke+shadow |

## 2. Accuracy by Surface Theme

| Theme | Tasks | Exact Match | Presence Acc |
|---|---|---|---|
| `white-on-gray` | 43 | 65.1% | 97.7% |
| `white-on-white` | 16 | 81.2% | 100.0% |
| `gray-tint-on-white` | 25 | 68.0% | 96.0% |
| `blue-tint-on-white` | 13 | 53.8% | 100.0% |
| `dark-mode` | 23 | 39.1% | 100.0% |

## 3. Accuracy by Corner Curvature

| Curvature | Tasks | Radius Acc | Exact Match |
|---|---|---|---|
| `sharp` | 21 | 0.0% | 76.2% |
| `subtle` | 21 | 0.0% | 57.1% |
| `medium` | 43 | 0.0% | 48.8% |
| `large` | 14 | 0.0% | 64.3% |
| `pill` | 21 | 0.0% | 76.2% |

## 4. Accuracy by Stroke Thickness

| Thickness | Tasks | Width Acc | Exact Match |
|---|---|---|---|
| `1px` | 50 | 0.0% | 66.0% |
| `0px` | 28 | 0.0% | 28.6% |
| `2px` | 24 | 0.0% | 66.7% |
| `4px` | 14 | 0.0% | 92.9% |
| `8px` | 4 | 0.0% | 100.0% |
