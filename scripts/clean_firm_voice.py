"""Clean up stale firm-voice language across insiderlawyers.com pages.

This is a one-off cleanup script for the June 2026 positioning shift.
It rewrites duplicated "Insider Accident Lawyers is a Los Angeles personal
injury firm..." lead paragraphs and similar firm-marketing language into
neutral resource voice so insiderlawyers.com stops overlapping with
insideraccidentlawyers.com.

It is safe to re-run: idempotent string replacements only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_PARTS = {"_old-site-extract", "_dev", "node_modules", "components", "legal", "scripts", "styles", "es"}


PAGE_HINTS: dict[str, str] = {
    "personal-injury/auto-accidents/index.html": (
        "California auto accident claims often involve disputed liability, low first offers, and "
        "policy-limit issues that decide how much a case is actually worth. This guide explains how "
        "California car accident claims work, what affects value, how insurance responds, and when "
        "a claim should be reviewed by an attorney before signing a release."
    ),
    "personal-injury/brain-injuries/index.html": (
        "California traumatic brain injury (TBI) claims are often undervalued because adjusters minimize "
        "\"mild\" TBIs and dispute long-term effects. This guide explains how brain injury claims work, "
        "what evidence supports value, how insurance evaluates causation, and when a claim should be "
        "reviewed by an attorney before settling."
    ),
    "personal-injury/truck-accidents/index.html": (
        "California truck accident claims involve commercial insurance layers, federal safety rules, "
        "and evidence that can disappear within days. This guide explains how truck accident claims "
        "work in California, what evidence matters most, how trucking insurance approaches valuation, "
        "and when to involve an attorney."
    ),
    "personal-injury/wrongful-death/index.html": (
        "California wrongful death claims have specific rules about who can recover, what damages "
        "are available, and how compensation is divided. This guide explains how wrongful death "
        "claims work in California, what affects value, how insurance evaluates these cases, and "
        "when families should get a claim review."
    ),
    "personal-injury/catastrophic-injuries/index.html": (
        "Catastrophic injury claims in California often require future-care planning, life-care "
        "plans, and a careful look at every layer of insurance coverage. This guide explains how "
        "catastrophic injury claims are valued, why initial offers are often low, and when to get "
        "a claim review before settling."
    ),
    "personal-injury/slip-and-fall/index.html": (
        "California slip and fall (premises liability) claims often turn on notice, dangerous "
        "conditions, and comparative fault. This guide explains how slip and fall claims work in "
        "California, what evidence matters, how store and property owners respond, and when to "
        "ask for a claim review."
    ),
    "personal-injury/product-liability/index.html": (
        "California product liability claims involve design defects, manufacturing defects, and "
        "failure-to-warn theories &mdash; and they require careful evidence preservation. This guide "
        "explains how product liability claims work in California and when to ask for a claim review."
    ),
    "personal-injury/spine-injuries/index.html": (
        "California spine and back injury claims (herniated discs, fusion surgery, chronic pain) "
        "are routinely disputed by insurance carriers using prior-injury arguments and \"degenerative\" "
        "defenses. This guide explains how spine injury claims are evaluated and when to ask for a "
        "claim review before settling."
    ),
    "brain-injury/index.html": (
        "California brain injury claims are often undervalued because adjusters minimize so-called "
        "\"mild\" TBIs and dispute long-term effects. This guide explains how California brain injury "
        "claims work, what evidence supports value, and when to ask for a claim review before "
        "accepting a settlement."
    ),
    "california-car-accident-lawyer/index.html": (
        "California car accident claims involve liability disputes, policy-limit issues, comparative "
        "fault, and adjuster tactics that can lower offers. This guide explains how California car "
        "accident claims work, what affects value, and when to ask for a free claim review."
    ),
    "injuries-truck-accidents/index.html": (
        "Truck accidents in California often cause severe injuries with long-term care needs. This "
        "guide explains the injuries most commonly seen in California truck accident claims, how "
        "they affect claim value, and when to ask for a claim review before settling."
    ),
    "insurance-company-playbook/index.html": (
        "Insurance carriers in California follow well-known patterns when valuing injury claims &mdash; "
        "early low offers, recorded-statement requests, soft-tissue framing, and delay. This guide "
        "explains the insurance playbook so you can decide when a free claim review or attorney "
        "review makes sense."
    ),
    "major-car-accident/index.html": (
        "Serious California car accidents often involve hospitalization, ongoing treatment, lost "
        "income, and high-value insurance disputes. This guide explains how major car accident "
        "claims are valued in California and when to get a claim review before signing anything."
    ),
    "motorcycle-accident-case/index.html": (
        "California motorcycle accident claims face bias from adjusters, comparative-fault arguments, "
        "and visibility disputes that can lower offers. This guide explains how motorcycle accident "
        "claims are valued in California and when to ask for a free claim review."
    ),
    "pedestrian-right-of-way/index.html": (
        "California pedestrian accident claims often turn on right-of-way, crosswalk rules, and "
        "comparative fault. This guide explains how pedestrian claims work in California and when "
        "to ask for a claim review before talking to the driver's insurance."
    ),
    "post-dog-bite/index.html": (
        "California dog bite claims follow a strict-liability rule, but insurance still pushes back "
        "on damages, treatment, and scarring valuation. This guide explains how California dog bite "
        "claims work and when to get a free claim review."
    ),
    "uber-or-lyft-accident/index.html": (
        "Uber and Lyft rideshare accident claims in California involve multiple insurance layers "
        "that change based on whether the app was on, a ride was accepted, or a passenger was in "
        "the car. This guide explains how rideshare claims work in California and when to ask for "
        "a claim review."
    ),
    "what-to-do-after-car-accident-california/index.html": (
        "The hours and days after a California car accident matter for both safety and your claim. "
        "This guide walks through what to do at the scene, what to document, how to handle "
        "insurance, and when to ask for a free claim review."
    ),
    "personal-injury-court/index.html": (
        "Most California personal injury claims settle without going to court, but trial preparation "
        "still shapes value. This guide explains how the California personal injury court process "
        "works and when a case may need attorney review."
    ),
    "adjuster-claim-valuation/index.html": (
        "California insurance adjusters use a mix of formulas, reserves, and internal authority "
        "levels to value claims. Understanding how that works can change whether an offer makes "
        "sense to accept. This guide explains adjuster valuation and when to get a claim review."
    ),
    "demand-letter-negotiation/index.html": (
        "California demand-letter negotiation is part written advocacy and part insurance strategy. "
        "This guide explains how demand letters drive injury claim negotiations and when to ask "
        "for a claim review."
    ),
    "lowball-offer-response/index.html": (
        "Lowball offers are common in California injury claims, especially early in the process. "
        "This guide explains why insurance offers come in low, how to respond, and when to ask "
        "for a free claim review before reacting."
    ),
    "proving-claim-value/index.html": (
        "Proving California injury claim value takes more than medical bills &mdash; it takes a "
        "documented story of liability, injury, treatment, and future impact. This guide explains "
        "what proves claim value and when to get a claim review."
    ),
}


GENERIC_LEAD = (
    "This page is a neutral California injury claim resource. It explains the issues that affect "
    "claim value, common insurance tactics, and when to consider a free claim review or second "
    "opinion before accepting an offer or signing a release."
)


RESOURCE_LINKS_BLOCK = """
                <div class="related-resources" style="border:1px solid #e1e8ef;border-radius:10px;padding:16px 20px;margin:24px 0;background:#f8fafc;">
                  <h3 style="margin-top:0;">Related California Injury Claim Resources</h3>
                  <ul style="margin:8px 0 0 0;padding-left:20px;">
                    <li><a href="/california-injury-claim-second-opinion">Get a second opinion on your injury claim</a></li>
                    <li><a href="/california-personal-injury-settlement-checklist">Review a settlement offer before accepting</a></li>
                    <li><a href="/california-personal-injury-demand-letter-guide">Learn what happens after a demand letter</a></li>
                    <li><a href="/personal-injury">Understand how California injury claim value is calculated</a></li>
                    <li><a href="/#case-evaluation">Request a free claim review</a></li>
                  </ul>
                </div>
