# -*- coding: utf-8 -*-
"""One-off generator: switching-lawyer / second-opinion cluster pages."""
import json
import os
import re

from gtm_head_guard import GTM_HEAD_GUARD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "when-should-i-call-lawyer-accident", "index.html")

with open(REF, "r", encoding="utf-8") as f:
    REF_FULL = f.read()

OPEN = '<div class="content-body">'
CLOSE = "\n            </div>\n        </div>\n    </section>\n    </main>"

bi = REF_FULL.index(OPEN) + len(OPEN)
ei = REF_FULL.index(CLOSE)
BODY_PREFIX = REF_FULL[REF_FULL.index("<body>") : bi]
SUFFIX = REF_FULL[ei:]

STYLE_BLOCK = re.search(
    r"<style>.*?</style>", REF_FULL, re.DOTALL
).group(0)


def head_html(title, meta_desc, path, schema_name, schema_desc):
    url = f"https://www.insiderlawyers.com/{path}"
    og_title = title.replace(" | Insider", " | Insider Accident Lawyers")
    if " | Insider Accident Lawyers" not in og_title:
        og_title = title + " | Insider Accident Lawyers"
    ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": schema_name,
        "url": url,
        "description": schema_desc,
        "isPartOf": {
            "@type": "WebSite",
            "name": "Insider Accident Lawyers",
            "url": "https://www.insiderlawyers.com/",
        },
    }
    ld2 = {
        "@context": "https://schema.org",
        "@type": "LegalService",
        "name": "Insider Accident Lawyers",
        "url": "https://www.insiderlawyers.com/",
        "telephone": "+1-844-467-4335",
        "areaServed": "Los Angeles, California",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "3435 Wilshire Blvd Suite 1620",
            "addressLocality": "Los Angeles",
            "addressRegion": "CA",
            "postalCode": "90010",
            "addressCountry": "US",
        },
    }
    return (
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/styles/main.css?v=2">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{url}">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="{url}">
    <meta property="og:site_name" content="Insider Accident Lawyers">
    <meta property="og:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    <script type="application/ld+json">
    {json.dumps(ld, ensure_ascii=False)}
    </script>
    <script type="application/ld+json">
    {json.dumps(ld2, ensure_ascii=False)}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    {STYLE_BLOCK}
"""
        + GTM_HEAD_GUARD
        + """

<link rel="stylesheet" href="/styles/footer.css">
</head>
"""
    )


CTA_MID = """
                <div class="consult-cta-block" style="margin:40px 0;padding:28px;background:linear-gradient(180deg,#f9fbfe,#f1f6fc);border:1px solid #dce6f2;border-radius:12px;text-align:center">
                <h3 style="margin-top:0;color:var(--brand-navy)">Free confidential consultation</h3>
                <p style="margin-bottom:8px;">Share where your case stands in confidence. We can discuss a second opinion, switching counsel, or simply what realistic next steps look like in California.</p>
                <p style="margin-top:12px;margin-bottom:0"><a href="/#case-evaluation" class="btn-primary">Free Case Review</a> <a href="tel:844-467-4335" class="btn-secondary" data-callrail-phone="844-467-4335">Call 844-467-4335</a></p>
                </div>
"""

CTA_END = """
                <p style="margin-top:32px"><a href="/#case-evaluation" class="btn-primary">Free Case Review</a> <a href="tel:844-467-4335" class="btn-secondary" data-callrail-phone="844-467-4335">Call 844-467-4335</a></p>
"""

HUB_LINKS = """<p>Our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> team handles serious motor vehicle injury matters. For broader injury topics, see <a href="/personal-injury">personal injury</a>. Referring counsel can review <a href="/attorney-referrals">attorney referrals</a> and the <a href="/lit-referral-core">litigation referral core</a> overview for co-counsel and file-transfer questions.</p>"""

PILLAR = "/changing-personal-injury-lawyer-california"

SPOKES = [
    "/can-i-change-my-personal-injury-lawyer-california",
    "/what-happens-if-i-fire-my-accident-attorney",
    "/contingency-fee-when-switching-lawyers-injury-case",
    "/second-opinion-personal-injury-claim-california",
    "/signs-personal-injury-lawyer-not-maximizing-case",
    "/personal-injury-case-feels-stalled-what-to-do",
]

SPOKE_LABELS = {
    "/can-i-change-my-personal-injury-lawyer-california": "Can I change my personal injury lawyer?",
    "/what-happens-if-i-fire-my-accident-attorney": "What happens if I fire my accident attorney?",
    "/contingency-fee-when-switching-lawyers-injury-case": "Contingency fee when switching lawyers",
    "/second-opinion-personal-injury-claim-california": "Second opinion on a personal injury claim",
    "/signs-personal-injury-lawyer-not-maximizing-case": "Signs your case may need a closer look",
    "/personal-injury-case-feels-stalled-what-to-do": "When your injury case feels stalled",
}


def faq_block(items):
    out = ['                <h2>FAQs</h2>\n']
    for q, a in items:
        out.append(
            f"""                <div class="faq-item">
                    <h4>{q}</h4>
                    <p>{a}</p>
                </div>
"""
        )
    return "".join(out)


def related_block(on_pillar=False, omit_spoke=None):
    lines = [
        '                <h2>Related resources</h2>',
        "                <ul>",
    ]
    if on_pillar:
        for sp in SPOKES:
            lines.append(
                f'                    <li><a href="{sp}">{SPOKE_LABELS[sp]}</a></li>'
            )
    else:
        lines.append(
            f'                    <li><a href="{PILLAR}">Changing a personal injury lawyer in California</a> (overview)</li>'
        )
        for sp in SPOKES:
            if omit_spoke and sp == omit_spoke:
                continue
            lines.append(
                f'                    <li><a href="{sp}">{SPOKE_LABELS[sp]}</a></li>'
            )
    lines.extend(
        [
            '                    <li><a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a></li>',
            '                    <li><a href="/personal-injury">Personal injury overview</a></li>',
            '                    <li><a href="/attorney-referrals">Attorney referrals</a></li>',
            '                    <li><a href="/lit-referral-core">Litigation referral core</a></li>',
            "                </ul>",
        ]
    )
    return "\n".join(lines) + "\n"


# --- Page bodies (inner HTML only, indented with 16 spaces) ---

PILLAR_BODY = f"""
                <h1>Changing Your Personal Injury Lawyer in California</h1>
                <p class="lead-text">Many injured people in California work with the first lawyer they find—and that is often the right choice. But when communication breaks down, deadlines feel unclear, or you simply want a second opinion, California law generally allows you to change counsel in a personal injury case. This guide explains the process in neutral terms, without criticizing any firm by name.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="Consultation about changing California personal injury counsel" style="width:100%;height:auto;display:block;"></figure>

                <h2>Why people consider switching injury lawyers</h2>
                <p>Common reasons include long gaps without updates, difficulty reaching the assigned attorney or staff, confusion about settlement strategy, or a sense that the case is not moving toward resolution. None of these automatically mean the first lawyer did something wrong—sometimes expectations differ, or docket congestion slows every case. Still, you are allowed to ask questions and explore options. If your case involves a motor vehicle crash, our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> page describes how we approach those claims.</p>
                <p>For a big-picture view of injury claims, see our <a href="/personal-injury">personal injury</a> hub. Lawyers who may transfer or associate a file can use <a href="/attorney-referrals">attorney referrals</a> and <a href="/lit-referral-core">litigation referral core</a> for process and criteria.</p>

                <h2>California context</h2>
                <p>California injury cases are usually handled on a contingency fee—no attorney fee unless there is a recovery, subject to your written agreement and State Bar rules. If you change lawyers, fees and costs are typically sorted through a lien or fee division agreement among counsel, not by paying two full separate contingency fees out of pocket in the way many clients fear. Exact arrangements depend on your contract and timing. Our spoke page on <a href="/contingency-fee-when-switching-lawyers-injury-case">contingency fees when switching lawyers</a> walks through that topic in more detail.</p>

                <h2>Topics in this cluster</h2>
                <p>Use these pages to go deeper on specific questions:</p>
                <ul>
                    <li><a href="/can-i-change-my-personal-injury-lawyer-california">Can I change my personal injury lawyer in California?</a></li>
                    <li><a href="/what-happens-if-i-fire-my-accident-attorney">What happens if I fire my accident attorney?</a></li>
                    <li><a href="/contingency-fee-when-switching-lawyers-injury-case">Contingency fee when switching lawyers in an injury case</a></li>
                    <li><a href="/second-opinion-personal-injury-claim-california">Second opinion on a personal injury claim in California</a></li>
                    <li><a href="/signs-personal-injury-lawyer-not-maximizing-case">Signs your personal injury lawyer may not be maximizing the case</a> (framed carefully—see that page)</li>
                    <li><a href="/personal-injury-case-feels-stalled-what-to-do">Personal injury case feels stalled—what to do</a></li>
                </ul>
{CTA_MID}
                <h2>Second opinions without burning bridges</h2>
                <p>Getting a second opinion does not have to be adversarial. Many clients simply want clarity on timeline, settlement range, or litigation risk. A consult can help you decide whether to stay the course or formally substitute counsel. Read <a href="/second-opinion-personal-injury-claim-california">second opinion on a personal injury claim</a> for a step-by-step framing.</p>

                <h2>When you are ready to talk</h2>
                <p>If you want a confidential discussion about your file—whether or not you ultimately switch—we are happy to review where things stand. This is general information, not legal advice for your specific contract or court order.</p>
{faq_block(
    [
        (
            "Can I switch personal injury lawyers in California?",
            "Often yes. Clients generally may hire new counsel; outgoing and incoming lawyers typically coordinate substitution of attorney filings and fee arrangements. Your written fee agreement and any court rules in your case matter, so review them with a licensed California attorney.",
        ),
        (
            "Will I pay two attorney fees?",
            "Usually not as two stacked full contingency fees against you in the way people fear. California State Bar rules govern fee divisions. Commonly, prior and new counsel share the contingent fee according to work performed and agreement—subject to your informed consent where required.",
        ),
        (
            "Is getting a second opinion disloyal?",
            "No. Understanding your case is prudent. Many people consult another lawyer to compare strategy or communication style before deciding whether to change representation.",
        ),
        (
            "What if my case is in litigation?",
            "Substitution still may be possible, but court procedures and timing differ. New counsel will review the docket, deadlines, and any hearing dates before filing to substitute in.",
        ),
    ]
)}
{related_block(on_pillar=True)}
{CTA_END}
"""

SPOKE_BODIES = {
    "can-i-change-my-personal-injury-lawyer-california": f"""
                <h1>Can I Change My Personal Injury Lawyer in California?</h1>
                <p class="lead-text">Yes—in most situations, you can change personal injury lawyers in California if you are unhappy with communication, strategy, or progress. The process should be handled carefully so court deadlines, liens, and fee agreements are respected.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="California client asking whether they can change injury lawyers" style="width:100%;height:auto;display:block;"></figure>

                <h2>Your relationship with counsel is contractual</h2>
                <p>You typically sign a fee agreement that describes the scope of representation and how fees are calculated. Ending or changing that relationship involves terminating or limiting the prior agreement and engaging new counsel. Incoming counsel often contacts the prior firm to obtain the file and discuss a lien or fee split consistent with State Bar rules—not a public attack on the other firm.</p>
                {HUB_LINKS}

                <h2>Practical steps</h2>
                <p>Before switching, gather your fee agreement, key dates (accident, treatment, lawsuit filed), and recent emails or letters from insurance or counsel. Ask any prospective new lawyer how they handle file transfer and substitution. For motor vehicle cases, see our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> practice description.</p>
{CTA_MID}
                <h2>Courts, deadlines, and substitution</h2>
                <p>If a lawsuit is on file, California courts have procedures for substituting attorneys. Missing a deadline can hurt your case, so timing matters. If you are pre-litigation, change may be simpler but still requires orderly transfer of records and demands.</p>
                <p>Return to the overview: <a href="{PILLAR}">changing your personal injury lawyer in California</a>.</p>
{faq_block(
    [
        (
            "Do I need a reason to change lawyers?",
            "You generally do not need to prove the first lawyer was “bad.” Many clients switch due to fit, communication, or strategy differences. What matters is doing it in a way that protects deadlines and complies with fee rules.",
        ),
        (
            "Can the old lawyer hold my file hostage?",
            "Lawyers have duties regarding client property and papers. There are processes to obtain your file. Disputes are usually resolved through bar rules and professional obligations—your new lawyer can explain typical practice.",
        ),
        (
            "Will changing lawyers delay my settlement?",
            "There can be a short transition while new counsel reviews the file. In some cases, fresh eyes and better pacing actually move the case forward. Much depends on case stage and insurer response times.",
        ),
    ]
)}
{related_block(omit_spoke="/can-i-change-my-personal-injury-lawyer-california")}
{CTA_END}
""",
    "what-happens-if-i-fire-my-accident-attorney": f"""
                <h1>What Happens If I Fire My Accident Attorney?</h1>
                <p class="lead-text">Firing your accident attorney ends (or narrows) the attorney-client relationship. What happens next depends on your fee agreement, whether a lawsuit is filed, and how quickly new counsel steps in. The goal is to protect your claim and comply with California ethics rules.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="What happens when dismissing an accident attorney in California" style="width:100%;height:auto;display:block;"></figure>

                <h2>Immediate priorities</h2>
                <p>Confirm upcoming deadlines—statutes of limitations, discovery cutoffs, hearings. If you dismiss counsel without a replacement ready, you risk missing dates. A new lawyer can file a substitution or notify the court as appropriate. For injury claims generally, our <a href="/personal-injury">personal injury</a> hub explains how cases typically unfold.</p>
                {HUB_LINKS}

                <h2>Fees and costs</h2>
                <p>Your former lawyer may have a lien for fees and reimbursable costs under your agreement and applicable rules. Incoming counsel usually addresses that in a written arrangement so you understand the net recovery. See <a href="/contingency-fee-when-switching-lawyers-injury-case">contingency fees when switching lawyers</a> for more detail.</p>
{CTA_MID}
                <h2>Professional handoff</h2>
                <p>In many situations, outgoing and incoming attorneys coordinate directly. That reduces friction for you. Referring lawyers evaluating a transfer may also use <a href="/attorney-referrals">attorney referrals</a> and <a href="/lit-referral-core">litigation referral core</a>.</p>
                <p>Overview: <a href="{PILLAR}">changing your personal injury lawyer in California</a>.</p>
{faq_block(
    [
        (
            "Should I fire my lawyer by email?",
            "Follow the termination process in your agreement if it has one. Written clarity helps. Many clients line up new counsel first so there is no gap in representation for active litigation.",
        ),
        (
            "What if I already accepted a settlement offer?",
            "Once a settlement is finalized and releases are signed, changing lawyers rarely changes that outcome. If you are still in negotiation, talk to qualified counsel immediately before signing.",
        ),
        (
            "Does firing my lawyer reset the statute of limitations?",
            "No. The limitations clock generally runs from the injury or discovery rule facts—not from who your lawyer is.",
        ),
    ]
)}
{related_block(omit_spoke="/what-happens-if-i-fire-my-accident-attorney")}
{CTA_END}
""",
    "contingency-fee-when-switching-lawyers-injury-case": f"""
                <h1>Contingency Fee When Switching Lawyers in an Injury Case</h1>
                <p class="lead-text">Most California personal injury cases are handled on contingency—you pay no attorney fee unless money is recovered, per your written agreement. Switching lawyers raises questions about how the fee is shared between prior and new counsel. This page explains the concepts clients ask about most.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="Contingency fee questions when changing injury lawyers" style="width:100%;height:auto;display:block;"></figure>

                <h2>One contingent fee, not necessarily double</h2>
                <p>Clients often worry they will pay 33% to the old lawyer and 33% to the new one. California’s Rules of Professional Conduct govern fee divisions between lawyers. Commonly, the total contingent percentage in your new agreement stays within what is typical for one case, and prior counsel participates in a division based on work performed and agreement—subject to required client disclosures when applicable. Your specific paperwork controls; this is not tax or legal advice for your file.</p>
                {HUB_LINKS}

                <h2>Costs vs. fees</h2>
                <p>Case costs (filing fees, records, experts) may be advanced by counsel and reimbursed from recovery per your contract. Changing lawyers may involve accounting for costs the first firm advanced. Ask any new lawyer to explain how costs are handled going forward.</p>
{CTA_MID}
                <h2>Why clarity matters</h2>
                <p>Before you switch, you should understand in writing how fee division and costs will work at settlement or verdict. If you have a <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident</a> matter, the same principles usually apply as in other PI cases.</p>
                <p>More context: <a href="{PILLAR}">changing your personal injury lawyer in California</a>.</p>
{faq_block(
    [
        (
            "Can I negotiate a lower fee with a new lawyer?",
            "Fees are negotiable within ethical limits and market practice. Any new agreement should be in writing and should address relationship to the prior firm’s lien or division.",
        ),
        (
            "Who pays if I lose the case?",
            "On a typical contingency agreement, you do not owe attorney fees if there is no recovery—again, subject to your contract and how costs are treated.",
        ),
        (
            "What is a lien from my old lawyer?",
            "It can assert the prior firm’s interest in fees (and sometimes costs) earned or advanced. New counsel explains how that is resolved at the end of the case.",
        ),
    ]
)}
{related_block(omit_spoke="/contingency-fee-when-switching-lawyers-injury-case")}
{CTA_END}
""",
    "second-opinion-personal-injury-claim-california": f"""
                <h1>Second Opinion on a Personal Injury Claim in California</h1>
                <p class="lead-text">A second opinion means having another licensed attorney review your facts, coverage, and strategy—without necessarily changing lawyers. Many clients do this when they feel uninformed, when a settlement offer arrives, or when they want to understand litigation risk.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="Second opinion on a California personal injury claim" style="width:100%;height:auto;display:block;"></figure>

                <h2>What to bring</h2>
                <p>Accident report or exchange information, key medical summaries, correspondence from insurers, your fee agreement (if asking about switching), and any lawsuit pleadings if filed. The reviewing attorney can compare your situation to typical <a href="/personal-injury">personal injury</a> patterns in California.</p>
                {HUB_LINKS}

                <h2>Neutral comparison, not mudslinging</h2>
                <p>A professional second opinion should focus on merits, damages, and process—not trashing another firm. If another lawyer’s conduct raises serious concerns, you may have separate remedies through the State Bar, but most issues are addressed by clearer communication or a orderly change of counsel.</p>
{CTA_MID}
                <h2>After the consult</h2>
                <p>You might stay with current counsel, ask for a case roadmap meeting, or retain new counsel. If you were hurt in a traffic crash, compare notes with how we describe case building on our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> page.</p>
                <p>Cluster overview: <a href="{PILLAR}">changing your personal injury lawyer in California</a>.</p>
{faq_block(
    [
        (
            "Will my current lawyer find out?",
            "Consultations are confidential when you engage a lawyer under normal professional rules. You choose whether to tell your current attorney you sought a second opinion.",
        ),
        (
            "Is there a fee for a second opinion?",
            "Some firms offer free case reviews; others charge consult fees for detailed analysis. Ask up front.",
        ),
        (
            "Does a second opinion delay my case?",
            "Usually not if it is a short consult. If you substitute counsel, expect some time for file review.",
        ),
    ]
)}
{related_block(omit_spoke="/second-opinion-personal-injury-claim-california")}
{CTA_END}
""",
    "signs-personal-injury-lawyer-not-maximizing-case": f"""
                <h1>Signs Your Personal Injury Lawyer May Not Be Maximizing the Case</h1>
                <p class="lead-text">This page lists common warning signs clients notice—not to accuse any lawyer of wrongdoing, but to help you decide when to ask better questions or seek a second opinion. Every case has slow periods; the issue is whether you understand why.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="Evaluating whether an injury case is being handled proactively" style="width:100%;height:auto;display:block;"></figure>

                <h2>Communication gaps</h2>
                <p>Repeated unanswered messages, no clarity on who is handling the file, or surprises (depositions, demands) without prior explanation can erode trust. A single busy week is normal; months without meaningful updates may warrant a direct conversation or a consult elsewhere.</p>
                {HUB_LINKS}

                <h2>Strategy opacity</h2>
                <p>You should understand, at a high level, whether the case is in investigation, treatment, demand, negotiation, or litigation—and what the next milestone is. If you cannot get that after asking, consider <a href="/second-opinion-personal-injury-claim-california">a second opinion</a>.</p>

                <h2>Settlement pressure without explanation</h2>
                <p>Attorneys may rightly recommend accepting a strong offer. But you should know how the number was derived, what risks trial carries, and what happens if you decline. If you feel rushed without reasoning, pause and verify with another lawyer before signing a release.</p>
{CTA_MID}
                <h2>Car accident cases</h2>
                <p>Traffic injury claims often hinge on liability photos, witness statements, and coverage stacks. If those were never discussed, ask why. Our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> section outlines how we typically develop those cases.</p>
                <p>Start with: <a href="{PILLAR}">changing your personal injury lawyer in California</a> and <a href="/personal-injury-case-feels-stalled-what-to-do">when a case feels stalled</a>.</p>
{faq_block(
    [
        (
            "Are these signs proof of malpractice?",
            "Not necessarily. They are reasons to ask questions, request a written status, or get a second opinion. Malpractice is a separate legal standard requiring proof of breach and harm.",
        ),
        (
            "What should I say to my current lawyer?",
            "Be direct: ask for a timeline, next steps, and major risks. Reasonable lawyers welcome that conversation.",
        ),
        (
            "Could the case simply be slow?",
            "Yes—treatment, insurer backlog, or court scheduling can delay matters. The difference is whether someone explains that to you.",
        ),
    ]
)}
{related_block(omit_spoke="/signs-personal-injury-lawyer-not-maximizing-case")}
{CTA_END}
""",
    "personal-injury-case-feels-stalled-what-to-do": f"""
                <h1>Personal Injury Case Feels Stalled—What to Do</h1>
                <p class="lead-text">Injury claims often have quiet stretches while records are gathered, treatment continues, or adjusters respond. If your case feels stalled, structured questions and documentation usually help more than assuming the worst.</p>
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="What to do when a California injury case feels stalled" style="width:100%;height:auto;display:block;"></figure>

                <h2>Step one: ask for a written status</h2>
                <p>Email your lawyer (or paralegal) for a short update: current phase, next action, and expected timing. That creates clarity and a record. Tie questions to milestones—records collection, demand, negotiation, filing suit—not vague frustration.</p>
                {HUB_LINKS}

                <h2>Step two: distinguish delay sources</h2>
                <p>Sometimes insurers or providers cause delay; sometimes court dates are far out. Your counsel should be able to explain which bottleneck applies. For broader process context, browse <a href="/personal-injury">personal injury</a> resources on our site.</p>
{CTA_MID}
                <h2>Step three: second opinion or new counsel</h2>
                <p>If answers stay unclear or deadlines worry you, a second consult may help. See <a href="/second-opinion-personal-injury-claim-california">second opinion on a personal injury claim</a> and the overview <a href="{PILLAR}">changing your personal injury lawyer in California</a>. Motor vehicle matters can also be discussed with our <a href="/los-angeles-car-accident-lawyer">Los Angeles car accident lawyer</a> team.</p>

                <h2>Referrals and co-counsel</h2>
                <p>Attorneys seeking help moving a stuck file may use <a href="/attorney-referrals">attorney referrals</a> or <a href="/lit-referral-core">litigation referral core</a>.</p>
{faq_block(
    [
        (
            "How long is “too long” without news?",
            "There is no single rule. If you have gone months with no substantive update after requesting one, that is a fair trigger for a follow-up call or second opinion.",
        ),
        (
            "Will nudging the insurance company myself help?",
            "Be cautious—statements you give can affect liability. Usually your lawyer should channel communications.",
        ),
        (
            "What if a lawsuit is already filed?",
            "Check discovery and motion deadlines with counsel. “Stall” in litigation sometimes reflects scheduling, sometimes strategy—ask which applies.",
        ),
    ]
)}
{related_block(omit_spoke="/personal-injury-case-feels-stalled-what-to-do")}
{CTA_END}
""",
}

META = {
    "changing-personal-injury-lawyer-california": (
        "Changing Personal Injury Lawyer in California | Insider",
        "How changing California personal injury lawyers works: second opinions, fees, file transfer, and communication—neutral guidance without attacking firms.",
        "Changing Your Personal Injury Lawyer in California",
        "Guide to changing California personal injury lawyers, second opinions, and contingency fee considerations.",
    ),
    "can-i-change-my-personal-injury-lawyer-california": (
        "Can I Change My Personal Injury Lawyer in California? | Insider",
        "Yes—most clients can change California personal injury counsel. Learn typical steps, file transfer, court substitution, and fee considerations.",
        "Can I Change My Personal Injury Lawyer in California?",
        "Whether and how you can change your California personal injury lawyer, with practical steps.",
    ),
    "what-happens-if-i-fire-my-accident-attorney": (
        "What Happens If I Fire My Accident Attorney? | Insider",
        "Firing your accident attorney in California: deadlines, fee liens, file transfer, and how new counsel steps in—explained in plain language.",
        "What Happens If I Fire My Accident Attorney?",
        "What happens when you dismiss your accident attorney in California, including fees and deadlines.",
    ),
    "contingency-fee-when-switching-lawyers-injury-case": (
        "Contingency Fee When Switching Injury Lawyers | Insider",
        "Contingency fees when you switch personal injury lawyers in California: fee division, liens, costs, and what clients usually pay.",
        "Contingency Fee When Switching Lawyers in an Injury Case",
        "Contingency fee and cost issues when switching California injury lawyers.",
    ),
    "second-opinion-personal-injury-claim-california": (
        "Second Opinion on a Personal Injury Claim in California | Insider",
        "Get clarity on a California injury claim: what a second opinion covers, what to bring, and how it differs from switching lawyers.",
        "Second Opinion on a Personal Injury Claim in California",
        "Second opinions on California personal injury claims: process, confidentiality, and next steps.",
    ),
    "signs-personal-injury-lawyer-not-maximizing-case": (
        "Signs Your Injury Lawyer May Not Be Maximizing the Case | Insider",
        "Neutral checklist: communication gaps, strategy questions, and settlement timing—when to ask more or seek a second opinion in California.",
        "Signs Your Personal Injury Lawyer May Not Be Maximizing the Case",
        "Neutral signs that may warrant questions or a second opinion on a California injury case.",
    ),
    "personal-injury-case-feels-stalled-what-to-do": (
        "Personal Injury Case Feels Stalled—What to Do | Insider",
        "If your California injury case feels stalled: how to request status, tell insurer delay from lawyer delay, and when to seek a second opinion.",
        "Personal Injury Case Feels Stalled—What to Do",
        "Practical steps when a California personal injury case feels stalled.",
    ),
}


def write_page(slug, inner_body):
    title, desc, schema_name, schema_desc = META[slug]
    head = head_html(title, desc, slug, schema_name, schema_desc)
    out = head + "\n" + BODY_PREFIX + inner_body + SUFFIX
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "index.html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("Wrote", path)


def main():
    write_page("changing-personal-injury-lawyer-california", PILLAR_BODY)
    for slug, body in SPOKE_BODIES.items():
        write_page(slug, body)
    print("Done.")


if __name__ == "__main__":
    main()
