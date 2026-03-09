(function() {
  function initSiteNav() {
    var navWrap = document.getElementById('header-nav-wrap');
    var mobileMenuToggle = document.getElementById('mobile-menu-toggle');

    if (navWrap && mobileMenuToggle) {
      mobileMenuToggle.setAttribute('type', 'button');
      mobileMenuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        var willOpen = !navWrap.classList.contains('is-open');
        navWrap.classList.toggle('is-open', willOpen);
        mobileMenuToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        mobileMenuToggle.setAttribute('aria-label', willOpen ? 'Close menu' : 'Open menu');
      });
    }

    var dropdownToggles = document.querySelectorAll('#primary-nav .nav-link--dropdown');
    dropdownToggles.forEach(function(toggle) {
      if (!toggle.hasAttribute('aria-expanded')) toggle.setAttribute('aria-expanded', 'false');
      toggle.addEventListener('click', function(e) {
        if (window.innerWidth > 900) return;
        e.preventDefault();
        e.stopPropagation();
        var parentItem = toggle.closest('.nav-item');
        if (!parentItem) return;
        var willOpen = !parentItem.classList.contains('is-open');
        parentItem.classList.toggle('is-open', willOpen);
        toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      });
      toggle.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          if (window.innerWidth > 900) return;
          var parentItem = toggle.closest('.nav-item');
          if (!parentItem) return;
          var willOpen = !parentItem.classList.contains('is-open');
          parentItem.classList.toggle('is-open', willOpen);
          toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
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
