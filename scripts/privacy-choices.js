/* Insider Lawyers - lightweight cookie / privacy choices banner.
   Designed to integrate with Google Consent Mode v2 + a custom dataLayer event
   that GTM tags can listen for to fire only after consent (or in a granular way).

   This file intentionally has no external dependencies. It is a baseline so the
   site is not running without any consent surface at all; for richer flows
   (geo-targeting, GPC honoring across all jurisdictions, full preferences UI)
   swap in Cookiebot, Complianz, OneTrust, or CookieYes and remove this file.
*/
(function () {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  var STORAGE_KEY = 'il_privacy_choices_v1';
  var COOKIE_NAME = 'il_consent';
  var COOKIE_DAYS = 180;

  function readStored() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* ignore */ }
    var m = document.cookie.match(new RegExp('(?:^|; )' + COOKIE_NAME + '=([^;]*)'));
    if (m) {
      try { return JSON.parse(decodeURIComponent(m[1])); } catch (e) { /* ignore */ }
    }
    return null;
  }

  function writeStored(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
    var d = new Date();
    d.setTime(d.getTime() + COOKIE_DAYS * 24 * 60 * 60 * 1000);
    document.cookie = COOKIE_NAME + '=' + encodeURIComponent(JSON.stringify(state)) +
      '; expires=' + d.toUTCString() + '; path=/; SameSite=Lax';
  }

  function detectGPC() {
    return !!(navigator && (navigator.globalPrivacyControl === true ||
      (typeof navigator.globalPrivacyControl === 'string' && navigator.globalPrivacyControl === 'true')));
  }

  function applyConsent(state) {
    window.dataLayer = window.dataLayer || [];
    // Push a consent event so GTM can gate marketing/advertising tags.
    window.dataLayer.push({
      event: 'il_consent_update',
      consent: {
        analytics: !!state.analytics,
        ads: !!state.ads,
        personalization: !!state.personalization,
        do_not_sell_or_share: !!state.doNotSellOrShare,
        gpc: !!state.gpc
      }
    });

    // Google Consent Mode v2 integration (no-op if gtag is not on the page).
    if (typeof window.gtag === 'function') {
      try {
        window.gtag('consent', 'update', {
          ad_storage: state.ads ? 'granted' : 'denied',
          ad_user_data: state.ads ? 'granted' : 'denied',
          ad_personalization: state.personalization ? 'granted' : 'denied',
          analytics_storage: state.analytics ? 'granted' : 'denied'
        });
      } catch (e) { /* ignore */ }
    }
  }

  function defaultStateFromGPC() {
    var gpc = detectGPC();
    return {
      analytics: !gpc,
      ads: !gpc,
      personalization: !gpc,
      doNotSellOrShare: gpc,
      gpc: gpc,
      timestamp: null
    };
  }

  function ensureBanner() {
    if (document.getElementById('privacy-choices-banner')) return;

    // The cookie/consent notice is mounted INSIDE the footer (as the first
    // child of `.site-footer .container`) so it reads as part of the footer
    // chrome rather than a floating overlay. The full-screen modal still
    // lives on document.body because it overlays the whole page.
    var bannerHtml = '' +
      '<div id="privacy-choices-banner" role="region" aria-label="Cookie and privacy choices">' +
        '<div class="pc-inner">' +
          '<p>We use cookies, pixels, and call tracking (including Google Analytics, Google Ads, Meta, Reddit, Taboola, and CallRail) to measure performance and improve this site. You can manage your choices anytime. See our <a href="/cookie-policy">Cookie Policy</a> and <a href="/privacy-policy">Privacy Policy</a>.</p>' +
          '<div class="pc-actions">' +
            '<button type="button" id="pc-accept">Accept all</button>' +
            '<button type="button" id="pc-reject" class="pc-secondary">Reject non-essential</button>' +
            '<button type="button" id="pc-manage" class="pc-secondary">Manage choices</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var modalHtml = '' +
      '<div id="privacy-choices-modal" role="dialog" aria-modal="true" aria-labelledby="pc-modal-title">' +
        '<div class="pc-modal">' +
          '<h2 id="pc-modal-title">Cookie &amp; Privacy Choices</h2>' +
          '<p>Choose how Insider Lawyers may use cookies and similar technologies on this device. Essential cookies cannot be disabled because they are required for the site to function.</p>' +
          '<label class="pc-toggle"><input type="checkbox" id="pc-essential" checked disabled><span><strong>Essential</strong> &mdash; required for site functionality.</span></label>' +
          '<label class="pc-toggle"><input type="checkbox" id="pc-analytics"><span><strong>Analytics</strong> &mdash; helps us understand how the site is used (e.g., GA4).</span></label>' +
          '<label class="pc-toggle"><input type="checkbox" id="pc-ads"><span><strong>Advertising</strong> &mdash; supports ad attribution and remarketing (e.g., Google Ads, Meta, Reddit, Taboola, CallRail attribution).</span></label>' +
          '<label class="pc-toggle"><input type="checkbox" id="pc-personalization"><span><strong>Personalization</strong> &mdash; tailors ads and content to your interests.</span></label>' +
          '<label class="pc-toggle"><input type="checkbox" id="pc-dns"><span><strong>Do Not Sell or Share My Personal Information</strong> &mdash; opt out of activity that may qualify as a sale or sharing under California law.</span></label>' +
          '<p style="font-size:12.5px;color:#6b7280;margin-bottom:12px;">If your browser sends a Global Privacy Control (GPC) signal, we will treat it as a Do Not Sell or Share request for this browser and device.</p>' +
          '<div class="pc-modal-actions">' +
            '<button type="button" id="pc-modal-save" class="pc-secondary">Save choices</button>' +
            '<button type="button" id="pc-modal-accept">Accept all</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var bannerWrap = document.createElement('div');
    bannerWrap.innerHTML = bannerHtml;
    var bannerEl = bannerWrap.firstChild;
    var footerHost = document.querySelector('.site-footer .container');
    if (footerHost) {
      footerHost.insertBefore(bannerEl, footerHost.firstChild);
    } else {
      // Pages without the global footer fall back to body append so the
      // notice is still reachable.
      document.body.appendChild(bannerEl);
    }

    var modalWrap = document.createElement('div');
    modalWrap.innerHTML = modalHtml;
    document.body.appendChild(modalWrap.firstChild);
  }

  function showBanner() {
    var b = document.getElementById('privacy-choices-banner');
    if (b) b.classList.add('is-visible');
  }

  function hideBanner() {
    var b = document.getElementById('privacy-choices-banner');
    if (b) b.classList.remove('is-visible');
  }

  function openModal(state) {
    var m = document.getElementById('privacy-choices-modal');
    if (!m) return;
    document.getElementById('pc-analytics').checked = !!state.analytics;
    document.getElementById('pc-ads').checked = !!state.ads;
    document.getElementById('pc-personalization').checked = !!state.personalization;
    document.getElementById('pc-dns').checked = !!state.doNotSellOrShare;
    m.classList.add('is-visible');
  }

  function closeModal() {
    var m = document.getElementById('privacy-choices-modal');
    if (m) m.classList.remove('is-visible');
  }

  function bind() {
    var stored = readStored();
    var gpc = detectGPC();

    document.getElementById('pc-accept').addEventListener('click', function () {
      var state = { analytics: true, ads: !gpc, personalization: !gpc, doNotSellOrShare: gpc, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); hideBanner();
    });
    document.getElementById('pc-reject').addEventListener('click', function () {
      var state = { analytics: false, ads: false, personalization: false, doNotSellOrShare: true, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); hideBanner();
    });
    document.getElementById('pc-manage').addEventListener('click', function () {
      openModal(stored || defaultStateFromGPC());
    });
    document.getElementById('pc-modal-save').addEventListener('click', function () {
      var state = {
        analytics: document.getElementById('pc-analytics').checked,
        ads: document.getElementById('pc-ads').checked,
        personalization: document.getElementById('pc-personalization').checked,
        doNotSellOrShare: document.getElementById('pc-dns').checked,
        gpc: gpc,
        timestamp: Date.now()
      };
      writeStored(state); applyConsent(state); closeModal(); hideBanner();
    });
    document.getElementById('pc-modal-accept').addEventListener('click', function () {
      var state = { analytics: true, ads: !gpc, personalization: !gpc, doNotSellOrShare: gpc, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); closeModal(); hideBanner();
    });

    // Close modal when clicking outside the inner panel.
    document.getElementById('privacy-choices-modal').addEventListener('click', function (e) {
      if (e.target === this) closeModal();
    });

    // Wire any "Manage Cookie & Privacy Choices" links / buttons on legal pages
    // (e.g., the Cookie Policy page and the footer button).
    document.querySelectorAll('[data-privacy-choices-open]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openModal(readStored() || defaultStateFromGPC());
      });
    });
  }

  function init() {
    ensureBanner();
    bind();
    var stored = readStored();
    if (!stored) {
      // No prior choice — set Consent Mode defaults to denied and show the banner.
      if (typeof window.gtag !== 'function' && Array.isArray(window.dataLayer)) {
        // Provide a minimal gtag fallback so pages without gtag.js still get the consent dataLayer event.
        window.gtag = function () { window.dataLayer.push(arguments); };
      }
      var initial = defaultStateFromGPC();
      applyConsent(initial);
      showBanner();
    } else {
      // Re-apply prior choice for this session (GTM tags can read this).
      applyConsent(stored);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
