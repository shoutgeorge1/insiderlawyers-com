(function () {
  function initTapToCallBar() {
    var bar = document.getElementById("tap-to-call-bar");
    if (!bar) return;
    var body = document.body;
    if (
      !body.classList.contains("home-ppc") &&
      !body.classList.contains("ppc-page")
    ) {
      return;
    }
    var threshold = 120;
    var reduceMotion = false;
    try {
      reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) {}
    if (reduceMotion) {
      bar.classList.add("is-visible");
      document.body.classList.add("has-tap-bar-visible");
      return;
    }
    function update() {
      if (window.matchMedia("(min-width: 901px)").matches) {
        bar.classList.remove("is-visible");
        document.body.classList.remove("has-tap-bar-visible");
        return;
      }
      var y = window.scrollY || window.pageYOffset;
      if (y >= threshold) {
        bar.classList.add("is-visible");
        document.body.classList.add("has-tap-bar-visible");
      } else {
        bar.classList.remove("is-visible");
        document.body.classList.remove("has-tap-bar-visible");
      }
    }
    update();
    window.addEventListener(
      "scroll",
      function () {
        window.requestAnimationFrame(update);
      },
      { passive: true }
    );
    window.addEventListener("resize", update, { passive: true });
  }

  function initSiteNav() {
    initTapToCallBar();

    var navWrap = document.getElementById("header-nav-wrap");
    var mobileMenuToggle = document.getElementById("mobile-menu-toggle");

    if (navWrap && mobileMenuToggle) {
      mobileMenuToggle.setAttribute("type", "button");
      mobileMenuToggle.addEventListener("click", function (e) {
        e.preventDefault();
        var willOpen = !navWrap.classList.contains("is-open");
        navWrap.classList.toggle("is-open", willOpen);
        mobileMenuToggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
        mobileMenuToggle.setAttribute(
          "aria-label",
          willOpen ? "Close menu" : "Open menu"
        );
      });
    }

    var dropdownToggles = document.querySelectorAll(
      "#primary-nav .nav-link--dropdown"
    );
    dropdownToggles.forEach(function (toggle) {
      if (!toggle.hasAttribute("aria-expanded"))
        toggle.setAttribute("aria-expanded", "false");
      toggle.addEventListener("click", function (e) {
        if (window.innerWidth > 900) return;
        e.preventDefault();
        e.stopPropagation();
        var parentItem = toggle.closest(".nav-item");
        if (!parentItem) return;
        var willOpen = !parentItem.classList.contains("is-open");
        parentItem.classList.toggle("is-open", willOpen);
        toggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
      });
      toggle.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (window.innerWidth > 900) return;
          var parentItem = toggle.closest(".nav-item");
          if (!parentItem) return;
          var willOpen = !parentItem.classList.contains("is-open");
          parentItem.classList.toggle("is-open", willOpen);
          toggle.setAttribute("aria-expanded", willOpen ? "true" : "false");
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSiteNav);
  } else {
    initSiteNav();
  }
})();
