#!/usr/bin/env python3
"""Apply 3 header replacements to all HTML files with old sticky-header in insiderlawyers-com."""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_HEADER_BLOCK = """    </script>    <script>
      document.addEventListener('DOMContentLoaded',function(){var h=document.querySelector('.sticky-header');var ly=0;var nw=document.getElementById('header-nav-wrap');var mt=document.getElementById('mobile-menu-toggle');if(h){window.addEventListener('scroll',function(){if(window.innerWidth>767){h.classList.remove('header--hidden');return;}var y=window.scrollY;if(y>80){if(y>ly){h.classList.add('header--hidden');if(nw)nw.classList.remove('is-open');if(mt)mt.setAttribute('aria-expanded','false');}else h.classList.remove('header--hidden');}else h.classList.remove('header--hidden');ly=y;},{passive:true});}});
    </script><header class="sticky-header">
        <div class="container">
            <div class="header-content">
                <div class="header-col header-col--logo">
                    <a href="/"><img src="https://www.insiderlawyers.com/images/la/logo.png" alt="Insider Accident Lawyers" class="header-logo"></a>
                </div>
                <div class="header-col header-col--proof">
                    <div class="header-proof-title">Over $100 Million Recovered</div>
                    <p>in Verdicts &amp; Settlements<small><sup><a href="#results-disclaimer-note" aria-label="Results disclaimer reference">*</a></sup></small></p>
                </div>
                <div class="header-col header-col--call">
                    <span class="header-call-label">Available 24/7 &#8212; Call Now:</span>
                    <a href="tel:844-467-4335" class="header-call-number" data-callrail-phone="844-467-4335">844-467-4335</a>
                    <span class="header-lang">Hablamos Espa&#241;ol</span>
                </div>
            </div>
            <div id="header-nav-wrap" class="header-nav-wrap">
            <button class="mobile-menu-toggle" id="mobile-menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle menu"><span></span><span></span><span></span></button>
            <nav class="header-nav-row" id="primary-nav" aria-label="Primary">"""

NEW_HEADER_BLOCK = """    </script>    <script>
      document.addEventListener('DOMContentLoaded',function(){var header=document.getElementById('header');var navWrap=document.getElementById('header-nav-wrap');var ly=0;function setHeaderHidden(hidden){if(header)header.classList.toggle('header--hidden',hidden);if(navWrap)navWrap.classList.toggle('header--hidden',hidden);}(header||navWrap)&&window.addEventListener('scroll',function(){if(window.innerWidth>767){setHeaderHidden(false);return;}var y=window.scrollY;if(y>80)setHeaderHidden(y>ly);else setHeaderHidden(false);ly=y;},{passive:true});});
    </script>
    <header class="header" id="header">
        <div class="mid-container">
            <div class="header__left">
                <figure class="header__logo" id="logo"><a href="/"><img src="https://www.insiderlawyers.com/images/la/logo.png" width="271" height="111" alt="Insider Accident Lawyers" class="header__logo-img"></a></figure>
            </div>
            <div class="header__middle">
                <div class="header__middle__title"><a href="/#case-results" style="color:inherit;text-decoration:none;">Over $100 Million Recovered</a></div>
                <p>in Verdicts &amp; Settlements<small><sup><a href="#footer-verdicts-note" id="verdicts-asterisk" style="color:inherit;text-decoration:none;">*</a></sup></small></p>
            </div>
            <div class="header__right">
                <span class="header__title">Available 24/7 &#8212; Call Now:</span>
                <a class="link header__number" href="tel:844-467-4335" data-callrail-phone="844-467-4335">844-467-4335</a>
                <span class="header__lang">Hablamos Espa&#241;ol</span>
            </div>
        </div>
    </header>
    <div class="header-nav-wrap" id="header-nav-wrap">
        <div class="container">
            <button type="button" class="mobile-menu-toggle" id="mobile-menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle menu"><span></span><span></span><span></span></button>
            <nav class="header-nav-row" id="primary-nav" aria-label="Primary">"""

OLD_CLOSE = """            </nav>
            </div>
        </div>
    </header>
    <main>"""

