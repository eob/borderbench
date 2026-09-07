# BorderBench Scorecard: `gemini-3.1-pro-preview`

- **Total Tasks**: 120
- **All-Correct (Exact Match)**: **68.3%**
- **Border Presence Accuracy**: **95.8%**
- **Average Latency**: 4.28s / task
- **Total Cost**: $0.0000

## 1. Dimension Accuracy Breakdown

| Dimension | Accuracy | Description |
|---|---|---|
| **Border Presence** | **95.8%** | Binary detection of container border |
| **Edge Selectivity** | **95.8%** | All-4, top, bottom, left callout bar, none |
| **Stroke Style** | **95.8%** | solid, dashed, dotted, double, none |
| **Stroke Width** | **95.0%** | hairline (1px), medium (2px), thick (4px), heavy (8px), none |
| **Corner Curvature** | **99.2%** | sharp, subtle (3px), medium (8px), large (18px), pill |
| **Corner Uniformity** | **96.7%** | all-corners, top-only, asymmetric |
| **Elevation & Shadow** | **71.7%** | flat, subtle-drop, floating-drop, ring-only, stroke+shadow |

## 2. Accuracy by Surface Theme

| Theme | Tasks | Exact Match | Presence Acc |
|---|---|---|---|
| `white-on-gray` | 43 | 88.4% | 97.7% |
| `white-on-white` | 16 | 56.2% | 93.8% |
| `gray-tint-on-white` | 25 | 64.0% | 88.0% |
| `blue-tint-on-white` | 13 | 61.5% | 100.0% |
| `dark-mode` | 23 | 47.8% | 100.0% |

## 3. Accuracy by Corner Curvature

| Curvature | Tasks | Radius Acc | Exact Match |
|---|---|---|---|
| `sharp` | 21 | 0.0% | 57.1% |
| `subtle` | 21 | 0.0% | 57.1% |
| `medium` | 43 | 0.0% | 79.1% |
| `large` | 14 | 0.0% | 64.3% |
| `pill` | 21 | 0.0% | 71.4% |

## 4. Accuracy by Stroke Thickness

| Thickness | Tasks | Width Acc | Exact Match |
|---|---|---|---|
| `1px` | 50 | 0.0% | 68.0% |
| `0px` | 28 | 0.0% | 60.7% |
| `2px` | 24 | 0.0% | 62.5% |
| `4px` | 14 | 0.0% | 85.7% |
| `8px` | 4 | 0.0% | 100.0% |
