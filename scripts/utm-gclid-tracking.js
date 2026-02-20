/**
 * Persistent Google Click ID and UTM parameter tracking + honeypot.
 * Insert once before </body>. Vanilla JS, no dependencies.
 */
(function() {
  'use strict';
  var STORAGE_KEY = 'ial_utm';
  var PARAMS = ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  function safeDecode(str) {
    try {
      return decodeURIComponent(String(str).replace(/\+/g, ' '));
    } catch (e) {
      return '';
    }
  }

  function getQueryObject() {
    var q = window.location.search.substring(1);
    var out = {};
    if (!q) return out;
    q.split('&').forEach(function(pair) {
      var i = pair.indexOf('=');
      if (i === -1) return;
      var k = safeDecode(pair.slice(0, i));
      var v = safeDecode(pair.slice(i + 1));
      if (k && out[k] === undefined) out[k] = v;
    });
    return out;
  }

  function readStored() {
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      return s ? JSON.parse(s) : {};
    } catch (e) {
      return {};
    }
  }

  function writeStored(obj) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
    } catch (e) {}
  }

  (function captureFromUrl() {
    var q = getQueryObject();
    var stored = readStored();
    PARAMS.forEach(function(key) {
      if (q[key] !== undefined && q[key] !== '') {
        stored[key] = q[key];
      }
    });
    writeStored(stored);
  })();

  function ensureHidden(form, name, value) {
    var existing = form.querySelector('input[name="' + name + '"]');
    if (existing) {
      if (existing.type === 'hidden') existing.value = value || '';
      return;
    }
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value || '';
    form.appendChild(input);
  }

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

  function wireForm(form) {
    var stored = readStored();
    PARAMS.forEach(function(key) {
      ensureHidden(form, key, stored[key]);
    });
    addHoneypot(form);
    form.addEventListener('submit', function(e) {
      var hp = form.querySelector('input[name="website_url"]');
      if (hp && hp.value && hp.value.trim() !== '') {
        e.preventDefault();
        return false;
      }
    }, false);
  }

  function run() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
      wireForm(forms[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
