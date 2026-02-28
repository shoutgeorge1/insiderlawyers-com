(function() {
  // #region agent log
  function debugLog(location, message, data, hypothesisId) {
    var payload = { sessionId: '92bc37', location: location, message: message, data: data || {}, timestamp: Date.now() };
    if (hypothesisId) payload.hypothesisId = hypothesisId;
    fetch('http://127.0.0.1:7246/ingest/947b9d3f-79c7-44a4-b813-d8911803c79c', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '92bc37' }, body: JSON.stringify(payload) }).catch(function() {});
  }
  // #endregion
  function initSiteNav() {
    var navWrap = document.getElementById('header-nav-wrap');
    var mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    var header = document.getElementById('header');
    if (header && navWrap) {
      var lastScrollY = 0;
      var scrollThreshold = 80;
      window.addEventListener('scroll', function() {
        if (window.innerWidth > 767) {
          header.classList.remove('header--hidden');
          navWrap.classList.remove('header--hidden');
          return;
        }
        var currentScrollY = window.scrollY;
        if (currentScrollY > scrollThreshold) {
          if (currentScrollY > lastScrollY) {
            header.classList.add('header--hidden');
            navWrap.classList.add('header--hidden');
            debugLog('site-nav.js:scroll', 'Mobile header hidden', { scrollY: currentScrollY, hidden: true }, 'H3');
          } else {
            header.classList.remove('header--hidden');
            navWrap.classList.remove('header--hidden');
          }
        } else {
          header.classList.remove('header--hidden');
          navWrap.classList.remove('header--hidden');
        }
        lastScrollY = currentScrollY;
      }, { passive: true });
      if (typeof requestAnimationFrame !== 'undefined') {
        requestAnimationFrame(function() {
          var hr = header.getBoundingClientRect();
          var nr = navWrap.getBoundingClientRect();
          debugLog('site-nav.js:init', 'Header heights on load', { headerHeight: hr.height, navHeight: nr.height, innerWidth: window.innerWidth, totalPx: hr.height + nr.height }, 'H1');
        });
      }
    }
    if (navWrap && mobileMenuToggle) {
      mobileMenuToggle.setAttribute('type', 'button');
      mobileMenuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        var willOpen = !navWrap.classList.contains('is-open');
        navWrap.classList.toggle('is-open', willOpen);
        mobileMenuToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      });
    }
    var dropdownToggles = document.querySelectorAll('.header-nav-row .nav-link--dropdown, #primary-nav .nav-link--dropdown');
    dropdownToggles.forEach(function(toggle) {
      toggle.setAttribute('role', 'button');
      toggle.setAttribute('tabindex', '0');
      toggle.setAttribute('aria-expanded', 'false');
      function handleToggle(e) {
        if (window.innerWidth > 900) return;
        var parentItem = toggle.closest('.nav-item');
        if (!parentItem) return;
        var willOpen = !parentItem.classList.contains('is-open');
        parentItem.classList.toggle('is-open', willOpen);
        toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        if (e) {
          e.preventDefault();
          e.stopPropagation();
        }
      }
      toggle.addEventListener('click', function(e) {
        if (toggle._touched) {
          toggle._touched = false;
          e.preventDefault();
          e.stopPropagation();
          return;
        }
        handleToggle(e);
      });
      toggle.addEventListener('touchend', function(e) {
        if (window.innerWidth > 900) return;
        toggle._touched = true;
        handleToggle(e);
      }, { passive: false });
      toggle.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleToggle();
        }
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteNav);
  } else {
    initSiteNav();
  }
})();