""".strip()


PAGE_DISCLAIMER = """
                <div class="page-disclaimer" style="border-left:4px solid #01468a;background:#f1f6fb;padding:14px 18px;margin:28px 0;border-radius:6px;font-size:0.95em;line-height:1.6;color:#374151;">
                  <strong>Important.</strong> This page is general information about California injury claims. It is not legal advice for any specific case and is not a promise about settlement value or outcome. Insider Lawyers provides claim review and information support. Submitting information through this website does not create an attorney-client relationship.
                </div>
""".strip()


CLAIM_REVIEW_BLOCK = """
                <div class="what-a-review-covers" style="border:1px solid #dce6f2;border-radius:10px;padding:18px 22px;margin:28px 0;background:#fff;">
                  <h3 style="margin-top:0;">What a Free Claim Review Covers</h3>
                  <p>A free claim review is a no-cost, no-commitment look at where a California injury claim actually stands. It does not require you to switch lawyers and it does not create an attorney-client relationship. A review typically covers:</p>
                  <ul style="margin:8px 0 0 0;padding-left:20px;">
                    <li><strong>Liability.</strong> How fault looks based on the facts, the police report, and any available evidence.</li>
                    <li><strong>Insurance coverage.</strong> Primary, excess, umbrella, employer, and UM/UIM layers that may apply.</li>
                    <li><strong>Damages.</strong> Medical bills paid and projected, lost wages, lost earning capacity, and pain and suffering framing.</li>
                    <li><strong>Settlement posture.</strong> Whether the current offer (or the absence of one) is in line with how California carriers usually value this kind of claim.</li>
                    <li><strong>Next step.</strong> Whether the situation calls for a <a href="/california-injury-claim-second-opinion">second opinion</a>, a <a href="/california-personal-injury-settlement-checklist">settlement checklist review</a>, an <a href="/california-personal-injury-demand-letter-guide">updated demand letter</a>, or attorney involvement.</li>
                  </ul>
                  <p style="margin-top:14px;"><a href="/#case-evaluation" class="btn-primary" style="display:inline-block;padding:0.75rem 1.4rem;background:#01468a;color:#fff;border-radius:6px;text-decoration:none;font-weight:700;">Get a Free Claim Review</a> <a href="tel:844-467-4335" data-callrail-phone="844-467-4335" style="display:inline-block;padding:0.75rem 1.4rem;color:#01366c;text-decoration:none;font-weight:700;">or call 844-467-4335</a></p>
                </div>
