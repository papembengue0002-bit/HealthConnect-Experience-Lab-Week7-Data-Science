# Week 7 Testing, Refinement & Validation Record

| Test / scenario | Expected result | Actual result | Status | Finding | Action | Retest result | Evidence |
|---|---|---|---|---|---|---|---|
| Week 6 candidate vs Week 5 baseline ROC-AUC | Candidate should materially improve discrimination | Candidate ROC-AUC 0.668 vs baseline 0.675 | Fail | Tree candidate did not improve discrimination | Removed redundant constructed segment and calendar variables; returned to interpretable regularised model | Refined ROC-AUC 0.676 | `testing_results.json`, Figure 02 |
| Patient-leakage check | No patient in both train and test | 0 shared patients | Pass | None | Kept grouped split | Pass | `testing_results.json` |
| Threshold-selection test | Threshold chosen without using final test labels | Selected 0.40 on patient-disjoint validation data | Pass | 0.50 was not justified for intervention workflow | Used validation F1 criterion | Refined test F1 0.672 | `testing_results.json`, Figure 01 |
| Error-pattern test | Errors should be quantified by risk-relevant segments | FP=570, FN=188 | Pass | Remaining false positives/falses negatives require human review | Added error and segment monitoring requirements | Documented for Week 8 | Figure 04 |
| Data Analytics -> Data Science validation | Analytics segments should match model feature logic | Requires an actual HC-POD analytics output | Pending | Counterpart evidence not yet attached | Use `HC_POD_Testing_Evidence_Template.md` with colleague/report link | Pending real counterpart confirmation | Template |
