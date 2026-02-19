#!/usr/bin/env python3
"""Add Accident & Claim Guides nav dropdown and footer section to all index.html that have Claim Playbooks but not yet the new block."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"scripts", "docs", "styles", "images", "legal"}
SKIP_SLUGS = {"index"}  # root index.html = home, do not modify

NAV_INSERT = '''
                <div class="nav-item">
                    <span class="nav-link nav-link--dropdown">Accident &amp; Claim Guides</span>
                    <div class="nav-dropdown">
                        <a href="/what-to-do-after-car-accident-california">What To Do After a Car Accident</a>
                        <a href="/uninsured-motorist-claims-california">Uninsured Motorist Claims California</a>
                        <a href="/electric-scooter-ebike-accident-lawyer-los-angeles">Scooter &amp; E-Bike Accidents LA</a>
                        <a href="/do-i-need-police-report-accident">Do I Need a Police Report?</a>
                        <a href="/when-should-i-call-lawyer-accident">When to Call a Lawyer</a>
                        <a href="/delayed-pain-after-car-accident">Delayed Pain After Accident</a>
                        <a href="/hit-and-run-accidents-los-angeles">Hit and Run Los Angeles</a>
                        <a href="/major-car-accident">Major Car Accident Guide</a>
                        <a href="/california-car-accident-lawyer">California Car Accident Guide</a>
                        <a href="/why-insurance-delays-claims">Why Insurance Delays Claims</a>
                        <a href="/recorded-statement-should-you-give-one">Recorded Statements</a>
                        <a href="/demand-letters-explained">Demand Letters Explained</a>
                        <a href="/comparative-negligence-california-explained">Comparative Negligence CA</a>
                    </div>
                </div>
'''

NAV_MARKER_AFTER = """</div>
                </div>
                <div class="nav-item">
                    <span class="nav-link nav-link--dropdown">Injury & Accident Types</span>"""

NAV_MARKER_AFTER_ALT = """</div>
                </div>
                <div class="nav-item">
                    <span class="nav-link nav-link--dropdown">Injury &amp; Accident Types</span>"""

FOOTER_INSERT = '''
        <div class="footer-section">
          <h4>Accident &amp; Claim Guides</h4>
          <ul>
            <li><a href="/what-to-do-after-car-accident-california">What To Do After a Car Accident</a></li><li><a href="/uninsured-motorist-claims-california">Uninsured Motorist Claims California</a></li><li><a href="/electric-scooter-ebike-accident-lawyer-los-angeles">Scooter &amp; E-Bike Accidents LA</a></li><li><a href="/do-i-need-police-report-accident">Do I Need a Police Report?</a></li><li><a href="/when-should-i-call-lawyer-accident">When to Call a Lawyer</a></li><li><a href="/delayed-pain-after-car-accident">Delayed Pain After Accident</a></li><li><a href="/hit-and-run-accidents-los-angeles">Hit and Run Los Angeles</a></li><li><a href="/what-if-i-cant-afford-deductible">What If I Can't Afford My Deductible?</a></li><li><a href="/what-is-uninsured-motorist-coverage">What Is UM Coverage?</a></li><li><a href="/underinsured-motorist-claims-explained">Underinsured Motorist Claims</a></li><li><a href="/who-is-liable-scooter-accident">Who Is Liable in a Scooter Accident?</a></li><li><a href="/why-insurance-delays-claims">Why Insurance Delays Claims</a></li><li><a href="/recorded-statement-should-you-give-one">Recorded Statements</a></li><li><a href="/demand-letters-explained">Demand Letters Explained</a></li><li><a href="/how-insurance-calculates-settlement-offers">How Insurance Calculates Settlements</a></li><li><a href="/comparative-negligence-california-explained">Comparative Negligence California</a></li><li><a href="/what-if-liability-disputed">What If Liability Is Disputed?</a></li>
          </ul>
        </div>
'''

FOOTER_MARKER_BEFORE = """        <div class="footer-section">
          <h4>Injury &amp; Accident Types</h4>"""


def main():
    count_nav = count_footer = 0
    for path in ROOT.rglob("index.html"):
        rel = path.relative_to(ROOT)
        parts = rel.parts[:-1]  # drop index.html
        if parts and parts[0] in SKIP_DIRS:
            continue
        if not parts or (len(parts) == 1 and parts[0] == "index"):
            continue
        text = path.read_text(encoding="utf-8")
        if "Accident &amp; Claim Guides" in text and "<h4>Accident &amp; Claim Guides</h4>" in text:
            continue  # already has both nav and footer
        if "Claim Playbooks" not in text:
            continue
        changed = False
        # Nav: insert before "Injury & Accident Types" nav item
        if "Accident &amp; Claim Guides" in text:
            pass  # already has nav
        elif NAV_MARKER_AFTER in text:
            text = text.replace(
                NAV_MARKER_AFTER,
                NAV_INSERT.strip() + "\n                <div class=\"nav-item\">\n                    <span class=\"nav-link nav-link--dropdown\">Injury & Accident Types</span>",
                1,
            )
            changed = True
            count_nav += 1
        elif NAV_MARKER_AFTER_ALT in text:
            text = text.replace(
                NAV_MARKER_AFTER_ALT,
                NAV_INSERT.strip() + "\n                <div class=\"nav-item\">\n                    <span class=\"nav-link nav-link--dropdown\">Injury &amp; Accident Types</span>",
                1,
            )
            changed = True
            count_nav += 1
        # Footer: insert before Injury & Accident Types footer section
        if FOOTER_MARKER_BEFORE in text and "<h4>Accident &amp; Claim Guides</h4>" not in text:
            text = text.replace(FOOTER_MARKER_BEFORE, FOOTER_INSERT.strip() + "\n" + FOOTER_MARKER_BEFORE, 1)
            changed = True
            count_footer += 1
        if changed:
            path.write_text(text, encoding="utf-8")
            print("Updated:", rel)
    print("Nav inserts:", count_nav, "Footer inserts:", count_footer)


if __name__ == "__main__":
    main()
