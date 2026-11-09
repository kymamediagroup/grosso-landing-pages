#!/usr/bin/env python3
"""
Grosso University Ad Landing Page Command Center & Slug Router
Production Server for Google Cloud Run (https://lp.grosso-university.com)
Zero external dependencies (Pure Python 3 standard library).
"""

import os
import sys
import json
import re
import time
import base64
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get('PORT', 8080))
GU_API_KEY = os.environ.get('GU_API_KEY', 'whsec_g_a42ja9qcyk')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_FILE = os.path.join(BASE_DIR, 'data', 'registry.json')
PAGES_DIR = os.path.join(BASE_DIR, 'pages')
UPLOADS_DIR = os.path.join(BASE_DIR, 'assets', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

def get_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading registry: {e}")
    return {"platform": {}, "pages": []}

def save_registry(data):
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def generate_landing_page_html(page_data):
    """Generates production-grade HTML for newly created ad landing pages based on template."""
    title = page_data.get('title', 'Grosso University')
    slug = page_data.get('slug', 'page')
    headline = page_data.get('headline') or title
    subtitle = page_data.get('subtitle') or 'North America’s Leading Sales Training for Contractors'
    hook = page_data.get('hook') or ''
    target_audience = page_data.get('targetAudience') or 'Home Improvement Contractors'
    cta_text = page_data.get('ctaText', 'Claim Your Free Access Now')
    offer_type = page_data.get('offerType', 'Strategy Call / VSL')
    category = page_data.get('category', 'Ad Campaign')
    hero_image = page_data.get('heroImage') or ''

    image_markup = ""
    if hero_image:
        image_markup = f'''
        <div style="margin-top:1.5rem; text-align:center;">
          <img src="{hero_image}" alt="{title}" style="max-width:100%; height:auto; border-radius:12px; border:1px solid rgba(163,129,78,0.35); box-shadow:0 12px 30px rgba(0,0,0,0.5); display:block; margin:0 auto;" />
        </div>'''

    template = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>{title} | Grosso University</title>
  <!-- Simpli.fi Pixel Tag -->
  <script async src='https://tag.simpli.fi/sifitag/4a187475-8ae5-41b0-a1e0-5bc3606437ee'></script>
  <meta name="description" content="{subtitle}" />
  <link rel="icon" type="image/png" href="/assets/brand/logo-mark.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cinzel:wght@600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/brand/grosso-brand.css" />
  <style>
    :root {{
      --bg-canvas: #060911;
      --bg-surface: #0E1628;
      --border-line: rgba(148, 163, 184, 0.14);
      --gold: #A3814E;
      --gold-light: #C5A26D;
      --blue: #4D6FA2;
      --text-main: #F8FAFC;
      --text-sub: #CBD5E1;
      --text-muted: #94A3B8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg-canvas);
      color: var(--text-main);
      font-family: var(--grosso-font-sans);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      background-image:
        radial-gradient(circle at 18% 12%, rgba(77, 111, 162, 0.18), transparent 45%),
        radial-gradient(circle at 82% 12%, rgba(163, 129, 78, 0.14), transparent 40%);
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 1.5rem; }}
    .nav-bar {{ border-bottom: 1px solid var(--border-line); padding: 1.1rem 0; background: rgba(6, 9, 17, 0.85); backdrop-filter: blur(16px); position: sticky; top: 0; z-index: 50; }}
    .nav-inner {{ display: flex; align-items: center; justify-content: space-between; }}
    .logo {{ height: 40px; width: auto; }}
    .hero {{ padding: 3.75rem 0 3rem; text-align: center; }}
    .pill {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.9rem; border-radius: 999px; background: rgba(163, 129, 78, 0.15); border: 1px solid rgba(163, 129, 78, 0.4); color: var(--gold-light); font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1.25rem; }}
    h1 {{ font-size: clamp(2rem, 4vw, 3.1rem); font-weight: 800; line-height: 1.18; margin-bottom: 1.25rem; letter-spacing: -0.02em; max-width: 900px; margin-left: auto; margin-right: auto; }}
    h1 span {{ background: linear-gradient(135deg, #F5E6CC 0%, #C5A26D 50%, #A3814E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .sub {{ color: var(--text-sub); font-size: clamp(1rem, 1.8vw, 1.2rem); max-width: 780px; margin: 0 auto 2.5rem; }}
    .card-grid {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 2.25rem; align-items: start; margin-bottom: 4rem; }}
    .info-card {{ background: var(--bg-surface); border: 1px solid var(--border-line); border-radius: 1.25rem; padding: 2.25rem; position: relative; }}
    .info-card::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--blue) 0%, var(--gold) 100%); border-radius: 1.25rem 1.25rem 0 0; }}
    .features {{ list-style: none; display: flex; flex-direction: column; gap: 1.25rem; margin-top: 1.5rem; }}
    .features li {{ display: flex; gap: 0.75rem; font-size: 0.95rem; color: var(--text-sub); }}
    .features li span {{ color: #34D399; font-weight: 800; font-size: 1.1rem; line-height: 1; }}
    .form-box {{ background: #FFFFFF; color: #0F172A; border-radius: 1.25rem; padding: 2.25rem; box-shadow: 0 24px 60px -15px rgba(0,0,0,0.8); position: relative; }}
    .form-box::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #A3814E 0%, #E7C996 50%, #A3814E 100%); border-radius: 1.25rem 1.25rem 0 0; }}
    .form-group {{ display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; text-align: left; }}
    .form-group label {{ font-size: 0.85rem; font-weight: 600; color: #334155; }}
    .form-group input, .form-group select {{ height: 46px; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0 12px; font-size: 0.95rem; }}
    .btn-submit {{ width: 100%; height: 50px; background: linear-gradient(135deg, #C5A26D 0%, #A3814E 60%, #846539 100%); color: #fff; font-weight: 800; font-size: 0.95rem; border: none; border-radius: 8px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 0.5rem; }}
    footer {{ border-top: 1px solid var(--border-line); padding: 2rem 0; text-align: center; color: var(--text-muted); font-size: 0.85rem; }}
    @media (max-width: 800px) {{ .card-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <nav class="nav-bar">
    <div class="wrap nav-inner">
      <img src="/assets/brand/logo-white.png" alt="Grosso University" class="logo" />
      <span style="font-size:0.75rem; color:var(--gold-light); font-weight:700; text-transform:uppercase;">Official Ad Offer</span>
    </div>
  </nav>

  <main class="wrap">
    <section class="hero">
      <div class="pill">{category} • Exclusive Access</div>
      <h1>{headline}</h1>
      <p class="sub">{subtitle}</p>
    </section>

    <div class="card-grid">
      <div class="info-card">
        <span style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--gold-light);">Targeted For: {target_audience}</span>
        <h3 style="font-size:1.35rem; margin:0.75rem 0 1rem; color:#fff;">Why Top Contractors Choose Grosso:</h3>
        <p style="color:var(--text-muted); font-size:0.95rem; margin-bottom:1.25rem;">{hook}</p>
        <ul class="features">
          <li><span>✓</span> Master the 11-Step Selling System proven across 500+ contractor companies</li>
          <li><span>✓</span> Overcome homeowner objections without slashing prices or eroding gross margin</li>
          <li><span>✓</span> 1-on-1 execution framework with senior Grosso University leadership</li>
        </ul>
        {image_markup}
      </div>

      <div class="form-box">
        <h3 style="font-size:1.4rem; font-weight:800; margin-bottom:0.4rem; color:#0F172A;">{cta_text}</h3>
        <p style="color:#64748B; font-size:0.88rem; margin-bottom:1.25rem;">Complete the form below to lock in priority access.</p>
        <form id="adLeadForm">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" name="name" required placeholder="John Smith" />
          </div>
          <div class="form-group">
            <label>Work Email *</label>
            <input type="email" name="email" required placeholder="john@company.com" />
          </div>
          <div class="form-group">
            <label>Phone Number *</label>
            <input type="tel" name="phone" required placeholder="(555) 000-0000" />
          </div>
          <div class="form-group">
            <label>Company Name *</label>
            <input type="text" name="company" required placeholder="Acme Roofing & Remodeling" />
          </div>
          <button type="submit" class="btn-submit" id="submitBtn">{cta_text} &rarr;</button>
        </form>
      </div>
    </div>
  </main>

  <footer>
    <div class="wrap">
      <p>&copy; 2026 Grosso University. All rights reserved. • <a href="https://grossouniversity.com" style="color:inherit;">grossouniversity.com</a></p>
    </div>
  </footer>

  <script src="/config.js"></script>
  <script>
    document.getElementById('adLeadForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const btn = document.getElementById('submitBtn');
      btn.disabled = true;
      btn.textContent = 'Submitting Request...';

      const formData = new FormData(e.target);
      const name = (formData.get('name') || '').trim();
      const email = (formData.get('email') || '').trim();
      const phone = (formData.get('phone') || '').trim();
      const company = (formData.get('company') || '').trim();

      const urlParams = new URLSearchParams(window.location.search);
      const payload = {{
        source: 'lp.grosso-university.com/{slug}',
        landing_page: '{slug}',
        landing_page_slug: '{slug}',
        landing_page_url: window.location.href,
        event_name: '{title}',
        full_name: name,
        email: email,
        phone: phone,
        company: company,
        page_url: window.location.href,
        slug: '{slug}',
        utm_source: urlParams.get('utm_source') || 'ad_campaign',
        utm_medium: urlParams.get('utm_medium') || 'paid_ad',
        utm_campaign: urlParams.get('utm_campaign') || '{slug}',
        notes: 'Landing Page Lead from /{slug} ({title})'
      }};

      try {{
        await fetch('https://kaos-gu.com/api/webhooks/lead-ingest', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json', 'x-webhook-secret': window.GU_API_KEY || 'whsec_g_a42ja9qcyk' }},
          body: JSON.stringify(payload)
        }});
      }} catch (_) {{}}

      e.target.closest('.form-box').innerHTML = `
        <div style="text-align:center; padding:1.5rem 0;">
          <div style="width:52px; height:52px; border-radius:50%; background:#10B981; color:#fff; display:flex; align-items:center; justify-content:center; margin:0 auto 1rem; font-size:24px;">✓</div>
          <h3 style="font-size:1.35rem; font-weight:800; color:#0F172A; margin-bottom:0.5rem;">Thank You, ${{name.split(' ')[0]}}!</h3>
          <p style="color:#64748B; font-size:0.95rem; margin-bottom:1.25rem;">Your request has been received. Our team will reach out to ${{email}} shortly.</p>
          <a href="/strategy-call" style="display:inline-block; padding:0.75rem 1.5rem; background:#A3814E; color:#fff; text-decoration:none; border-radius:8px; font-weight:700; font-size:0.9rem;">Book Strategy Call Now &rarr;</a>
        </div>
      `;
    }});
  </script>
</body>
</html>
"""
    return template

class GrossoRouterHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and standard caching headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-webhook-secret')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Health check for Cloud Run
        if path in ['/health', '/_health', '/ping']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        # 2. Dynamic config.js
        if path == '/config.js':
            body = (
                f'window.GU_API_KEY = "{GU_API_KEY}";\n'
                f'window.BASE_URL = "https://lp.grosso-university.com";\n'
            ).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(body)
            return

        # 3. REST API: Get All Pages
        if path == '/api/pages' or path == '/api/events':
            reg = get_registry()
            body = json.dumps(reg, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 4. REST API: Route Check
        if path == '/api/route-check':
            slug = query.get('slug', [''])[0].strip().lower().strip('/')
            slug = re.sub(r'[^a-z0-9-_]', '-', slug)
            page_dir = os.path.join(PAGES_DIR, slug)
            index_file = os.path.join(page_dir, 'index.html')
            exists = os.path.isfile(index_file)
            
            # Check in registry too
            reg = get_registry()
            in_reg = any(p.get('slug') == slug for p in reg.get('pages', []))

            res = {
                'exists': exists or in_reg,
                'slug': slug,
                'filePath': f'pages/{slug}/index.html' if exists else None,
                'productionUrl': f'https://lp.grosso-university.com/{slug}',
                'status': 'active' if (exists or in_reg) else 'available'
            }
            body = json.dumps(res).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 5. REST API: Stats
        if path == '/api/stats':
            reg = get_registry()
            pages = reg.get('pages', [])
            total_pages = len(pages)
            live_pages = sum(1 for p in pages if p.get('status') == 'live')
            total_ads = sum(int(p.get('stats', {}).get('activeAds', 1)) for p in pages)
            stats = {
                'totalPages': total_pages,
                'livePages': live_pages,
                'activeAds': total_ads,
                'domain': 'lp.grosso-university.com',
                'leadIngestActive': True
            }
            body = json.dumps(stats).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 6. REST API: Leads Feed
        if path == '/api/leads':
            leads_file = os.path.join(BASE_DIR, 'data', 'leads.json')
            leads_data = []
            if os.path.isfile(leads_file):
                with open(leads_file, 'r', encoding='utf-8') as f:
                    leads_data = json.load(f)
            body = json.dumps({'leads': leads_data, 'total': len(leads_data)}, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 6. Root Dashboard
        if path == '/' or path == '/index.html':
            dashboard_file = os.path.join(BASE_DIR, 'index.html')
            if os.path.isfile(dashboard_file):
                self.serve_file(dashboard_file, 'text/html; charset=utf-8')
                return

        # 7. Wildcard Slug Routing (e.g. /strategy-call, /roofing-sales-blueprint, /ribbon-cutting)
        clean_slug = path.strip('/').split('/')[0]
        if clean_slug and clean_slug not in ['api', 'css', 'js', 'assets', 'pages', 'data']:
            slug_page_file = os.path.join(PAGES_DIR, clean_slug, 'index.html')
            if os.path.isfile(slug_page_file):
                # If subpath requested inside the slug directory (e.g. /strategy-call/thank-you.html)
                sub_parts = path.strip('/').split('/')[1:]
                if sub_parts:
                    sub_file = os.path.join(PAGES_DIR, clean_slug, *sub_parts)
                    if os.path.isfile(sub_file):
                        mime, _ = mimetypes.guess_type(sub_file)
                        self.serve_file(sub_file, mime or 'text/html')
                        return
                self.serve_file(slug_page_file, 'text/html; charset=utf-8')
                return

        # 8. Check direct static file in workspace
        target_path = os.path.join(BASE_DIR, path.lstrip('/'))
        if os.path.isfile(target_path):
            mime, _ = mimetypes.guess_type(target_path)
            self.serve_file(target_path, mime or 'application/octet-stream')
            return

        # 8b. Fallback for /assets/... inside pages/top-500/assets
        if path.startswith('/assets/'):
            top500_asset = os.path.join(PAGES_DIR, 'top-500', path.lstrip('/'))
            if os.path.isfile(top500_asset):
                mime, _ = mimetypes.guess_type(top500_asset)
                self.serve_file(top500_asset, mime or 'application/octet-stream')
                return

        # 9. 404 Handler with Grosso branding
        self.serve_404(clean_slug)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Lead Ingest API (Dual-ingest with KAOS)
        if path == '/api/leads' or path == '/api/lead-capture':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_json_error(400, f'Invalid JSON payload: {e}')
                return

            leads_file = os.path.join(BASE_DIR, 'data', 'leads.json')
            leads_data = []
            if os.path.isfile(leads_file):
                try:
                    with open(leads_file, 'r', encoding='utf-8') as f:
                        leads_data = json.load(f)
                except Exception:
                    leads_data = []

            import datetime
            lead_id = f"lead_{len(leads_data) + 1045}"
            raw_url = data.get('page_url', '')
            slug = data.get('slug') or (raw_url.rstrip('/').split('/')[-1] if raw_url else 'strategy-call')

            new_lead = {
                "id": lead_id,
                "slug": slug,
                "name": data.get('full_name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or 'Home Improvement Contractor',
                "email": data.get('email') or '',
                "phone": data.get('phone') or '',
                "company": data.get('company') or 'Contracting Co.',
                "role": data.get('position') or data.get('role') or 'Owner',
                "trade": data.get('trade') or 'Roofing / Remodeling',
                "revenue": data.get('revenue_tier') or data.get('revenue') or '$2M - $5M',
                "source": data.get('source') or 'Paid Ad Campaign',
                "utm_source": data.get('utm_source') or 'meta',
                "utm_campaign": data.get('utm_campaign') or slug,
                "kaosStatus": "Synced to KAOS & GHL",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            leads_data.insert(0, new_lead)
            with open(leads_file, 'w', encoding='utf-8') as f:
                json.dump(leads_data, f, indent=2)

            resp = {
                "success": True,
                "leadId": lead_id,
                "lead": new_lead,
                "kaosStatus": "Synced to KAOS & GHL"
            }
            body = json.dumps(resp, indent=2).encode('utf-8')
            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Image Upload API for Landing Pages
        if path == '/api/upload-image':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_json_error(400, f'Invalid JSON payload: {e}')
                return

            image_data = data.get('image') or data.get('dataUrl') or ''
            filename = data.get('filename') or 'upload.png'

            if not image_data or ',' not in image_data:
                self.send_json_error(400, 'Invalid image data. Expected data URL.')
                return

            header, b64content = image_data.split(',', 1)
            ext = 'png'
            if 'image/jpeg' in header or 'image/jpg' in header:
                ext = 'jpg'
            elif 'image/webp' in header:
                ext = 'webp'
            elif 'image/gif' in header:
                ext = 'gif'
            elif 'image/svg+xml' in header:
                ext = 'svg'

            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', os.path.splitext(filename)[0]) or 'img'
            timestamp = int(time.time())
            save_filename = f"{clean_name}-{timestamp}.{ext}"
            save_path = os.path.join(UPLOADS_DIR, save_filename)

            try:
                file_bytes = base64.b64decode(b64content)
                with open(save_path, 'wb') as f:
                    f.write(file_bytes)
            except Exception as e:
                self.send_json_error(500, f'Failed to write uploaded image: {e}')
                return

            public_url = f"/assets/uploads/{save_filename}"
            resp = {
                "success": True,
                "url": public_url,
                "filename": save_filename,
                "size": len(file_bytes)
            }
            body = json.dumps(resp, indent=2).encode('utf-8')
            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Archive / Restore / Status Update API
        if path == '/api/pages/archive' or path == '/api/pages/status':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_json_error(400, f'Invalid JSON payload: {e}')
                return

            slug = (data.get('slug') or '').strip().lower()
            new_status = data.get('status') or 'archived'

            if not slug:
                self.send_json_error(400, 'Slug is required.')
                return

            reg = get_registry()
            pages = reg.get('pages', [])
            matched = False
            for p in pages:
                if p.get('slug') == slug:
                    p['status'] = new_status
                    p['updatedAt'] = '2026-10-27'
                    matched = True
                    break

            if not matched:
                self.send_json_error(404, f'Page /{slug} not found in registry.')
                return

            reg['pages'] = pages
            save_registry(reg)

            resp = {
                "success": True,
                "slug": slug,
                "status": new_status,
                "message": f"Page /{slug} set to {new_status}"
            }
            body = json.dumps(resp, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Create New Ad Landing Page API
        if path == '/api/pages' or path == '/api/create-page':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_json_error(400, f'Invalid JSON payload: {e}')
                return

            title = (data.get('title') or '').strip()
            raw_slug = (data.get('slug') or '').strip().lower()
            if not title:
                self.send_json_error(400, 'Page title is required.')
                return

            # Clean and sanitize slug
            slug = re.sub(r'[^a-z0-9-_]', '-', raw_slug) if raw_slug else re.sub(r'[^a-z0-9-_]', '-', title.lower())
            slug = slug.strip('-')
            if not slug:
                slug = f'ad-page-{int(os.times().system * 100)}'

            reg = get_registry()
            pages = reg.get('pages', [])
            existing_page = next((p for p in pages if p.get('slug') == slug), None)

            # Build metadata record
            page_record = {
                "slug": slug,
                "title": title,
                "subtitle": data.get('subtitle') or data.get('headline') or title,
                "headline": data.get('headline') or title,
                "description": data.get('description') or f"High-converting ad landing page for {title}",
                "category": data.get('category') or (existing_page.get('category') if existing_page else 'Ad Campaign'),
                "adPlatform": data.get('adPlatform') or (existing_page.get('adPlatform') if existing_page else 'Meta Ads'),
                "campaignName": data.get('campaignName') or (existing_page.get('campaignName') if existing_page else f"GU_{slug.upper().replace('-', '_')}_2026"),
                "targetAudience": data.get('targetAudience') or (existing_page.get('targetAudience') if existing_page else 'Home Improvement Contractors'),
                "hook": data.get('hook') or (existing_page.get('hook') if existing_page else 'Scale your close rates and profit margins.'),
                "offerType": data.get('offerType') or (existing_page.get('offerType') if existing_page else 'Strategy Call / VSL'),
                "ctaText": data.get('ctaText') or (existing_page.get('ctaText') if existing_page else 'Claim Your Free Access Now'),
                "heroImage": data.get('heroImage') if data.get('heroImage') is not None else (existing_page.get('heroImage', '') if existing_page else ''),
                "status": data.get('status') or (existing_page.get('status') if existing_page else 'live'),
                "conversionGoal": data.get('conversionGoal') or (existing_page.get('conversionGoal') if existing_page else 'Lead Capture'),
                "createdAt": existing_page.get('createdAt') if existing_page else (data.get('createdAt') or '2026-10-27'),
                "updatedAt": '2026-10-27',
                "accentColor": data.get('accentColor') or (existing_page.get('accentColor') if existing_page else '#A3814E'),
                "url": f"https://lp.grosso-university.com/{slug}",
                "stats": existing_page.get('stats') if existing_page else {
                    "traffic": "0",
                    "leads": "0",
                    "cvr": "0.0%",
                    "activeAds": int(data.get('activeAds') or 1)
                },
                "utmDefaults": {
                    "utm_source": (data.get('adPlatform') or 'meta').lower().split(' ')[0],
                    "utm_medium": "paid_social",
                    "utm_campaign": slug.replace('-', '_')
                },
                "tags": [data.get('adPlatform') or 'Meta Ads', data.get('offerType') or 'Lead Magnet']
            }

            # Update registry.json
            existing_idx = next((i for i, p in enumerate(pages) if p.get('slug') == slug), -1)
            if existing_idx >= 0:
                pages[existing_idx] = page_record
            else:
                pages.insert(0, page_record)
            reg['pages'] = pages
            save_registry(reg)

            # Write landing page HTML to disk under pages/<slug>/index.html
            page_dir = os.path.join(PAGES_DIR, slug)
            os.makedirs(page_dir, exist_ok=True)
            index_file_path = os.path.join(page_dir, 'index.html')
            custom_html = data.get('customHtml')
            if custom_html:
                with open(index_file_path, 'w', encoding='utf-8') as f:
                    f.write(custom_html)
            elif not os.path.isfile(index_file_path):
                final_html = generate_landing_page_html(page_record)
                with open(index_file_path, 'w', encoding='utf-8') as f:
                    f.write(final_html)

            resp = {
                "success": True,
                "message": f"Landing page published successfully for /{slug}",
                "slug": slug,
                "url": f"https://lp.grosso-university.com/{slug}",
                "localPath": f"/{slug}",
                "page": page_record
            }
            body = json.dumps(resp, indent=2).encode('utf-8')
            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_json_error(404, 'Endpoint not found')

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith('/api/pages/'):
            slug = path[len('/api/pages/'):].strip('/').lower()
            reg = get_registry()
            pages = [p for p in reg.get('pages', []) if p.get('slug') != slug]
            reg['pages'] = pages
            save_registry(reg)
            body = json.dumps({"success": True, "deleted": slug}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_json_error(404, 'Not found')

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            if 'html' in content_type:
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            else:
                self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json_error(500, f'Error serving file: {e}')

    def serve_404(self, requested_slug):
        content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Route Not Found | Grosso University Ad Command Center</title>
  <link rel="icon" type="image/png" href="/assets/brand/logo-mark.png" />
  <link rel="stylesheet" href="/assets/brand/grosso-brand.css" />
  <style>
    body {{
      background: #060911;
      color: #F8FAFC;
      font-family: 'Plus Jakarta Sans', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      text-align: center;
      padding: 2rem;
      margin: 0;
    }}
    .box {{
      max-width: 560px;
      background: #0E1628;
      border: 1px solid rgba(77, 111, 162, 0.35);
      border-radius: 1.25rem;
      padding: 3rem 2rem;
      box-shadow: 0 24px 60px -15px rgba(0,0,0,0.8);
    }}
    .code {{ font-size: 3.5rem; font-weight: 800; color: #A3814E; line-height: 1; margin-bottom: 1rem; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.75rem; }}
    p {{ color: #94A3B8; font-size: 0.95rem; margin-bottom: 2rem; }}
    .btn {{
      display: inline-block;
      background: linear-gradient(135deg, #C5A26D 0%, #A3814E 60%, #846539 100%);
      color: #060911;
      font-weight: 700;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="box">
    <div class="code">404</div>
    <h1>No Ad Landing Page at /{requested_slug}</h1>
    <p>The requested route does not exist yet on <code>lp.grosso-university.com</code>. You can create this page directly from the Command Center dashboard.</p>
    <a href="/" class="btn">Return to Ad Command Center &rarr;</a>
  </div>
</body>
</html>""".encode('utf-8')
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json_error(self, code, message):
        body = json.dumps({'error': message, 'statusCode': code}).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run():
    target_port = PORT
    httpd = None
    for p in [target_port, 8081, 8088, 3000]:
        try:
            server_address = ('0.0.0.0', p)
            httpd = HTTPServer(server_address, GrossoRouterHandler)
            target_port = p
            break
        except OSError as e:
            if e.errno == 48:
                continue
            raise

    if not httpd:
        print(f"Could not bind to any port.")
        sys.exit(1)

    print(f"============================================================")
    print(f"Grosso University Ad Command Center running on port {target_port}")
    print(f"Local URL:      http://localhost:{target_port}")
    print(f"Production URL: https://lp.grosso-university.com")
    print(f"Registry:       {REGISTRY_FILE}")
    print(f"GU_API_KEY:     {GU_API_KEY[:7]}*** (length: {len(GU_API_KEY)})")
    print(f"============================================================")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
