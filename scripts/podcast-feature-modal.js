/**
 * Podcast Feature Modal - Beyond the Gavel
 * 8s delay or exit intent (desktop). 7-day localStorage suppression.
 * Vanilla JS, no dependencies.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'podcast_feature_dismissed_until';
  var SUPPRESS_DAYS = 7;
  var DELAY_MS = 8000;
  var LINKEDIN_EVENT_URL = 'https://www.linkedin.com/events/7428108930947518464/';

  function isSuppressed() {
    try {
      var val = localStorage.getItem(STORAGE_KEY);
      if (!val) return false;
      return Date.now() < parseInt(val, 10);
    } catch (e) {
      return false;
    }
  }

  function suppress() {
    try {
      var until = Date.now() + (SUPPRESS_DAYS * 24 * 60 * 60 * 1000);
      localStorage.setItem(STORAGE_KEY, String(until));
    } catch (e) {}
  }

  function isReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function isDesktop() {
    return window.matchMedia('(min-width: 768px)').matches;
  }

  var modal = null;
  var timerId = null;
  var exitIntentBound = false;

  function getModalHTML() {
    return (
      '<div class="podcast-feature-modal" id="podcast-feature-modal" role="dialog" aria-modal="true" aria-labelledby="podcast-modal-headline" aria-describedby="podcast-modal-desc" data-open="false">' +
        '<div class="podcast-feature-modal__backdrop" data-dismiss></div>' +
        '<div class="podcast-feature-modal__box" role="document">' +
          '<button type="button" class="podcast-feature-modal__close" aria-label="Close" data-close>' +
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>' +
          '</button>' +
          '<div class="podcast-feature-modal__inner">' +
            '<div class="podcast-feature-modal__layout">' +
              '<div class="podcast-feature-modal__visual">' +
                '<img src="https://www.insiderlawyers.com/images/la/donn-christensen.webp" alt="Attorney Donn Christensen" width="140" height="140" loading="lazy">' +
                '<span class="podcast-feature-modal__badge">Beyond the Gavel</span>' +
              '</div>' +
              '<div class="podcast-feature-modal__content">' +
                '<p class="podcast-feature-modal__eyebrow" aria-hidden="true">' +
                  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/></svg>' +
                  ' Featured Guest' +
                '</p>' +
                '<h2 id="podcast-modal-headline" class="podcast-feature-modal__headline"><span class="podcast-feature-modal__name">Donn Christensen</span> on Beyond the Gavel</h2>' +
                '<p id="podcast-modal-desc" class="podcast-feature-modal__body">Trial attorney Donn Christensen shares real-world legal perspective and advocacy beyond the courtroom. Tune in on LinkedIn.</p>' +
                '<a href="' + LINKEDIN_EVENT_URL + '" class="podcast-feature-modal__cta" target="_blank" rel="noopener noreferrer" data-cta>' +
                  '<svg class="podcast-feature-modal__cta-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>' +
                  ' Watch on LinkedIn' +
                '</a>' +
                '<button type="button" class="podcast-feature-modal__dismiss" data-dismiss-btn>No thanks</button>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  function focusable(el) {
    var sel = 'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])';
    return Array.prototype.slice.call(el.querySelectorAll(sel)).filter(function (n) {
      return n.offsetParent !== null && !n.disabled;
    });
  }

  function trapFocus(container) {
    var nodes = focusable(container);
    if (nodes.length === 0) return;
    var first = nodes[0];
    var last = nodes[nodes.length - 1];
    container.addEventListener('keydown', function onKey(e) {
      if (e.key !== 'Tab') return;
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });
  }

  function openModal() {
    if (!modal) return;
    if (timerId) {
      clearTimeout(timerId);
      timerId = null;
    }
    modal.setAttribute('data-open', 'true');
    document.body.style.overflow = 'hidden';
    var first = focusable(modal)[0];
    if (first) first.focus();
  }

  function closeModal(suppressShow) {
    if (!modal) return;
    modal.setAttribute('data-open', 'false');
    document.body.style.overflow = '';
    if (suppressShow) suppress();
  }

  function init() {
    if (isSuppressed()) return;

    var wrap = document.createElement('div');
    wrap.innerHTML = getModalHTML();
    modal = wrap.firstElementChild;
    document.body.appendChild(modal);

    var box = modal.querySelector('.podcast-feature-modal__box');
    trapFocus(box);

    function handleClose(suppressShow) {
      closeModal(suppressShow);
    }

    modal.querySelector('[data-close]').addEventListener('click', function () {
      handleClose(true);
    });

    modal.querySelector('[data-dismiss]').addEventListener('click', function (e) {
      if (e.target === modal.querySelector('[data-dismiss]')) handleClose(true);
    });

    modal.querySelector('[data-dismiss-btn]').addEventListener('click', function () {
      handleClose(true);
    });

    modal.querySelector('[data-cta]').addEventListener('click', function () {
      handleClose(true);
    });

    document.addEventListener('keydown', function onEsc(e) {
      if (e.key === 'Escape' && modal.getAttribute('data-open') === 'true') {
        handleClose(true);
      }
    });

    if (isDesktop()) {
      document.addEventListener('mouseout', function exitIntent(e) {
        if (e.clientY <= 0 && !exitIntentBound) {
          exitIntentBound = true;
          document.removeEventListener('mouseout', exitIntent);
          openModal();
        }
      });
    }

    timerId = setTimeout(function () {
      if (modal.getAttribute('data-open') !== 'true' && !exitIntentBound) {
        openModal();
      }
    }, DELAY_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
