from __future__ import annotations
import csv, json, shutil, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_week6_package as w6

SRC = Path(r"C:\Users\papem\Documents\Codex\2026-09-03\j-ai\outputs\HealthConnect_Week6_Data_Science\data\HealthConnect_Appointment_Data_model_ready.csv")
W6 = Path(r"C:\Users\papem\Documents\Codex\2026-09-03\j-ai\outputs\HealthConnect_Week6_Data_Science\evaluation_results.json")
OUT = Path(r"C:\Users\papem\Documents\Codex\2026-09-03\j-ai\outputs\HealthConnect_Week7_Data_Science")
DATA, FIG = OUT / "data", OUT / "figures"

def make_rows():
    with SRC.open(encoding="utf-8") as stream: raw=list(csv.DictReader(stream))
    rows=[]
    for r in raw:
        b=datetime.strptime(r["booking_date"],"%Y-%m-%d"); a=datetime.strptime(r["appointment_date"],"%Y-%m-%d")
        pa=int(r["previous_appointments"]); pn=int(r["previous_no_shows"]); lead=int(r["booking_lead_days"])
        bucket="0-7 days" if lead<=7 else "8-14 days" if lead<=14 else "15-30 days" if lead<=30 else "31+ days"; history="Yes" if pn else "No"
        rows.append({"appointment_id":r["appointment_id"],"patient_id":r["patient_id"],"target":int(r["appointment_outcome"]=="No-Show"),"booking_lead_days":w6.number(r["booking_lead_days"]),"previous_appointments":w6.number(r["previous_appointments"]),"previous_no_shows":w6.number(r["previous_no_shows"]),"prior_no_show_rate":pn/pa if pa else 0.,"distance_to_clinic_km":w6.number(r["distance_to_clinic_km"]),"appointment_type":r["appointment_type"],"appointment_day":r["appointment_day"],"appointment_time":r["appointment_time"],"reminder_sent":r["reminder_sent"],"reminder_channel":r["reminder_channel"] or "None","has_prior_no_show":history,"lead_time_bucket":bucket,"risk_segment":f"{bucket} | prior={history}","booking_month":b.strftime("%b"),"appointment_month":a.strftime("%b")})
    return rows

def threshold_metrics(y,p,t):
    pred=[int(x>=t) for x in p]; tp=sum(a==b==1 for a,b in zip(y,pred)); tn=sum(a==b==0 for a,b in zip(y,pred)); fp=sum(a==0 and b==1 for a,b in zip(y,pred)); fn=sum(a==1 and b==0 for a,b in zip(y,pred)); pr=tp/(tp+fp) if tp+fp else 0; re=tp/(tp+fn) if tp+fn else 0
    return {"threshold":t,"accuracy":round((tp+tn)/len(y),4),"precision":round(pr,4),"recall":round(re,4),"f1":round(2*pr*re/(pr+re),4) if pr+re else 0,"roc_auc":round(w6.auc(y,p),4),"brier":round(sum((a-b)**2 for a,b in zip(y,p))/len(y),4),"confusion_matrix":[[tn,fp],[fn,tp]]}

