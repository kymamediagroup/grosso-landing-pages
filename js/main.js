// ============================================================================
// GROSSO UNIVERSITY - GRAND OPENING & RIBBON-CUTTING RSVP LOGIC
// Connects Landing Page Form -> KAOS Universal Lead Ingest (/api/webhooks/lead-ingest)
// KAOS handles CRM contact creation, event attribution, and downstream GHL sync.
// ============================================================================

// KAOS Universal Lead Ingest Webhook
var KAOS_WEBHOOK_URL = 'https://kaos-gu.com/api/webhooks/lead-ingest';

// Webhook Secret / API Key:
// In Cloud Run, GU_API_KEY can be set via environment variable (or window.GU_API_KEY).
// Defaults to the verified Grosso KAOS webhook secret key.
var KAOS_SECRET = (typeof window !== 'undefined' && (window.GU_API_KEY || window.KAOS_SECRET))
  ? (window.GU_API_KEY || window.KAOS_SECRET)
  : 'whsec_g_a42ja9qcyk';

document.addEventListener('DOMContentLoaded', function () {
  var form = document.querySelector('#rsvp-form') || document.querySelector('#rsvpForm') || document.querySelector('form');
  var formCard = document.getElementById('rsvp') || document.getElementById('formContainer');
  var submitBtn = document.getElementById('rsvpSubmitBtn') || (form ? form.querySelector('button[type="submit"]') : null);
  var mobileBar = document.getElementById('mobileRsvpBar');

  // Mobile Sticky RSVP Bar show/hide on scroll
  if (mobileBar) {
    var checkScroll = function () {
      var scrollY = window.pageYOffset || document.documentElement.scrollTop;
      var hero = document.querySelector('.hero');
      var heroHeight = hero ? hero.offsetHeight : 400;

      var formInView = false;
      if (formCard) {
        var rect = formCard.getBoundingClientRect();
        formInView = (rect.top >= -100 && rect.bottom <= (window.innerHeight + 100));
      }

      if (scrollY > heroHeight && !formInView) {
        mobileBar.classList.add('visible');
      } else {
        mobileBar.classList.remove('visible');
      }
    };

    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll();
  }

  if (!form) return;

  var fields = {
    firstName: {
      input: document.getElementById('firstName') || form.querySelector('[name="firstName"]'),
      container: document.getElementById('field-firstName'),
      validate: function (val) { return val.trim().length >= 2; }
    },
    lastName: {
      input: document.getElementById('lastName') || form.querySelector('[name="lastName"]'),
      container: document.getElementById('field-lastName'),
      validate: function (val) { return val.trim().length >= 2; }
    },
    email: {
      input: document.getElementById('email') || form.querySelector('[name="email"]'),
      container: document.getElementById('field-email'),
      validate: function (val) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()); }
    },
    phone: {
      input: document.getElementById('phone') || form.querySelector('[name="phone"]'),
      container: document.getElementById('field-phone'),
      validate: function (val) {
        var cleaned = val.replace(/\D/g, '');
        return cleaned.length === 0 || cleaned.length >= 7;
      }
    },
    company: {
      input: document.getElementById('company') || form.querySelector('[name="company"]'),
      container: document.getElementById('field-company'),
      validate: function (val) { return val.trim().length >= 2; }
    },
    role: {
      input: document.getElementById('role') || form.querySelector('[name="role"]'),
      container: document.getElementById('field-role'),
      validate: function (val) { return val.trim().length >= 2; }
    },
    attendeeCount: {
      input: document.getElementById('attendeeCount') || form.querySelector('[name="attendeeCount"]') || document.getElementById('guests'),
      container: document.getElementById('field-attendeeCount') || document.getElementById('field-guests'),
      validate: function (val) {
        var num = parseInt(val, 10);
        return !isNaN(num) && num >= 1 && num <= 50;
      }
    }
  };

  // Real-time error removal
  Object.keys(fields).forEach(function (key) {
    var item = fields[key];
    if (!item.input) return;

    item.input.addEventListener('input', function () {
      if (item.container && item.validate(item.input.value)) {
        item.container.classList.remove('error');
      }
    });

    item.input.addEventListener('change', function () {
      if (item.container && item.validate(item.input.value)) {
        item.container.classList.remove('error');
      }
    });
  });

  // Handle Form Submission
  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    var isValid = true;
    var firstInvalid = null;

    Object.keys(fields).forEach(function (key) {
      var item = fields[key];
      if (!item.input) return;
      var valid = item.validate(item.input.value);
      if (!valid) {
        isValid = false;
        if (item.container) item.container.classList.add('error');
        if (!firstInvalid) firstInvalid = item.input;
      } else {
        if (item.container) item.container.classList.remove('error');
      }
    });

    if (!isValid) {
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Reserving Your Spot...';
    }

    var formData = new FormData(form);
    var firstName = (formData.get('firstName') || (fields.firstName.input ? fields.firstName.input.value : '')).trim();
    var lastName = (formData.get('lastName') || (fields.lastName.input ? fields.lastName.input.value : '')).trim();
    var email = (formData.get('email') || (fields.email.input ? fields.email.input.value : '')).trim();
    var phone = (formData.get('phone') || (fields.phone.input ? fields.phone.input.value : '')).trim();
    var company = (formData.get('company') || (fields.company.input ? fields.company.input.value : '')).trim();
    var role = (formData.get('role') || (fields.role.input ? fields.role.input.value : '')).trim();
    
    var rawAttendee = formData.get('attendeeCount') || (fields.attendeeCount.input ? fields.attendeeCount.input.value : '1');
    var attendeeCount = parseInt(rawAttendee, 10);
    if (isNaN(attendeeCount) || attendeeCount < 1) {
      attendeeCount = 1;
    }

    // KAOS Attendance Math:
    // Every registered lead = 1 Lead Attended + N Additional Attendees = Total Party Seats
    // If attendeeCount = 1, additional attendees = "" (0 additional guests)
    // If attendeeCount = 3, additional attendees = "2" (2 additional guests)
    var additionalAttendees = attendeeCount > 1 ? String(attendeeCount - 1) : '';

    var podcastCheckbox = document.getElementById('podcastInterest');
    var podcastInterested = podcastCheckbox ? podcastCheckbox.checked : false;

    // Standardized KAOS /api/webhooks/lead-ingest Payload
    var payload = {
      // Event Source & Attribution
      source: 'lp.grosso-university.com/ribbon-cutting',
      landing_page: 'ribbon-cutting',
      landing_page_url: 'https://lp.grosso-university.com/ribbon-cutting',
      landing_page_slug: 'ribbon-cutting',
      event: 'Grosso Ribbon Cutting & Grand Opening',
      event_name: 'Grosso University Training Center Grand Opening & Ribbon Cutting',
      
      // Primary Contact Information
      first_name: firstName,
      last_name: lastName,
      full_name: (firstName + ' ' + lastName).trim(),
      email: email,
      phone: phone,
      company: company,
      position: role,

      // Event Attendance & Headcount
      attendees: additionalAttendees,
      ticket_tier: 'Free RSVP',
      amount_paid: 0,
      
      // Context & Attribution Metadata
      page_url: window.location.href,
      slug: 'ribbon-cutting',
      notes: 'Landing Page: /ribbon-cutting | Event RSVP for ' + attendeeCount + ' attendee(s) | Position: ' + role + (podcastInterested ? ' | Interested in Podcast Open Mic' : ''),

      // Compatibility & Downstream Mirror Fields
      firstName: firstName,
      lastName: lastName,
      headcount: attendeeCount,
      attendeeCount: attendeeCount,
      role: role,
      podcastOpenMicInterested: podcastInterested,
      submittedAt: new Date().toISOString()
    };

    // Store in sessionStorage for immediate thank-you page personalization
    try {
      sessionStorage.setItem('grosso_rsvp_lead', JSON.stringify(payload));
    } catch (err) {}

    // Dual dispatch: Ingest into KAOS Universal Lead Ingest + Local Command Center
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
      console.warn('Lead Ingest dispatch:', err);
    }

    // Redirect to confirmation screen
    window.location.href = 'thank-you.html';
  });
});
