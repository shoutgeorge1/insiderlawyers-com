/**
 * Google Ads / UTM form tracking for insiderlawyers.com lead form.
 * Reads ial_* from localStorage, adds tracking + combined "tracking" field, honeypot check.
 * Include after utm-gclid-tracking.js on home and PPC pages.
 */
(function() {
  'use strict';
  var TRACK_KEYS = ['gclid','gbraid','wbraid','utm_source','utm_medium','utm_campaign','utm_term','utm_content'];

  function addHoneypot(form) {
    if (form.querySelector('input[name="website_url"]')) return;
    var hp = document.createElement('input');
    hp.type = 'text';
    hp.name = 'website_url';
    hp.setAttribute('tabindex', '-1');
    hp.setAttribute('autocomplete', 'off');
    hp.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none;';
    hp.setAttribute('aria-hidden', 'true');
    form.appendChild(hp);
  }

  function run() {
    var form = document.getElementById('case-evaluation-form');
    if (!form) return;

    addHoneypot(form);

    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var hp = form.querySelector('input[name="website_url"]');
      if (hp && hp.value && hp.value.trim() !== '') {
        return false;
      }

      var fd = new FormData(form);
      fd.delete('website_url');

      var parts = [];
      for (var k = 0; k < TRACK_KEYS.length; k++) {
        var key = TRACK_KEYS[k];
        var v = null;
        try { v = localStorage.getItem('ial_' + key); } catch (err) {}
        if (v) {
          fd.set(key, v);
          parts.push(key + '=' + encodeURIComponent(v));
        }
      }
      if (parts.length) fd.set('tracking', parts.join(' | '));

      var nextUrl = '';
      var nextInput = form.querySelector('input[name="_next"]');
      if (nextInput && nextInput.value) nextUrl = nextInput.value;

      var action = form.getAttribute('action') || form.action;
      if (!action) return false;

      var submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        if (submitBtn.textContent) submitBtn.setAttribute('data-original-text', submitBtn.textContent);
        submitBtn.textContent = 'Sending…';
      }

      fetch(action, {
        method: 'POST',
        body: fd,
        headers: { 'Accept': 'application/json' }
      })
        .then(function(res) {
          if (nextUrl) window.location.href = nextUrl;
          else if (res.ok) window.location.href = 'https://call.insideraccidentlawyers.com/thank-you.html';
        })
        .catch(function() {
          if (submitBtn) {
            submitBtn.disabled = false;
            if (submitBtn.getAttribute('data-original-text')) submitBtn.textContent = submitBtn.getAttribute('data-original-text');
            else submitBtn.textContent = 'Get My Free Review';
          }
        });

      return false;
    }, false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
