# Deployment Guide — Grosso University Ad Landing Page Command Center
## Domain: `https://lp.grosso-university.com/`

This guide explains how to deploy the Grosso University Ad Landing Page Command Center and wildcard slug router to **Google Cloud Run** and configure the custom domain `lp.grosso-university.com`.

---

### 1. Google Cloud Run Deployment (Turnkey)

Deploy directly from this directory using the `gcloud` CLI:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login
gcloud config set project <YOUR_GCP_PROJECT_ID>

# 2. Deploy to Cloud Run
gcloud run deploy grosso-lp-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GU_API_KEY=whsec_g_a42ja9qcyk
```

Cloud Run will build the container from `Dockerfile` and start `server.py` on port 8080.

---

### 2. Custom Domain Mapping (`lp.grosso-university.com`)

1. In the Google Cloud Console, navigate to **Cloud Run** &rarr; **Manage Custom Domains**.
2. Click **Add Mapping**:
   - **Service to route to**: `grosso-lp-dashboard`
   - **Domain**: `lp.grosso-university.com`
3. Add the DNS records provided by Google Cloud to your DNS registrar (GoDaddy, Cloudflare, Namecheap, etc.):
   - Record type: `CNAME` or `A` / `AAAA`
   - Host: `lp`
   - Target: `ghs.googlehosted.com.` (or Google anycast IP addresses)
4. Google Cloud Run automatically provisions and manages free SSL/TLS certificates for `https://lp.grosso-university.com/`.

---

### 3. Verification Checklist

Once deployed to `https://lp.grosso-university.com`:
- [ ] Visit `https://lp.grosso-university.com/` — Ensure the Command Center loads with Dark/Light theme toggle.
- [ ] Test route `https://lp.grosso-university.com/strategy-call` — Verify the Strategy Call booking funnel renders and submits.
- [ ] Test route `https://lp.grosso-university.com/roofing-sales-blueprint` — Verify the 11-step playbook download funnel renders.
- [ ] Test route `https://lp.grosso-university.com/sales-process-audit` — Verify the 4-step diagnostic audit renders.
- [ ] Test route `https://lp.grosso-university.com/ribbon-cutting` — Verify the grand opening event page renders.
- [ ] Verify lead records arrive in KAOS (`https://kaos-gu.com/api/webhooks/lead-ingest`) and GoHighLevel (GHL).
- [ ] Test "+ New Ad Landing Page" modal on the dashboard to confirm new ad pages can be built and deployed instantly.
