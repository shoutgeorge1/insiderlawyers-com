/**
 * Google Ads / UTM form tracking for insiderlawyers.com lead form.
 * Uses FormSubmit AJAX endpoint so we control the redirect and can see errors.
 * v5
 */
(function() {
  'use strict';
  var TRACK_KEYS = ['gclid','gbraid','wbraid','utm_source','utm_medium','utm_campaign','utm_term','utm_content'];
  var THANK_YOU = 'https://www.insiderlawyers.com/thank-you/';

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
      e.stopImmediatePropagation();

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

      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn ? submitBtn.textContent : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending\u2026';
      }

      var actionUrl = form.getAttribute('action') || '';
      var ajaxUrl = actionUrl.replace('https://formsubmit.co/', 'https://formsubmit.co/ajax/');

      fetch(ajaxUrl, {
        method: 'POST',
        body: fd,
        headers: { 'Accept': 'application/json' }
      })
        .then(function(res) { return res.json(); })
        .then(function(data) {
          if (data && data.success) {
            window.location.href = THANK_YOU;
          } else {
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.textContent = originalText;
            }
            alert('Something went wrong. Please call us at 844-467-4335.');
            console.error('FormSubmit response:', data);
          }
        })
        .catch(function(err) {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
          alert('Connection error. Please call us at 844-467-4335.');
          console.error('FormSubmit error:', err);
        });

      return false;
    }, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
