# -*- coding: utf-8 -*-
# Centralized SEO configuration for insiderlawyers.com.
# Consumed by scripts/seo_normalize_head.py and scripts/seo_audit.py.
SITE_URL = "https://www.insiderlawyers.com"
SITE_NAME = "Insider Lawyers"
SITE_NAME_ES = "Insider Lawyers"
BRAND_SUFFIX_EN = " | Insider Lawyers"
BRAND_SUFFIX_ES = " | Insider Lawyers"
DEFAULT_TITLE_EN = "California Injury Claim Resource | Insider Lawyers"
DEFAULT_TITLE_ES = "Reclamos por Lesiones en California | Insider Lawyers"
DEFAULT_DESC_EN = (
    "Plain-English California injury claim information, settlement reviews, second opinions, "
    "and guidance before you accept an insurance offer."
)
DEFAULT_DESC_ES = (
    "Informacion clara sobre reclamos por lesiones, ofertas del seguro, acuerdos, segundas "
    "opiniones y revision de casos en California."
)
DEFAULT_OG_IMAGE = SITE_URL + "/og-default.png"
THEME_COLOR = "#01366c"

# Title and description length guardrails.
TITLE_MAX = 62
TITLE_TARGET = 58
DESC_MIN = 110
DESC_MAX = 165
DESC_TARGET = 150

# ---------------------------------------------------------------------------
# Spanish terminology map (English -> Spanish). Used for consistency in
# /es/ pages and reviewable by editors. Spanish copy on this site uses
# natural Southern California Spanish, not literal machine translation.
# ---------------------------------------------------------------------------
ES_TERMS = {
    "injury claim": "reclamo por lesiones",
    "claim review": "revision del reclamo",
    "free claim review": "revision gratuita del reclamo",
    "settlement offer": "oferta de acuerdo",
    "insurance offer": "oferta del seguro",
    "insurance company": "compania de seguros / aseguranza",
    "insurance adjuster": "ajustador del seguro",
    "demand letter": "carta de demanda",
    "second opinion": "segunda opinion",
    "attorney review": "revision con un abogado",
    "medical bills": "facturas medicas",
    "lost wages": "salarios perdidos",
    "property damage": "danos a la propiedad",
    "uninsured motorist": "conductor sin seguro",
    "underinsured motorist": "conductor con cobertura insuficiente",
    "release": "liberacion / acuerdo final",
    "medical lien": "gravamen medico / lien medico",
    "personal injury": "lesiones personales",
    "wrongful death": "muerte injusta / muerte por negligencia",
    "comparative fault": "negligencia comparada",
    "comparative negligence": "negligencia comparada",
    "no obligation to hire anyone": "sin obligacion de contratar a nadie",
}

# ---------------------------------------------------------------------------
# Page-category routing rules.
# Used by audit / normalize to classify each route consistently.
# ---------------------------------------------------------------------------
CATEGORY_RULES = [
    ("homepage", lambda p: p in ("/", "/es")),
    ("contact", lambda p: p == "/contact"),
    ("contact-es", lambda p: p == "/es/contacto"),
    ("legal", lambda p: p in (
        "/privacy-policy", "/legal-terms", "/disclaimer", "/cookie-policy",
        "/california-privacy-rights",
        "/do-not-sell-or-share-my-personal-information",
        "/accessibility",
    )),
    ("legal-es", lambda p: p in (
        "/es/politica-privacidad", "/es/terminos-legales", "/es/aviso-legal",
        "/es/politica-cookies", "/es/derechos-privacidad-california",
        "/es/no-vender-compartir-informacion-personal", "/es/accesibilidad",
    )),
    ("referral", lambda p: p == "/attorney-referrals" or p.startswith("/lit-referral-")),
    ("hub", lambda p: p == "/personal-injury" or p == "/settlements" or p.startswith("/personal-injury/")),
    ("la-claim", lambda p: p.startswith("/los-angeles-") or p.endswith("-los-angeles")),
    ("claim-guide", lambda p: p.startswith("/california-") or "settlement" in p or "claim" in p),
    ("es-content", lambda p: p.startswith("/es/")),
    ("guide", lambda p: True),  # default
]


def classify(path: str) -> str:
    for name, fn in CATEGORY_RULES:
        if fn(path):
            return name
    return "guide"
