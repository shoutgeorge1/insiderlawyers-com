# Generates index.html for each slug with shared header/footer and unique content.
# Run from repo root: python scripts/generate-slug-pages.py

import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Shared header HTML (from line 122 to 223 of adjuster-claim-valuation) - read from template
# Shared footer HTML - read from template
# We only output the variable parts: head meta, main content.

def read_template():
    path = os.path.join(BASE, "adjuster-claim-valuation", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_between(s, start_marker, end_marker):
    i = s.find(start_marker)
    if i == -1:
        return ""
    j = s.find(end_marker, i)
    if j == -1:
        return s[i:]
    return s[i:j + len(end_marker)]

def main():
    template = read_template()
    header_start = '    <header class="sticky-header">'
    header_end = '    </header>'
    footer_start = '      <footer class="site-footer"'
    footer_end = '</footer>'
    style_start = '    <style>'
    style_end = '    </style>'
    head_script = '''    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f)})(window,document,'script','dataLayer','GTM-WS8XT5FC');</script>

<link rel="stylesheet" href="/styles/footer.css">
</head>
<body>
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WS8XT5FC" height="0" width="0" style="display:none"></iframe></noscript>
    <script>
      document.addEventListener('DOMContentLoaded',function(){window.dataLayer=window.dataLayer||[];document.querySelectorAll('a[href^="tel:"]').forEach(function(l){l.addEventListener('click',function(){window.dataLayer.push({event:'phone_click',phone_number:(this.getAttribute('href')||'').replace('tel:',''),page_path:location.pathname})})});setTimeout(function(){window.dataLayer.push({event:'engaged_30s'})},30000);var navWrap=document.getElementById('header-nav-wrap');var mobileMenuToggle=document.getElementById('mobile-menu-toggle');if(navWrap&&mobileMenuToggle){mobileMenuToggle.addEventListener('click',function(){var willOpen=!navWrap.classList.contains('is-open');navWrap.classList.toggle('is-open',willOpen);mobileMenuToggle.setAttribute('aria-expanded',willOpen?'true':'false')})}var dropdownToggles=document.querySelectorAll('.header-nav-row .nav-link--dropdown');dropdownToggles.forEach(function(toggle){toggle.setAttribute('role','button');toggle.setAttribute('tabindex','0');toggle.setAttribute('aria-expanded','false');function handleToggle(){if(window.innerWidth>900)return;var parentItem=toggle.closest('.nav-item');if(!parentItem)return;var willOpen=!parentItem.classList.contains('is-open');parentItem.classList.toggle('is-open',willOpen);toggle.setAttribute('aria-expanded',willOpen?'true':'false')}toggle.addEventListener('click',handleToggle);toggle.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();handleToggle()}})});
    </script>
'''
    header_block = extract_between(template, header_start, header_end)
    footer_block = extract_between(template, footer_start, footer_end)
    style_block = extract_between(template, style_start, style_end)

    pages = [
        {
            "slug": "do-i-need-police-report-accident",
            "title": "Do I Need a Police Report After a Car Accident?",
            "meta_title": "Do I Need a Police Report After a Car Accident? | Insider",
            "meta_desc": "California law and insurance: when a police report helps your car accident claim and how to get one.",
            "h1": "Do I Need a Police Report After a Car Accident?",
            "lead": "In California, you are not always legally required to get a police report after a car accident, but a report often strengthens your insurance claim and your injury case. This guide explains when to call police, what the report does, and how it affects your claim.",
            "content": """<h2>When California Law Requires a Report</h2>
                <p>California Vehicle Code § 20008 requires the driver to make a written report to the DMV within 10 days when someone is injured or killed, or when property damage exceeds $1,000. For serious or injury accidents, calling 911 and having law enforcement respond creates an official record that insurers and attorneys use to establish facts and liability.</p>

                <h2>Why a Police Report Helps Your Claim</h2>
                <p>A report documents the time, place, parties, and often the responding officer's observations. It can note citations, witness information, and sometimes fault. Insurers use it to evaluate claims; if <a href="/what-if-liability-disputed">liability is disputed</a>, the report is key evidence. For <a href="/hit-and-run-accidents-los-angeles">hit-and-run</a> or uninsured-driver cases, the report is usually required before your <a href="/what-is-uninsured-motorist-coverage">uninsured motorist coverage</a> will pay.</p>

                <div class="asset-preview-block" style="margin:24px 0;">
                    <p class="lead-text" style="margin-bottom:0;"><strong>Reassurance:</strong> If police did not come to the scene, you can often file a report afterward at the local station or CHP. Your insurer may still accept the claim, but a report strengthens your position.</p>
                </div>

                <h2>What If I Didn't Get a Report?</h2>
                <p>You can still pursue a claim. Evidence from photos, witnesses, medical records, and your own account matters. For minor fender-benders with no injury, some people settle without a report—but for any injury or significant damage, getting a report (even after the fact) is advisable. A <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> can help gather evidence and advise on <a href="/when-should-i-call-lawyer-accident">when to call a lawyer</a>.</p>

                <h2>FAQs</h2>
                <div class="faq-item">
                    <h4>Is a police report required to file an insurance claim in California?</h4>
                    <p>No. Insurers can accept claims without one, but many require a report for injury or hit-and-run claims. UM claims typically need a report showing the other driver was uninsured or unidentified.</p>
                </div>
                <div class="faq-item">
                    <h4>Can I get a police report after the accident?</h4>
                    <p>Yes. You can file a report at the local police department or CHP office. Do it as soon as possible so the details are fresh.</p>
                </div>
                <div class="faq-item">
                    <h4>What if the other driver doesn't want to call the police?</h4>
                    <p>You can still call 911. In California, it is your right to request law enforcement, especially if anyone is hurt or damage is significant.</p>
                </div>
                <div class="faq-item">
                    <h4>Does the report determine who is at fault?</h4>
                    <p>The report is evidence; it does not legally decide fault. Insurers and courts consider the report along with other evidence. Fault in California is evaluated under <a href="/comparative-negligence-california-explained">comparative negligence</a> rules.</p>
                </div>

                <p>Related: <a href="/what-to-do-after-car-accident-california">what to do after a car accident in California</a>, <a href="/personal-injury/auto-accidents">auto accidents</a>, <a href="/demand-letters-explained">demand letters explained</a>.</p>""",
        },
        {
            "slug": "when-should-i-call-lawyer-accident",
            "title": "When Should I Call a Lawyer After an Accident?",
            "meta_title": "When Should I Call a Lawyer After an Accident? | Insider",
            "meta_desc": "When to contact a California injury lawyer after a car accident: timing, red flags, and what to expect.",
            "h1": "When Should I Call a Lawyer After an Accident?",
            "lead": "Calling a lawyer soon after a car accident in California can protect your rights and improve your outcome. This guide covers the best time to call, what to do first, and when it's especially important.",
            "content": """<h2>Call Soon After the Accident</h2>
                <p>There is no single rule, but many attorneys and insurers recommend contacting a lawyer within days of the crash—especially if you were injured. Early involvement helps preserve evidence, get a <a href="/do-i-need-police-report-accident">police report</a>, document injuries, and avoid saying or signing things that can hurt your claim. You can still call later, but waiting can mean lost evidence or missed deadlines.</p>

                <h2>When You Should Call a Lawyer Sooner</h2>
                <p>Call quickly if: anyone was seriously injured or killed; the crash was a <a href="/hit-and-run-accidents-los-angeles">hit-and-run</a>; the other driver was uninsured or underinsured; you're being pressured to give a <a href="/recorded-statement-should-you-give-one">recorded statement</a> or sign a release; the insurer is delaying or lowballing; or you're unsure about <a href="/comparative-negligence-california-explained">comparative negligence</a> or <a href="/what-if-liability-disputed">disputed liability</a>. A <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> can advise on next steps and handle the insurer for you.</p>

                <div class="asset-preview-block" style="margin:24px 0;">
                    <p class="lead-text" style="margin-bottom:0;"><strong>You're not suing a friend.</strong> In California, your claim is against the at-fault driver's insurance, not usually the person personally. A lawyer works to get you full compensation from the insurer.</p>
                </div>

                <h2>What a Lawyer Does for You</h2>
                <p>An injury lawyer investigates the crash, gathers medical records, deals with the insurance company, and negotiates or litigates for a fair settlement. They can explain <a href="/how-insurance-calculates-settlement-offers">how insurance calculates settlement offers</a> and <a href="/why-insurance-delays-claims">why insurers delay claims</a>. Most work on contingency—no fee unless you recover.</p>

                <h2>FAQs</h2>
                <div class="faq-item">
                    <h4>Is it too late to call a lawyer weeks after the accident?</h4>
                    <p>No. You can still hire a lawyer. The sooner you call, the better for evidence and strategy, but California's statute of limitations is generally two years for personal injury.</p>
                </div>
                <div class="faq-item">
                    <h4>What if I already talked to the insurance company?</h4>
                    <p>You can still hire a lawyer. Tell your attorney what you said. They will handle further communication and work to protect your interests.</p>
                </div>
                <div class="faq-item">
                    <h4>Do I need a lawyer for a small claim?</h4>
                    <p>For minor property damage and no injury, many people handle it themselves. For any injury, significant medical bills, or lost wages, a lawyer often gets a better result.</p>
                </div>
                <div class="faq-item">
                    <h4>How much does a car accident lawyer cost?</h4>
                    <p>Most California injury lawyers work on contingency: they get a percentage of what you recover. You typically pay nothing upfront and nothing if you don't recover.</p>
                </div>

                <p>Related: <a href="/what-to-do-after-car-accident-california">what to do after a car accident</a>, <a href="/delayed-pain-after-car-accident">delayed pain after car accident</a>, <a href="/personal-injury">personal injury</a>.</p>""",
        },
    ]

    for p in pages:
        slug = p["slug"]
        dirpath = os.path.join(BASE, slug)
        os.makedirs(dirpath, exist_ok=True)
        url = f"https://www.insiderlawyers.com/{slug}"
        name_short = p["title"][:50] if len(p["title"]) > 50 else p["title"]
        head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p["meta_title"]}</title>
    <meta name="description" content="{p["meta_desc"]}">
    <link rel="canonical" href="{url}">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{p["meta_title"]}">
    <meta property="og:description" content="{p["meta_desc"]}">
    <meta property="og:url" content="{url}">
    <meta property="og:site_name" content="Insider Accident Lawyers">
    <meta property="og:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{p["meta_title"]}">
    <meta name="twitter:description" content="{p["meta_desc"]}">
    <meta name="twitter:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"WebPage","name":"{name_short}","url":"{url}","description":"{p["meta_desc"][:120]}","isPartOf":{{"@type":"WebSite","name":"Insider Accident Lawyers","url":"https://www.insiderlawyers.com/"}}}}
    </script>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"LegalService","name":"Insider Accident Lawyers","url":"https://www.insiderlawyers.com/","telephone":"+1-844-467-4335","areaServed":"Los Angeles, California","address":{{"@type":"PostalAddress","streetAddress":"3435 Wilshire Blvd Suite 1620","addressLocality":"Los Angeles","addressRegion":"CA","postalCode":"90010","addressCountry":"US"}}}}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
"""
        main_content = f'''                <h1>{p["h1"]}</h1>
                <p class="lead-text">{p["lead"]}</p>

                {p["content"]}

                <p style="margin-top:32px"><a href="/#case-evaluation" class="btn-primary">Free Case Review</a> <a href="tel:844-467-4335" class="btn-secondary" data-callrail-phone="844-467-4335">Call 844-467-4335</a></p>'''
        full = head + style_block + head_script + header_block + "\n    <main>\n    <section class=\"section-content\">\n        <div class=\"container\">\n            <div class=\"content-body\">\n" + main_content + "\n            </div>\n        </div>\n    </section>\n    </main>\n  " + footer_block + "\n\n</body>\n</html>\n"
        outpath = os.path.join(dirpath, "index.html")
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(full)
        print("Wrote", outpath)

if __name__ == "__main__":
    main()
