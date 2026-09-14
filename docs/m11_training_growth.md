# M11 — Training Growth & Campaign 360

CampaignOS M11 introduces a reusable vertical layer for training lead generation while preserving the vendor-neutral campaign operations core.

## End-user promise

> Understand the training campaign, identify the right audience, recommend a relevant learning path, track intent and decide what to do next.

## HAC implementation direction

Hands-On Agile Coaching is the first vertical example. The public HAC site currently lists training areas including Azure Data Engineering, DevOps, Python, QA, AI/ML, Cybersecurity, Generative/Agentic AI, Power BI, Technical Business Analysis, Scrum/Product Owner, PMP, SAFe and Data Science, plus other offerings.

The catalogue in `data/training/hac_programs.csv` is for CampaignOS demonstration purposes. It is not a claim that every program is currently delivered on-demand or on a specific schedule.

## Architecture

```text
CampaignOS Core
      |
      +-- Campaign
      +-- Segmentation
      +-- Scoring
      +-- Journey
      +-- Content
      +-- Analytics
      +-- Copilot
      +-- Agentic Operations
      |
      v
Training Growth Layer
      |
      +-- Program catalogue
      +-- Career personas
      +-- Career Path Finder
      +-- Training intent
      +-- Campaign templates
      +-- Lead funnel
      +-- Training campaign intelligence
      |
      v
HAC Vertical Configuration
```

## First concrete workflow

`Training Program -> Audience -> Campaign -> Content -> Engagement -> Intent -> Enquiry -> Human follow-up`