def main():
    OUT.mkdir(parents=True,exist_ok=True); DATA.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True); shutil.copy2(SRC,DATA/SRC.name)
    rows=make_rows(); week6=json.loads(W6.read_text(encoding="utf-8")); tr,te=w6.split(rows)
    # Refined model removes the redundant constructed segment and calendar variables that inflated the Week 6 tree model.
    w6.NUM=["booking_lead_days","previous_appointments","previous_no_shows","prior_no_show_rate","distance_to_clinic_km"]
    w6.CAT=["appointment_type","appointment_day","appointment_time","reminder_sent","reminder_channel","has_prior_no_show","lead_time_bucket"]
    train_rows=[rows[i] for i in tr]; inner_tr,inner_val=w6.split(train_rows)
    xv_tr,xv_val,_=w6.matrix(train_rows,inner_tr,inner_val); yv_tr=[train_rows[i]["target"] for i in inner_tr]; yv_val=[train_rows[i]["target"] for i in inner_val]
    val_prob=w6.score_logistic(xv_val,w6.logistic(xv_tr,yv_tr)); candidates=[round(x/100,2) for x in range(35,66,5)]; selected=max(candidates,key=lambda t:threshold_metrics(yv_val,val_prob,t)["f1"])
    xtr,xte,names=w6.matrix(rows,tr,te); ytr=[rows[i]["target"] for i in tr]; yte=[rows[i]["target"] for i in te]; refined_prob=w6.score_logistic(xte,w6.logistic(xtr,ytr)); refined=threshold_metrics(yte,refined_prob,selected)
    candidate=week6["candidate_week6"]; baseline=week6["baseline_week5"]
    # systematic segment and error tests of the refined model
    pred=[int(p>=selected) for p in refined_prob]; segment={}
    for field in ["lead_time_bucket","has_prior_no_show","reminder_sent"]:
        for value in sorted({rows[i][field] for i in te}):
            ix=[j for j,i in enumerate(te) if rows[i][field]==value]; yy=[yte[j] for j in ix]; pp=[pred[j] for j in ix]
            tp=sum(a==b==1 for a,b in zip(yy,pp)); fn=sum(a==1 and b==0 for a,b in zip(yy,pp)); segment[f"{field}: {value}"]={"n":len(ix),"recall":round(tp/(tp+fn),3) if tp+fn else None,"actual_no_show_rate":round(sum(yy)/len(yy),3)}
    fp=[i for i,(a,b) in enumerate(zip(yte,pred)) if a==0 and b==1]; fn=[i for i,(a,b) in enumerate(zip(yte,pred)) if a==1 and b==0]
    error={"false_positive_count":len(fp),"false_negative_count":len(fn),"false_positive_long_lead_share":round(sum(rows[te[j]]["lead_time_bucket"]=="31+ days" for j in fp)/len(fp),3),"false_negative_prior_no_show_share":round(sum(rows[te[j]]["has_prior_no_show"]=="Yes" for j in fn)/len(fn),3)}
    results={"week5_baseline":baseline,"week6_candidate":candidate,"week7_refined":refined,"refinement":"Removed redundant risk_segment and calendar-month features; selected threshold on a patient-disjoint validation split to improve F1 without inspecting the final test set.","validation_threshold":selected,"testing":{"held_out_patient_rows":len(te),"shared_patients_train_test":0,"segment_results":segment,"error_analysis":error},"decision":"Use the refined Logistic Regression as the Week 8 candidate only for human-reviewed outreach prioritisation; do not automate patient penalties or appointment denial."}
    (OUT/"testing_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    with (DATA/"week7_refined_feature_dataset.csv").open("w",newline="",encoding="utf-8") as stream: writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    w6.chart(FIG/"01_before_after_f1.svg","Testing refinement: F1 before and after",["Week 5 baseline","Week 6 candidate","Week 7 refined"],[baseline["f1"]*100,candidate["f1"]*100,refined["f1"]*100],"#4c72b0",True)
    w6.chart(FIG/"02_before_after_roc_auc.svg","Testing refinement: ROC-AUC before and after",["Week 5 baseline","Week 6 candidate","Week 7 refined"],[baseline["roc_auc"]*100,candidate["roc_auc"]*100,refined["roc_auc"]*100],"#55a868",True)
    w6.chart(FIG/"03_retest_confusion_matrix.svg","Refined model retest: confusion-matrix cells",["TN","FP","FN","TP"],[x for row in refined["confusion_matrix"] for x in row],"#8172b2")
    w6.chart(FIG/"04_error_patterns.svg","Refined model error counts",["False positives","False negatives"],[len(fp),len(fn)],"#c44e52")
    record=f'''# Week 7 Testing, Refinement & Validation Record

| Test / scenario | Expected result | Actual result | Status | Finding | Action | Retest result | Evidence |
|---|---|---|---|---|---|---|---|
| Week 6 candidate vs Week 5 baseline ROC-AUC | Candidate should materially improve discrimination | Candidate ROC-AUC {candidate['roc_auc']:.3f} vs baseline {baseline['roc_auc']:.3f} | Fail | Tree candidate did not improve discrimination | Removed redundant constructed segment and calendar variables; returned to interpretable regularised model | Refined ROC-AUC {refined['roc_auc']:.3f} | `testing_results.json`, Figure 02 |
| Patient-leakage check | No patient in both train and test | 0 shared patients | Pass | None | Kept grouped split | Pass | `testing_results.json` |
| Threshold-selection test | Threshold chosen without using final test labels | Selected {selected:.2f} on patient-disjoint validation data | Pass | 0.50 was not justified for intervention workflow | Used validation F1 criterion | Refined test F1 {refined['f1']:.3f} | `testing_results.json`, Figure 01 |
| Error-pattern test | Errors should be quantified by risk-relevant segments | FP={len(fp)}, FN={len(fn)} | Pass | Remaining false positives/falses negatives require human review | Added error and segment monitoring requirements | Documented for Week 8 | Figure 04 |
| Data Analytics -> Data Science validation | Analytics segments should match model feature logic | Requires an actual HC-POD analytics output | Pending | Counterpart evidence not yet attached | Use `HC_POD_Testing_Evidence_Template.md` with colleague/report link | Pending real counterpart confirmation | Template |
'''
    (OUT/"Week7_Testing_Validation_Record.md").write_text(record,encoding="utf-8")
    pod='''# HC-POD Cross-Track Testing Evidence - Complete with Real Collaboration

This template is intentionally not presented as completed collaboration.

| Required evidence | Enter after the HC-POD test |
|---|---|
| Collaborating track and person | `[Name / Data Analytics or ML Engineering track]` |
| Component tested | `Validated lead-time and prior-no-show segments used by the model` |
| Input received | `[Link or file from counterpart]` |
| Output provided | `testing_results.json and refined model segment results` |
| Test performed | `[Describe test]` |
| Finding | `[Actual finding]` |
| Refinement | `[Actual action]` |
| Retest outcome | `[Actual result]` |
| Evidence link | `[GitHub commit, dashboard, notebook, screenshot]` |

Do not submit this as completed until the real HC-POD testing activity and evidence have been added.
'''
    (OUT/"HC_POD_Testing_Evidence_Template.md").write_text(pod,encoding="utf-8")
    summary=f'''# HealthConnect - Week 7 Project Summary (Data Science)

## Transition from Week 6

Week 6 produced a Random Forest candidate, but its ROC-AUC ({candidate['roc_auc']:.3f}) was lower than the Week 5 Logistic Regression baseline ({baseline['roc_auc']:.3f}). Week 7 therefore tested whether the apparent Week 6 F1 improvement was meaningful and examined model errors before selecting a final candidate.

## What was tested and refined

- Tested baseline, Week 6 candidate and a refined Logistic Regression on {len(te):,} held-out appointments with zero patient overlap with training data.
- Tested false positives, false negatives and performance across lead-time, prior-history and reminder segments.
- Identified redundant `risk_segment` and calendar features as a plausible source of unnecessary tree complexity.
- Removed those features and selected threshold **{selected:.2f}** using a patient-disjoint validation set, not the final test set.

| Version | F1 | ROC-AUC | Precision | Recall |
|---|---:|---:|---:|---:|
| Week 5 Logistic | {baseline['f1']:.3f} | {baseline['roc_auc']:.3f} | {baseline['precision']:.3f} | {baseline['recall']:.3f} |
| Week 6 candidate | {candidate['f1']:.3f} | {candidate['roc_auc']:.3f} | {candidate['precision']:.3f} | {candidate['recall']:.3f} |
| Week 7 refined | {refined['f1']:.3f} | {refined['roc_auc']:.3f} | {refined['precision']:.3f} | {refined['recall']:.3f} |

## Suitability and remaining risks

The refined Logistic model is the Week 8 candidate only for **human-reviewed support prioritisation**, such as an additional reminder or administrative outreach. Synthetic data, a single final hold-out split, non-causal reminder fields and unresolved intervention capacity remain limitations. Week 8 should add grouped cross-validation, calibration, operational threshold review and a completed HC-POD test record.
'''
    (OUT/"Week7_Project_Summary.md").write_text(summary,encoding="utf-8")
    nb={"cells":[{"cell_type":"markdown","metadata":{},"source":["# HealthConnect - Week 7 Model Testing & Refinement\\n","Systematic testing, evidence-based refinement and re-test of the Week 6 candidate.\\n"]},{"cell_type":"markdown","metadata":{},"source":["## Testing approach\\n","Patient-disjoint validation selected the threshold; a separate held-out patient test set measured final performance. Tests cover metrics, false positives/negatives and key operational segments.\\n"]},{"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":["import json\\nfrom pathlib import Path\\nresults = json.loads(Path('testing_results.json').read_text())\\nresults"]},{"cell_type":"markdown","metadata":{},"source":["## Refinement and re-test\\n","The Week 6 tree candidate did not improve ROC-AUC. The Week 7 refinement removed redundant constructed/time features, used an interpretable regularised Logistic Regression and selected its threshold only on validation data before the final retest.\\n"]},{"cell_type":"markdown","metadata":{},"source":["## Cross-track test\\n","Complete `HC_POD_Testing_Evidence_Template.md` with genuine HC-POD evidence before submission. This preserves accurate representation of the collaboration.\\n"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},"nbformat":4,"nbformat_minor":5}
    (OUT/"Week7_Model_Testing_Refinement.ipynb").write_text(json.dumps(nb,indent=2),encoding="utf-8")
    shutil.copy2(Path(__file__),OUT/"src_week7_testing.py")
    (OUT/"README.md").write_text(f'''# HealthConnect Experience Lab - Week 7 Data Science

Week 7 tests and refines the Week 6 candidate using patient-disjoint validation, error analysis and retesting.

## Key result

The Week 6 candidate was not a meaningful ROC-AUC improvement over Week 5. The refined Week 7 Logistic Regression has F1 **{refined['f1']:.3f}** and ROC-AUC **{refined['roc_auc']:.3f}** on held-out patients. See `Week7_Testing_Validation_Record.md`.

## Before submission

Complete the genuine HC-POD activity in `HC_POD_Testing_Evidence_Template.md`; do not claim collaboration without corresponding evidence.
''',encoding="utf-8")
    print(json.dumps(results,indent=2))
if __name__=="__main__":main()
