# M11.5 Training Intent Scoring

M11.5 turns explicit learner engagement signals into a deterministic 0–100 training intent score.

## Signal weights

| Signal | Weight |
|---|---:|
| Campaign engaged | 5 |
| Course viewed | 10 |
| Specific course selected | 15 |
| Course details requested | 15 |
| Session registered | 20 |
| Session attended | 20 |
| Course question asked | 15 |
| Counselling requested | 25 |
| Enquiry submitted | 30 |

The score is capped at 100.

## Intent stages

- 0–29: Awareness
- 30–49: Interested
- 50–69: Engaged
- 70–84: High Intent
- 85–100: Enquiry Ready

## Flow

Learner Profile → Career Persona → Career Path → Engagement Signals → Intent Score → Intent Stage → Recommended Follow-up

## Governance

The feature uses synthetic data and explicit supplied signals only. It does not infer sensitive attributes, send messages, update CRM records, or execute campaigns.