""".strip()


# Patterns we replace globally on the cleaned pages.
GLOBAL_REPLACEMENTS: list[tuple[str, str]] = [
    # Title/meta firm tag → resource tag
    ("| Insider Accident Lawyers", "| Insider Lawyers"),
    ("- Insider Accident Lawyers", "- Insider Lawyers"),
    ("Insider Accident Lawyers - California injury", "Insider Lawyers - California injury"),
    # Firm-voice section headings → neutral resource headings
    ("<h2>Why Experience Matters</h2>", "<h2>Why Claim Review Matters</h2>"),
    ("<h2>Injuries We Handle</h2>", "<h2>Common Injuries in These Claims</h2>"),
    ("<h2>How We Help</h2>", "<h2>How a Free Claim Review Helps</h2>"),
    ("<h2>Insider Case Evaluation Framework</h2>", "<h2>How California Injury Claims Are Evaluated</h2>"),
    ("<h3>Why Former Insurance Defense Attorneys Approach Cases Differently</h3>", "<h3>How Former Insurance Defense Lawyers Look at Claims</h3>"),
    ("<h3>Trusted for Complex Collision Claims</h3>", "<h3>What Affects Complex Collision Claims</h3>"),
    ("<h2>Speak With a Los Angeles Auto Accident Attorney</h2>", "<h2>Request a Free California Auto Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Brain Injury Attorney</h2>", "<h2>Request a Free California Brain Injury Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Truck Accident Attorney</h2>", "<h2>Request a Free California Truck Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Wrongful Death Attorney</h2>", "<h2>Request a Free California Wrongful Death Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Motorcycle Accident Attorney</h2>", "<h2>Request a Free California Motorcycle Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Pedestrian Accident Attorney</h2>", "<h2>Request a Free California Pedestrian Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Uber and Lyft Accident Attorney</h2>", "<h2>Request a Free California Rideshare Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Bicycle Accident Attorney</h2>", "<h2>Request a Free California Bicycle Accident Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Slip and Fall Attorney</h2>", "<h2>Request a Free California Slip and Fall Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Premises Liability Attorney</h2>", "<h2>Request a Free California Premises Liability Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Catastrophic Injury Attorney</h2>", "<h2>Request a Free California Catastrophic Injury Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Spine Injury Attorney</h2>", "<h2>Request a Free California Spine Injury Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Product Liability Attorney</h2>", "<h2>Request a Free California Product Liability Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Animal Attack Attorney</h2>", "<h2>Request a Free California Dog Bite Claim Review</h2>"),
    ("<h2>Speak With a Los Angeles Personal Injury Attorney</h2>", "<h2>Request a Free California Personal Injury Claim Review</h2>"),
    # Firm-voice lead sentences under those H2s
    ('<p class="lead-text">We use insurance defense insight to outmaneuver low offers.</p>',
     '<p class="lead-text">A claim review checks the case against the same factors insurance defense lawyers look at &mdash; before you accept an offer.</p>'),
    ('<p class="lead-text">We build TBI cases with medical evidence and insurer-level strategy.</p>',
     '<p class="lead-text">Strong TBI claims are built on medical evidence and an understanding of how insurers evaluate causation &mdash; a claim review covers both.</p>'),
    ('<p class="lead-text">We prove liability, document damages, and negotiate assertively.</p>',
     '<p class="lead-text">A free claim review covers liability, damages, and how the carrier is likely to respond to a demand.</p>'),
    ('<p class="lead-text">Our auto accident strategy starts with the same four pillars we use in high-value litigation.</p>',
     '<p class="lead-text">California auto accident claims are typically evaluated against the same four pillars used in high-value litigation.</p>'),
    ('<p class="lead-text">Early legal help protects evidence and your claim value.</p>',
     '<p class="lead-text">Getting a neutral claim review early protects evidence and helps you understand your options before accepting an offer.</p>'),
    ('<p class="lead-text">Trucking defendants often move immediately after a crash.</p>',
     '<p class="lead-text">Trucking defendants and their insurers often move immediately after a crash. Evidence preservation should start right away.</p>'),
    # "We prepare every claim" sales line that appears repeatedly
    ("<li>We prepare every claim as if it could be tried in Los Angeles Superior Court.</li>",
     "<li>Strong California injury claims are built as if they could be tried in Los Angeles Superior Court &mdash; even when they settle.</li>"),
    ("<li>We evaluate policy limits and layered coverage early to avoid missed recovery.</li>",
     "<li>A claim review identifies primary, excess, and UM/UIM coverage layers early to avoid missed recovery.</li>"),
    ("<li>We document long-term impairment with medical records and expert support.</li>",
     "<li>Long-term impairment should be documented with medical records and, where needed, expert support.</li>"),
    ("<li>We anticipate insurer arguments on speed, impact, and causation.</li>",
     "<li>Strong claims anticipate insurer arguments on speed, impact, and causation.</li>"),
    ("<li>We build evidence packages designed for adjusters and juries.</li>",
     "<li>Evidence packages should be built for both adjusters and juries.</li>"),
    ("<li>We negotiate with a clear view of coverage and policy limits.</li>",
     "<li>Negotiation works best when coverage and policy limits are clearly understood up front.</li>"),
    ("<li>We focus on causation and future-care projections early.</li>",
     "<li>Causation and future-care projections should be developed early.</li>"),
    ("<li>We counter \"mild TBI\" minimization with expert proof.</li>",
     "<li>\"Mild TBI\" minimization is countered with expert medical proof.</li>"),
    ("<li>We evaluate policy limits and bad faith exposure.</li>",
     "<li>Policy limits and bad-faith exposure should be evaluated as part of any review.</li>"),
    ("<li>We prepare trial-ready records that strengthen negotiation leverage.</li>",
     "<li>Trial-ready records strengthen negotiation leverage even when a case settles.</li>"),
    # "Early work in these four areas..." kept as is (it is neutral)
    # "Insider Lawyer Personal Injury Playbook" reframe
    (" - Shawn S. Rokni, Insider Lawyer Personal Injury Playbook",
     " - Shawn S. Rokni, California Personal Injury Playbook"),
    ("&mdash; Shawn S. Rokni, Insider Lawyer Personal Injury Playbook",
     "&mdash; Shawn S. Rokni, California Personal Injury Playbook"),
    # Lead-paragraph anchor lines
    (
        "meet our attorneys at <a href=\"/#our-attorneys\">our attorneys</a>",
        "see <a href=\"/attorney-referrals\">attorney review &amp; referral</a>",
    ),
    (
        "meet our attorneys at <a href=\"/#our-attorneys\">attorneys</a>",
        "see <a href=\"/attorney-referrals\">attorney review &amp; referral</a>",
    ),
    (
        "meet our team at <a href=\"/#our-attorneys\">our attorneys</a>",
        "see <a href=\"/attorney-referrals\">attorney review &amp; referral</a>",
    ),
    (
        "meet our team at <a href=\"/#about-us\">our attorneys</a>",
        "see <a href=\"/attorney-referrals\">attorney review &amp; referral</a>",
    ),
    (
        "meet our trial team at <a href=\"/#our-attorneys\">our attorneys</a>",
        "see <a href=\"/attorney-referrals\">attorney review &amp; referral</a>",
    ),
    # Standalone broken anchors
    ("/#our-attorneys", "/attorney-referrals"),
    ("/#about-us", "/attorney-referrals"),
    # Contact-us-as-firm sentences
    ("Contact Insider Accident Lawyers to discuss your options.", "Request a free claim review to discuss your options."),
    ("Contact Insider Accident Lawyers to discuss your case.", "Request a free claim review to discuss your case."),
    # Form autoresponse firm reference
    ("Our legal team will contact you shortly.", "Our team will contact you shortly. Submitting this form does not create an attorney-client relationship."),
    # Firm-voice CTA buttons
    (">Free Case Review<", ">Get a Free Claim Review<"),
    (">Free Consultation<", ">Get a Free Claim Review<"),
    # Image alt firm references
    ("alt=\"Our Legal Team\"", "alt=\"California injury claim review team\""),
    ("alt=\"Our legal team of 20+ attorneys\"", "alt=\"California injury claim review team\""),
    # Generic firm-credentials line that appears repeatedly
    (
        "<li>Our attorneys include litigators with decades of courtroom experience, including trials dating back to 1979.</li>",
        "<li>Review and referral support is provided by attorneys with decades of California trial experience.</li>",
    ),
    (
        "<li>Our team includes senior litigators with decades of trial experience and a record that highlights 100 million+ recovered across 5,000+ cases.</li>",
        "<li>Review and referral support is provided by California trial attorneys with a track record on serious injury claims. Past results do not guarantee a similar outcome.</li>",
    ),
    (
        "<li>Our leadership includes seasoned trial attorneys and a record that highlights 100 million+ recovered across 5,000+ cases.</li>",
        "<li>Review and referral support is provided by California trial attorneys experienced with serious injury claims. Past results do not guarantee a similar outcome.</li>",
    ),
    # Common sales tagline soften
    ("Real trial lawyers, real results.", "California injury claim information and free claim review support."),
    # CTA block sales line on truck page
    ("Your legal team should too.", "Evidence preservation should start right away."),
    # Lit-referral / motor-vehicle "How We Help Referring Attorneys" → neutral
    ("<h2>How We Help Referring Attorneys</h2>", "<h2>How Co-Counsel and Referral Support Works</h2>"),
    # Common "we counter / anticipate / focus on" li items
    ("<li>We counter minimization of \"mild\" symptoms.</li>",
     "<li>Minimization of \"mild\" symptoms can be countered with consistent treatment records and expert support.</li>"),
    ("<li>We counter lowball tactics and liability defenses early.</li>",
     "<li>Lowball tactics and liability defenses can be countered early with documented evidence.</li>"),
    ("<li>We counter rider-bias defenses with evidence.</li>",
     "<li>Rider-bias defenses can be countered with scene evidence and reconstruction.</li>"),
    ("<li>We anticipate lowball tactics and coverage defenses.</li>",
     "<li>A claim review anticipates lowball tactics and coverage defenses.</li>"),
    ("<li>We anticipate how adjusters use injury coding and documentation gaps.</li>",
     "<li>A claim review accounts for how adjusters use injury coding and documentation gaps.</li>"),
    ("<li>We counter liability disputes with expert reconstruction.</li>",
     "<li>Liability disputes can be countered with expert reconstruction.</li>"),
    ("<li>We anticipate how carriers evaluate liability and damages.</li>",
     "<li>A claim review accounts for how carriers evaluate liability and damages.</li>"),
    ("<li>We prepare every case for trial, which improves settlement authority.</li>",
     "<li>Cases built for trial tend to settle for stronger value than ones positioned only for settlement.</li>"),
    ("<li>We focus on evidence that supports fault and damages-not speculative theories.</li>",
     "<li>The focus is on evidence that supports fault and damages &mdash; not speculative theories.</li>"),
    ("<li>Liability and insurance strategy drive recovery; we focus on fault, policy limits, and UM/UIM.</li>",
     "<li>Liability and insurance strategy drive recovery: fault, policy limits, and UM/UIM coverage all matter.</li>"),
    # motor-vehicle lead-text and other fragments
    ('<p class="lead-text">From fender-benders to catastrophic crashes, we focus on liability and insurance.</p>',
     '<p class="lead-text">From fender-benders to catastrophic crashes, California motor vehicle claims turn on liability and insurance coverage.</p>'),
    ('<p class="lead-text">We focus on cases that require advanced litigation strategy.</p>',
     '<p class="lead-text">Co-counsel and referral support is geared toward cases that require advanced California litigation strategy.</p>'),
    ('<p class="lead-text">We focus on complex injury and liability disputes.</p>',
     '<p class="lead-text">Co-counsel and referral support focuses on complex California injury and liability disputes.</p>'),
    # FAQ schema "we" answers on motor-vehicle/index.html (escape regex-y chars carefully)
    (
        '"text":"We handle car, truck, bus, motorcycle, pedestrian, bicycle, and scooter accidents. We focus on who was at fault, what insurance applies, and how to maximize leverage with insurers so you get a fair outcome."',
        '"text":"California motor vehicle accident claims cover car, truck, bus, motorcycle, pedestrian, bicycle, and scooter crashes. A claim review focuses on who was at fault, what insurance applies, and how to position leverage with insurers."',
    ),
    (
        '"text":"California fault rules and insurance requirements directly affect what you can recover. Uninsured and underinsured motorist coverage, policy limits, and comparative negligence all play a role. We identify every source of recovery and push back on lowball offers."',
        '"text":"California fault rules and insurance requirements directly affect what you can recover. Uninsured and underinsured motorist coverage, policy limits, and comparative negligence all play a role. A claim review identifies every source of recovery and helps push back on lowball offers."',
    ),
    (
        '"text":"Yes. We offer a free case review for motor vehicle accident claims. Call 844-467-4335 or submit our online form. We are available 24/7 and speak Spanish."',
        '"text":"Yes. A free claim review is available for California motor vehicle accident claims. Call 844-467-4335 or submit the online form. Available 24/7. Hablamos Espa\\u00f1ol."',
    ),
    (
        '<p>We handle car, truck, bus, motorcycle, pedestrian, bicycle, and scooter accidents. We focus on who was at fault, what insurance applies, and how to maximize leverage with insurers so you get a fair outcome.</p>',
        '<p>California motor vehicle accident claims cover car, truck, bus, motorcycle, pedestrian, bicycle, and scooter crashes. A free claim review focuses on who was at fault, what insurance applies, and how to position leverage with insurers.</p>',
    ),
    # motor-vehicle / motor-vehicle long lead-text — replace whole block
    (
        '<p class="lead-text"><strong>Motor vehicle accident lawyers Los Angeles</strong> and a <strong>Los Angeles motor vehicle accident lawyer</strong> can help when you are hurt in a car, truck, motorcycle, or other traffic crash. Insider Accident Lawyers handles liability and insurance for <a href="/personal-injury">personal injury</a>, <a href="/los-angeles-car-accident-lawyer">car accidents</a>, <a href="/los-angeles-truck-accident-lawyer">truck</a>, <a href="/los-angeles-motorcycle-accident-lawyer">motorcycle</a>, <a href="/los-angeles-pedestrian-accident-lawyer">pedestrian</a>, and <a href="/premises-liability">premises</a> cases across California. We focus on fault, insurance disputes, and trial-ready strategy-the same approach we use for every serious injury case. Free case review 24/7.</p>',
        '<p class="lead-text">California motor vehicle accident claims cover crashes involving cars, trucks, motorcycles, pedestrians, bicycles, scooters, and rideshare vehicles. They turn on liability, available insurance, comparative fault, and how an injury claim is documented. This resource explains how California motor vehicle claims work and links to focused guides on <a href="/personal-injury">personal injury</a>, <a href="/los-angeles-car-accident-lawyer">Los Angeles car accidents</a>, <a href="/los-angeles-truck-accident-lawyer">truck</a>, <a href="/los-angeles-motorcycle-accident-lawyer">motorcycle</a>, <a href="/los-angeles-pedestrian-accident-lawyer">pedestrian</a>, and <a href="/premises-liability">premises</a> claims. Free claim review available 24/7.</p>',
    ),
    # Schema / OG / Twitter site_name firm brand → resource brand
    ('"og:site_name" content="Insider Accident Lawyers"', '"og:site_name" content="Insider Lawyers"'),
    ('content="Insider Accident Lawyers"', 'content="Insider Lawyers"'),
    ('"WebSite","name":"Insider Accident Lawyers"', '"WebSite","name":"Insider Lawyers"'),
    ('"Organization","name":"Insider Accident Lawyers"', '"Organization","name":"Insider Lawyers"'),
    # Footer trust line remnants
    ('Over $100M recovered*', 'California injury claim resource'),
    # Generic "No fee unless we win" sales tagline → neutral
    ('<p>No Fee Unless We Win</p>', ''),
    ('No fee unless we win.', 'A free claim review does not commit you to hiring anyone.'),
    # Body "Contact Insider Accident Lawyers to discuss your <topic> case." (very common pattern)
    ('Contact Insider Accident Lawyers to discuss your premises liability case.',
     'Request a free claim review to discuss your premises liability situation.'),
    ('Contact Insider Accident Lawyers to discuss your truck case.',
     'Request a free claim review to discuss your truck accident claim.'),
    ('Contact Insider Accident Lawyers to discuss your motor vehicle accident case.',
     'Request a free claim review to discuss your motor vehicle accident claim.'),
    ('Contact Insider Accident Lawyers to discuss your bus accident case.',
     'Request a free claim review to discuss your bus accident claim.'),
    ('Contact Insider Accident Lawyers to discuss your hit-and-run case.',
     'Request a free claim review to discuss your hit-and-run claim.'),
    ('Contact Insider Accident Lawyers to discuss your rear-end accident case.',
     'Request a free claim review to discuss your rear-end accident claim.'),
    ('Contact Insider Accident Lawyers to discuss your nursing home neglect case.',
     'Request a free claim review to discuss your nursing home neglect concerns.'),
    # Body sentences with firm framing on the rear-end / LA-* type pages
    ('Insider Accident Lawyers prepares rear-end cases as if they will be tried in Los Angeles Superior Court, because that is what creates leverage in negotiations.',
     'California rear-end claims gain leverage when they are built as if they could be tried in Los Angeles Superior Court &mdash; even when they settle.'),
    ('Call Insider Accident Lawyers now for a free bilingual case review.',
     'Request a free bilingual claim review.'),
    ('We are available 24/7 and we build claims with trial-ready leverage from day one.',
     'Free claim review available 24/7. Strong California injury claims are built with trial-ready leverage from day one.'),
    ('Call now for a free case review and a same-day evidence preservation plan.',
     'Request a free claim review for a same-day evidence preservation plan.'),
    # Body firm sentences on T-bone / parking / pedestrian pages
    ('Call Insider Accident Lawyers for a free, no-pressure case review.',
     'Request a free, no-pressure claim review.'),
    ('Contact Insider Accident Lawyers for a free case review and to start an evidence preservation plan.',
     'Request a free claim review to start an evidence preservation plan.'),
    # premises-liability lead-text
    (
        '<p class="lead-text">A <strong>premises liability lawyer Los Angeles</strong> and <strong>Los Angeles premises liability lawyer</strong> can help when you are hurt on someone else\'s property. Insider Accident Lawyers handles slip and fall, trip and fall, negligent security, and unsafe conditions across California. We focus on duty, breach, notice, and causation\u2014the same trial-ready approach we use for <a href="/personal-injury">personal injury</a>, <a href="/los-angeles-car-accident-lawyer">car accidents</a>, and <a href="/motor-vehicle">motor vehicle</a> cases. Property and liability insurers work to minimize payouts; we gather evidence early and prepare every case for trial so you get a fair outcome. Free case review 24/7.</p>',
        '<p class="lead-text">California premises liability claims cover injuries on someone else\'s property &mdash; slip and fall, trip and fall, negligent security, and other unsafe conditions. They turn on duty, breach, notice, and causation under California law. This guide explains how premises liability claims work and links to focused resources on <a href="/personal-injury">personal injury</a>, <a href="/los-angeles-car-accident-lawyer">car accidents</a>, and <a href="/motor-vehicle">motor vehicle</a> claims. Free claim review available 24/7.</p>',
    ),
    # Misc body remnants
    ("We serve LA and California with a", "Related resources include a"),
    ("the same trial-ready approach we use", "the approach trial-ready California injury claims usually take"),
    ("we gather evidence early and prepare every case for trial", "evidence preservation should start right away and the case should be built as if it could go to trial"),
    ("we focus on duty, breach, notice, and causation", "California premises claims turn on duty, breach, notice, and causation"),
]


# Schema cleanup: strip standalone LegalService schema blocks. This site is now
# positioned as a neutral resource, not a legal services provider, so the
# LegalService schema in some older pages is incorrect and risks confusing
# Google's understanding of the entity. Match both compact (one-line) and
# pretty-printed (multi-line) JSON-LD blocks.
LEGAL_SERVICE_RE = re.compile(
    r'<script type="application/ld\+json">\s*\{\s*(?:"@context"\s*:\s*"https://schema\.org"\s*,\s*"@type"\s*:\s*"LegalService"|"@type"\s*:\s*"LegalService"\s*,\s*"@context"\s*:\s*"https://schema\.org")[\s\S]*?\}\s*</script>\s*',
    re.IGNORECASE,
)


# Regex-based replacements for the formulaic lead paragraph.
LEAD_FIRM_RE = re.compile(
    r'<p class="lead-text">Insider Accident Lawyers is a Los Angeles personal injury firm[\s\S]*?</p>',
    re.IGNORECASE,
)


def neutral_lead(hint_html: str) -> str:
    return f'<p class="lead-text">{hint_html}</p>'


def is_live_html(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    if path.suffix.lower() != ".html":
        return False
    for part in rel_parts:
        if part in SKIP_DIR_PARTS:
            return False
    return True


def add_resource_block_once(html: str) -> str:
    if "related-resources" in html:
        return html
    # Insert after the first lead-text paragraph closing tag, if found.
    m = re.search(r'<p class="lead-text">[\s\S]*?</p>', html)
    if not m:
        return html
    insert_at = m.end()
    block = "\n" + RESOURCE_LINKS_BLOCK + "\n"
    return html[:insert_at] + block + html[insert_at:]


def add_page_disclaimer_once(html: str) -> str:
    if "page-disclaimer" in html:
        return html
    m = re.search(r"</main>", html, flags=re.IGNORECASE)
    if not m:
        return html
    block = "\n" + PAGE_DISCLAIMER + "\n"
    return html[: m.start()] + block + html[m.start() :]


def add_claim_review_block_once(html: str) -> str:
    if "what-a-review-covers" in html:
        return html
    m = re.search(r"</main>", html, flags=re.IGNORECASE)
    if not m:
        return html
    block = "\n" + CLAIM_REVIEW_BLOCK + "\n"
    return html[: m.start()] + block + html[m.start() :]


# Pages we should NOT auto-enrich (legal pages, the homepage, the new resource
# hubs, anything where we already wrote richer custom copy).
ENRICH_DENY_SLUGS = {
    "index.html",
    "personal-injury/index.html",
    "settlements/index.html",
    "second-opinion-personal-injury-claim-california/index.html",
    "recover-destroyed-scooter-ebike/index.html",
    "california-injury-claim-second-opinion/index.html",
    "california-personal-injury-settlement-checklist/index.html",
    "california-personal-injury-demand-letter-guide/index.html",
    "california-parking-lot-accident-claim-guide/index.html",
    "t-bone-accident-claim-value-california/index.html",
    "thank-you/index.html",
    "thank-you.html",
    # Legal / compliance / contact pages already carry their own structure.
    "privacy-policy/index.html",
    "legal-terms/index.html",
    "disclaimer/index.html",
    "cookie-policy/index.html",
    "california-privacy-rights/index.html",
    "do-not-sell-or-share-my-personal-information/index.html",
    "accessibility/index.html",
    "contact/index.html",
}


def should_enrich(rel: str) -> bool:
    if rel in ENRICH_DENY_SLUGS:
        return False
    if rel.startswith("legal/"):
        return False
    return True


def rewrite_lead(html: str, hint_html: str | None) -> str:
    new_lead = neutral_lead(hint_html or GENERIC_LEAD)
    return LEAD_FIRM_RE.sub(new_lead, html, count=1)


def apply_global_replacements(html: str) -> str:
    for old, new in GLOBAL_REPLACEMENTS:
        html = html.replace(old, new)
    return html


def process_file(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    raw = path.read_text(encoding="utf-8", errors="replace")
    out = raw

    out = apply_global_replacements(out)
    # Strip LegalService schema (this site is now positioned as an information
    # resource, not a legal-services provider).
    out = LEGAL_SERVICE_RE.sub("", out)

    if "Insider Accident Lawyers is a Los Angeles personal injury firm" in out:
        hint = PAGE_HINTS.get(rel)
        out = rewrite_lead(out, hint)

    if should_enrich(rel):
        out = add_resource_block_once(out)
        out = add_page_disclaimer_once(out)
        out = add_claim_review_block_once(out)

    if out != raw:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if not is_live_html(path):
            continue
        if process_file(path):
            changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    print(f"Cleaned {len(changed)} files")
    for p in changed:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