NEW_CLOSE = """            </nav>
        </div>
    </div>
    <a href="tel:844-467-4335" class="tap-to-call-bar" data-callrail-phone="844-467-4335" aria-label="Tap to call for free consultation">
        <svg class="tap-to-call-bar__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
        <span class="tap-to-call-bar__text">Tap to Call</span>
    </a>
    <main>"""

# CSS: remove .sticky-header through .content-body a (before footer)
CSS_OLD_1 = """        .btn-secondary:hover{background:#0f3261;transform:translateY(-2px)}
        .sticky-header{position:sticky;top:0;background:var(--brand-white);border-bottom:3px solid var(--brand-accent-yellow);padding:10px 0 8px;z-index:1000;box-shadow:0 4px 14px rgba(1,54,108,.12)};transition:transform .25s ease;transition:transform .25s ease
        .header-content{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px}
        .header-col--proof{text-align:center;display:flex;flex-direction:column;align-items:center}
        .header-proof-title{font-family:Roboto,Arial,sans-serif;font-size:1rem;font-weight:900;color:var(--brand-navy);line-height:1.1;letter-spacing:-.01em;text-transform:uppercase;background:linear-gradient(180deg,#ffffff 0%,#f4f8fd 100%);border:1px solid rgba(1,54,108,.2);border-radius:999px;padding:7px 14px;box-shadow:0 3px 10px rgba(1,54,108,.1)}
        .header-col--proof p{margin:6px 0 0;font-size:.78rem;color:var(--brand-gray-700);font-weight:700;letter-spacing:.02em;text-transform:uppercase}
        .header-col--call{text-align:right}
        .header-call-label{display:block;font-size:.74rem;color:var(--brand-gray-700);font-weight:800;text-transform:uppercase;letter-spacing:.03em}
        .header-call-number{display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#ffd54f 0%,#ffbf00 50%,#f5a623 100%);color:#01366c;font-family:Roboto,Arial,sans-serif;font-size:1.08rem;line-height:1;font-weight:900;text-decoration:none;padding:.62rem .9rem;border-radius:10px;box-shadow:0 3px 0 #c99400,0 6px 16px rgba(255,191,0,.35);border:1px solid rgba(201,148,0,.55);margin-top:4px}
        .header-logo{max-width:250px;height:auto;filter:brightness(0) saturate(100%)}
        .header-nav-row{display:flex;justify-content:center;flex-wrap:wrap;gap:10px;padding-top:10px}
        .nav-link{display:inline-flex;align-items:center;justify-content:center;min-height:38px;color:var(--brand-navy);text-decoration:none;font-weight:700;font-size:.82rem;padding:8px 14px;background:linear-gradient(180deg,#ffffff 0%,#f6f9fd 100%);border:1px solid rgba(1,54,108,.2);border-radius:8px;box-shadow:0 1px 3px rgba(1,54,108,.07);transition:all .2s ease}
        .nav-link:hover{color:var(--brand-blue);border-color:#9fbadb;background:#eef4fb;transform:translateY(-1px)}
        .nav-link--primary{background:linear-gradient(180deg,#01468a 0%,#01366c 100%);color:#fff;border-color:#01366c}
        .nav-link--primary:hover{color:#fff;background:linear-gradient(180deg,#0253a4 0%,#01468a 100%)}
        .nav-link--dropdown{cursor:default}
        .nav-item{position:relative}
        .mobile-menu-toggle{display:none;width:44px;height:38px;border:1px solid rgba(1,54,108,.25);border-radius:8px;background:#fff;align-items:center;justify-content:center;flex-direction:column;gap:5px;cursor:pointer}
        .mobile-menu-toggle span{width:20px;height:2px;background:#01366c;border-radius:2px;display:block}
        .nav-dropdown{position:absolute;left:0;top:100%;min-width:880px;max-width:1100px;background:#fff;border:1px solid #d3e0f0;border-radius:10px;box-shadow:0 10px 26px rgba(1,54,108,.15);padding:12px;display:none;z-index:1200;grid-template-columns:repeat(4,minmax(200px,1fr));gap:6px 12px;align-items:start}
        .nav-item:hover .nav-dropdown,.nav-item:focus-within .nav-dropdown{display:grid}
        .nav-dropdown a{display:block;padding:9px 10px;color:var(--brand-navy);text-decoration:none;font-size:.84rem;font-weight:600;border-radius:6px}
        .nav-dropdown a:hover{background:#eef4fb;color:var(--brand-blue)}
        .content-body a{color:var(--brand-blue);text-decoration:underline}"""

