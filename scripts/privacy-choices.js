/* Insider Lawyers - lightweight cookie / privacy choices banner.
   Designed to integrate with Google Consent Mode v2 + a custom dataLayer event
   that GTM tags can listen for to fire only after consent (or in a granular way).

   This file intentionally has no external dependencies. It is a baseline so the
   site is not running without any consent surface at all; for richer flows
   (geo-targeting, GPC honoring across all jurisdictions, full preferences UI)
   swap in Cookiebot, Complianz, OneTrust, or CookieYes and remove this file.

   v3 (June 2026): language-aware (EN/ES), accessible modal with close button,
   ESC key, focus trap, body scroll lock, and compact bottom-right banner card.
*/
(function () {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  var STORAGE_KEY = 'il_privacy_choices_v1';
  var COOKIE_NAME = 'il_consent';
  var COOKIE_DAYS = 180;

  // Detect Spanish if <html lang="es"> or URL path starts with /es/
  function isSpanish() {
    var html = document.documentElement;
    var lang = (html.getAttribute('lang') || '').toLowerCase();
    if (lang === 'es' || lang.indexOf('es-') === 0) return true;
    try {
      if (location.pathname.indexOf('/es/') === 0 || location.pathname === '/es') return true;
    } catch (e) { /* ignore */ }
    return false;
  }

  var COPY = {
    en: {
      banner_title: 'Cookies & Privacy',
      banner_body: 'We use cookies, pixels, and call tracking to measure performance and improve this site. You can manage your choices anytime. See our <a href="/cookie-policy">Cookie Policy</a> and <a href="/privacy-policy">Privacy Policy</a>.',
      accept: 'Accept All',
      reject: 'Reject Non-Essential',
      manage: 'Manage Preferences',
      modal_title: 'Cookie & Privacy Choices',
      modal_intro: 'Choose how Insider Lawyers may use cookies and similar technologies on this device. Essential cookies cannot be disabled because they are required for the site to function.',
      essential_label: 'Essential',
      essential_desc: 'Required for site functionality.',
      analytics_label: 'Analytics',
      analytics_desc: 'Helps us understand how the site is used (e.g., GA4).',
      ads_label: 'Advertising',
      ads_desc: 'Supports ad attribution and remarketing (e.g., Google Ads, Meta, Reddit, Taboola, CallRail attribution).',
      personalization_label: 'Personalization',
      personalization_desc: 'Tailors ads and content to your interests.',
      dns_label: 'Do Not Sell or Share My Personal Information',
      dns_desc: 'Opt out of activity that may qualify as a sale or sharing under California law.',
      gpc_note: 'If your browser sends a Global Privacy Control (GPC) signal, we will treat it as a Do Not Sell or Share request for this browser and device.',
      save: 'Save Choices',
      close_label: 'Close cookie preferences'
    },
    es: {
      banner_title: 'Cookies y Privacidad',
      banner_body: 'Usamos cookies, p&iacute;xeles y seguimiento de llamadas para medir el rendimiento y mejorar este sitio. Puede administrar sus opciones en cualquier momento. Vea nuestra <a href="/es/politica-cookies/">Pol&iacute;tica de Cookies</a> y <a href="/es/politica-privacidad/">Pol&iacute;tica de Privacidad</a>.',
      accept: 'Aceptar Todo',
      reject: 'Rechazar No Esenciales',
      manage: 'Administrar Preferencias',
      modal_title: 'Preferencias de Cookies y Privacidad',
      modal_intro: 'Elija c&oacute;mo Insider Lawyers puede usar cookies y tecnolog&iacute;as similares en este dispositivo. Las cookies esenciales no se pueden desactivar porque son necesarias para que el sitio funcione.',
      essential_label: 'Esenciales',
      essential_desc: 'Necesarias para el funcionamiento del sitio.',
      analytics_label: 'Anal&iacute;tica',
      analytics_desc: 'Nos ayuda a entender c&oacute;mo se usa el sitio (por ejemplo, GA4).',
      ads_label: 'Publicidad',
      ads_desc: 'Apoya la atribuci&oacute;n de anuncios y el remarketing (Google Ads, Meta, Reddit, Taboola, CallRail).',
      personalization_label: 'Personalizaci&oacute;n',
      personalization_desc: 'Adapta los anuncios y el contenido a sus intereses.',
      dns_label: 'No Vender ni Compartir Mi Informaci&oacute;n Personal',
      dns_desc: 'Opte por no participar en actividades que puedan considerarse venta o compartir bajo la ley de California.',
      gpc_note: 'Si su navegador env&iacute;a una se&ntilde;al de Global Privacy Control (GPC), la trataremos como una solicitud de No Vender ni Compartir para este navegador y dispositivo.',
      save: 'Guardar preferencias',
      close_label: 'Cerrar preferencias de cookies'
    }
  };

  function t() { return isSpanish() ? COPY.es : COPY.en; }

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

  var lastFocusedTrigger = null;

  function ensureBanner() {
    if (document.getElementById('privacy-choices-banner')) return;
    var c = t();

    var bannerHtml = '' +
      '<div id="privacy-choices-banner" role="region" aria-label="' + c.banner_title + '">' +
        '<div class="pc-inner">' +
          '<p>' + c.banner_body + '</p>' +
          '<div class="pc-actions">' +
            '<button type="button" id="pc-accept">' + c.accept + '</button>' +
            '<button type="button" id="pc-reject" class="pc-secondary">' + c.reject + '</button>' +
            '<button type="button" id="pc-manage" class="pc-secondary">' + c.manage + '</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var modalHtml = '' +
      '<div id="privacy-choices-modal" role="dialog" aria-modal="true" aria-labelledby="pc-modal-title">' +
        '<div class="pc-modal" role="document">' +
          '<button type="button" class="pc-modal-close" id="pc-modal-close" aria-label="' + c.close_label + '">&times;</button>' +
          '<h2 id="pc-modal-title">' + c.modal_title + '</h2>' +
          '<p class="pc-modal-intro">' + c.modal_intro + '</p>' +
          '<div class="pc-category">' +
            '<label class="pc-toggle"><input type="checkbox" id="pc-essential" checked disabled><span><strong>' + c.essential_label + '</strong> &mdash; ' + c.essential_desc + '</span></label>' +
          '</div>' +
          '<div class="pc-category">' +
            '<label class="pc-toggle"><input type="checkbox" id="pc-analytics"><span><strong>' + c.analytics_label + '</strong> &mdash; ' + c.analytics_desc + '</span></label>' +
          '</div>' +
          '<div class="pc-category">' +
            '<label class="pc-toggle"><input type="checkbox" id="pc-ads"><span><strong>' + c.ads_label + '</strong> &mdash; ' + c.ads_desc + '</span></label>' +
          '</div>' +
          '<div class="pc-category">' +
            '<label class="pc-toggle"><input type="checkbox" id="pc-personalization"><span><strong>' + c.personalization_label + '</strong> &mdash; ' + c.personalization_desc + '</span></label>' +
          '</div>' +
          '<div class="pc-category">' +
            '<label class="pc-toggle"><input type="checkbox" id="pc-dns"><span><strong>' + c.dns_label + '</strong> &mdash; ' + c.dns_desc + '</span></label>' +
          '</div>' +
          '<p class="pc-gpc-note">' + c.gpc_note + '</p>' +
          '<div class="pc-modal-actions">' +
            '<button type="button" id="pc-modal-reject" class="pc-secondary">' + c.reject + '</button>' +
            '<button type="button" id="pc-modal-save" class="pc-secondary">' + c.save + '</button>' +
            '<button type="button" id="pc-modal-accept">' + c.accept + '</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var bannerWrap = document.createElement('div');
    bannerWrap.innerHTML = bannerHtml;
    document.body.appendChild(bannerWrap.firstChild);

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

  function focusableIn(modal) {
    return modal.querySelectorAll(
      'a[href], area[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
  }

  function trapTab(modal, e) {
    if (e.key !== 'Tab') return;
    var nodes = focusableIn(modal);
    if (!nodes.length) return;
    var first = nodes[0];
    var last = nodes[nodes.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openModal(state, triggerEl) {
    var m = document.getElementById('privacy-choices-modal');
    if (!m) return;
    lastFocusedTrigger = triggerEl || document.activeElement;
    document.getElementById('pc-analytics').checked = !!state.analytics;
    document.getElementById('pc-ads').checked = !!state.ads;
    document.getElementById('pc-personalization').checked = !!state.personalization;
    document.getElementById('pc-dns').checked = !!state.doNotSellOrShare;
    m.classList.add('is-visible');
    document.documentElement.classList.add('pc-modal-open');
    document.body.classList.add('pc-modal-open');
    setTimeout(function () {
      var closeBtn = document.getElementById('pc-modal-close');
      if (closeBtn) closeBtn.focus();
    }, 30);
  }

  function closeModal() {
    var m = document.getElementById('privacy-choices-modal');
    if (m) m.classList.remove('is-visible');
    document.documentElement.classList.remove('pc-modal-open');
    document.body.classList.remove('pc-modal-open');
    if (lastFocusedTrigger && typeof lastFocusedTrigger.focus === 'function') {
      try { lastFocusedTrigger.focus(); } catch (e) { /* ignore */ }
    }
  }

  function bind() {
    var gpc = detectGPC();

    document.getElementById('pc-accept').addEventListener('click', function () {
      var state = { analytics: true, ads: !gpc, personalization: !gpc, doNotSellOrShare: gpc, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); hideBanner();
    });
    document.getElementById('pc-reject').addEventListener('click', function () {
      var state = { analytics: false, ads: false, personalization: false, doNotSellOrShare: true, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); hideBanner();
    });
    document.getElementById('pc-manage').addEventListener('click', function (e) {
      openModal(readStored() || defaultStateFromGPC(), e.currentTarget);
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
    document.getElementById('pc-modal-reject').addEventListener('click', function () {
      var state = { analytics: false, ads: false, personalization: false, doNotSellOrShare: true, gpc: gpc, timestamp: Date.now() };
      writeStored(state); applyConsent(state); closeModal(); hideBanner();
    });
    document.getElementById('pc-modal-close').addEventListener('click', function () {
      closeModal();
    });

    var modal = document.getElementById('privacy-choices-modal');
    modal.addEventListener('click', function (e) {
      if (e.target === this) closeModal();
    });
    document.addEventListener('keydown', function (e) {
      if (!modal.classList.contains('is-visible')) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        closeModal();
      } else if (e.key === 'Tab') {
        trapTab(modal, e);
      }
    });

    // Wire "Manage Cookie & Privacy Choices" links / buttons (footer button, cookie policy page).
    document.querySelectorAll('[data-privacy-choices-open]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openModal(readStored() || defaultStateFromGPC(), el);
      });
    });
  }

  function init() {
    ensureBanner();
    bind();
    var stored = readStored();
    if (!stored) {
      if (typeof window.gtag !== 'function' && Array.isArray(window.dataLayer)) {
        window.gtag = function () { window.dataLayer.push(arguments); };
      }
      var initial = defaultStateFromGPC();
      applyConsent(initial);
      showBanner();
    } else {
      applyConsent(stored);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
