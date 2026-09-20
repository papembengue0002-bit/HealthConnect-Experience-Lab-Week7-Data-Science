# HC-POD Cross-Track Testing & Validation Record

## Collaboration details

| Field | Evidence |
|---|---|
| Collaborating track | Data Analytics - @renishamondi (Slack) |
| Data Science contributor | M'Bengue Mama (Slack) |
| Project dependency | Validate that the operational segments used by the no-show model agree with independently calculated analytics KPIs. |
| Data Science output provided | Week 7 test results, error analysis and refined model segment results. |
| Data Analytics output received | HealthConnect Analytics Testing & Refinement Report/Notebook, cleaned dataset, refined charts and written segment-validation results. |
| Testing activity | Compared Data Science held-out-test no-show rates with Data Analytics baseline rates across booking lead time, prior no-show history and reminder status. |

## Test -> finding -> action -> retest

| Segment | Data Science test set | Data Analytics baseline | Difference (percentage points) | Result |
|---|---:|---:|---:|---|
| Booking lead: 0-7 days | 29.3% | 29.5% | -0.2 | Pass |
| Booking lead: 8-14 days | 33.5% | 35.2% | -1.7 | Pass |
| Booking lead: 15-30 days | 45.5% | 45.5% | 0.0 | Pass |
| Booking lead: 31+ days | 63.7% | 64.0% | -0.3 | Pass |
| No prior no-shows | 45.6% | 46.3% | -0.7 | Pass |
| Has prior no-shows | 57.8% | 57.1% | +0.7 | Pass |
| No reminder | 53.7% | 54.6% | -0.9 | Pass |
| Reminder sent | 49.6% | 49.9% | -0.3 | Pass |

**Finding:** all independently validated segment rates were within 1.7 percentage points. The strongest high-risk pattern remains long booking lead time. Data Analytics also confirmed the reminder-attendance association and the policy interpretation that predictions should guide supportive outreach only.

**Action taken:** retained lead time, prior no-show history and reminder status as validated model inputs; added a Week 8 monitoring requirement to compare model segment rates against Data Analytics KPIs. The 0.40 threshold remains appropriate for friendly reminders because the model achieves 99.8% recall for the 31+ day high-risk segment, while false positives do not trigger penalties.

**Retest / validated outcome:** the refined model's held-out segment results align with the independent analytics baseline. This supports using the model for human-reviewed outreach prioritisation, not automatic denial, penalties or overbooking.

## Evidence links

- Analytics report PDF: `https://analystlabafrica.slack.com/files/U0BPAPTA3M1/F0C2YS38WTD/healthconnect_analytics_testing___refinement_report.pdf`
- Analytics notebook: `https://analystlabafrica.slack.com/files/U0BPAPTA3M1/F0C350HNRKL/healthconnect_analytics_testing___refinement_report.ipynb`
- Analytics cleaned data: `https://analystlabafrica.slack.com/files/U0BPAPTA3M1/F0C3060TQBX/healthconnect_appointment_data_cleaned.csv`
- Analytics refined charts (Slack): `https://analystlabafrica.slack.com/files/U0BPAPTA3M1/F0C334LTSMC/healthconnect_refined_charts.png`
- Data Science evidence: `testing_results.json`, `Week7_Testing_Validation_Record.md`, and `figures/`

> Collaboration identities have been recorded from the HC-POD Slack exchange. Add the date or a screenshot of the exchange if your mentor requests it.
