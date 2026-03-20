# -*- coding: utf-8 -*-
"""Emit lifecycle cluster HTML pages from insurance-says template shell."""
import json
from pathlib import Path

from gtm_head_guard import GTM_HEAD_GUARD

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "insurance-says-injury-is-minor-california" / "index.html"
SPLIT_END = "            </div>\n        </div>\n    </section>\n    </main>"

LEGAL = (
    '<script type="application/ld+json">\n    '
    '{"@context": "https://schema.org", "@type": "LegalService", "name": "Insider Accident Lawyers", '
    '"url": "https://www.insiderlawyers.com/", "telephone": "+1-844-467-4335", "areaServed": "Los Angeles, California", '
    '"address": {"@type": "PostalAddress", "streetAddress": "3435 Wilshire Blvd Suite 1620", '
    '"addressLocality": "Los Angeles", "addressRegion": "CA", "postalCode": "90010", "addressCountry": "US"}}\n'
    "    </script>"
)

MANDATORY = {
    "changing": ('/changing-personal-injury-lawyer-california', "changing a personal injury lawyer in California"),
    "second": ('/second-opinion-personal-injury-claim-california', "second opinion on a personal injury claim in California"),
    "tactics": ('/insurance-company-tactics-personal-injury', "common insurance tactics in personal injury claims"),
    "la": ('/los-angeles-car-accident-lawyer', "Los Angeles car accident lawyer"),
}


def faq_block(items):
    parts = ['{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[']
    for i, (q, a) in enumerate(items):
        if i:
            parts.append(",")
        parts.append(
            '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
            % (json.dumps(q), json.dumps(a))
        )
    parts.append("]}")
    inner = "".join(parts)
    return f'    <script type="application/ld+json">\n    {inner}\n    </script>'


def related_ul(links):
    out = ["                <h2>Related resources</h2>", "                <ul>"]
    for href, label in links:
        out.append(f'                    <li><a href="{href}">{label}</a></li>')
    out.append("                </ul>")
    return "\n".join(out)


def cta_block(text):
    return f"""                <div class="consult-cta-block" style="margin:40px 0;padding:28px;background:linear-gradient(180deg,#f9fbfe,#f1f6fc);border:1px solid #dce6f2;border-radius:12px;text-align:center">
                <h3 style="margin-top:0;color:var(--brand-navy)">Free confidential case review</h3>
                <p style="margin-bottom:8px;">{text}</p>
                <p style="margin-top:12px;margin-bottom:0"><a href="/#case-evaluation" class="btn-primary">Free Case Review</a> <a href="tel:844-467-4335" class="btn-secondary" data-callrail-phone="844-467-4335">Call 844-467-4335</a></p>
                </div>"""


def footer_buttons():
    return """                <p style="margin-top:32px"><a href="/#case-evaluation" class="btn-primary">Free Case Review</a> <a href="tel:844-467-4335" class="btn-secondary" data-callrail-phone="844-467-4335">Call 844-467-4335</a></p>"""


def hero(alt):
    return f"""                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img decoding="async" src="/images/call-lawyer-accident-smartphone.jpg" alt="{alt}" style="width:100%;height:auto;display:block;"></figure>"""


