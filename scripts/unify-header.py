#!/usr/bin/env python3
"""
Replace old sticky-header with home-page header across all HTML in insiderlawyers-com.
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Marker: end of old header block (before <nav>)
NAV_START = '<nav class="header-nav-row" id="primary-nav" aria-label="Primary">'

# New header bar + nav wrapper opening (same as home; for inner pages use /#case-results and #footer-verdicts-note)
NEW_HEADER_AND_NAV_OPEN = '''    <header class="header" id="header">
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
            <button type="button" class="mobile-menu-toggle" id="mobile-menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle menu">
                <span></span><span></span><span></span>
            </button>
            ''' + NAV_START

TAP_TO_CALL = '''
    <a href="tel:844-467-4335" class="tap-to-call-bar" data-callrail-phone="844-467-4335" aria-label="Tap to call for free consultation">
        <svg class="tap-to-call-bar__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
        <span class="tap-to-call-bar__text">Tap to Call</span>
    </a>'''

SCROLL_SCRIPT_OLD = "var h=document.querySelector('.sticky-header')"
SCROLL_SCRIPT_NEW = "var header=document.getElementById('header');var navWrap=document.getElementById('header-nav-wrap')"

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'sticky-header' not in content or NAV_START not in content:
        return False
    original = content

    # 1) Replace from <header class="sticky-header"> through just before <nav ...>
    start_marker = '<header class="sticky-header">'
    idx = content.find(start_marker)
    if idx == -1:
        return False
    nav_idx = content.find(NAV_START, idx)
    if nav_idx == -1:
        return False
    content = content[:idx] + NEW_HEADER_AND_NAV_OPEN + content[nav_idx + len(NAV_START):]

    # 2) Replace closing: </nav> ... </div> </div> </header> -> </nav> </div> </div> + tap-to-call
    # Try common patterns
    for old_end in (
        '</nav>\n            </div>\n        </div>\n    </header>',
        '</nav>\n            </div>\n        </div>\n    </header>\n',
        '</nav>\n        </div>\n    </div>\n    </header>',
        '</nav>\r\n            </div>\r\n        </div>\r\n    </header>',
    ):
        if old_end in content:
            content = content.replace(
                old_end,
                '</nav>\n        </div>\n    </div>' + TAP_TO_CALL + '\n',
                1,
            )
            break
    else:
        # Regex fallback
        content = re.sub(
            r'</nav>\s*</div>\s*</div>\s*</header>',
            '</nav>\n        </div>\n    </div>' + TAP_TO_CALL + '\n',
            content,
            count=1,
        )

    # 3) Fix scroll script
    NEW_SCROLL_INNER = "var header=document.getElementById('header');var navWrap=document.getElementById('header-nav-wrap');var ly=0;function setHeaderHidden(hidden){if(header)header.classList.toggle('header--hidden',hidden);if(navWrap)navWrap.classList.toggle('header--hidden',hidden);}(header||navWrap)&&window.addEventListener('scroll',function(){if(window.innerWidth>767){setHeaderHidden(false);return;}var y=window.scrollY;if(y>80)setHeaderHidden(y>ly);else setHeaderHidden(false);ly=y;},{passive:true});"

    content = content.replace(SCROLL_SCRIPT_OLD, SCROLL_SCRIPT_NEW)
    # Multi-line Type B: var header = document.querySelector('.sticky-header'); ... if (header) { window.addEventListener('scroll', ...); }
    content = re.sub(
        r"var\s+header\s*=\s*document\.querySelector\s*\(\s*['\"]\.sticky-header['\"]\s*\)\s*;"
        r"[\s\S]*?"
        r"\},\s*\{\s*passive:\s*true\s*\}\s*\)\s*;\s*\n\s*\}\s*",
        NEW_SCROLL_INNER + " ",
        content,
        count=1,
        flags=re.DOTALL,
    )
    # Toggle header--hidden on both header and navWrap (Type A minified)
    content = re.sub(
        r"if\s*\(\s*h\s*\)\s*\{[^}]*window\.addEventListener\s*\(\s*['\"]scroll['\"]\s*,\s*function\s*\(\)\s*\{[^}]*h\.classList\.(add|remove)\s*\(\s*['\"]header--hidden['\"]\s*\)",
        "function setHeaderHidden(hidden){if(header)header.classList.toggle('header--hidden',hidden);if(navWrap)navWrap.classList.toggle('header--hidden',hidden);}(header||navWrap)&&window.addEventListener('scroll',function(){if(window.innerWidth>767){setHeaderHidden(false);return;}var y=window.scrollY;if(y>80)setHeaderHidden(y>ly);else setHeaderHidden(false);ly=y;},{passive:true});",
        content,
        count=1,
        flags=re.DOTALL,
    )
    # Fix remaining h.classList in that script block (simplify: replace "if(h)" block with our version)
    content = re.sub(
        r"var\s+ly\s*=\s*0\s*;[^;]*;\s*if\s*\(\s*h\s*\)\s*\{[^}]*\}\s*\}\s*\}\)",
        "var ly=0;" + NEW_SCROLL_INNER,
        content,
        count=1,
        flags=re.DOTALL,
    )
    # Fallback: replace querySelector with getElementById and add navWrap; make scroll toggle both
    if "querySelector('.sticky-header')" in content or 'querySelector(".sticky-header")' in content:
        content = content.replace("document.querySelector('.sticky-header')", "document.getElementById('header')")
        content = content.replace('document.querySelector(".sticky-header")', 'document.getElementById("header")')
        # Add navWrap after the header variable (same script block)
        content = re.sub(
            r"(var\s+header\s*=\s*document\.getElementById\s*\(\s*['\"]header['\"]\s*\)\s*;)\s*",
            r"\1 var navWrap=document.getElementById('header-nav-wrap'); ",
            content,
            count=1,
        )
        content = re.sub(
            r"(var\s+h\s*=\s*document\.getElementById\s*\(\s*['\"]header['\"]\s*\)\s*;)\s*",
            r"\1 var navWrap=document.getElementById('header-nav-wrap'); ",
            content,
            count=1,
        )
        # Toggle both header and navWrap on scroll (header.classList -> both)
        content = re.sub(
            r"header\.classList\.(add|remove)\s*\(\s*['\"]header--hidden['\"]\s*\)\s*;",
            r"header.classList.\1('header--hidden');if(navWrap)navWrap.classList.\1('header--hidden');",
            content,
        )
        content = re.sub(
            r"\bh\.classList\.(add|remove)\s*\(\s*['\"]header--hidden['\"]\s*\)",
            r"header.classList.\1('header--hidden');if(navWrap)navWrap.classList.\1('header--hidden')",
            content,
        )
        content = re.sub(r"\bif\s*\(\s*h\s*\)\b", "if(header||navWrap)", content)
        content = re.sub(r"\bif\s*\(\s*header\s*\)\b", "if(header||navWrap)", content, count=1)

    if content == original:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    count = 0
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('_old-site-extract', 'components', 'scripts', '.git', 'node_modules')]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, BASE)
            if '_old-site-extract' in rel or 'components' in rel:
                continue
            try:
                if process_file(path):
                    count += 1
                    print('Updated:', rel)
            except Exception as e:
                print('Error', rel, e)
    print('Done. Updated', count, 'files.')

if __name__ == '__main__':
    main()
