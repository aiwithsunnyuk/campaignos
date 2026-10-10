# CampaignOS M13 — Reetha IT Hub Readiness Board

## Purpose

Connect the CampaignOS product surface to the actual Reetha IT Hub business
objective.

CampaignOS must eventually help Reetha:

1. Define and promote its offerings
2. Identify target audiences
3. Acquire and understand prospects
4. Run campaigns
5. Recommend next actions
6. Obtain human approval
7. Execute approved actions
8. Measure business outcomes
9. Learn from those outcomes

M13 establishes the product and integration readiness view before deeper
backend implementation.

---

# 1. Reetha Business Loop

Offerings
  ↓
Target Audiences
  ↓
Campaigns
  ↓
Prospects / Leads
  ↓
Engagement
  ↓
Registration / Opportunity
  ↓
Enrollment / Conversion
  ↓
Business Outcome
  ↓
Measure
  ↓
Learn
  ↺

---

# 2. Readiness Board

| Capability | CampaignOS Today | Reetha Input Required | UI Destination | Real Integration |
|---|---|---|---|---|
| Offerings | Partial / synthetic | Actual offering catalogue | Acquire | Later |
| Target audiences | Partial | Audience definitions and segmentation criteria | Acquire / Understand | Later |
| Lead generation | Strong synthetic foundation | Real lead sources | Acquire | Yes |
| Lead 360 | Strong synthetic foundation | Real lead/contact data | Understand | Yes |
| Training programmes | Synthetic foundation | Actual programmes, schedules and capacity | Understand / Act | Yes |
| Training registrations | Synthetic | Actual registration data | Measure | Yes |
| Training enrollments | Synthetic | Actual enrollment/outcome data | Measure | Yes |
| SAP services | Concept / capability surface | Actual SAP services and business offerings | Acquire / Understand | Yes |
| SAP project context | Not live | Authorized SAP/project data | Understand | Yes |
| Campaigns | Strong foundation | Reetha campaigns and campaign sources | Acquire | Yes |
| Audience engagement | Synthetic | Real engagement events | Understand / Measure | Yes |
| Next Best Action | Strong foundation | Real signals | Decide | Yes |
| Campaign recommendations | Foundation | Real campaign performance | Decide | Later |
| Approval workflow | Foundation | Reetha approval policy | Approve | Later |
| Campaign execution | Dry-run / foundation | Authorized execution systems | Act | Yes |
| CRM actions | Foundation | Reetha CRM/system access | Act | Yes |
| Marketing channels | Foundation | Connected channel accounts | Act | Yes |
| Campaign measurement | Synthetic | Real campaign outcomes | Measure | Yes |
| Revenue / business outcomes | Limited | Actual business outcome data | Measure | Yes |
| Learning loop | Foundation | Real outcome history | Learn | Later |
| Identity | Google OIDC | Reetha users/accounts | Admin | Connected |
| Tenant membership | Implemented | Reetha user/role mapping | Admin | Connected |
| Governance | Foundation | Reetha governance policy | Approve / Admin | Later |

---

# 3. Current State

## GREEN — Existing / usable foundation

- CampaignOS multi-tenant foundation
- Google identity
- Tenant membership
- Identity-backed workspace
- Synthetic Reetha tenant
- Lead 360
- Marketing intelligence
- Explainable signals
- Next Best Action
- Campaign planning
- Campaign analytics
- Campaign Copilot
- Agentic Campaign Operations
- Training-oriented surfaces
- Streamlit Command Center

## AMBER — Foundation exists, but business integration is missing

- Reetha offering catalogue
- Target audience definitions
- Real campaign data
- Training programme catalogue
- Training registration/enrollment
- SAP service catalogue
- Business outcome model
- Approval policy
- Real marketing channels
- Real CRM context

## RED — Not connected yet

- Real Reetha SAP server/data
- Real Reetha CRM data
- Real Reetha campaign platforms
- Real Reetha training system data
- Production execution credentials
- Real-time event feeds
- Production business outcome feeds

RED means "not connected", not "unsupported".

---

# 4. Data Integration States

CampaignOS will support three explicit operating states.

## DEMO

Synthetic data
  ↓
CampaignOS
  ↓
UI + intelligence

Purpose:
Demonstration, development and testing.

---

## SHADOW / INTEGRATION READY

Authorized Reetha data
  ↓
Tenant-specific adapters
  ↓
CampaignOS
  ↓
Existing UI + intelligence

Purpose:
Validate CampaignOS against real Reetha information without autonomous
execution.

---

## LIVE

Reetha business systems
  ↓
Authorized ingestion
  ↓
CampaignOS tenant context
  ↓
Intelligence
  ↓
Human approval
  ↓
Approved execution
  ↓
Measurement
  ↓
Learning

Purpose:
Production operation.

---

# 5. Reetha Command Center Target

The Reetha Command Center should eventually answer:

## What are we selling?

- Current offerings
- Training programmes
- SAP services
- AI / GenAI services
- Other active business offerings

## Who should we target?

- Audience segments
- Personas
- Geography
- Industry
- Role
- Skills
- Intent
- Existing engagement

## What is happening?

- Campaign reach
- Engagement
- Registrations
- Opportunities
- Enrollments
- Conversions
- Business outcomes

## What should we do next?

- Priority audience
- Priority leads
- Recommended campaigns
- Recommended follow-ups
- Recommended channels

## What requires human approval?

- Campaign launch
- Audience activation
- Content
- Budget
- AI recommendations
- External actions

## What happened after execution?

- Engagement
- Conversion
- Enrollment
- Revenue / business outcome
- Campaign effectiveness

## What did we learn?

- Successful audiences
- Successful offerings
- Successful channels
- Successful messages
- Failed approaches
- Next recommendations

---

# 6. SAP Integration Boundary

CampaignOS must not assume direct SAP access exists.

Before implementing a real SAP integration, Reetha must establish:

- SAP system type
- SAP environment
- Authorized API/interface
- Available business objects
- Authentication mechanism
- Network/connectivity requirements
- Read/write permissions
- Data ownership
- Security requirements
- Refresh expectations

Until those are confirmed, CampaignOS uses synthetic or controlled integration
contracts.

No fake "real-time SAP" implementation should be created.

---

# 7. M13 Product Surface Mapping

| Business Need | CampaignOS Surface |
|---|---|
| Offerings | Acquire |
| Target audience | Acquire / Understand |
| Lead intelligence | Understand |
| SAP/project intelligence | Understand |
| Recommendations | Decide |
| Human governance | Approve |
| Execution | Act |
| Performance | Measure |
| Feedback / optimization | Learn |
| Tenant / users / integrations | Admin |

---

# 8. M13 Definition of Done

- [ ] Reetha business objective represented in CampaignOS
- [ ] Offering → Audience → Campaign → Lead → Outcome loop represented
- [ ] Existing Lead 360 reused rather than rebuilt
- [ ] Existing Next Best Action reused rather than rebuilt
- [ ] Reetha-specific UI surfaces identified
- [ ] Missing real-data integrations explicitly identified
- [ ] SAP integration boundary documented
- [ ] Demo / Shadow / Live states explicitly separated
- [ ] No unsupported claims of real-time integration
- [ ] Streamlit UI validated against the business loop
- [ ] Missing capabilities represented as safe UI contracts/placeholders
- [ ] Backend implementation deferred until the corresponding business
      surface is validated
