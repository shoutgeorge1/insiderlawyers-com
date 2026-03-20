(function () {
  "use strict";

  function isConversionBody() {
    var b = document.body;
    return (
      b.classList.contains("home-ppc") ||
      b.classList.contains("ppc-page") ||
      b.classList.contains("has-sticky-cta")
    );
  }

  function setNavOpen(open) {
    document.body.classList.toggle("nav-open", !!open);
    var navWrap = document.getElementById("header-nav-wrap");
    var mobileMenuToggle = document.getElementById("mobile-menu-toggle");
    if (navWrap) {
      navWrap.classList.toggle("is-open", !!open);
    }
    if (mobileMenuToggle) {
      mobileMenuToggle.setAttribute("aria-expanded", open ? "true" : "false");
      mobileMenuToggle.setAttribute(
        "aria-label",
        open ? "Close menu" : "Open menu"
      );
    }
    if (window.matchMedia("(max-width: 900px)").matches) {
      document.documentElement.classList.toggle("nav-open-lock", !!open);
    }
  }

  function initTapToCallBar() {
    if (!isConversionBody()) {
      var bar = document.getElementById("tap-to-call-bar");
      if (bar) {
        bar.classList.remove("is-visible");
      }
      document.body.classList.remove("has-tap-bar-visible");
      return;
    }
    var bar = document.getElementById("tap-to-call-bar");
    if (!bar) return;
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
        e.stopPropagation();
        var open = !document.body.classList.contains("nav-open");
        setNavOpen(open);
      });

      document.addEventListener(
        "click",
        function (e) {
          if (!document.body.classList.contains("nav-open")) return;
          if (window.matchMedia("(min-width: 901px)").matches) return;
          var t = e.target;
          if (navWrap.contains(t) || mobileMenuToggle.contains(t)) return;
          setNavOpen(false);
        },
        false
      );

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          setNavOpen(false);
        }
      });

      window.addEventListener(
        "resize",
        function () {
          if (window.matchMedia("(min-width: 901px)").matches) {
            setNavOpen(false);
          }
        },
        { passive: true }
      );
    }

    var dropdownToggles = document.querySelectorAll(
      "#primary-nav .nav-link--dropdown"
    );
    dropdownToggles.forEach(function (toggle) {
      if (!toggle.hasAttribute("aria-expanded")) {
        toggle.setAttribute("aria-expanded", "false");
      }
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
