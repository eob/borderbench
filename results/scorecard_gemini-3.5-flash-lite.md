# BorderBench Scorecard: `gemini-3.5-flash-lite`

- **Total Tasks**: 120
- **All-Correct (Exact Match)**: **38.3%**
- **Border Presence Accuracy**: **94.2%**
- **Average Latency**: 0.94s / task
- **Total Cost**: $0.0000

## 1. Dimension Accuracy Breakdown

| Dimension | Accuracy | Description |
|---|---|---|
| **Border Presence** | **94.2%** | Binary detection of container border |
| **Edge Selectivity** | **92.5%** | All-4, top, bottom, left callout bar, none |
| **Stroke Style** | **94.2%** | solid, dashed, dotted, double, none |
| **Stroke Width** | **92.5%** | hairline (1px), medium (2px), thick (4px), heavy (8px), none |
| **Corner Curvature** | **72.5%** | sharp, subtle (3px), medium (8px), large (18px), pill |
| **Corner Uniformity** | **92.5%** | all-corners, top-only, asymmetric |
| **Elevation & Shadow** | **65.8%** | flat, subtle-drop, floating-drop, ring-only, stroke+shadow |

## 2. Accuracy by Surface Theme

| Theme | Tasks | Exact Match | Presence Acc |
|---|---|---|---|
| `white-on-gray` | 43 | 37.2% | 90.7% |
| `white-on-white` | 16 | 50.0% | 93.8% |
| `gray-tint-on-white` | 25 | 48.0% | 92.0% |
| `blue-tint-on-white` | 13 | 30.8% | 100.0% |
| `dark-mode` | 23 | 26.1% | 100.0% |

## 3. Accuracy by Corner Curvature

| Curvature | Tasks | Radius Acc | Exact Match |
|---|---|---|---|
| `sharp` | 21 | 0.0% | 52.4% |
| `subtle` | 21 | 0.0% | 38.1% |
| `medium` | 43 | 0.0% | 11.6% |
| `large` | 14 | 0.0% | 57.1% |
| `pill` | 21 | 0.0% | 66.7% |

## 4. Accuracy by Stroke Thickness

| Thickness | Tasks | Width Acc | Exact Match |
|---|---|---|---|
| `1px` | 50 | 0.0% | 38.0% |
| `0px` | 28 | 0.0% | 35.7% |
| `2px` | 24 | 0.0% | 37.5% |
| `4px` | 14 | 0.0% | 50.0% |
| `8px` | 4 | 0.0% | 25.0% |
