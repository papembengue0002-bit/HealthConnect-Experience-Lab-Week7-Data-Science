# HealthConnect - Week 7 Project Summary (Data Science)

## Transition from Week 6

Week 6 produced a Random Forest candidate, but its ROC-AUC (0.668) was lower than the Week 5 Logistic Regression baseline (0.675). Week 7 therefore tested whether the apparent Week 6 F1 improvement was meaningful and examined model errors before selecting a final candidate.

## What was tested and refined

- Tested baseline, Week 6 candidate and a refined Logistic Regression on 1,903 held-out appointments with zero patient overlap with training data.
- Tested false positives, false negatives and performance across lead-time, prior-history and reminder segments.
- Identified redundant `risk_segment` and calendar features as a plausible source of unnecessary tree complexity.
- Removed those features and selected threshold **0.40** using a patient-disjoint validation set, not the final test set.

| Version | F1 | ROC-AUC | Precision | Recall |
|---|---:|---:|---:|---:|
| Week 5 Logistic | 0.632 | 0.675 | 0.621 | 0.645 |
| Week 6 candidate | 0.635 | 0.668 | 0.624 | 0.648 |
| Week 7 refined | 0.672 | 0.676 | 0.577 | 0.805 |

## Suitability and remaining risks

The refined Logistic model is the Week 8 candidate only for **human-reviewed support prioritisation**, such as an additional reminder or administrative outreach. Data Analytics independently validated the booking-lead, prior-no-show and reminder segments: all comparisons were within 1.7 percentage points of the Data Science held-out test set. This confirms that the feature logic is consistent with the analytical dashboard and supports retaining the 0.40 outreach threshold for the 31+ day high-risk segment. Synthetic data, a single final hold-out split, non-causal reminder fields and unresolved intervention capacity remain limitations. Week 8 should add grouped cross-validation, calibration and operational threshold review.
