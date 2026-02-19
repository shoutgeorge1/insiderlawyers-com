(function() {
  function initSiteNav() {
    var navWrap = document.getElementById('header-nav-wrap');
    var mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    if (navWrap && mobileMenuToggle) {
      mobileMenuToggle.addEventListener('click', function() {
        var willOpen = !navWrap.classList.contains('is-open');
        navWrap.classList.toggle('is-open', willOpen);
        mobileMenuToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      });
    }
    var dropdownToggles = document.querySelectorAll('.header-nav-row .nav-link--dropdown');
    dropdownToggles.forEach(function(toggle) {
      toggle.setAttribute('role', 'button');
      toggle.setAttribute('tabindex', '0');
      toggle.setAttribute('aria-expanded', 'false');
      function handleToggle() {
        if (window.innerWidth > 900) return;
        var parentItem = toggle.closest('.nav-item');
        if (!parentItem) return;
        var willOpen = !parentItem.classList.contains('is-open');
        parentItem.classList.toggle('is-open', willOpen);
        toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      }
      toggle.addEventListener('click', handleToggle);
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
