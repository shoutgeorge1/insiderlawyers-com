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

  function ensureHidden(form, name, value) {
    var el = form.querySelector('input[name="' + name + '"]');
    if (el) {
      el.value = value || '';
      return;
    }
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value || '';
    form.appendChild(input);
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

      var parts = [];
      for (var k = 0; k < TRACK_KEYS.length; k++) {
        var key = TRACK_KEYS[k];
        var v = null;
        try { v = localStorage.getItem('ial_' + key); } catch (err) {}
        if (v) {
          ensureHidden(form, key, v);
          parts.push(key + '=' + encodeURIComponent(v));
        }
      }
      if (parts.length) ensureHidden(form, 'tracking', parts.join(' | '));

      if (hp) hp.removeAttribute('name');

      form.submit();
      return false;
    }, false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
