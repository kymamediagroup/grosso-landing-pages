// Grosso University Strategy Call Funnel Lead Capture
// Posts to KAOS Universal Lead Ingest and redirects to Calendly / Booking

(function () {
  var KAOS_WEBHOOK_URL = 'https://kaos-gu.com/api/webhooks/lead-ingest';
  var KAOS_SECRET = (typeof window !== 'undefined' && (window.GU_API_KEY || window.KAOS_SECRET))
    ? (window.GU_API_KEY || window.KAOS_SECRET)
    : 'whsec_g_a42ja9qcyk';

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('leadForm');
    if (!form) return;

    var fullNameInput = document.getElementById('fullName');
    var emailInput = document.getElementById('email');
    var phoneInput = document.getElementById('phone');
    var companyInput = document.getElementById('company');
    var titleInput = document.getElementById('title');
    var submitBtn = document.getElementById('submitBtn');

    // Parse URL params for UTM tracking
    var urlParams = new URLSearchParams(window.location.search);
    var utmSource = urlParams.get('utm_source') || 'meta';
    var utmMedium = urlParams.get('utm_medium') || 'paid_social';
    var utmCampaign = urlParams.get('utm_campaign') || 'contractor_scale_vsl';
    var utmContent = urlParams.get('utm_content') || '';
    var utmTerm = urlParams.get('utm_term') || '';

    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      var nameVal = (fullNameInput ? fullNameInput.value : '').trim();
      var emailVal = (emailInput ? emailInput.value : '').trim();
      var phoneVal = (phoneInput ? phoneInput.value : '').trim();
      var companyVal = (companyInput ? companyInput.value : '').trim();
      var titleVal = (titleInput ? titleInput.value : '').trim();

      var hasError = false;

      function checkField(input, valid) {
        var parent = input ? input.closest('.field') : null;
        if (!valid) {
          if (parent) parent.classList.add('error');
          hasError = true;
        } else {
          if (parent) parent.classList.remove('error');
        }
      }

      checkField(fullNameInput, nameVal.length >= 2);
      checkField(emailInput, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal));
      checkField(phoneInput, phoneVal.replace(/\D/g, '').length >= 7);
      checkField(companyInput, companyVal.length >= 2);
      checkField(titleInput, titleVal.length >= 2);

      if (hasError) return;

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Securing Your Time...</span>';
      }

      var nameParts = nameVal.split(' ');
      var firstName = nameParts[0] || '';
      var lastName = nameParts.slice(1).join(' ') || '';

      var payload = {
        source: 'lp.grosso-university.com/strategy-call',
        landing_page: 'strategy-call',
        landing_page_url: 'https://lp.grosso-university.com/strategy-call',
        landing_page_slug: 'strategy-call',
        campaign_name: 'Grosso University Free Strategy Call',
        event_name: 'Grosso University Free Strategy Call',
        first_name: firstName,
        last_name: lastName,
        full_name: nameVal,
        email: emailVal,
        phone: phoneVal,
        company: companyVal,
        position: titleVal,
        ticket_tier: 'Free Strategy Call',
        amount_paid: 0,
        page_url: window.location.href,
        slug: 'strategy-call',
        utm_source: utmSource,
        utm_medium: utmMedium,
        utm_campaign: utmCampaign,
        utm_content: utmContent,
        utm_term: utmTerm,
        notes: 'Landing Page: /strategy-call | Lead: ' + nameVal + ' (' + titleVal + ' at ' + companyVal + ') | Ad Source: ' + utmSource + ' | Campaign: ' + utmCampaign,
        submittedAt: new Date().toISOString()
      };

      // Dual dispatch: Ingest into KAOS CRM webhook and local Command Center
      try {
        await Promise.allSettled([
          fetch(KAOS_WEBHOOK_URL, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-webhook-secret': KAOS_SECRET
            },
            body: JSON.stringify(payload)
          }),
          fetch('/api/leads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          })
        ]);
      } catch (err) {
        console.warn('Lead Ingest error:', err);
      }

      // Track conversion if pixel is available
      if (typeof window.fbq === 'function') {
        window.fbq('track', 'Lead', { content_name: 'Strategy Call Booking' });
      }

      // Show instant confirmation overlay or redirect to booking
      var bookCard = form.closest('.book-card');
      if (bookCard) {
        bookCard.innerHTML = `
          <div style="text-align: center; padding: 2rem 1rem;">
            <div style="width: 58px; height: 58px; border-radius: 50%; background: #10B981; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem; font-size: 28px;">✓</div>
            <h3 style="font-size: 24px; font-weight: 800; color: #111827; margin-bottom: 0.5rem;">You're Confirmed, ${firstName}!</h3>
            <p style="color: #4B5563; font-size: 15px; margin-bottom: 1.5rem; line-height: 1.5;">Our senior strategist Matt has received your request. We've reserved your priority review for <strong>${companyVal}</strong>.</p>
            <div style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: left;">
              <div style="font-size: 13px; font-weight: 700; color: #374151; text-transform: uppercase; margin-bottom: 6px;">Next Step: Select Exact Zoom Slot</div>
              <p style="font-size: 14px; color: #6B7280; margin: 0;">An invitation has been dispatched to <strong>${emailVal}</strong>. Or click below to pick your immediate time slot.</p>
            </div>
            <a href="https://calendly.com/grossouniversity" target="_blank" class="btn btn-submit" style="display: inline-flex; text-decoration: none;">
              Open Calendar & Pick Time Slot &rarr;
            </a>
          </div>
        `;
      }
    });
  });
})();
