# Grosso University — Ad Landing Page Command Center & Slug Router

**Production URL**: [https://lp.grosso-university.com/](https://lp.grosso-university.com/)  
**Wildcard Slug Format**: `https://lp.grosso-university.com/<slug>`  
**Deployment Target**: Google Cloud Run (Containerized via Dockerfile)

---

## Overview

The **Grosso University Ad Landing Page Command Center** is the centralized executive operations hub for managing, building, tracking, and routing high-converting paid advertising landing pages across Meta (Facebook & Instagram), Google Search & Performance Max, YouTube Ads, TikTok Ads, and retargeting campaigns.

Modeled after the executive architecture of the Events Command Center (`events.grosso-university.com`), this platform provides:
1. **Command Center Dashboard (`/`)**: Executive Dark/Light theme dashboard with telemetry, KPI cards, interactive page directory, search & channel filters, and instant route verification.
2. **Interactive Page Creation & Builder Studio**: Deploy new landing pages on the fly with battle-tested direct-response templates (Strategy Call / VSL Funnel, Lead Magnet PDF Download, Sales Diagnostic Audit, Event RSVP).
3. **UTM Ad Campaign Builder**: 1-click tracking generator for Meta Ads Manager macros (`{{campaign.name}}`, `{{ad.name}}`), Google Ads tags (`{campaignid}`, `{keyword}`), and TikTok ads.
4. **Interactive Device Simulator**: Responsive iframe preview (Desktop 100%, Tablet 768px, iPhone 390px) to inspect live ad pages directly from the dashboard.
5. **Dynamic Slug Router (`server.py`)**: Zero-dependency Python server powering root-level wildcard routing (`/<slug>`), REST APIs (`/api/pages`, `/api/route-check`, `/api/stats`), and static file serving.
6. **Universal Lead Ingest (KAOS)**: Automatic attribution and dispatch to `https://kaos-gu.com/api/webhooks/lead-ingest` with downstream synchronization to GoHighLevel (GHL).

---

## Active Ad Landing Pages

| Route / Slug | Campaign Title | Target Ad Platform | Conversion Goal |
| :--- | :--- | :--- | :--- |
| **`/strategy-call`** | Free 1-on-1 Sales Scaling Strategy Call | Meta Ads & Google Ads | Direct Consultation Booking |
| **`/roofing-sales-blueprint`** | The 11-Step Roofing & Remodeling Sales Playbook | Meta Ads & TikTok | Digital PDF Lead Magnet Capture |
| **`/sales-process-audit`** | Free 2-Minute Contractor Sales Process Audit | Google Search & LinkedIn | Diagnostic Quiz & Scorecard |
| **`/ribbon-cutting`** | Training Center Grand Opening & Ribbon-Cutting Ceremony | Meta & Retargeting | Free Event RSVP |

---

## Local Run & Preview

Run the built-in Cloud Run server locally:

```bash
python3 server.py
```

Then visit:
- **Command Center Dashboard**: [http://localhost:8080/](http://localhost:8080/)
- **Strategy Call Funnel**: [http://localhost:8080/strategy-call](http://localhost:8080/strategy-call)
- **Playbook Download**: [http://localhost:8080/roofing-sales-blueprint](http://localhost:8080/roofing-sales-blueprint)
- **Sales Process Audit**: [http://localhost:8080/sales-process-audit](http://localhost:8080/sales-process-audit)
- **Ribbon Cutting**: [http://localhost:8080/ribbon-cutting](http://localhost:8080/ribbon-cutting)

---

## Architecture & File Structure

```text
grosso-landing/
├── index.html                   # Command Center Dashboard (Executive Dark/Light UI)
├── server.py                    # Cloud Run wildcard slug router & REST API server
├── Dockerfile                   # Cloud Run container configuration
├── config.js                    # Injected environment config (GU_API_KEY, BASE_URL)
├── data/
│   └── registry.json            # Canonical database of all ad landing pages & metrics
├── pages/
│   ├── strategy-call/
│   │   └── index.html           # High-ticket consultation & VSL booking funnel
│   ├── roofing-sales-blueprint/
│   │   └── index.html           # Digital guide / lead magnet download page
│   ├── sales-process-audit/
│   │   └── index.html           # Interactive 4-step diagnostic audit quiz
│   └── ribbon-cutting/
│       ├── index.html           # Ribbon-cutting event registration page
│       └── thank-you.html       # Post-RSVP confirmation screen
├── assets/
│   ├── brand/
│   │   ├── grosso-brand.css     # Official Grosso University Design System
│   │   ├── logo-dark.png        # Official navy/gold logo for light backgrounds
│   │   ├── logo-white.png       # Official white logo for dark surfaces
│   │   └── logo-mark.png        # Crest mark favicon & branding
│   └── img/                     # Photography, proof assets & team imagery
├── css/
│   └── styles.css               # Supporting styles & responsive components
└── js/
    ├── strategy-call.js         # Strategy call lead submission & Calendly redirect
    └── main.js                  # Lead validation & calendar generation logic
```

---

## REST API Endpoints

- `GET /api/pages`: Returns the full registry of all active and draft ad landing pages.
- `POST /api/pages`: Creates a new ad landing page, generates the template files on disk under `pages/<slug>/index.html`, and registers it in `data/registry.json`.
- `GET /api/route-check?slug=<slug>`: Verifies whether a given slug exists and is active.
- `GET /api/stats`: Returns telemetry and aggregated campaign metrics.
- `GET /health`: Health check for Cloud Run container probes.
- `GET /config.js`: Injects `GU_API_KEY` and `BASE_URL = 'https://lp.grosso-university.com'`.

---

## KAOS Universal Lead Ingest Webhook

All landing page forms dispatch lead records directly to the **KAOS Universal Lead Ingest** endpoint:
- **Endpoint**: `https://kaos-gu.com/api/webhooks/lead-ingest`
- **Header**: `x-webhook-secret: <GU_API_KEY>` (Defaults to verified secret `whsec_g_a42ja9qcyk`)
- **Method**: `POST`
- **Payload Fields**: `source`, `event_name`, `first_name`, `last_name`, `email`, `phone`, `company`, `page_url`, `utm_source`, `utm_campaign`, `notes`.