def build_document(t, slug, title, desc, wp_name, wp_desc, faq_items, body_html):
    style_block = t.split("<style>", 1)[1].split("</style>", 1)[0]
    pre_head = t.split("<head>", 1)[0] + "<head>"
    post_head = "</head>" + t.split("</head>", 1)[1].split('<div class="content-body">', 1)[0]
    post = t.split(SPLIT_END, 1)[1]
    u = f"https://www.insiderlawyers.com/{slug}"
    wp = (
        '{"@context": "https://schema.org", "@type": "WebPage", "name": %s, "url": %s, "description": %s, '
        '"isPartOf": {"@type": "WebSite", "name": "Insider Accident Lawyers", "url": "https://www.insiderlawyers.com/"}}'
        % (json.dumps(wp_name), json.dumps(u), json.dumps(wp_desc))
    )
    wp_script = f"    <script type=\"application/ld+json\">\n    {wp}\n    </script>"
    head_inner = (
        f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/styles/main.css?v=2">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{u}">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{u}">
    <meta property="og:site_name" content="Insider Accident Lawyers">
    <meta property="og:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="https://www.insiderlawyers.com/images/hero/ktown-bg.jpg">
    {wp_script}
    {LEGAL}
    {faq_block(faq_items)}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
{style_block}
    </style>
"""
        + GTM_HEAD_GUARD
        + """

<link rel="stylesheet" href="/styles/footer.css">
"""
    )
    return (
        pre_head
        + head_inner
        + post_head
        + '<div class="content-body">'
        + body_html
        + "\n\n"
        + SPLIT_END
        + post
    )


def main():
    t = TEMPLATE.read_text(encoding="utf-8")
    C, S, TAC, LA = MANDATORY["changing"], MANDATORY["second"], MANDATORY["tactics"], MANDATORY["la"]

    # --- Page 1: stalled ---
    slug1 = "personal-injury-case-stalled-california"
    faq1 = [
        (
            "Why does my California injury claim feel stuck?",
            "Claims often move in phases. A stuck feeling can mean waiting on records, investigation, or negotiation—or it can mean unclear communication. If you are not getting updates, ask for a written status and timeline.",
        ),
        (
            "How can I tell a normal delay from a warning sign?",
            "Normal delays can happen around holidays, medical scheduling, or insurer review cycles. Warning signs include repeated unanswered requests, no clear next step, or pressure to settle without explanation. Trust patterns more than a single slow week.",
        ),
        (
            "How do insurance companies delay personal injury claims?",
            "Insurers may request additional information, revisit liability, or slow communication. That is not always improper—but it can affect timing. Understanding common tactics can help you respond without panic.",
        ),
        (
            "What should I do if I feel my case is not moving?",
            "Start with a calm request for clarity: what has been done, what is pending, and what deadlines matter. If you still feel lost, a second opinion can help you understand whether you need a clearer plan or a different fit.",
        ),
        (
            "When should I consider changing lawyers or a second opinion?",
            "Consider a second opinion when you feel uninformed or when settlement pressure arrives without explanation. Changing counsel is a bigger step and depends on your contract, court deadlines, and what a new attorney sees in your file.",
        ),
    ]
    body1 = f"""
                <h1>When Your Personal Injury Case Feels Stalled in California</h1>
                <p class="lead-text">Waiting is hard when you are hurt, bills are real, and you cannot see forward motion. If your claim feels frozen, you are not imagining it—many injured people feel the same way. This page is about naming what “stalled” can mean, what to watch for, and what you can do next without rushing a bad decision.</p>
                {hero("Person concerned that a California personal injury claim has stalled")}
                <blockquote class="content-quote"><strong>Quick answer:</strong> A case can feel slow without being broken. It can also feel slow because communication is missing, records are stuck, or negotiation has no clear direction. If you are unsure which you are in, ask for a case roadmap in plain language—and keep a simple log of what you are told.
                <ul class="plus-list" style="margin-top:14px;margin-bottom:0">
                    <li>Ask what stage you are in: investigation, treatment, demand, negotiation, litigation, or something else.</li>
                    <li>Request written updates when something is time-sensitive (deadlines, settlement offers, or releases).</li>
                    <li>If pressure arrives, treat it as a reason to slow down and read—not sign.</li>
                </ul>
                </blockquote>

                <h2>Emotional validation</h2>
                <p>Stalling is not just logistics. It can feel like your pain is being ignored, or like your life is on hold while other people move on. In Los Angeles, where traffic crashes and busy schedules collide, that feeling can hit harder.</p>
                <p>You are allowed to want clarity. Wanting updates does not make you “difficult.” You can explore a <a href="{S[0]}">{S[1]}</a> without turning your case into a fight overnight.</p>

                <h2>Normal delays vs warning signs</h2>
                <p><strong>Normal delays</strong> can include waiting on medical records, imaging, scheduling, or a fair negotiation window.</p>
                <p><strong>Warning signs</strong> include repeated unanswered messages, shifting explanations, vague answers about deadlines, or pressure to make big decisions without explanation. If you are seeing a pattern, it may help to read <a href="{C[0]}">{C[1]}</a> so you understand what changing counsel can involve—without committing to it yet.</p>

                <h2>Insurance delay tactics</h2>
                <p>Insurance companies manage risk and cost. That can show up as requests for more information, repeated questions, or slow responses. Sometimes that is routine. Sometimes it is strategic.</p>
                <p>For a grounded overview of how pressure and timing can show up in claims, see our guide on <a href="{TAC[0]}">{TAC[1]}</a>.</p>

                <h2>Treatment timeline reality</h2>
                <p>Healing is not predictable on a spreadsheet. Gaps in care can happen because life is expensive, schedules are tight, or symptoms fluctuate. Unfortunately, gaps can also become talking points later.</p>
                <p>Where you can, keep treatment coherent and follow reasonable medical advice—then make sure your file reflects what you are doing.</p>

                <h2>Settlement pressure risk</h2>
                <p>Fast money can sound like relief—until you realize what a release can mean. If you are being rushed while you still do not understand your injuries, treat that as a risk signal, not a reason to sign tonight.</p>

                {cta_block("If you are unsure what is normal and what is not, you can share where things stand in confidence. We can help you understand what questions to ask and what a fair process can look like in California.")}

                <h2>What should be happening in your case</h2>
                <p>You should generally understand what has been sent to insurance, what records are outstanding, and what the next milestone is. If you were hurt in a motor vehicle crash, you can compare how we describe case-building on our <a href="{LA[0]}">{LA[1]}</a> page.</p>

                <h2>Options if progress stopped</h2>
                <p>Start with a respectful request for clarity: email is fine. Ask for a timeline, a point of contact, and copies of key documents you are entitled to review. If you still feel stuck, a second opinion or a structured change of counsel may be appropriate—sometimes the issue is workload, sometimes fit, and sometimes the file needs a closer look.</p>
                <p>Related reads on timing and pressure: <a href="/insurance-says-injury-is-minor-california">when insurance says your injury is minor</a>, <a href="/how-long-personal-injury-case-takes-california">how long a personal injury case can take in California</a>, and <a href="/should-i-accept-first-settlement-offer-california">whether to accept a first settlement offer</a>.</p>

                <h2>Calm next step</h2>
                <p>You do not have to prove anything to deserve orientation. If your case feels stalled, the most useful move is often the simplest: get clarity—about your file, your deadlines, and your options.</p>
                <p>It may help to speak with someone who reviews cases like this and can explain what should be happening at your stage, without pressure and without promises.</p>

                <h2>FAQs</h2>
                <div class="faq-item"><h4>Why does my California injury claim feel stuck?</h4><p>Claims often move in phases. A stuck feeling can mean waiting on records, investigation, or negotiation—or unclear communication. Ask for a written status and timeline.</p></div>
                <div class="faq-item"><h4>How can I tell a normal delay from a warning sign?</h4><p>Normal delays happen around scheduling and review cycles. Warning signs include repeated unanswered requests, no clear next step, or pressure to settle without explanation.</p></div>
                <div class="faq-item"><h4>How do insurance companies delay personal injury claims?</h4><p>Insurers may request more information or slow communication. That is not always improper—but it can affect timing. Understanding common tactics can help you respond without panic.</p></div>
                <div class="faq-item"><h4>What should I do if I feel my case is not moving?</h4><p>Ask for clarity on what has been done, what is pending, and what deadlines matter. If you still feel lost, a second opinion can help you understand whether you need a clearer plan or a different fit.</p></div>
                <div class="faq-item"><h4>When should I consider changing lawyers or a second opinion?</h4><p>Consider a second opinion when you feel uninformed or when settlement pressure arrives without explanation. Changing counsel depends on your contract, deadlines, and what a new attorney sees in your file.</p></div>

                {related_ul([
                    ("/changing-personal-injury-lawyer-california", "Changing a personal injury lawyer in California"),
                    ("/second-opinion-personal-injury-claim-california", "Second opinion on a personal injury claim in California"),
                    ("/los-angeles-car-accident-lawyer", "Los Angeles car accident lawyer"),
                    ("/insurance-company-tactics-personal-injury", "Insurance company tactics in personal injury claims"),
                    ("/how-long-personal-injury-case-takes-california", "How long a personal injury case takes in California"),
                    ("/lawyer-pushing-settlement-too-fast-california", "When a lawyer is pushing settlement too fast"),
                ])}

                {footer_buttons()}
"""

    # --- Page 2: insurance says minor (refresh) ---
    slug2 = "insurance-says-injury-is-minor-california"
    faq2 = [
        (
            "Why would an insurance adjuster say my injury is minor?",
            "Adjusters often work from claim narratives that emphasize vehicle damage, gaps in treatment, or prior health history. Calling an injury minor can be a way to frame the claim for a smaller reserve or a faster resolution. It is not a medical diagnosis and it is not the final word on what you are experiencing.",
        ),
        (
            "Does low vehicle damage mean my injury claim is weak?",
            "Photos of a bumper or a parking-lot scrape do not measure pain, nerve irritation, or delayed symptoms. What matters for a claim is credible documentation over time—not a single snapshot of sheet metal.",
        ),
        (
            "What should I do if I feel pressured to settle early?",
            "Slow down and read what you are signing. Early offers often arrive before the full picture of treatment is clear. If you are unsure what a release means, ask questions, and consider whether a confidential review makes sense before you give up rights.",
        ),
        (
            "Is it normal to worry my lawyer agrees with the insurance company?",
            "It is common to feel that way when everyone sounds calm while you are hurting. A good lawyer should be able to explain the strategy in plain language and show you how your case is being built. If you feel minimized, it may help to ask direct questions—or get a second opinion on how your claim is being handled.",
        ),
        (
            "When should I consider a second opinion on my injury claim?",
            "Consider it when you feel uninformed, when the story of your case keeps changing, or when you are close to signing something you do not fully understand. A second opinion is a way to reduce uncertainty—not a guarantee about outcomes.",
        ),
    ]
    body2 = f"""
                <h1>When Insurance Says Your Injury Is Minor After an Accident</h1>
                <p class="lead-text">Hearing that your injury is “minor” can land like an insult—especially when you are in pain, missing work, or watching your life shrink to appointments and worry. This page is not here to diagnose you. It is here to explain how that label can shape a claim, what it does and does not prove, and what you can do to protect your side of the story.</p>
                {hero("Person reviewing an injury claim after an insurer called the injury minor")}
                <blockquote class="content-quote"><strong>Quick answer:</strong> When an adjuster calls an injury “minor,” it is often a <em>claim narrative</em>—a way of framing the file for internal notes, reserves, and negotiation. It is not a full medical judgment, and it is not the final word on what you are experiencing. What usually matters next is documentation, timing, and whether you understand what you are being asked to sign.
                <ul class="plus-list" style="margin-top:14px;margin-bottom:0">
                    <li>Separate bumper photos from your body: vehicle damage is one data point; symptoms and records tell another story.</li>
                    <li>Keep treatment coherent and follow reasonable medical advice—gaps get used against you, fairly or not.</li>
                    <li>If you feel rushed toward a check, pause until you understand what rights you may be giving up.</li>
                </ul>
                </blockquote>

                <h2>Why insurers frame injuries as minor</h2>
                <p>A “minor injury” storyline can affect how a claim is handled internally: what gets emphasized in notes, how aggressively an offer is pushed, and how much time is spent arguing over records versus resolving the case.</p>
                <p>That does not mean every adjuster is acting in bad faith on day one. It does mean the words you hear are not neutral clinical conclusions. For how timing and pressure often show up, read <a href="{TAC[0]}">{TAC[1]}</a>. For motor-vehicle context, see our <a href="{LA[0]}">{LA[1]}</a> page.</p>

                <h2>Damage photos vs medical reality</h2>
                <p>Photos of a small dent or a “low impact” scene can be real—and still incomplete. Vehicles absorb force differently than bodies do. Pain can be delayed, fluctuating, or hard to show on an X-ray early on.</p>
                <p>This is why the argument “look at the bumper” is often an incomplete picture of <em>you</em>. Your claim is not supposed to be decided like a photo contest. It is supposed to be supported by a credible story in the records: what happened, what hurt, what changed, and what treatment followed.</p>

                <h2>Documentation timing</h2>
                <p>In the real world, people wait, hope the pain passes, or try to muscle through a workweek—especially when money is tight. Unfortunately, gaps in care can become talking points later, even when the gap has a normal human explanation.</p>
                <p>Where you can, tell your providers what you feel, go to follow-ups you agree to, and keep a simple timeline: appointments, imaging, referrals, flare-ups. You do not need a perfect diary. You need a file that reflects reality well enough that your experience is harder to flatten into a single word like “minor.”</p>

                <h2>Early offer pressure</h2>
                <p>Fast money can sound like relief—until you realize what a release can mean for future treatment or disputes. Early offers often arrive when the full picture of an injury is still unfolding.</p>
                <p>If you are being told your injury is not serious while someone is also pushing you to settle quickly, treat that combination as a reason to slow down—not to panic, but to read, ask questions, and understand what you are trading away.</p>

                {cta_block("If you are being told your injury is not serious—and it does not match what you are living with—you can share what happened in confidence. We can help you understand what questions to ask and what a fair process can look like in California.")}

                <h2>Representation doubt emergence</h2>
                <p>Many injured people do not want drama. They want their lawyer to fight—but also to explain. If you feel your attorney is mirroring the insurance tone—calling your case small, pushing you to accept quickly, or avoiding your questions—you may start to wonder whose narrative is driving the file.</p>
                <p>That doubt does not make you disloyal. It means you need orientation. Sometimes the right next step is a direct conversation with your current counsel. Sometimes it is learning what <a href="{C[0]}">{C[1]}</a> can involve—without rushing—or exploring a <a href="{S[0]}">{S[1]}</a>.</p>

                <h2>Next step clarity</h2>
                <p>You do not have to accept a label that feels wrong just because it was delivered calmly. You also do not have to make a permanent decision tonight. The most useful move is often information: what is in your records, what the insurer is arguing, and what options you still have.</p>
                <p>If your case feels stuck while this narrative is unfolding, you may also find grounding on <a href="/personal-injury-case-stalled-california">when a personal injury case feels stalled in California</a> and on <a href="/should-i-accept-first-settlement-offer-california">whether to accept a first settlement offer</a>.</p>

                <h2>FAQs</h2>
                <div class="faq-item"><h4>Why would an insurance adjuster say my injury is minor?</h4><p>Adjusters often work from claim narratives that emphasize vehicle damage, gaps in treatment, or prior health history. Calling an injury minor can frame the claim for a smaller reserve or a faster resolution. It is not a medical diagnosis and it is not the final word on what you are experiencing.</p></div>
                <div class="faq-item"><h4>Does low vehicle damage mean my injury claim is weak?</h4><p>Photos of a bumper or a parking-lot scrape do not measure pain, nerve irritation, or delayed symptoms. What matters for a claim is credible documentation over time—not a single snapshot of sheet metal.</p></div>
                <div class="faq-item"><h4>What should I do if I feel pressured to settle early?</h4><p>Slow down and read what you are signing. Early offers often arrive before the full picture of treatment is clear. If you are unsure what a release means, ask questions, and consider whether a confidential review makes sense before you give up rights.</p></div>
                <div class="faq-item"><h4>Is it normal to worry my lawyer agrees with the insurance company?</h4><p>It is common to feel that way when everyone sounds calm while you are hurting. A good lawyer should explain strategy in plain language. If you feel minimized, ask direct questions—or consider a second opinion on how your claim is being handled.</p></div>
                <div class="faq-item"><h4>When should I consider a second opinion on my injury claim?</h4><p>Consider it when you feel uninformed, when the story of your case keeps changing, or when you are close to signing something you do not fully understand. A second opinion is a way to reduce uncertainty—not a guarantee about outcomes.</p></div>

                {related_ul([
                    ("/insurance-company-tactics-personal-injury", "Insurance company tactics in personal injury claims"),
                    ("/los-angeles-car-accident-lawyer", "Los Angeles car accident lawyer"),
                    ("/changing-personal-injury-lawyer-california", "Changing a personal injury lawyer in California"),
                    ("/second-opinion-personal-injury-claim-california", "Second opinion on a personal injury claim in California"),
                    ("/personal-injury-case-stalled-california", "When your personal injury case feels stalled"),
                    ("/should-i-accept-first-settlement-offer-california", "Should I accept a first settlement offer in California"),
                ])}

                {footer_buttons()}
"""

    # --- Page 3: first offer ---
    slug3 = "should-i-accept-first-settlement-offer-california"
    faq3 = [
        (
            "Should I accept the first settlement offer from insurance in California?",
            "Not automatically. The first offer is often a starting point in a negotiation. What matters is whether you understand your injuries, your treatment path, and what rights you give up when you sign a release.",
        ),
        (
            "What is the biggest risk of accepting an early settlement?",
            "A release can end your ability to seek more money later if your condition changes or new costs appear. That is why timing and clarity matter more than the size of the first number.",
        ),
        (
            "How do I know if my treatment is mature enough to evaluate an offer?",
            "Treatment maturity is not perfection—it is having enough information to understand what you are dealing with and what reasonable care may still involve. Your doctor’s guidance and your records usually matter more than a calendar guess.",
        ),
        (
            "What if I do not trust how my lawyer is handling negotiation?",
            "Ask for a plain-language explanation of the strategy and the tradeoffs. If answers stay vague, a second opinion on your claim—or learning what changing counsel involves—can help you decide calmly.",
        ),
        (
            "Is it okay to pause before signing?",
            "Yes. If you feel rushed, that is information. Pausing to read, ask questions, and understand the document is often the responsible move.",
        ),
    ]
    body3 = f"""
                <h1>Should I Accept the First Settlement Offer in California?</h1>
                <p class="lead-text">A check can feel like oxygen when bills stack up and your body still hurts. It can also feel scary—because signing often means closing a door. This page is about early offers, releases, and how to think clearly without pretending outcomes are guaranteed.</p>
                {hero("Person deciding whether to accept a first insurance settlement offer in California")}
                <blockquote class="content-quote"><strong>Quick answer:</strong> You do not have to accept the first offer just because it arrived first. In many claims, the first number is a starting point—not a final judgment of your worth. Before you sign, you want to understand what you are trading away, what is still unknown about your health, and whether the process feels explained.
                <ul class="plus-list" style="margin-top:14px;margin-bottom:0">
                    <li>Read the release language—or have it explained in plain terms.</li>
                    <li>Separate “fast relief” from “complete information.”</li>
                    <li>If you feel pressured, treat that as a signal to slow down, not shame yourself.</li>
                </ul>
                </blockquote>

                <h2>Why early offers happen</h2>
                <p>Insurance companies manage cost and closure. An early offer can be a way to resolve uncertainty quickly—for them and sometimes for you. It can also arrive before your file reflects what you are still learning about your body.</p>
                <p>For how insurers often approach timing and pressure, see <a href="{TAC[0]}">{TAC[1]}</a>.</p>

                <h2>Release risk</h2>
                <p>Settlement documents are not emotional—they are legal tools. A release can mean you are giving up future claims related to the incident, depending on the language. That is not inherently “bad,” but it is serious.</p>
                <p>If you do not understand what you are signing, pause. Questions are not weakness.</p>

                <h2>Treatment maturity</h2>
                <p>Some injuries look clearer after a few weeks. Some unfold slowly. “Mature enough” is not a buzzword—it is a practical idea: do you understand enough to make a knowing decision, with help from your providers and your records?</p>
                <p>If you were hurt in a crash, you may find it useful to compare how case-building is described on our <a href="{LA[0]}">{LA[1]}</a> page.</p>

                <h2>Negotiation dynamics</h2>
                <p>Negotiation is not a personality contest. It is a back-and-forth where information, documentation, and credibility matter. A first offer does not have to define the conversation—unless you let it define your timeline.</p>

                {cta_block("If you have an offer in hand and you are not sure what it means for your situation, you can request a confidential review. We can help you understand tradeoffs and questions—without pushing you toward a particular outcome.")}

                <h2>What to evaluate</h2>
                <p>Look at the whole picture: medical records, future care your doctor is discussing, lost income, and how stable your symptoms are. Also look at the document: what rights it mentions, what it asks you to give up, and whether anything feels rushed or vague.</p>

                <h2>When people question their lawyer</h2>
                <p>If your attorney is pushing you to accept quickly and you do not understand why, ask for the reasoning in plain language. If you still feel uneasy, you are not “betraying” anyone by seeking a <a href="{S[0]}">{S[1]}</a> or learning about <a href="{C[0]}">{C[1]}</a>.</p>

                <h2>FAQs</h2>
                <div class="faq-item"><h4>Should I accept the first settlement offer from insurance in California?</h4><p>Not automatically. The first offer is often a starting point. What matters is whether you understand your injuries, your treatment path, and what rights you give up when you sign a release.</p></div>
                <div class="faq-item"><h4>What is the biggest risk of accepting an early settlement?</h4><p>A release can end your ability to seek more money later if your condition changes or new costs appear. Timing and clarity matter more than the size of the first number.</p></div>
                <div class="faq-item"><h4>How do I know if my treatment is mature enough to evaluate an offer?</h4><p>Treatment maturity means having enough information to understand what you are dealing with and what reasonable care may still involve. Your doctor’s guidance and your records usually matter more than a calendar guess.</p></div>
                <div class="faq-item"><h4>What if I do not trust how my lawyer is handling negotiation?</h4><p>Ask for a plain-language explanation of strategy and tradeoffs. If answers stay vague, a second opinion—or learning what changing counsel involves—can help you decide calmly.</p></div>
                <div class="faq-item"><h4>Is it okay to pause before signing?</h4><p>Yes. If you feel rushed, that is information. Pausing to read and ask questions is often the responsible move.</p></div>

                {related_ul([
                    ("/insurance-says-injury-is-minor-california", "When insurance says your injury is minor"),
                    ("/lawyer-pushing-settlement-too-fast-california", "When a lawyer is pushing settlement too fast"),
                    ("/personal-injury-case-stalled-california", "When your personal injury case feels stalled"),
                    ("/how-long-personal-injury-case-takes-california", "How long a personal injury case takes in California"),
                    ("/second-opinion-personal-injury-claim-california", "Second opinion on a personal injury claim in California"),
                    ("/los-angeles-car-accident-lawyer", "Los Angeles car accident lawyer"),
                ])}

                {footer_buttons()}
"""

    # --- Page 4: timeline ---
    slug4 = "how-long-personal-injury-case-takes-california"
    faq4 = [
        (
            "How long does a typical personal injury case take in California?",
            "There is no single normal timeline. Some claims resolve in months; others take longer because of treatment, records, disputes, or court schedules. The timeline depends on facts, injuries, and process—not a universal clock.",
        ),
        (
            "Why do personal injury cases slow down?",
            "Common reasons include waiting on medical records, scheduling treatment, investigation, negotiation back-and-forth, or litigation steps. Sometimes slow is procedural; sometimes it signals communication issues.",
        ),
        (
            "Does filing a lawsuit always make things faster?",
            "Not necessarily. Litigation adds structure and deadlines, but it can also add time. Faster or slower depends on the case and the court.",
        ),
        (
            "When should I worry that delay means something is wrong?",
            "Worry less about a single slow week and more about patterns: no clear next step, repeated silence, or pressure to sign without explanation. Those patterns are worth addressing directly or exploring a second opinion.",
        ),
        (
            "What can I do while I wait?",
            "Keep treatment coherent where you can, keep copies of bills and notes, and ask your representative for milestones in plain language. Waiting feels better when you understand what stage you are in.",
        ),
    ]
    body4 = f"""
                <h1>How Long Does a Personal Injury Case Take in California?</h1>
                <p class="lead-text">If you are asking this question, you are probably tired—tired of pain, tired of phone tags, tired of not knowing when your life stops revolving around a claim number. This page offers a calm map: phases, common slowdowns, and what timeline talk usually leaves out.</p>
                {hero("Person wondering how long a California personal injury case will take")}
                <blockquote class="content-quote"><strong>Quick answer:</strong> California injury claims do not follow one schedule. Some resolve sooner; others take longer because healing, records, disputes, or court timelines do not cooperate with impatience. What helps most is understanding what stage you are in—and what should be happening next.
                <ul class="plus-list" style="margin-top:14px;margin-bottom:0">
                    <li>Separate “slow” from “stuck without explanation.”</li>
                    <li>Ask for milestones you can recognize: records sent, demand made, negotiation active, litigation filed—whatever fits your file.</li>
                    <li>Use worry as a prompt to ask questions—not to sign under pressure.</li>
                </ul>
                </blockquote>

                <h2>Typical case phases</h2>
                <p>Many files move through investigation and information gathering, treatment and documentation, demand and negotiation, and sometimes litigation. Not every case hits every phase, and phases can overlap.</p>
                <p>For motor-vehicle matters, our <a href="{LA[0]}">{LA[1]}</a> page describes how cases are often built over time.</p>

                <h2>Why cases slow down</h2>
                <p>Common reasons include medical scheduling, imaging, record requests, insurer review, witness coordination, or negotiation spacing. Sometimes the delay is mundane. Sometimes it is strategic—see <a href="{TAC[0]}">{TAC[1]}</a> for a grounded overview.</p>

                <h2>Insurance investigation reality</h2>
                <p>Insurers often review liability, coverage, and records before they move money. That can feel like stalling when you are the one hurting. It can also be standard process—until communication disappears.</p>

                <h2>Litigation vs settlement timelines</h2>
                <p>Settlement can happen without a lawsuit. Litigation adds steps: pleadings, discovery, motions, and court dates. Litigation does not automatically mean “faster,” but it can change the tone and the leverage.</p>

                {cta_block("If you are unsure whether your timeline is ordinary for your situation—or you feel left in the dark—you can share what you know in confidence. We can help you understand what questions to ask about your stage and your options.")}

                <h2>Expectations vs myths</h2>
                <p>Myth: there is a fixed number of months for every case. Reality: facts drive time. Myth: silence always means malice. Reality: silence can mean overload—or a communication gap you should close.</p>

                <h2>When delays signal risk</h2>
                <p>Risk signals include repeated unanswered messages, vague explanations about deadlines, or pressure to settle without clarity. If that sounds familiar, you may find orientation on <a href="/personal-injury-case-stalled-california">when a personal injury case feels stalled</a>, on <a href="{S[0]}">{S[1]}</a>, and on <a href="{C[0]}">{C[1]}</a>.</p>

                <h2>FAQs</h2>
                <div class="faq-item"><h4>How long does a typical personal injury case take in California?</h4><p>There is no single normal timeline. Some claims resolve in months; others take longer because of treatment, records, disputes, or court schedules. The timeline depends on facts and process—not a universal clock.</p></div>
                <div class="faq-item"><h4>Why do personal injury cases slow down?</h4><p>Common reasons include waiting on records, scheduling treatment, investigation, negotiation, or litigation steps. Sometimes slow is procedural; sometimes it signals communication issues.</p></div>
                <div class="faq-item"><h4>Does filing a lawsuit always make things faster?</h4><p>Not necessarily. Litigation adds structure and deadlines, but it can also add time. It depends on the case and the court.</p></div>
                <div class="faq-item"><h4>When should I worry that delay means something is wrong?</h4><p>Worry less about a single slow week and more about patterns: no clear next step, repeated silence, or pressure to sign without explanation.</p></div>
                <div class="faq-item"><h4>What can I do while I wait?</h4><p>Keep treatment coherent where you can, keep copies of bills and notes, and ask for milestones in plain language. Waiting feels better when you understand what stage you are in.</p></div>

                {related_ul([
                    ("/personal-injury-case-stalled-california", "When your personal injury case feels stalled"),
                    ("/should-i-accept-first-settlement-offer-california", "Should I accept a first settlement offer"),
                    ("/lawyer-pushing-settlement-too-fast-california", "When a lawyer is pushing settlement too fast"),
                    ("/insurance-company-tactics-personal-injury", "Insurance company tactics in personal injury claims"),
                    ("/second-opinion-personal-injury-claim-california", "Second opinion on a personal injury claim in California"),
                    ("/los-angeles-car-accident-lawyer", "Los Angeles car accident lawyer"),
                ])}

                {footer_buttons()}
"""

    # --- Page 5: lawyer pushing fast ---
    slug5 = "lawyer-pushing-settlement-too-fast-california"
    faq5 = [
        (
            "Why would a personal injury lawyer push a fast settlement?",
            "Sometimes a lawyer believes the offer is fair for the known facts. Sometimes timing is driven by deadlines, risk, or client pressure. Sometimes the file is not as developed as it should be. The reason matters—ask for it in plain language.",
        ),
        (
            "Is it ever reasonable to settle quickly?",
            "It can be—when the facts are clear, the documentation supports the outcome, and you understand the release. Quick is not automatically wrong; rushed without understanding is the problem.",
        ),
        (
            "What are file maturity issues?",
            "A file may be immature if records are incomplete, future treatment is still unknown, or liability is still contested. Settling on an immature file can mean guessing—and guessing is stressful.",
        ),
        (
            "What if I feel financial pressure to say yes?",
            "Financial pressure is real. It can also push people to accept before they understand the trade. If you feel cornered, naming that out loud—to yourself and, when appropriate, your attorney—can be the first step toward clarity.",
        ),
        (
            "What can I do without escalating conflict?",
            "Ask for a written summary of pros and cons, request a follow-up call after you read the release, and consider a second opinion if answers stay vague. You can seek clarity without declaring war.",
        ),
    ]
    body5 = f"""
                <h1>When Your Lawyer Is Pushing Settlement Too Fast in California</h1>
                <p class="lead-text">You hired help because you were overwhelmed. If your attorney is now pressing you to “just sign,” you may feel a strange mix of gratitude and doubt. This page is for that doubt—without turning it into a fight by default.</p>
                {hero("Person uncomfortable with pressure to settle a personal injury case quickly")}
                <blockquote class="content-quote"><strong>Quick answer:</strong> Fast is not automatically wrong—but rushed without understanding is risky. If you feel pushed, you deserve a clear explanation of what you are signing away, what facts the offer is based on, and what alternatives exist. Calm questions are not disloyalty.
                <ul class="plus-list" style="margin-top:14px;margin-bottom:0">
                    <li>Ask what the lawyer believes is still unknown—and how that uncertainty is priced into the decision.</li>
                    <li>Ask what happens if your symptoms change after you sign.</li>
                    <li>If the room feels rushed, ask for time to read in quiet.</li>
                </ul>
                </blockquote>

                <h2>Why quick settlements occur</h2>
                <p>Sometimes counsel believes an offer matches the strength of the evidence. Sometimes there are deadlines—policy limits, court dates, or risk shifts. Sometimes the push comes from outside the law: bills, rent, fear.</p>
                <p>Understanding the “why” helps you respond without spiraling.</p>

                <h2>File maturity issues</h2>
                <p>An offer may arrive before your records tell a full story. That does not mean the offer is always wrong—but it means you should know what is still unknown. Immature files make decisions feel like guessing.</p>
                <p>For timing context, see <a href="/how-long-personal-injury-case-takes-california">how long a personal injury case can take in California</a> and <a href="/personal-injury-case-stalled-california">when a case feels stalled</a>—two different problems that can both create anxiety.</p>

                <h2>Financial pressure dynamics</h2>
                <p>Money stress can make any offer look like salvation. It can also make you vulnerable to regret. Naming financial pressure does not mean you are “only in it for money.” It means you are human.</p>

                {cta_block("If you feel rushed to sign and you are not sure the tradeoffs are explained, you can request a confidential review. We can help you understand what questions to ask your current counsel—and what a second look can clarify.")}

                <h2>Second opinion timing</h2>
                <p>If answers feel thin, a <a href="{S[0]}">{S[1]}</a> can reduce uncertainty. It is not a betrayal. It is a way to check whether the plan matches the file—and your comfort level.</p>
                <p>If you are considering a change, learn what <a href="{C[0]}">{C[1]}</a> can involve before you make a move.</p>

                <h2>Options without conflict escalation</h2>
                <p>You can ask for a written summary, a follow-up appointment after you read documents, or a clearer walkthrough of the release. You can also bring a trusted friend to listen—if that helps you think.</p>
                <p>For insurer-side pressure patterns, <a href="{TAC[0]}">{TAC[1]}</a> may help you separate lawyer urgency from insurance tactics.</p>
                <p>Crash cases often raise overlapping worries; our <a href="{LA[0]}">{LA[1]}</a> page discusses how cases are commonly built and evaluated.</p>

                <h2>FAQs</h2>
                <div class="faq-item"><h4>Why would a personal injury lawyer push a fast settlement?</h4><p>Sometimes a lawyer believes the offer is fair for the known facts. Sometimes timing is driven by deadlines, risk, or client pressure. Sometimes the file is not as developed as it should be. Ask for the reason in plain language.</p></div>
                <div class="faq-item"><h4>Is it ever reasonable to settle quickly?</h4><p>It can be—when the facts are clear, the documentation supports the outcome, and you understand the release. Quick is not automatically wrong; rushed without understanding is the problem.</p></div>
                <div class="faq-item"><h4>What are file maturity issues?</h4><p>A file may be immature if records are incomplete, future treatment is still unknown, or liability is still contested. Settling on an immature file can mean guessing.</p></div>
                <div class="faq-item"><h4>What if I feel financial pressure to say yes?</h4><p>Financial pressure is real. If you feel cornered, naming that can be the first step toward clarity—without shame.</p></div>
                <div class="faq-item"><h4>What can I do without escalating conflict?</h4><p>Ask for a written summary, request time to read the release, and consider a second opinion if answers stay vague. You can seek clarity without declaring war.</p></div>

                {related_ul([
                    ("/second-opinion-personal-injury-claim-california", "Second opinion on a personal injury claim in California"),
                    ("/changing-personal-injury-lawyer-california", "Changing a personal injury lawyer in California"),
                    ("/should-i-accept-first-settlement-offer-california", "Should I accept a first settlement offer"),
                    ("/insurance-says-injury-is-minor-california", "When insurance says your injury is minor"),
                    ("/insurance-company-tactics-personal-injury", "Insurance company tactics in personal injury claims"),
                    ("/los-angeles-car-accident-lawyer", "Los Angeles car accident lawyer"),
                ])}

                {footer_buttons()}
"""

    pages = [
        (
            slug1,
            "Personal Injury Case Feels Stalled? What It Can Mean in California | Insider Lawyers",
            "If your California injury claim feels stuck, you are not alone. Learn normal delays, warning signs, insurance timing, and calm next steps.",
            "When Your Personal Injury Case Feels Stalled in California",
            "Practical guidance for California injury claims that feel stalled: communication, delays, insurance timing, and next steps.",
            faq1,
            body1,
        ),
        (
            slug2,
            "Insurance Says Your Injury Is Minor? What It Can Mean in California | Insider Lawyers",
            "If an insurance company says your injury is minor after an accident, it may affect how your claim is handled. Learn what this can mean and what steps may help protect your case.",
            "When Insurance Says Your Injury Is Minor After an Accident",
            "How insurance narratives about minor injuries can affect a California injury claim, and practical steps around documentation, timing, and representation.",
            faq2,
            body2,
        ),
        (
            slug3,
            "Should I Accept the First Settlement Offer in California? | Insider Lawyers",
            "Worried about an early settlement offer in California? Understand releases, timing, negotiation basics, and how to evaluate an offer without guarantees.",
            "Should I Accept the First Settlement Offer in California",
            "Guidance for injured people considering an early insurance settlement in California: releases, treatment timing, negotiation dynamics, and next steps.",
            faq3,
            body3,
        ),
        (
            slug4,
            "How Long Does a Personal Injury Case Take in California? | Insider Lawyers",
            "California personal injury timelines vary by case. Learn common phases, why claims slow down, litigation vs settlement pacing, and when delays deserve a closer look.",
            "How Long Does a Personal Injury Case Take in California",
            "A practical overview of personal injury case timing in California: phases, slowdowns, insurer investigation, litigation, and expectations.",
            faq4,
            body4,
        ),
        (
            slug5,
            "Lawyer Pushing Settlement Too Fast in California? What to Consider | Insider Lawyers",
            "Feeling rushed to settle your California injury case? Understand why quick settlements happen, file maturity, pressure dynamics, and calm options—including a second opinion.",
            "When Your Lawyer Is Pushing Settlement Too Fast in California",
            "Supportive guidance for clients who feel pressured to settle quickly: maturity of the file, financial stress, second opinions, and options without unnecessary conflict.",
            faq5,
            body5,
        ),
    ]

    for slug, title, desc, wp_name, wp_desc, faq_items, body_html in pages:
        doc = build_document(t, slug, title, desc, wp_name, wp_desc, faq_items, body_html)
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(doc, encoding="utf-8")
        print("Wrote", slug)


if __name__ == "__main__":
    main()
