# M12.4 Reetha Synthetic Data Model

## Purpose

Create a realistic synthetic GTM dataset for the Reetha IT Hub
tenant without modifying the existing CampaignOS demo dataset.

The dataset is synthetic and must not be interpreted as real
Reetha customer or operational data.

## Tenant

- tenant_id: reetha
- tenant_name: Reetha IT Hub
- initial data_mode: synthetic

## Entities

### Courses

Represents Reetha's training/course catalogue.

Key fields:

- course_id
- tenant_id
- name
- category
- delivery_mode
- duration
- price
- status

### Campaigns

Represents marketing campaigns.

Key fields:

- campaign_id
- tenant_id
- name
- channel
- campaign_type
- status
- start_date
- end_date
- budget

### Leads

Represents prospective learners/customers.

Key fields:

- lead_id
- tenant_id
- first_name
- last_name
- email
- phone
- source
- lifecycle_stage
- interest
- course_id
- lead_score
- created_at
- updated_at

### Engagements

Represents behavioral interactions.

Key fields:

- engagement_id
- tenant_id
- lead_id
- channel
- event_type
- campaign_id
- course_id
- occurred_at
- metadata

### Registrations

Represents demo, webinar, counselling or course registrations.

Key fields:

- registration_id
- tenant_id
- lead_id
- course_id
- registration_type
- status
- registered_at
- converted_at

### Enrollments

Represents successful conversion into a course.

Key fields:

- enrollment_id
- tenant_id
- lead_id
- course_id
- enrollment_status
- enrollment_date
- amount
- payment_status

## Relationship Rules

Campaigns generate or influence Leads.

Leads can generate multiple Engagements.

Leads may register for a Course.

A Lead may have multiple registrations.

A successful registration may result in an Enrollment.

Every entity is tenant-scoped.

No Reetha dataset may contain records belonging to another tenant.

## Data Integrity Rules

1. Every record must contain `tenant_id = reetha`.
2. Foreign keys must reference records within the Reetha dataset.
3. Lead IDs must be unique.
4. Course IDs must be unique.
5. Campaign IDs must be unique.
6. Engagements must reference an existing lead.
7. Registrations must reference an existing lead and course.
8. Enrollments must reference an existing lead and course.
9. Synthetic data must never be represented as real customer data.
10. Existing `data/synthetic/` datasets must remain unchanged.

## Funnel

The synthetic dataset should support analysis of:

Acquire
→ Understand
→ Decide
→ Approve
→ Act
→ Measure
→ Learn

The primary marketing funnel is:

Campaign
→ Lead
→ Engagement
→ Registration
→ Enrollment
