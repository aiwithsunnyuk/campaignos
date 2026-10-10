# CampaignOS M13 Product Surface Board

## Objective

Establish the complete CampaignOS GTM operating surface in Streamlit before
deepening backend implementation.

M13 prioritizes product flow, navigation, UX coherence, and functional
screen-level behavior.

---

## GTM Operating Loop

Acquire
  ↓
Understand
  ↓
Decide
  ↓
Approve
  ↓
Act
  ↓
Measure
  ↓
Learn
  ↺

---

## Product Surfaces

### 1. Home

Purpose:
Executive command center.

Expected experience:
- GTM health
- Pipeline overview
- Campaign overview
- Lead/engagement summary
- Priorities
- Alerts
- Pending approvals
- AI recommendations

Status: M13

---

### 2. Acquire

Purpose:
Demand generation and acquisition.

Expected experience:
- Campaigns
- Leads
- Sources
- Channels
- Social
- Forms
- Opportunities

Status: M13

---

### 3. Understand

Purpose:
Customer and prospect intelligence.

Expected experience:
- Lead 360
- Account 360
- Engagement
- Journey
- Segments
- Signals
- Intent

Existing capability:
- Lead 360

Status: M13 surface only

---

### 4. Decide

Purpose:
Decision intelligence.

Expected experience:
- Next Best Action
- Lead prioritization
- Campaign recommendations
- Audience recommendations
- Channel recommendations
- AI insights

Existing capability:
- Lead Next Best Action

Status: M13 surface only

---

### 5. Approve

Purpose:
Human governance before execution.

Expected experience:
- Campaign approvals
- Content approvals
- Audience approvals
- Budget approvals
- AI recommendation approvals
- Execution approvals

Status: Initial M13 surface

---

### 6. Act

Purpose:
GTM execution.

Expected experience:
- Campaign launch
- Email
- Social
- CRM actions
- Lead assignment
- Follow-up
- Automation

M13 principle:
Actions may initially be simulated.

Status: Initial M13 surface

---

### 7. Measure

Purpose:
Performance and business outcomes.

Expected experience:
- Campaign performance
- Funnel
- Engagement
- Conversion
- Attribution
- ROI
- Executive KPIs

Status: M13 surface

---

### 8. Learn

Purpose:
Close the GTM feedback loop.

Expected experience:
- What worked?
- What failed?
- Audience response
- Channel performance
- Conversion signals
- Learning signals
- Recommendations

Status: Initial M13 surface

---

### 9. Admin

Purpose:
Tenant and operating configuration.

Expected experience:
- Tenant
- Identity
- Membership
- Roles
- Configuration
- Integrations
- Governance

Existing capability:
- Google identity
- Tenant membership
- Identity session

Status: M13 surface

---

## M13 Engineering Principle

Do not deepen backend capabilities merely to populate a screen.

Build the complete product surface first.

Where functionality already exists:
- reuse it.

Where functionality does not exist:
- create a clean UI contract or safe simulation.

Deep backend implementation belongs to subsequent milestones.

---

## M13 Definition of Done

- [ ] Complete CampaignOS navigation exists
- [ ] Home surface is functional
- [ ] Acquire surface is functional
- [ ] Understand surface exposes Lead 360
- [ ] Decide surface exposes existing NBA
- [ ] Approve surface exists
- [ ] Act surface exists
- [ ] Measure surface exists
- [ ] Learn surface exists
- [ ] Admin surface exists
- [ ] Tenant context remains visible
- [ ] Google identity remains functional
- [ ] Streamlit navigation works end-to-end
- [ ] Existing functionality is not duplicated
- [ ] Synthetic/demo data remains intact
- [ ] Full test suite remains green
- [ ] Browser walkthrough completed
