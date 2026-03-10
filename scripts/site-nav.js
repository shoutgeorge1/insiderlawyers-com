(function() {
  function injectHeaderScrollStyles() {
    if (document.getElementById('header-scroll-styles')) return;
    var style = document.createElement('style');
    style.id = 'header-scroll-styles';
    style.textContent = [
      '.header.header--scroll-ready, .header-nav-wrap.header--scroll-ready { transition: transform 0.25s ease-out; }',
      '.header.header--scroll-hide { transform: translateY(-100%); }',
      '.header-nav-wrap.header--scroll-hide { transform: translateY(-100%); }'
    ].join('\n');
    document.head.appendChild(style);
  }

  function initHeaderScrollHide() {
    var header = document.getElementById('header');
    var navWrap = document.getElementById('header-nav-wrap');
    if (!header && !navWrap) return;

    injectHeaderScrollStyles();
    var lastScrollY = window.scrollY || window.pageYOffset;
    var threshold = 80;
    var ticking = false;

    function updateHeaderVisibility() {
      var scrollY = window.scrollY || window.pageYOffset;
      if (scrollY <= threshold) {
        header && header.classList.remove('header--scroll-hide');
        navWrap && navWrap.classList.remove('header--scroll-hide');
      } else if (scrollY > lastScrollY) {
        header && header.classList.add('header--scroll-hide');
        navWrap && navWrap.classList.add('header--scroll-hide');
      } else {
        header && header.classList.remove('header--scroll-hide');
        navWrap && navWrap.classList.remove('header--scroll-hide');
      }
      lastScrollY = scrollY;
      ticking = false;
    }

    function onScroll() {
      if (!ticking) {
        window.requestAnimationFrame(updateHeaderVisibility);
        ticking = true;
      }
    }

    header && header.classList.add('header--scroll-ready');
    navWrap && navWrap.classList.add('header--scroll-ready');
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function initSiteNav() {
    var navWrap = document.getElementById('header-nav-wrap');
    var mobileMenuToggle = document.getElementById('mobile-menu-toggle');

    initHeaderScrollHide();

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