CSS_NEW_1 = """        .btn-secondary:hover{background:#0f3261;transform:translateY(-2px)}
        .content-body a{color:var(--brand-blue);text-decoration:underline}"""

# Two variants of @media block (with and without padding-bottom:0)
MEDIA_OLD_A = """        @media(max-width:767px){.sticky-header.header--hidden{transform:translateY(-100%)}}
 @media(max-width:900px){.header-content{grid-template-columns:1fr;gap:10px}.header-col--logo{order:1;text-align:center}.header-col--call{order:2;text-align:center}.header-col--proof{order:3;text-align:center}.mobile-menu-toggle{display:inline-flex}.header-nav-row{display:none;flex-direction:column;gap:8px;padding:8px 0 4px}.header-nav-wrap.is-open .header-nav-row{display:flex}.nav-link{width:100%;justify-content:space-between;min-height:36px;padding:7px 12px}.nav-item{display:block;width:100%;padding-bottom:0}.nav-item .nav-link{width:100%}.nav-dropdown{position:static;display:none;margin-top:6px;min-width:0;box-shadow:none;border:1px solid #dce6f3;grid-template-columns:1fr}.nav-item.is-open .nav-dropdown{display:grid}}
        @media(max-width:768px){h1{font-size:28px}h2{font-size:24px}.footer-content{grid-template-columns:1fr;text-align:center}}"""

MEDIA_OLD_B = """        @media(max-width:767px){.sticky-header.header--hidden{transform:translateY(-100%)}}
 @media(max-width:900px){.header-content{grid-template-columns:1fr;gap:10px}.header-col--logo{order:1;text-align:center}.header-col--call{order:2;text-align:center}.header-col--proof{order:3;text-align:center}.mobile-menu-toggle{display:inline-flex}.header-nav-row{display:none;flex-direction:column;gap:8px;padding:8px 0 4px}.header-nav-wrap.is-open .header-nav-row{display:flex}.nav-link{width:100%;justify-content:space-between;min-height:36px;padding:7px 12px}.nav-item{display:block;width:100%}.nav-item .nav-link{width:100%}.nav-dropdown{position:static;display:none;margin-top:6px;min-width:0;box-shadow:none;border:1px solid #dce6f3;grid-template-columns:1fr}.nav-item.is-open .nav-dropdown{display:grid}}
        @media(max-width:768px){h1{font-size:28px}h2{font-size:24px}.footer-content{grid-template-columns:1fr;text-align:center}}"""

MEDIA_NEW = """        @media(max-width:768px){h1{font-size:28px}h2{font-size:24px}.footer-content{grid-template-columns:1fr;text-align:center}}"""


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'sticky-header' not in content:
        return False
    original = content

    # 1) Header block
    if OLD_HEADER_BLOCK in content:
        content = content.replace(OLD_HEADER_BLOCK, NEW_HEADER_BLOCK, 1)
    else:
        return False

    # 2) Closing + tap-to-call
    if OLD_CLOSE not in content:
        return False
    content = content.replace(OLD_CLOSE, NEW_CLOSE, 1)

    # 3) CSS block
    if CSS_OLD_1 in content:
        content = content.replace(CSS_OLD_1, CSS_NEW_1, 1)

    # 4) @media blocks (try A then B)
    if MEDIA_OLD_A in content:
        content = content.replace(MEDIA_OLD_A, MEDIA_NEW, 1)
    elif MEDIA_OLD_B in content:
        content = content.replace(MEDIA_OLD_B, MEDIA_NEW, 1)

    if content == original:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def main():
    count = 0
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('_old-site-extract', 'components', 'scripts', '.git', 'node_modules', '_dev')]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, BASE)
            if '_old-site-extract' in rel or 'components' in rel or 'social-assets' in rel:
                continue
            try:
                if process(path):
                    count += 1
                    print('Updated:', rel)
            except Exception as e:
                print('Error', rel, e)
    print('Done. Updated', count, 'files.')


if __name__ == '__main__':
    main()
