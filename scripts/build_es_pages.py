# -*- coding: utf-8 -*-
"""Build Spanish /es/ pages, add hreflang to English pages, refresh sitemap.

This is idempotent: re-running overwrites only generated /es/ pages and
re-injects hreflang into mapped English pages. It never modifies content
on English pages outside the <head> hreflang block.

Tier 1 only. Tier 2 / Tier 3 can be added later by extending PAGES below.

Run after:
    python scripts/build_es_pages.py
    python scripts/apply_global_layout.py   # populates Spanish chrome
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES_ROOT = ROOT / "es"
SITEMAP = ROOT / "sitemap.xml"
SITE = "https://www.insiderlawyers.com"
TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# Shared HTML chunks
# ---------------------------------------------------------------------------

# Inline style block (same vocabulary as English content pages so visuals match)
INLINE_CSS = """
:root{--brand-navy:#01366c;--brand-blue:#01468a;--brand-light-blue:#f3f6fa;--brand-accent-yellow:#fbba00;--brand-white:#fff;--brand-gray-900:#1f2937;--brand-gray-700:#374151;--brand-border:#e5e7eb;--card-radius:12px}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:"Inter","Poppins",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.7;color:var(--brand-gray-900);background:var(--brand-white);font-size:16px}
.container{max-width:1100px;margin:0 auto;padding:0 20px}
section{padding:40px 0}
.section-content{padding:36px 0}
h1,h2,h3,h4{font-weight:700;color:var(--brand-navy)}
h1{font-size:38px;margin-bottom:18px;line-height:1.2}
h2{font-size:26px;margin:30px 0 14px;line-height:1.3}
h3{font-size:20px;margin:22px 0 10px;color:#0f3f72}
h4{font-size:17px;margin:14px 0 6px}
p{margin-bottom:14px;line-height:1.75}
.lead-text{font-size:18px;color:var(--brand-gray-700);margin-bottom:20px}
ul{margin:14px 0 18px;padding-left:24px}
li{margin:6px 0}
.content-body h2{position:relative;padding:12px 16px;background:linear-gradient(180deg,#f9fbfe 0%,#f1f6fc 100%);border:1px solid #dce6f2;border-left:4px solid var(--brand-blue);border-radius:10px}
.faq-item{margin:16px 0;padding:18px 20px;background:#f8fbff;border:1px solid #d8e5f4;border-radius:var(--card-radius);box-shadow:0 4px 14px rgba(1,54,108,.06)}
.faq-item h3{margin-top:0;color:var(--brand-navy)}
.btn-primary{display:inline-block;background:var(--brand-accent-yellow);color:var(--brand-navy);font-weight:700;padding:14px 24px;border-radius:8px;text-decoration:none;font-size:17px;margin:8px 6px 8px 0;transition:all .2s}
.btn-primary:hover{background:#e6b300;transform:translateY(-2px)}
.btn-secondary{display:inline-block;background:var(--brand-blue);color:var(--brand-white);font-weight:700;padding:14px 24px;border-radius:8px;text-decoration:none;font-size:17px;margin:8px 6px 8px 0;transition:all .2s}
.btn-secondary:hover{background:#0f3261;transform:translateY(-2px)}
.content-body a{color:var(--brand-blue);text-decoration:underline}
.content-body a:hover{color:var(--brand-navy)}
.content-body a.btn-primary,.content-body a.btn-secondary{text-decoration:none}
.content-body a.btn-secondary{color:#fff!important}
.cta-block{margin:30px 0;padding:24px 28px;background:linear-gradient(180deg,#f9fbfe,#f1f6fc);border:1px solid #dce6f2;border-left:4px solid var(--brand-accent-yellow);border-radius:12px}
.cta-block h3{margin-top:0}
.disclaimer-block{margin:24px 0;padding:16px 20px;background:#fffbe6;border:1px solid #f1e0a1;border-radius:10px;font-size:14px;color:#594613;line-height:1.6}
.related-list{list-style:none;padding-left:0}
.related-list li{margin:8px 0;padding-left:18px;position:relative}
.related-list li:before{content:"\\2192";color:var(--brand-blue);font-weight:700;position:absolute;left:0}
.toc-block{margin:20px 0 28px;padding:18px 22px;background:#f3f6fa;border:1px solid #d8e3ef;border-radius:10px}
.toc-block h3{margin:0 0 8px;color:var(--brand-navy);font-size:16px;text-transform:uppercase;letter-spacing:.06em}
.toc-block ul{margin:0;padding-left:20px;columns:2;column-gap:24px}
.toc-block li{margin:4px 0;break-inside:avoid}
/* Hero / section imagery (Spanish Tier 1) — neutral editorial photography
   reused from approved English-side assets. Constant aspect ratio so
   pages don't shift while loading. */
.es-hero-img{margin:0 0 24px;border-radius:14px;overflow:hidden;box-shadow:0 10px 28px rgba(1,54,108,.14);background:#eef2f7}
.es-hero-img img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}
.es-inline-image{display:grid;grid-template-columns:5fr 6fr;gap:28px;align-items:center;margin:30px 0;padding:18px;background:#f8fbfe;border:1px solid #e2ecf6;border-radius:14px}
.es-inline-image .es-inline-image__media{margin:0;overflow:hidden;border-radius:10px;background:#eef2f7}
.es-inline-image .es-inline-image__media img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}
.es-inline-image .es-inline-image__copy h3{margin-top:0;color:var(--brand-navy);font-size:1.2rem}
.es-inline-image .es-inline-image__copy p{margin:0 0 8px;color:var(--brand-gray-700);font-size:0.96rem;line-height:1.6}
.es-inline-image--flip{grid-template-columns:6fr 5fr}
.es-inline-image--flip .es-inline-image__media{order:2}
@media(max-width:760px){
  .es-inline-image,.es-inline-image--flip{grid-template-columns:1fr;padding:14px}
  .es-inline-image .es-inline-image__media{order:0!important}
}
@media(max-width:700px){.toc-block ul{columns:1}h1{font-size:28px}h2{font-size:22px}.container{padding:0 16px}}
"""

GTM_HEAD = """<script>
(function() {
var allowedHosts = ["insiderlawyers.com","www.insiderlawyers.com","insideraccidentlawyers.com","www.insideraccidentlawyers.com","call.insideraccidentlawyers.com"];
if (allowedHosts.includes(window.location.hostname)) {
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-WS8XT5FC');
}
})();
</script>"""

GTM_NOSCRIPT = """<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WS8XT5FC" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

UTM_CAPTURE = """<script>
(function(){ var k=['gclid','gbraid','wbraid','utm_source','utm_medium','utm_campaign','utm_term','utm_content']; var q=window.location.search?new URLSearchParams(window.location.search):null; if(q){ for(var i=0;i<k.length;i++){ var v=q.get(k[i]); if(v) try{ localStorage.setItem('ial_'+k[i],v); }catch(e){} } }
})();
</script>"""

# Spanish Tier 1 lead form (shared between hero + footer CTA blocks).
# IDs/name attributes preserved so ial-form-tracking.js + GTM events fire.
FORM_HTML = """<form action=\"https://formsubmit.co/ial.leads.2024@gmail.com\" method=\"POST\" id=\"case-evaluation-form\" novalidate>
  <input type=\"hidden\" name=\"_subject\" value=\"Nueva solicitud de revisi\u00f3n - Espa\u00f1ol\">
  <input type=\"hidden\" name=\"_captcha\" value=\"false\">
  <input type=\"hidden\" name=\"_template\" value=\"table\">
  <input type=\"hidden\" name=\"_autoresponse\" value=\"Gracias. Recibimos su solicitud de revisi\u00f3n. Nuestro equipo se comunicar\u00e1 con usted en breve. Esta es una revisi\u00f3n gratuita del reclamo y no crea una relaci\u00f3n abogado-cliente.\">
  <input type=\"hidden\" name=\"_next\" value=\"https://www.insiderlawyers.com/thank-you/\">
  <input type=\"hidden\" name=\"language\" value=\"es\">
  <label class=\"ial-label\" for=\"es-full-name\">Nombre completo *</label>
  <input type=\"text\" class=\"ial-input\" id=\"es-full-name\" name=\"full_name\" placeholder=\"Su nombre completo\" required>
  <label class=\"ial-label\" for=\"es-phone\">Tel\u00e9fono *</label>
  <input type=\"tel\" class=\"ial-input\" id=\"es-phone\" name=\"phone\" placeholder=\"(555) 555-5555\" required>
  <label class=\"ial-label\" for=\"es-accident\">Cu\u00e9ntenos qu\u00e9 pas\u00f3 *</label>
  <textarea class=\"ial-input ial-textarea\" id=\"es-accident\" name=\"accident_reason\" rows=\"3\" placeholder=\"Descripci\u00f3n breve del accidente, lesi\u00f3n u oferta de la aseguranza\u2026\" required></textarea>
  <div class=\"ial-checkbox-wrap\">
    <input type=\"checkbox\" name=\"text_consent\" id=\"es-text-consent\">
    <label for=\"es-text-consent\" class=\"ial-checkbox-label\">Al marcar esta casilla, doy mi consentimiento para recibir mensajes SMS sobre la revisi\u00f3n de mi reclamo. La frecuencia de los mensajes var\u00eda. Pueden aplicarse tarifas. Responda STOP para cancelar o HELP para obtener ayuda. El consentimiento no es necesario para contratar a un abogado ni para solicitar una revisi\u00f3n. Consulte nuestra <a href=\"/es/politica-privacidad/\" style=\"color:#fbba00;text-decoration:underline;\">Pol\u00edtica de Privacidad</a> y nuestros <a href=\"/es/terminos-legales/\" style=\"color:#fbba00;text-decoration:underline;\">T\u00e9rminos Legales</a>.</label>
  </div>
  <button type=\"submit\" class=\"ial-submit\">Solicitar Revisi\u00f3n Gratuita</button>
  <p class=\"ial-form-disclaimer\" style=\"margin-top:0.6rem;font-size:0.78rem;color:rgba(255,255,255,0.85);line-height:1.45;\">Enviar este formulario no crea una relaci\u00f3n abogado-cliente. No env\u00ede informaci\u00f3n confidencial ni urgente hasta que se confirme la representaci\u00f3n.</p>
</form>"""

# Tracking + form helper script (Spanish hero form variant).
# Mirrors the English homepage's inline behaviour so phone_click, form_start,
# and form_submit dataLayer events fire on /es/ pages exactly like the EN home.
FORM_TRACKING_INLINE = """<script>
window.dataLayer = window.dataLayer || [];
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a[href^="tel:"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof dataLayer !== 'undefined') {
        dataLayer.push({ 'event': 'phone_click', 'phone_number': this.getAttribute('href').replace('tel:', ''), 'page_path': location.pathname });
      }
    });
  });
  var form = document.getElementById('case-evaluation-form');
  if (form) {
    var formStarted = false;
    form.querySelectorAll('input, select, textarea').forEach(function(field) {
      field.addEventListener('focus', function() {
        if (!formStarted && typeof dataLayer !== 'undefined') {
          formStarted = true;
          dataLayer.push({ 'event': 'form_start', 'form_name': 'case_evaluation', 'language': 'es' });
        }
      }, { once: true });
    });
    form.addEventListener('submit', function() {
      if (typeof dataLayer !== 'undefined') {
        dataLayer.push({ event: 'form_submit', form_name: 'case_evaluation', language: 'es' });
      }
      var phoneInput = form.querySelector('input[name="phone"]');
      if (phoneInput) { phoneInput.value = phoneInput.value.replace(/\\D/g, ''); }
    });
    var phoneInput = form.querySelector('input[name="phone"]');
    if (phoneInput) {
      phoneInput.addEventListener('input', function() {
        var v = this.value.replace(/\\D/g, '');
        if (v.length >= 6) this.value = '(' + v.slice(0,3) + ') ' + v.slice(3,6) + '-' + v.slice(6,10);
        else if (v.length >= 3) this.value = '(' + v.slice(0,3) + ') ' + v.slice(3);
        else if (v.length > 0) this.value = '(' + v;
      });
      phoneInput.addEventListener('keydown', function(e) { if (e.key === 'Backspace' && this.value.length === 4) this.value = ''; });
    }
  }
  (window.requestIdleCallback || function(cb) { setTimeout(cb, 1); })(function() {
    setTimeout(function() { if (typeof dataLayer !== 'undefined') dataLayer.push({ 'event': 'engaged_30s' }); }, 30000);
    var scroll90Fired = false;
    window.addEventListener('scroll', function() {
      if (!scroll90Fired && (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight >= 0.90) {
        scroll90Fired = true;
        if (typeof dataLayer !== 'undefined') dataLayer.push({ 'event': 'scroll_90' });
      }
    }, { passive: true });
  });
});
</script>"""

BODY_END_SCRIPTS = """<script src=\"/scripts/ial-form-tracking.js?v=5\"></script>
<script src=\"/scripts/site-nav.js?v=3\" defer></script>
<script src=\"/scripts/utm-gclid-tracking.js\"></script>
<script src=\"/scripts/privacy-choices.js\" defer></script>"""

# Standard CTA block (Spanish)
def cta_block(heading: str, body: str, primary: str = "Solicitar Revisi\u00f3n Gratuita") -> str:
    return f"""<div class=\"cta-block\">
  <h3>{heading}</h3>
  <p>{body}</p>
  <p><a href=\"/es/#case-evaluation\" class=\"btn-primary\">{primary}</a> <a href=\"tel:844-467-4335\" class=\"btn-secondary\" data-callrail-phone=\"844-467-4335\">Llame al 844-467-4335</a></p>
</div>"""

# Standard disclaimer block (Spanish)
DISCLAIMER_ES = (
    "<strong>Importante.</strong> Esta p\u00e1gina ofrece informaci\u00f3n general sobre reclamos por lesiones en California y no constituye "
    "asesor\u00eda legal para ning\u00fan caso espec\u00edfico. Insider Lawyers ofrece informaci\u00f3n y apoyo para la revisi\u00f3n de reclamos. "
    "Enviar informaci\u00f3n a trav\u00e9s de este sitio web no crea una relaci\u00f3n abogado-cliente. Si su situaci\u00f3n requiere "
    "representaci\u00f3n legal, es posible que un abogado calificado o un equipo legal se comunique con usted para revisar su caso. "
    "Los resultados anteriores no garantizan un resultado similar. Cada reclamo depende de sus propios hechos, lesiones y cobertura de seguro."
)

# ---------------------------------------------------------------------------
# Page data model
# ---------------------------------------------------------------------------

class Page:
    """Spanish page definition.

    en_path is the canonical English URL path (no trailing slash).
    es_path is the canonical Spanish URL path (with trailing slash).
    """

    def __init__(
        self,
        *,
        en_path: str,
        es_path: str,
        title: str,
        description: str,
        h1: str,
        lead: str,
        sections: list[tuple[str, str]],
        faqs: list[tuple[str, str]],
        related: list[tuple[str, str]] | None = None,
        sitemap_priority: float = 0.7,
        sitemap_changefreq: str = "monthly",
        breadcrumb_label: str | None = None,
        schema_type: str = "Article",
        extra_head: str = "",
        page_kind: str = "content",  # content | home | contact | legal
        legal_source: str | None = None,  # e.g. "/privacy-policy" for legal pages
    ) -> None:
        self.en_path = en_path.rstrip("/")
        self.es_path = es_path if es_path.endswith("/") else es_path + "/"
        self.title = title
        self.description = description
        self.h1 = h1
        self.lead = lead
        self.sections = sections
        self.faqs = faqs
        self.related = related or []
        self.sitemap_priority = sitemap_priority
        self.sitemap_changefreq = sitemap_changefreq
        self.breadcrumb_label = breadcrumb_label or h1
        self.schema_type = schema_type
        self.extra_head = extra_head
        self.page_kind = page_kind
        self.legal_source = legal_source
        # Image fields populated from IMAGE_MAP after PAGES is built.
        self.hero_image: str | None = None
        self.hero_image_alt: str = ""
        self.hero_image_width: int = 1200
        self.hero_image_height: int = 720
        self.section_image: str | None = None
        self.section_image_alt: str = ""

    @property
    def es_url(self) -> str:
        return f"{SITE}{self.es_path}"

    @property
    def en_url(self) -> str:
        return f"{SITE}{self.en_path}" if self.en_path else SITE + "/"

    @property
    def fs_dir(self) -> Path:
        rel = self.es_path.strip("/")
        return ROOT / Path(rel)

    @property
    def fs_index(self) -> Path:
        return self.fs_dir / "index.html"


# ---------------------------------------------------------------------------
# Central image map (Spanish Tier 1)
# ---------------------------------------------------------------------------
# Each entry maps an ES path -> dict with:
#   hero  : (src, alt)            # 16:10ish editorial photo near the top
#   sect  : (src, alt)            # secondary contextual photo lower on page
#
# Rules:
# - All images live locally under /images/ (no hotlinks, no base64).
# - Reuse approved English-side assets (no duplicates).
# - Skip legal/privacy pages on purpose (text-focused).
# - Skip the contact page (text + form focused).
# - Existing site-wide CSS scales images responsively (.es-hero-img, .es-inline-img).
IMAGE_MAP: dict[str, dict[str, tuple[str, str]]] = {
    # Hubs
    "/es/segunda-opinion-reclamo-lesiones-california/": {
        "hero": ("/images/insurance-adjuster-claim-valuation.jpg",
                 "Persona revisando documentos de un reclamo por lesiones con una calculadora"),
        "sect": ("/images/insurance-settlement-offer-check-hesitation.jpg",
                 "Cheque de oferta de liquidaci\u00f3n de la aseguranza sobre una mesa"),
    },
    "/es/lesiones-personales/": {
        "hero": ("/images/personal-injury-medical-waiting-room.jpg",
                 "Sala de espera m\u00e9dica donde un lesionado contin\u00faa su tratamiento"),
        "sect": ("/images/insurance-settlement-calculation-tablet.jpg",
                 "Tableta digital con c\u00e1lculo de una oferta de liquidaci\u00f3n por lesiones"),
    },
    "/es/acuerdos-liquidaciones-lesiones/": {
        "hero": ("/images/insurance-settlement-offer-check-hesitation.jpg",
                 "Persona dudando antes de aceptar una oferta de liquidaci\u00f3n de la aseguranza"),
        "sect": ("/images/legal-demand-letter-preparation.jpg",
                 "Pluma sobre una carta de demanda preparada para enviar a la aseguranza"),
    },
    "/es/lista-revision-liquidacion-lesiones-california/": {
        "hero": ("/images/insurance-settlement-calculation-tablet.jpg",
                 "Revisi\u00f3n de los n\u00fameros de una oferta de liquidaci\u00f3n en una tableta"),
        "sect": ("/images/what-to-do-after-car-accident-checklist.jpg",
                 "Lista de verificaci\u00f3n para revisar una oferta de liquidaci\u00f3n"),
    },
    "/es/carta-demanda-lesiones-personales-california/": {
        "hero": ("/images/legal-demand-letter-preparation.jpg",
                 "Carta de demanda preparada para enviar a la compa\u00f1\u00eda de seguros"),
        "sect": ("/images/demand-letter-negotiation-meeting.jpg",
                 "Reuni\u00f3n de negociaci\u00f3n para discutir la carta de demanda"),
    },
    "/es/segunda-opinion-caso-lesiones-california/": {
        "hero": ("/images/proving-claim-value-analysis.jpg",
                 "An\u00e1lisis del valor de un caso de lesiones personales en California"),
        "sect": ("/images/insurance-claim-rates-review.jpg",
                 "Revisi\u00f3n de documentos de una p\u00f3liza de seguro y reclamo"),
    },
    # Accident hubs / types
    "/es/accidentes-vehiculos/": {
        "hero": ("/images/california-car-accident-lawyer-highway.jpg",
                 "Carretera de California donde ocurren accidentes de veh\u00edculos"),
        "sect": ("/images/evidence-preservation-accident-photos.jpg",
                 "Fotos del lugar de un accidente para preservar evidencia"),
    },
    "/es/abogado-accidentes-auto-los-angeles/": {
        "hero": ("/images/car-accident-lawyer-los-angeles-downtown.jpg",
                 "Centro de Los \u00c1ngeles donde ocurren accidentes de auto diariamente"),
        "sect": ("/images/los-angeles-car-crash-emergency-lights.jpg",
                 "Luces de emergencia en la escena de un accidente en Los \u00c1ngeles"),
    },
    "/es/abogado-accidentes-auto-california/": {
        "hero": ("/images/california-car-accident-lawyer-highway.jpg",
                 "Carretera de California al atardecer despu\u00e9s de un accidente de auto"),
        "sect": ("/images/insurance-adjuster-claim-valuation-calculator.jpg",
                 "Ajustador de seguros calculando el valor de un reclamo por accidente"),
    },
    "/es/accidente-auto-grave/": {
        "hero": ("/images/major-car-accident-traffic-jam.jpg",
                 "Tr\u00e1fico detenido en la escena de un accidente de auto grave"),
        "sect": ("/images/los-angeles-catastrophic-injury-crutches.jpg",
                 "Persona usando muletas durante la recuperaci\u00f3n de una lesi\u00f3n grave"),
    },
    "/es/abogado-choque-por-alcance-los-angeles/": {
        "hero": ("/images/rear-end-accident-bumper-damage.jpg",
                 "Da\u00f1o en el par-choques despu\u00e9s de un choque por alcance en Los \u00c1ngeles"),
        "sect": ("/images/delayed-pain-after-car-accident.jpg",
                 "Dolor de cuello que aparece d\u00edas despu\u00e9s de un choque por alcance"),
    },
    "/es/abogado-choque-lateral-los-angeles/": {
        "hero": ("/images/t-bone-accident-intersection-scene.jpg",
                 "Intersecci\u00f3n donde ocurri\u00f3 un choque lateral tipo T-Bone en Los \u00c1ngeles"),
        "sect": ("/images/los-angeles-car-crash-emergency-lights.jpg",
                 "Luces de emergencia en la escena de un choque lateral"),
    },
    "/es/valor-reclamo-choque-lateral-california/": {
        "hero": ("/images/t-bone-accident-intersection-scene.jpg",
                 "Intersecci\u00f3n con un choque lateral en California"),
        "sect": ("/images/insurance-settlement-calculation-tablet.jpg",
                 "C\u00e1lculo del valor de un reclamo por choque lateral en una tableta"),
    },
    "/es/abogado-accidente-fuga-los-angeles/": {
        "hero": ("/images/hit-and-run-accident-lawyer-night.jpg",
                 "Calle de Los \u00c1ngeles de noche donde ocurri\u00f3 un accidente con fuga"),
        "sect": ("/images/hit-and-run-accident-evidence-glass.jpg",
                 "Vidrios rotos en la calle como evidencia de un accidente con fuga"),
    },
    "/es/abogado-accidente-uber-lyft-los-angeles/": {
        "hero": ("/images/uber-lyft-accident-scene-night.jpg",
                 "Escena nocturna de un accidente con un veh\u00edculo de Uber o Lyft en Los \u00c1ngeles"),
        "sect": ("/images/uber-accident-lawyer-app-file.jpg",
                 "Recibo de viaje de rideshare usado como evidencia en un reclamo"),
    },
    "/es/abogado-accidente-conductor-sin-seguro-los-angeles/": {
        "hero": ("/images/uninsured-driver-accident-frustration.jpg",
                 "Conductor frustrado tras un choque con un conductor sin seguro"),
        "sect": ("/images/uninsured-motorist-coverage-policy.jpg",
                 "P\u00f3liza de cobertura UM/UIM para conductores sin seguro"),
    },
    "/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/": {
        "hero": ("/images/electric-scooter-accident-lawyer-santa-monica.jpg",
                 "Scooter el\u00e9ctrico en una acera de Santa Monica despu\u00e9s de un accidente"),
        "sect": ("/images/scooter-accident-liability-hazard.jpg",
                 "Peligro en la calle que puede causar un accidente de scooter o bici el\u00e9ctrica"),
    },
    "/es/recuperar-scooter-bicicleta-electrica-danada/": {
        "hero": ("/images/recover-destroyed-scooter-repair.jpg",
                 "Scooter el\u00e9ctrico da\u00f1ado en reparaci\u00f3n despu\u00e9s de un accidente"),
        "sect": ("/images/insurance-claim-rates-review.jpg",
                 "Revisi\u00f3n de la cobertura de seguro para da\u00f1os al scooter o bicicleta"),
    },
    "/es/abogado-accidente-peaton-los-angeles/": {
        "hero": ("/images/los-angeles-pedestrian-accident-crosswalk.jpg",
                 "Cruce peatonal en Los \u00c1ngeles donde ocurren accidentes de peat\u00f3n"),
        "sect": ("/images/pedestrian-right-of-way-sign.jpg",
                 "Se\u00f1al de paso peatonal mostrando el derecho de paso del peat\u00f3n"),
    },
    "/es/abogado-accidente-estacionamiento-los-angeles/": {
        "hero": ("/images/parking-lot-accident-lawyer-dusk.jpg",
                 "Estacionamiento de Los \u00c1ngeles al atardecer donde ocurren accidentes"),
        "sect": ("/images/evidence-preservation-accident-photos.jpg",
                 "Fotos del estacionamiento para preservar evidencia despu\u00e9s del accidente"),
    },
    "/es/guia-reclamo-accidente-estacionamiento-california/": {
        "hero": ("/images/parking-lot-accident-lawyer-dusk.jpg",
                 "Estacionamiento en California, escenario com\u00fan de accidentes con baja velocidad"),
        "sect": ("/images/what-to-do-after-car-accident-checklist.jpg",
                 "Lista de pasos a seguir despu\u00e9s de un accidente en estacionamiento"),
    },
    "/es/responsabilidad-de-propiedad/": {
        "hero": ("/images/los-angeles-premises-liability-wet-floor.jpg",
                 "Piso mojado en un negocio sin se\u00f1al de advertencia para clientes"),
        "sect": ("/images/los-angeles-slip-and-fall-sidewalk.jpg",
                 "Acera deteriorada en Los \u00c1ngeles donde ocurre un resbal\u00f3n y ca\u00edda"),
    },
    "/es/abogado-negligencia-asilo-ancianos-los-angeles/": {
        "hero": ("/images/nursing-home/caregiver-elderly-resident.png",
                 "Cuidadora ayudando a una residente adulta mayor en un asilo de ancianos"),
        "sect": ("/images/nursing-home/family-with-elderly-wheelchair.png",
                 "Familiares acompa\u00f1ando a un adulto mayor en silla de ruedas"),
    },
    "/es/ulceras-presion-negligencia-asilo-ancianos/": {
        "hero": ("/images/nursing-home/nurse-documenting-wound-care.png",
                 "Enfermera documentando el cuidado de una herida en un asilo"),
        "sect": ("/images/nursing-home/family-holding-hands-patient.png",
                 "Familiar tomando la mano de un paciente adulto mayor"),
    },
    # Lesiones-personales subpages (legacy slugs)
    "/es/lesiones-personales/accidentes-auto/": {
        "hero": ("/images/personal-injury-auto-accidents-blur.jpg",
                 "Tr\u00e1fico desenfocado de California en una escena de accidente de auto"),
        "sect": ("/images/california-car-accident-lawyer-highway.jpg",
                 "Carretera de California al atardecer"),
    },
    "/es/lesiones-personales/accidentes-camion/": {
        "hero": ("/images/personal-injury-truck-accidents-mirror-view.jpg",
                 "Vista del espejo retrovisor de un cami\u00f3n comercial en California"),
        "sect": ("/images/truck-accident-evidence-skid-marks.jpg",
                 "Marcas de frenado como evidencia de un accidente con cami\u00f3n"),
    },
    "/es/lesiones-personales/lesion-cerebral/": {
        "hero": ("/images/personal-injury-brain-injuries-illustration.jpg",
                 "Ilustraci\u00f3n m\u00e9dica de una lesi\u00f3n cerebral despu\u00e9s de un accidente"),
        "sect": ("/images/brain-injury-mri-scan-review.jpg",
                 "Revisi\u00f3n m\u00e9dica de una resonancia magn\u00e9tica del cerebro"),
    },
    "/es/lesiones-personales/lesiones-catastroficas/": {
        "hero": ("/images/personal-injury-catastrophic-injuries-hospital-bed.jpg",
                 "Cama de hospital donde un paciente se recupera de lesiones catastr\u00f3ficas"),
        "sect": ("/images/los-angeles-catastrophic-injury-crutches.jpg",
                 "Muletas y bastones usados durante la recuperaci\u00f3n de una lesi\u00f3n grave"),
    },
    "/es/lesiones-personales/lesiones-columna/": {
        "hero": ("/images/personal-injury-spine-injuries-xray.jpg",
                 "Radiograf\u00eda de la columna que muestra una lesi\u00f3n por accidente"),
        "sect": ("/images/herniated-disc-spine-model-doctor.jpg",
                 "M\u00e9dico explicando una hernia de disco con un modelo de columna"),
    },
    "/es/lesiones-personales/muerte-injusta/": {
        "hero": ("/images/personal-injury-wrongful-death-memorial.jpg",
                 "Memorial respetuoso para una v\u00edctima de muerte injusta"),
        "sect": ("/images/los-angeles-wrongful-death-legal-desk.jpg",
                 "Escritorio legal con documentos de un reclamo por muerte injusta"),
    },
    "/es/lesiones-personales/resbalon-caida/": {
        "hero": ("/images/personal-injury-slip-and-fall-wet-floor.jpg",
                 "Piso mojado en una tienda sin se\u00f1al de advertencia"),
        "sect": ("/images/los-angeles-slip-and-fall-sidewalk.jpg",
                 "Acera deteriorada en Los \u00c1ngeles, causa com\u00fan de ca\u00eddas"),
    },
}


def apply_image_map() -> None:
    """Populate Page image fields from IMAGE_MAP. Idempotent."""
    for p in PAGES:
        m = IMAGE_MAP.get(p.es_path)
        if not m:
            continue
        hero = m.get("hero")
        if hero:
            p.hero_image, p.hero_image_alt = hero
        sect = m.get("sect")
        if sect:
            p.section_image, p.section_image_alt = sect


# ---------------------------------------------------------------------------
# Content definitions - Tier 1
# ---------------------------------------------------------------------------

# NOTE: All Spanish copy below is handwritten for natural Southern California
# Spanish-speaking users. Tone is helpful, calm, direct - per the briefing.

PAGES: list[Page] = []


def _add(p: Page) -> None:
    PAGES.append(p)


# 1. HOMEPAGE (built separately via build_home() - included in PAGES so we
# can also produce hreflang on the English homepage and a sitemap entry.)
_add(Page(
    en_path="/",
    es_path="/es/",
    title="Recurso de reclamos por lesiones en California | Insider Lawyers en Espa\u00f1ol",
    description=(
        "Recurso en espa\u00f1ol para personas lesionadas en California. Revisi\u00f3n gratuita del reclamo, "
        "segunda opini\u00f3n del caso y ayuda para entender ofertas de la aseguranza antes de firmar."
    ),
    h1="Entienda su reclamo por lesiones antes de tomar una decisi\u00f3n",
    lead=(
        "Si sufri\u00f3 un accidente en California, puede ser dif\u00edcil saber si la aseguranza est\u00e1 tratando su "
        "reclamo de manera justa. Insider Lawyers le ayuda a entender sus opciones, revisar una oferta de "
        "liquidaci\u00f3n y pedir una segunda opini\u00f3n antes de firmar o tomar el siguiente paso."
    ),
    sections=[],  # rendered separately
    faqs=[],
    sitemap_priority=1.0,
    sitemap_changefreq="weekly",
    schema_type="WebSite",
    page_kind="home",
))


# 2. /es/segunda-opinion-reclamo-lesiones-california/
_add(Page(
    en_path="/california-injury-claim-second-opinion",
    es_path="/es/segunda-opinion-reclamo-lesiones-california/",
    title="Segunda opini\u00f3n para reclamos por lesiones en California | Insider Lawyers",
    description=(
        "\u00bfSu caso de lesiones est\u00e1 estancado o le ofrecieron menos de lo esperado? Pida una segunda opini\u00f3n "
        "gratuita sobre su reclamo en California antes de firmar o aceptar."
    ),
    h1="Segunda opini\u00f3n para reclamos por lesiones en California",
    lead=(
        "Una segunda opini\u00f3n es una revisi\u00f3n neutral de su reclamo por lesiones: los hechos, las lesiones, la "
        "cobertura de seguro disponible y la oferta actual. No tiene que despedir a su abogado para pedirla y "
        "tampoco tiene compromiso de contratar a nadie."
    ),
    sections=[
        ("\u00bfQu\u00e9 es una segunda opini\u00f3n del reclamo?",
         "<p>Es una revisi\u00f3n imparcial de d\u00f3nde est\u00e1 hoy su caso: si la oferta es razonable, si los "
         "gastos m\u00e9dicos y la p\u00e9rdida de ingresos est\u00e1n bien documentados, si hay otras p\u00f3lizas de "
         "seguro que no se han identificado y si la l\u00ednea de tiempo tiene sentido.</p>"),
        ("Cu\u00e1ndo conviene pedir una segunda opini\u00f3n",
         "<ul>"
         "<li>La aseguranza le est\u00e1 presionando para aceptar una oferta r\u00e1pida.</li>"
         "<li>Su abogado actual no le est\u00e1 respondiendo o no le explica c\u00f3mo se calcul\u00f3 el valor del caso.</li>"
         "<li>Le pidieron firmar un <em>release</em> (liberaci\u00f3n) y no est\u00e1 seguro de qu\u00e9 est\u00e1 cediendo.</li>"
         "<li>Su caso lleva meses sin movimiento.</li>"
         "<li>Le dijeron que su lesi\u00f3n es \u201cmenor\u201d cuando todav\u00eda tiene s\u00edntomas o tratamiento pendiente.</li>"
         "</ul>"),
        ("Qu\u00e9 cubre la revisi\u00f3n",
         "<ul>"
         "<li>Hechos del accidente y disputas de culpa.</li>"
         "<li>Gastos m\u00e9dicos pasados y futuros, incluido tratamiento pendiente.</li>"
         "<li>P\u00e9rdida de ingresos y capacidad para trabajar.</li>"
         "<li>Cobertura disponible: aseguranza del responsable, su propia UM/UIM, paraguas, comercial.</li>"
         "<li>Liens m\u00e9dicos, Medi-Cal, Medicare o liens hospitalarios.</li>"
         "<li>Dolor y sufrimiento.</li>"
         "</ul>"),
        ("Confidencialidad",
         "<p>Lo que comparta se trata como confidencial. Si ya tiene un abogado, pedir una segunda opini\u00f3n "
         "no requiere que se lo diga \u2014 aunque muchas personas terminan teniendo una conversaci\u00f3n m\u00e1s clara con "
         "su abogado actual despu\u00e9s de la revisi\u00f3n.</p>"),
        ("Qu\u00e9 traer a la revisi\u00f3n",
         "<ul>"
         "<li>Reporte del accidente o n\u00famero de reporte policial.</li>"
         "<li>Cartas o correos de la aseguranza.</li>"
         "<li>Cualquier oferta por escrito.</li>"
         "<li>Facturas o estados m\u00e9dicos que tenga.</li>"
         "<li>Si tiene abogado: el contrato y comunicaciones recientes.</li>"
         "</ul>"
         "<p>Si no tiene todos los documentos, igual puede llamar. La revisi\u00f3n se ajusta a lo que tenga disponible.</p>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto cuesta la segunda opini\u00f3n?",
         "La revisi\u00f3n inicial es gratuita. No tiene obligaci\u00f3n de contratar a nadie."),
        ("\u00bfTengo que despedir a mi abogado actual?",
         "No. La segunda opini\u00f3n es una revisi\u00f3n separada. Muchas personas se quedan con su abogado actual despu\u00e9s de aclarar sus dudas."),
        ("\u00bfQu\u00e9 pasa si la oferta de la aseguranza ya est\u00e1 sobre la mesa?",
         "Conviene revisar la oferta <em>antes</em> de firmar. Una vez firmado el <em>release</em>, el reclamo generalmente se cierra."),
        ("\u00bfMe van a contactar abogados de afuera si pido la revisi\u00f3n?",
         "Solo si su caso parece necesitar representaci\u00f3n legal. Aun en ese caso, usted decide si quiere avanzar."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed. La revisi\u00f3n puede hacerse completamente en espa\u00f1ol."),
    ],
    related=[
        ("Antes de firmar una oferta: lista de revisi\u00f3n", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Gu\u00eda de la carta de demanda", "/es/carta-demanda-lesiones-personales-california/"),
        ("Gu\u00eda de reclamos por lesiones en California", "/es/lesiones-personales/"),
        ("Segunda opini\u00f3n del caso", "/es/segunda-opinion-caso-lesiones-california/"),
        ("Gu\u00eda de liquidaciones en California", "/es/acuerdos-liquidaciones-lesiones/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="weekly",
    breadcrumb_label="Segunda Opini\u00f3n",
))

# 3. /es/contacto/
_add(Page(
    en_path="/contact",
    es_path="/es/contacto/",
    title="Contacto | Insider Lawyers en Espa\u00f1ol",
    description=(
        "Comun\u00edquese con Insider Lawyers para una revisi\u00f3n gratuita de su reclamo por lesiones en California. "
        "Tel\u00e9fono, formulario y horarios."
    ),
    h1="Cont\u00e1ctenos en espa\u00f1ol",
    lead=(
        "Llame al 844-467-4335 o env\u00ede el formulario para una revisi\u00f3n gratuita de su reclamo. Nuestro equipo "
        "habla espa\u00f1ol y le ayudar\u00e1 a entender qu\u00e9 hacer despu\u00e9s."
    ),
    sections=[
        ("C\u00f3mo comunicarse",
         "<ul>"
         "<li><strong>Tel\u00e9fono:</strong> <a href=\"tel:844-467-4335\" class=\"phone-link\" data-callrail-phone=\"844-467-4335\">844-467-4335</a> (24/7).</li>"
         "<li><strong>Formulario:</strong> use el formulario de <a href=\"/es/#case-evaluation\">revisi\u00f3n gratuita</a> en la p\u00e1gina principal.</li>"
         "<li><strong>Direcci\u00f3n:</strong> 3435 Wilshire Blvd Suite 1620, Los Angeles, CA 90010.</li>"
         "</ul>"),
        ("Cu\u00e1ndo usar cada canal",
         "<ul>"
         "<li><strong>Llame</strong> si su situaci\u00f3n es urgente: la aseguranza le est\u00e1 presionando, le pidieron firmar algo hoy, o un plazo legal est\u00e1 cerca.</li>"
         "<li><strong>Use el formulario</strong> si prefiere escribir y que el equipo le devuelva la llamada.</li>"
         "<li><strong>Visita en persona</strong> es por cita previa.</li>"
         "</ul>"),
        ("Qu\u00e9 sucede despu\u00e9s",
         "<p>Cuando recibimos su informaci\u00f3n, una persona del equipo revisa lo b\u00e1sico del caso y le devuelve "
         "la llamada para hablar sobre el accidente, la lesi\u00f3n, la cobertura de seguro y las opciones. "
         "La revisi\u00f3n inicial es gratuita y no crea relaci\u00f3n abogado-cliente.</p>"),
    ],
    faqs=[
        ("\u00bfEs gratis llamar?", "S\u00ed. La revisi\u00f3n inicial del reclamo es gratuita."),
        ("\u00bfPuedo escribir si no quiero hablar todav\u00eda?", "S\u00ed. Use el formulario o env\u00ede un texto al 844-467-4335 y el equipo le responder\u00e1."),
        ("\u00bfQu\u00e9 horas atienden?", "El tel\u00e9fono est\u00e1 disponible 24/7. La revisi\u00f3n detallada generalmente sucede dentro de un d\u00eda h\u00e1bil."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed. Toda la revisi\u00f3n puede hacerse en espa\u00f1ol."),
    ],
    related=[
        ("Solicite una revisi\u00f3n gratuita", "/es/#case-evaluation"),
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.6,
    sitemap_changefreq="monthly",
    breadcrumb_label="Contacto",
    page_kind="contact",
))


# 4. /es/lesiones-personales/
_add(Page(
    en_path="/personal-injury",
    es_path="/es/lesiones-personales/",
    title="Reclamos por lesiones personales en California | Gu\u00eda en espa\u00f1ol",
    description=(
        "Gu\u00eda en espa\u00f1ol sobre c\u00f3mo funcionan los reclamos por lesiones personales en California: c\u00e1lculo de "
        "valor, plazos, seguros, ofertas y cu\u00e1ndo pedir una revisi\u00f3n del caso."
    ),
    h1="Reclamos por lesiones personales en California",
    lead=(
        "Si sufri\u00f3 un accidente en California, usted tiene un reclamo por lesiones personales, haya contratado "
        "o no a un abogado. Esta gu\u00eda explica c\u00f3mo funcionan los reclamos, c\u00f3mo se calcula el valor, qu\u00e9 plazos "
        "aplican y cu\u00e1ndo conviene pedir una revisi\u00f3n gratuita antes de aceptar una oferta o firmar un release."
    ),
    sections=[
        ("Qu\u00e9 es un reclamo por lesiones personales",
         "<p>Es una solicitud de compensaci\u00f3n a la persona o aseguranza responsable de su lesi\u00f3n. La mayor\u00eda "
         "de los reclamos en California se presentan contra una compa\u00f1\u00eda de seguros: la aseguranza de auto del "
         "conductor culpable, la aseguranza comercial de un negocio, una p\u00f3liza de propiedad o su propia cobertura "
         "de motorista sin seguro (UM/UIM) cuando el otro no tiene suficiente.</p>"
         "<p>El reclamo no se convierte en demanda judicial a menos que alguien presente el caso en la corte. La "
         "mayor\u00eda se resuelve antes, pero la posibilidad real de demandar es lo que da peso al reclamo.</p>"),
        ("C\u00f3mo se mueve un reclamo paso a paso",
         "<ul>"
         "<li><strong>Tratamiento m\u00e9dico.</strong> Comienza el tratamiento y la documentaci\u00f3n.</li>"
         "<li><strong>Investigaci\u00f3n.</strong> Reporte policial, fotos, testigos, da\u00f1os al veh\u00edculo.</li>"
         "<li><strong>Aviso a las aseguranzas.</strong> Carta de representaci\u00f3n si hay abogado, apertura del reclamo.</li>"
         "<li><strong>Estabilizaci\u00f3n del tratamiento.</strong> La mayor\u00eda de las demandas esperan hasta que el tratamiento se estabilice.</li>"
         "<li><strong>Carta de demanda.</strong> <a href=\"/es/carta-demanda-lesiones-personales-california/\">Vea la gu\u00eda de la carta de demanda</a>.</li>"
         "<li><strong>Negociaci\u00f3n.</strong> La aseguranza responde con oferta, negaci\u00f3n o reserva de derechos.</li>"
         "<li><strong>Resoluci\u00f3n o demanda.</strong> Si se llega a un acuerdo justo, se firma; si no, se puede demandar.</li>"
         "<li><strong>Liens y desembolso.</strong> Se pagan los honorarios, gastos del caso, liens m\u00e9dicos y el resto va al cliente.</li>"
         "</ul>"),
        ("Qu\u00e9 da\u00f1os se pueden reclamar",
         "<ul>"
         "<li>Gastos m\u00e9dicos pasados y futuros.</li>"
         "<li>P\u00e9rdida de ingresos y capacidad de trabajar.</li>"
         "<li>Gastos de bolsillo (transporte, equipo m\u00e9dico, ayuda en casa).</li>"
         "<li>Da\u00f1o a la propiedad: veh\u00edculo, bicicleta, scooter, casco, tel\u00e9fono.</li>"
         "<li>Dolor y sufrimiento.</li>"
         "<li>Da\u00f1os por p\u00e9rdida de consorcio en algunos casos.</li>"
         "<li>Da\u00f1os por muerte injusta para la familia sobreviviente.</li>"
         "</ul>"),
        ("C\u00f3mo se calcula el valor del reclamo",
         "<p>No hay una f\u00f3rmula oficial. En la pr\u00e1ctica, el valor se construye a partir de:</p>"
         "<ul>"
         "<li>Qu\u00e9 tan clara est\u00e1 la culpa.</li>"
         "<li>Severidad y permanencia de la lesi\u00f3n.</li>"
         "<li>Documentaci\u00f3n m\u00e9dica.</li>"
         "<li>Impacto en sus ingresos.</li>"
         "<li>Cobertura de seguro disponible (l\u00edmites de la p\u00f3liza).</li>"
         "<li>Condiciones preexistentes (s\u00ed se pueden reclamar las agravaciones).</li>"
         "<li>Credibilidad y consistencia del relato.</li>"
         "</ul>"),
        ("Culpa compartida en California",
         "<p>California usa <em>pura culpa comparativa</em>. Si usted tiene parte de culpa, su recuperaci\u00f3n se reduce "
         "en ese porcentaje pero no se elimina. Si tiene 30% de culpa, puede recuperar el 70% de sus da\u00f1os.</p>"),
        ("Plazos en California",
         "<ul>"
         "<li><strong>2 a\u00f1os</strong> en general para presentar el reclamo desde la fecha del accidente.</li>"
         "<li><strong>6 meses</strong> para reclamos contra entidades p\u00fablicas (ciudades, condados, transporte p\u00fablico).</li>"
         "<li><strong>Menores de edad</strong> y casos de descubrimiento tard\u00edo pueden tener m\u00e1s tiempo, pero no siempre.</li>"
         "</ul>"
         "<p>Si un plazo est\u00e1 cerca, no espere para pedir una revisi\u00f3n.</p>"),
        ("Capas de cobertura de seguro",
         "<ul>"
         "<li><strong>Aseguranza del conductor culpable.</strong></li>"
         "<li><strong>P\u00f3lizas comerciales</strong> si manejaba por trabajo (delivery, rideshare, mandado de trabajo).</li>"
         "<li><strong>P\u00f3lizas paraguas</strong> que aumentan los l\u00edmites principales.</li>"
         "<li><strong>Su UM/UIM</strong> cuando el otro no tiene o no tiene suficiente seguro.</li>"
         "<li><strong>Med-Pay</strong> en su propia p\u00f3liza, sin importar la culpa.</li>"
         "<li><strong>Aseguranza de propiedad o comercial</strong> para resbalones y ca\u00eddas.</li>"
         "</ul>"),
        ("T\u00e1cticas comunes de la aseguranza",
         "<ul>"
         "<li>Ofertas r\u00e1pidas y bajas antes de que se vea la lesi\u00f3n completa.</li>"
         "<li>Declaraciones grabadas que despu\u00e9s se usan en su contra.</li>"
         "<li>Etiqueta de \u201clesi\u00f3n menor\u201d o \u201cimpacto bajo\u201d sin importar las im\u00e1genes m\u00e9dicas.</li>"
         "<li>Argumentos de \u201cgap de tratamiento\u201d aunque el gap tenga una raz\u00f3n.</li>"
         "<li>Cambio silencioso de culpa al claimante.</li>"
         "<li>Releases con lenguaje amplio que va m\u00e1s all\u00e1 de la oferta.</li>"
         "</ul>"),
        ("Cu\u00e1ndo conviene contratar a un abogado",
         "<p>No es obligatorio contratar abogado para presentar un reclamo. La pregunta es si la ayuda legal "
         "vale el honorario por contingencia. Suele tener sentido cuando hay lesiones serias, disputa de culpa, "
         "varias capas de seguro, liens, demandados comerciales o cuando la aseguranza no est\u00e1 moviendo la oferta.</p>"),
        ("Revisi\u00f3n gratuita y segunda opini\u00f3n",
         "<p>Una revisi\u00f3n gratuita es una mirada neutral a su caso: hechos, lesi\u00f3n, oferta, cobertura, liens y el "
         "siguiente paso realista. Ayuda a decidir. No empuja a firmar nada.</p>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto tiempo tengo para presentar un reclamo por lesiones en California?",
         "Generalmente 2 a\u00f1os desde la fecha del accidente. Para reclamos contra entidades p\u00fablicas, el plazo es de 6 meses. Casos de menores o de descubrimiento tard\u00edo pueden tener reglas distintas."),
        ("\u00bfC\u00f3mo se calcula el valor del reclamo?",
         "Se construye a partir de gastos m\u00e9dicos, p\u00e9rdida de ingresos, da\u00f1os a la propiedad y dolor y sufrimiento, ajustado por la culpa y la cobertura disponible."),
        ("\u00bfQu\u00e9 pasa si tengo parte de culpa?",
         "California usa culpa comparativa pura. Su recuperaci\u00f3n se reduce por su porcentaje de culpa, pero no se elimina."),
        ("\u00bfTengo que aceptar la primera oferta?",
         "Usualmente conviene revisar la oferta primero. Las primeras ofertas suelen ser bajas y no incluir tratamiento futuro o p\u00e9rdida de ingresos."),
        ("\u00bfNecesito abogado obligatoriamente?",
         "No. Puede negociar directamente con la aseguranza. La pregunta es si un abogado agrega suficiente valor en su caso."),
        ("\u00bfPuedo pedir una segunda opini\u00f3n si ya tengo abogado?",
         "S\u00ed. Una segunda opini\u00f3n no requiere despedir a su abogado actual."),
    ],
    related=[
        ("Gu\u00eda de liquidaciones en California", "/es/acuerdos-liquidaciones-lesiones/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Carta de demanda en California", "/es/carta-demanda-lesiones-personales-california/"),
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Resbal\u00f3n y ca\u00edda", "/es/lesiones-personales/resbalon-caida/"),
    ],
    sitemap_priority=0.95,
    sitemap_changefreq="weekly",
    breadcrumb_label="Lesiones Personales",
))

# 5. /es/acuerdos-liquidaciones-lesiones/
_add(Page(
    en_path="/settlements",
    es_path="/es/acuerdos-liquidaciones-lesiones/",
    title="Gu\u00eda de liquidaciones por lesiones en California | Antes de firmar",
    description=(
        "C\u00f3mo funcionan las liquidaciones por lesiones en California: qu\u00e9 cubren, cu\u00e1ndo conviene firmar, liens, "
        "releases y c\u00f3mo se desembolsa el dinero."
    ),
    h1="Gu\u00eda de liquidaciones por lesiones en California",
    lead=(
        "Una liquidaci\u00f3n (settlement) cierra su reclamo a cambio de un pago. Antes de firmar conviene revisar "
        "si el monto cubre realmente sus gastos m\u00e9dicos, p\u00e9rdida de ingresos, tratamiento futuro y el impacto "
        "real del accidente. Una vez firmado el release, el reclamo generalmente se cierra para siempre."
    ),
    sections=[
        ("Qu\u00e9 suele cubrir una liquidaci\u00f3n",
         "<ul>"
         "<li>Gastos m\u00e9dicos pasados y futuros.</li>"
         "<li>P\u00e9rdida de ingresos y capacidad para trabajar.</li>"
         "<li>Da\u00f1o a la propiedad.</li>"
         "<li>Dolor y sufrimiento.</li>"
         "<li>Gastos de bolsillo relacionados.</li>"
         "</ul>"),
        ("Cu\u00e1ndo suele firmarse",
         "<p>La mayor\u00eda de las liquidaciones se firman cuando el tratamiento m\u00e9dico est\u00e1 estable y se conoce el "
         "alcance de la lesi\u00f3n. Firmar antes puede dejar fuera tratamiento futuro o complicaciones que aparezcan despu\u00e9s.</p>"),
        ("Qu\u00e9 revisar antes de aceptar",
         "<ul>"
         "<li>\u00bfEst\u00e1n incluidos todos los gastos m\u00e9dicos?</li>"
         "<li>\u00bfSe tom\u00f3 en cuenta el tratamiento futuro probable?</li>"
         "<li>\u00bfEst\u00e1 incluida la p\u00e9rdida de ingresos y capacidad para trabajar?</li>"
         "<li>\u00bfHay liens m\u00e9dicos, Medi-Cal o Medicare que negociar?</li>"
         "<li>\u00bfEl release est\u00e1 limitado a este reclamo o es amplio?</li>"
         "<li>\u00bfSe valoraron correctamente el dolor y sufrimiento?</li>"
         "</ul>"
         "<p>Para una revisi\u00f3n estructurada vea la "
         "<a href=\"/es/lista-revision-liquidacion-lesiones-california/\">lista para revisar el acuerdo</a>.</p>"),
        ("Liens m\u00e9dicos y subrogaci\u00f3n",
         "<p>Hospitales, planes de salud privados, Medi-Cal, Medicare y proveedores con lien tienen derecho a "
         "recuperar parte de la liquidaci\u00f3n. Estos montos casi siempre se pueden negociar antes del desembolso, "
         "pero deben identificarse primero. Si un lien no se paga correctamente, el cliente puede quedar responsable.</p>"),
        ("Qu\u00e9 hace exactamente un release",
         "<p>Un release es un documento que renuncia al derecho de reclamar m\u00e1s sobre el accidente. Una vez "
         "firmado, generalmente no se puede reabrir el reclamo aunque aparezca una lesi\u00f3n nueva. Por eso conviene "
         "leerlo con cuidado y, si tiene dudas, pedir una "
         "<a href=\"/es/segunda-opinion-reclamo-lesiones-california/\">segunda opini\u00f3n antes de firmar</a>.</p>"),
        ("Pago \u00fanico vs. estructura",
         "<p>La mayor\u00eda de las liquidaciones se pagan en una sola suma. En casos grandes, a veces se ofrece un "
         "pago estructurado (pagos peri\u00f3dicos en el tiempo) que puede tener ventajas fiscales y de planificaci\u00f3n.</p>"),
        ("C\u00f3mo se desembolsa el dinero",
         "<ul>"
         "<li>La aseguranza emite un cheque al abogado (o al cliente si no hay abogado).</li>"
         "<li>Se deducen honorarios y gastos del caso si hay representaci\u00f3n.</li>"
         "<li>Se pagan liens m\u00e9dicos.</li>"
         "<li>El cliente recibe el neto.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto tarda recibir el dinero despu\u00e9s de firmar?",
         "Generalmente entre 30 y 60 d\u00edas, dependiendo de la aseguranza, liens pendientes y procesamiento."),
        ("\u00bfPuedo cambiar de opini\u00f3n despu\u00e9s de firmar?",
         "Generalmente no. El release cierra el reclamo. Por eso es importante revisar antes de firmar."),
        ("\u00bfTengo que pagar impuestos sobre la liquidaci\u00f3n?",
         "La parte por lesiones f\u00edsicas usualmente no es ingreso gravable a nivel federal. Otros componentes pueden tener tratamiento distinto. Conviene consultar a un contador en casos grandes."),
        ("\u00bfQu\u00e9 pasa si descubro despu\u00e9s que necesito m\u00e1s tratamiento?",
         "Si el release ya est\u00e1 firmado, generalmente no se puede reabrir. Por eso conviene esperar a que el tratamiento est\u00e9 estable o que se proyecte correctamente."),
        ("\u00bfPuedo negociar los liens m\u00e9dicos?",
         "Casi siempre s\u00ed. La negociaci\u00f3n de liens puede aumentar significativamente lo que llega a su bolsillo."),
    ],
    related=[
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Carta de demanda en California", "/es/carta-demanda-lesiones-personales-california/"),
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="weekly",
    breadcrumb_label="Acuerdos y Liquidaciones",
))


# 6. /es/segunda-opinion-caso-lesiones-california/
_add(Page(
    en_path="/second-opinion-personal-injury-claim-california",
    es_path="/es/segunda-opinion-caso-lesiones-california/",
    title="Segunda opini\u00f3n para casos de lesiones en California | Antes de aceptar",
    description=(
        "Cu\u00e1ndo y c\u00f3mo pedir una segunda opini\u00f3n sobre su caso de lesiones en California. Qu\u00e9 cubre, qu\u00e9 traer "
        "y c\u00f3mo decidir sin presi\u00f3n."
    ),
    h1="Segunda opini\u00f3n para casos de lesiones en California",
    lead=(
        "Si ya tiene un abogado pero siente que su caso est\u00e1 estancado, que no recibe respuestas claras o que "
        "le est\u00e1n presionando para aceptar una oferta, puede pedir una segunda opini\u00f3n antes de tomar una decisi\u00f3n. "
        "Es una mirada neutral, no requiere despedir a nadie y la revisi\u00f3n inicial es gratuita."
    ),
    sections=[
        ("Qu\u00e9 cubre la segunda opini\u00f3n",
         "<ul>"
         "<li>Estado actual del caso y la l\u00ednea de tiempo.</li>"
         "<li>Oferta de la aseguranza versus da\u00f1os documentados.</li>"
         "<li>Cobertura de seguro identificada y faltante.</li>"
         "<li>Plazos legales (statute of limitations) y avisos a entidades p\u00fablicas.</li>"
         "<li>Liens y posibles deducciones del neto al cliente.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedirla",
         "<ul>"
         "<li>Cuando el caso lleva meses sin movimiento.</li>"
         "<li>Cuando no le explican c\u00f3mo se calcul\u00f3 el valor.</li>"
         "<li>Cuando le piden firmar un release sin haber visto la oferta por escrito.</li>"
         "<li>Cuando el abogado actual no responde llamadas o correos.</li>"
         "<li>Cuando la aseguranza dice que la lesi\u00f3n es \u201cmenor\u201d sin haberla evaluado completamente.</li>"
         "</ul>"),
        ("Segunda opini\u00f3n vs. cambiar de abogado",
         "<p>No son lo mismo. La segunda opini\u00f3n es una revisi\u00f3n separada. Cambiar de abogado es una decisi\u00f3n "
         "aparte que solo conviene tomar si despu\u00e9s de la revisi\u00f3n hay razones concretas. En California, "
         "los honorarios totales no aumentan por cambiar de abogado porque los abogados se reparten el honorario contractual.</p>"),
        ("Qu\u00e9 no hace una segunda opini\u00f3n",
         "<ul>"
         "<li>No \u201csabotea\u201d a su abogado actual.</li>"
         "<li>No lo obliga a firmar nada nuevo.</li>"
         "<li>No es un juicio sobre el abogado, sino una mirada al caso.</li>"
         "</ul>"),
        ("Confidencialidad",
         "<p>Lo que comparta se trata como confidencial. Si decide no hacer cambios, su abogado actual no se entera de la revisi\u00f3n.</p>"),
    ],
    faqs=[
        ("\u00bfTengo que avisarle a mi abogado actual?",
         "No. Pedir una revisi\u00f3n no requiere notificar a su abogado actual."),
        ("\u00bfPuedo cambiar de abogado despu\u00e9s de la segunda opini\u00f3n?",
         "S\u00ed, pero no es obligatorio. La revisi\u00f3n solo busca darle informaci\u00f3n para decidir."),
        ("\u00bfAumenta el honorario si cambio de abogado?",
         "Generalmente no. Los abogados involucrados se reparten el honorario contractual."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed. Toda la revisi\u00f3n puede hacerse en espa\u00f1ol."),
        ("\u00bfQu\u00e9 pasa si la aseguranza ya hizo una oferta?",
         "Conviene revisar la oferta antes de firmar. Una vez firmado el release, el reclamo se cierra."),
    ],
    related=[
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Gu\u00eda de liquidaciones", "/es/acuerdos-liquidaciones-lesiones/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="weekly",
    breadcrumb_label="Segunda Opini\u00f3n del Caso",
))


# 7. /es/lista-revision-liquidacion-lesiones-california/
_add(Page(
    en_path="/california-personal-injury-settlement-checklist",
    es_path="/es/lista-revision-liquidacion-lesiones-california/",
    title="Lista para revisar un acuerdo de lesiones en California | Antes de firmar",
    description=(
        "Lista pr\u00e1ctica de qu\u00e9 revisar antes de aceptar una oferta de liquidaci\u00f3n por lesiones en California: "
        "gastos m\u00e9dicos, tratamiento futuro, liens, release y m\u00e1s."
    ),
    h1="Revise su oferta de liquidaci\u00f3n antes de firmar",
    lead=(
        "Una oferta de la aseguranza puede parecer urgente, pero firmar demasiado r\u00e1pido puede cerrar su reclamo. "
        "Antes de aceptar, revise si la oferta considera sus gastos m\u00e9dicos, dolor, p\u00e9rdida de ingresos y el "
        "impacto real del accidente."
    ),
    sections=[
        ("Por qu\u00e9 revisar antes de aceptar",
         "<p>Una vez firmado el release, generalmente no puede reabrir el reclamo, aunque aparezca una lesi\u00f3n nueva "
         "o necesite m\u00e1s tratamiento. Por eso conviene revisar la oferta con la documentaci\u00f3n a la mano.</p>"),
        ("La lista de revisi\u00f3n",
         "<ul>"
         "<li>\u00bfIncluye <strong>todos</strong> los gastos m\u00e9dicos hasta hoy?</li>"
         "<li>\u00bfSe consider\u00f3 el tratamiento futuro probable (terapia, cirug\u00edas, inyecciones)?</li>"
         "<li>\u00bfEst\u00e1 incluida la p\u00e9rdida de ingresos pasada y la capacidad para trabajar?</li>"
         "<li>\u00bfHay gastos de bolsillo (transporte, equipo, ayuda en casa)?</li>"
         "<li>\u00bfSe consider\u00f3 el da\u00f1o a la propiedad?</li>"
         "<li>\u00bfEst\u00e1n valorados correctamente el dolor y sufrimiento?</li>"
         "<li>\u00bfHay liens m\u00e9dicos, Medi-Cal, Medicare, ERISA o liens hospitalarios identificados?</li>"
         "<li>\u00bfLos liens fueron negociados o solo se est\u00e1n descontando del total?</li>"
         "<li>\u00bfEl release est\u00e1 limitado a este reclamo o tiene lenguaje amplio (indemnidad)?</li>"
         "<li>\u00bfLa oferta se compar\u00f3 contra el l\u00edmite real de la p\u00f3liza?</li>"
         "<li>\u00bfHay otras p\u00f3lizas (paraguas, comercial, UM/UIM) que no se han usado?</li>"
         "<li>\u00bfEl plazo legal (statute of limitations) sigue protegido?</li>"
         "</ul>"),
        ("Se\u00f1ales de oferta baja",
         "<ul>"
         "<li>Le hicieron la oferta muy r\u00e1pido, antes de tener todas las facturas m\u00e9dicas.</li>"
         "<li>No explican c\u00f3mo llegaron al monto.</li>"
         "<li>El monto apenas alcanza para los gastos m\u00e9dicos pasados.</li>"
         "<li>No incluye tratamiento futuro aunque sigue en terapia.</li>"
         "<li>Le presionan con un plazo artificial para firmar.</li>"
         "</ul>"),
        ("Qu\u00e9 hacer si el release ya lleg\u00f3",
         "<p>No firme todav\u00eda. Pida tiempo y obtenga una "
         "<a href=\"/es/segunda-opinion-reclamo-lesiones-california/\">segunda opini\u00f3n del reclamo</a> antes "
         "de comprometerse. La aseguranza no puede retirar la oferta legalmente solo porque usted pidi\u00f3 tiempo razonable.</p>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto tiempo tengo para responder una oferta?",
         "La oferta generalmente no expira de inmediato. La aseguranza puede dar un plazo informal, pero hay tiempo para revisar."),
        ("\u00bfPuedo pedir m\u00e1s informaci\u00f3n antes de firmar?",
         "S\u00ed. Tiene derecho a pedir el desglose, el lenguaje exacto del release y los liens identificados."),
        ("\u00bfQu\u00e9 pasa si no estoy de acuerdo con el monto?",
         "Puede contraofertar. La negociaci\u00f3n con la aseguranza es normal y esperada."),
        ("\u00bfEl release puede ir m\u00e1s all\u00e1 del accidente?",
         "Algunos releases tienen lenguaje amplio. Conviene revisar el texto antes de firmar."),
        ("\u00bfPuedo pedir una revisi\u00f3n en espa\u00f1ol?",
         "S\u00ed. Toda la revisi\u00f3n puede hacerse en espa\u00f1ol."),
    ],
    related=[
        ("Gu\u00eda de liquidaciones", "/es/acuerdos-liquidaciones-lesiones/"),
        ("Carta de demanda", "/es/carta-demanda-lesiones-personales-california/"),
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="weekly",
    breadcrumb_label="Lista de Revisi\u00f3n del Acuerdo",
))

# 8. /es/carta-demanda-lesiones-personales-california/
_add(Page(
    en_path="/california-personal-injury-demand-letter-guide",
    es_path="/es/carta-demanda-lesiones-personales-california/",
    title="Carta de demanda por lesiones personales en California | Qu\u00e9 significa",
    description=(
        "Qu\u00e9 es una carta de demanda por lesiones, qu\u00e9 debe incluir, cu\u00e1nto tarda la aseguranza en responder "
        "y qu\u00e9 pasa despu\u00e9s en un caso de California."
    ),
    h1="Qu\u00e9 es una carta de demanda por lesiones personales",
    lead=(
        "La carta de demanda (demand letter) es la solicitud formal de pago que se env\u00eda a la aseguranza para "
        "abrir la negociaci\u00f3n. Explica la culpa, las lesiones, el tratamiento y el monto que se pide. Es uno de "
        "los pasos m\u00e1s importantes del reclamo."
    ),
    sections=[
        ("Qu\u00e9 debe incluir",
         "<ul>"
         "<li>Resumen de c\u00f3mo ocurri\u00f3 el accidente y por qu\u00e9 la otra parte es responsable.</li>"
         "<li>Lesiones diagnosticadas y tratamiento recibido.</li>"
         "<li>Tratamiento futuro probable.</li>"
         "<li>P\u00e9rdida de ingresos pasada y futura.</li>"
         "<li>Gastos de bolsillo.</li>"
         "<li>Da\u00f1o a la propiedad.</li>"
         "<li>Dolor, sufrimiento e impacto en la vida diaria.</li>"
         "<li>Monto solicitado y plazo razonable de respuesta.</li>"
         "</ul>"),
        ("Por qu\u00e9 importa",
         "<p>La carta de demanda pone por escrito el caso y obliga a la aseguranza a poner un valor. Una carta "
         "d\u00e9bil casi siempre genera una oferta d\u00e9bil. Una carta bien construida y bien documentada genera una "
         "respuesta m\u00e1s seria.</p>"),
        ("Qu\u00e9 pasa despu\u00e9s de enviarla",
         "<ul>"
         "<li>La aseguranza revisa el archivo y los documentos adjuntos.</li>"
         "<li>Hace una contraoferta, niega el reclamo o pide m\u00e1s informaci\u00f3n.</li>"
         "<li>Comienza la negociaci\u00f3n.</li>"
         "<li>Si no se llega a un acuerdo razonable, puede presentarse una demanda judicial para proteger el plazo.</li>"
         "</ul>"),
        ("Cu\u00e1nto tarda la respuesta",
         "<p>No hay un plazo legal r\u00edgido, pero la mayor\u00eda de las aseguranzas responden en 30 a 60 d\u00edas. Si la aseguranza "
         "se demora sin raz\u00f3n, eso puede ser parte del patr\u00f3n del ajustador, no necesariamente del caso.</p>"),
        ("Errores comunes que bajan el valor",
         "<ul>"
         "<li>Enviar la carta antes de que el tratamiento se estabilice.</li>"
         "<li>No incluir tratamiento futuro proyectado.</li>"
         "<li>No documentar la p\u00e9rdida de ingresos con pay stubs o cartas del empleador.</li>"
         "<li>Pedir un monto sin sustento o demasiado bajo.</li>"
         "<li>No identificar todas las p\u00f3lizas disponibles.</li>"
         "</ul>"),
        ("Cu\u00e1ndo conviene una revisi\u00f3n legal",
         "<p>Si la carta de demanda fue enviada y la aseguranza no se mueve, o si la respuesta fue mucho menor de lo "
         "esperado, una <a href=\"/es/segunda-opinion-reclamo-lesiones-california/\">segunda opini\u00f3n</a> puede ayudarle a entender qu\u00e9 cambiar.</p>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto tiempo despu\u00e9s del accidente se env\u00eda la carta?",
         "Generalmente despu\u00e9s de que el tratamiento se estabiliza, para poder calcular el da\u00f1o completo."),
        ("\u00bfEs obligatorio enviar carta de demanda?",
         "No siempre, pero es la forma est\u00e1ndar de iniciar la negociaci\u00f3n y de documentar el caso."),
        ("\u00bfQu\u00e9 pasa si la aseguranza no responde?",
         "Despu\u00e9s de un plazo razonable, se puede enviar una carta de seguimiento o, si el plazo legal est\u00e1 cerca, presentar la demanda."),
        ("\u00bfPuedo enviar la carta yo mismo?",
         "S\u00ed, pero la calidad de la carta afecta directamente la respuesta. Conviene revisarla con alguien con experiencia antes de enviarla."),
        ("\u00bfCu\u00e1nto pido en la carta?",
         "El monto debe basarse en gastos m\u00e9dicos pasados y futuros, p\u00e9rdida de ingresos, dolor y sufrimiento, y la cobertura disponible."),
    ],
    related=[
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Gu\u00eda de liquidaciones", "/es/acuerdos-liquidaciones-lesiones/"),
        ("Segunda opini\u00f3n del reclamo", "/es/segunda-opinion-reclamo-lesiones-california/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="weekly",
    breadcrumb_label="Carta de Demanda",
))


# 9. /es/accidentes-vehiculos/
_add(Page(
    en_path="/motor-vehicle",
    es_path="/es/accidentes-vehiculos/",
    title="Accidentes de veh\u00edculos en California | Reclamos y opciones",
    description=(
        "Reclamos por accidentes de auto, cami\u00f3n, motocicleta, Uber/Lyft, autob\u00fas y otros veh\u00edculos en California. "
        "C\u00f3mo proteger su caso y revisar la oferta de la aseguranza."
    ),
    h1="Reclamos por accidentes de veh\u00edculos en California",
    lead=(
        "Los reclamos por accidentes de veh\u00edculos cubren autos, camiones, motocicletas, rideshare, autobuses, "
        "scooters y bicicletas el\u00e9ctricas. Cada tipo tiene sus propios temas de cobertura, culpa y lesiones."
    ),
    sections=[
        ("Tipos principales de accidente",
         "<ul>"
         "<li><a href=\"/es/abogado-accidentes-auto-los-angeles/\">Accidentes de auto en Los \u00c1ngeles</a></li>"
         "<li><a href=\"/es/abogado-accidentes-auto-california/\">Accidentes de auto en California</a></li>"
         "<li><a href=\"/es/accidente-auto-grave/\">Accidentes graves de auto</a></li>"
         "<li><a href=\"/es/abogado-choque-lateral-los-angeles/\">Choque lateral (T-Bone)</a></li>"
         "<li><a href=\"/es/abogado-choque-por-alcance-los-angeles/\">Choque por alcance</a></li>"
         "<li><a href=\"/es/abogado-accidente-fuga-los-angeles/\">Accidente con fuga del responsable</a></li>"
         "<li><a href=\"/es/abogado-accidente-uber-lyft-los-angeles/\">Accidentes de Uber y Lyft</a></li>"
         "<li><a href=\"/es/abogado-accidente-conductor-sin-seguro-los-angeles/\">Conductor sin seguro</a></li>"
         "<li><a href=\"/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/\">Scooter y bicicleta el\u00e9ctrica</a></li>"
         "<li><a href=\"/es/abogado-accidente-peaton-los-angeles/\">Accidentes de peat\u00f3n</a></li>"
         "<li><a href=\"/es/lesiones-personales/accidentes-camion/\">Accidentes de cami\u00f3n</a></li>"
         "</ul>"),
        ("Qu\u00e9 hacer despu\u00e9s del choque",
         "<ul>"
         "<li>Pida atenci\u00f3n m\u00e9dica aunque crea que la lesi\u00f3n es leve.</li>"
         "<li>Reporte el accidente a la polic\u00eda y obtenga el n\u00famero de reporte.</li>"
         "<li>Tome fotos del lugar, los veh\u00edculos y las lesiones visibles.</li>"
         "<li>Anote testigos.</li>"
         "<li>Notifique a su aseguranza, pero no d\u00e9 declaraci\u00f3n grabada a la aseguranza del otro hasta haber revisado el caso.</li>"
         "</ul>"),
        ("T\u00e1cticas comunes de la aseguranza",
         "<ul>"
         "<li>Ofertas r\u00e1pidas antes de tener diagn\u00f3stico completo.</li>"
         "<li>Llamadas para pedir declaraci\u00f3n grabada.</li>"
         "<li>Etiqueta de \u201cimpacto bajo\u201d o \u201clesi\u00f3n menor\u201d.</li>"
         "<li>Argumentos de culpa compartida para reducir la oferta.</li>"
         "</ul>"),
        ("Cu\u00e1ndo conviene una revisi\u00f3n",
         "<p>Si hay lesiones, tratamiento m\u00e9dico, p\u00e9rdida de ingresos, o si la aseguranza ya hizo una oferta, "
         "una revisi\u00f3n gratuita le ayuda a entender si el caso est\u00e1 siendo valorado correctamente.</p>"),
    ],
    faqs=[
        ("\u00bfTengo que dar declaraci\u00f3n grabada a la aseguranza del otro conductor?",
         "Generalmente no es obligatorio. Conviene revisar el caso antes de dar declaraci\u00f3n a una aseguranza distinta a la suya."),
        ("\u00bfQu\u00e9 pasa si el otro conductor no tiene seguro?",
         "Su propia cobertura UM/UIM puede pagar. Consulte la <a href=\"/es/abogado-accidente-conductor-sin-seguro-los-angeles/\">p\u00e1gina de conductor sin seguro</a>."),
        ("\u00bfQu\u00e9 pasa si fui pasajero?",
         "Como pasajero usted casi nunca tiene culpa y puede reclamar contra la aseguranza del conductor responsable."),
        ("\u00bfCu\u00e1nto tiempo tengo para reclamar?",
         "En California, generalmente 2 a\u00f1os desde el accidente. Casos contra entidades p\u00fablicas tienen solo 6 meses."),
        ("\u00bfQu\u00e9 documentos debo guardar?",
         "Reporte policial, fotos, facturas m\u00e9dicas, recibos, cartas de la aseguranza y cualquier oferta por escrito."),
    ],
    related=[
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidente en Los \u00c1ngeles", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Conductor sin seguro", "/es/abogado-accidente-conductor-sin-seguro-los-angeles/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="weekly",
    breadcrumb_label="Accidentes de Veh\u00edculos",
))


# 10. /es/responsabilidad-de-propiedad/
_add(Page(
    en_path="/premises-liability",
    es_path="/es/responsabilidad-de-propiedad/",
    title="Responsabilidad del due\u00f1o de propiedad en California | Resbal\u00f3n y ca\u00edda",
    description=(
        "Cu\u00e1ndo el due\u00f1o de una propiedad responde por lesiones: resbalones y ca\u00eddas, seguridad negligente, "
        "condiciones peligrosas y reclamos en California."
    ),
    h1="Responsabilidad del due\u00f1o de propiedad en California",
    lead=(
        "Los due\u00f1os y operadores de propiedades en California tienen la obligaci\u00f3n razonable de mantener el lugar "
        "seguro. Cuando ignoran un riesgo conocido y alguien se lesiona, puede haber un reclamo por responsabilidad de propiedad."
    ),
    sections=[
        ("Tipos comunes de reclamo",
         "<ul>"
         "<li>Resbalones y ca\u00eddas en tiendas, supermercados, restaurantes.</li>"
         "<li>Ca\u00eddas por suelo mojado sin se\u00f1al.</li>"
         "<li>Lesiones por escaleras o pisos en mal estado.</li>"
         "<li>Iluminaci\u00f3n insuficiente.</li>"
         "<li>Seguridad negligente que permite asaltos o agresiones.</li>"
         "<li>Lesiones en estacionamientos por mantenimiento deficiente.</li>"
         "</ul>"),
        ("Qu\u00e9 hay que demostrar",
         "<ul>"
         "<li>La condici\u00f3n peligrosa exist\u00eda.</li>"
         "<li>El due\u00f1o sab\u00eda o deber\u00eda haber sabido del peligro.</li>"
         "<li>El due\u00f1o no tom\u00f3 medidas razonables para corregirlo o advertir.</li>"
         "<li>La condici\u00f3n caus\u00f3 la lesi\u00f3n.</li>"
         "</ul>"),
        ("Evidencia importante",
         "<ul>"
         "<li>Fotos del lugar y de la condici\u00f3n peligrosa.</li>"
         "<li>Reporte del incidente al gerente o due\u00f1o.</li>"
         "<li>Testigos.</li>"
         "<li>Cualquier video de c\u00e1mara de seguridad (pide preservarlo r\u00e1pido).</li>"
         "<li>Documentaci\u00f3n m\u00e9dica.</li>"
         "</ul>"),
        ("T\u00e1cticas comunes",
         "<ul>"
         "<li>Decir que el cliente \u201ctambi\u00e9n tuvo culpa\u201d por no ver el peligro.</li>"
         "<li>Argumentar que el peligro era \u201cobvio\u201d.</li>"
         "<li>Borrar o no entregar video despu\u00e9s de cierto tiempo.</li>"
         "</ul>"),
        ("Cu\u00e1ndo conviene una revisi\u00f3n",
         "<p>Si la lesi\u00f3n requiere tratamiento m\u00e9dico, si perdi\u00f3 ingresos o si el negocio est\u00e1 negando responsabilidad, "
         "una revisi\u00f3n gratuita le ayuda a entender qu\u00e9 evidencia preservar y qu\u00e9 sigue.</p>"),
    ],
    faqs=[
        ("\u00bfTengo culpa por no haber visto el l\u00edquido en el piso?",
         "California usa culpa comparativa. La culpa del cliente reduce la recuperaci\u00f3n pero no la elimina, y en muchos casos no aplica si el negocio sab\u00eda del peligro."),
        ("\u00bfCu\u00e1nto tiempo tengo para reclamar?",
         "Generalmente 2 a\u00f1os, pero solo 6 meses si la propiedad es de una entidad p\u00fablica."),
        ("\u00bfNecesito ir al hospital antes de reclamar?",
         "S\u00ed conviene buscar atenci\u00f3n m\u00e9dica r\u00e1pido para documentar la lesi\u00f3n y comenzar tratamiento."),
        ("\u00bfQu\u00e9 hago si el gerente no quiso hacer un reporte?",
         "Documente la negativa, anote la fecha y hora, pida testigos y consulte la revisi\u00f3n gratuita."),
        ("\u00bfPuedo reclamar si me asaltaron por mala seguridad?",
         "S\u00ed, en algunos casos. Cuando hay historial de delitos en el lugar y el due\u00f1o ignor\u00f3 medidas razonables de seguridad."),
    ],
    related=[
        ("Resbal\u00f3n y ca\u00edda", "/es/lesiones-personales/resbalon-caida/"),
        ("Accidente en estacionamiento", "/es/guia-reclamo-accidente-estacionamiento-california/"),
        ("Abogado de accidente en estacionamiento (LA)", "/es/abogado-accidente-estacionamiento-los-angeles/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="monthly",
    breadcrumb_label="Responsabilidad de Propiedad",
))


# 11. /es/accidente-auto-grave/
_add(Page(
    en_path="/major-car-accident",
    es_path="/es/accidente-auto-grave/",
    title="Accidente de auto grave en California | Qu\u00e9 hacer y c\u00f3mo proteger su caso",
    description=(
        "Pasos pr\u00e1cticos despu\u00e9s de un accidente de auto grave en California: tratamiento, evidencia, aseguranza, "
        "p\u00e9rdida de ingresos y cu\u00e1ndo pedir una revisi\u00f3n del caso."
    ),
    h1="Accidente de auto grave en California",
    lead=(
        "Un accidente grave cambia muchas cosas al mismo tiempo: hospital, facturas, trabajo, familia, y una "
        "aseguranza que ya est\u00e1 tomando decisiones sobre su caso. Esta gu\u00eda explica qu\u00e9 hacer para no perder valor "
        "del reclamo mientras se enfoca en recuperarse."
    ),
    sections=[
        ("Primeras 72 horas",
         "<ul>"
         "<li>Atenci\u00f3n m\u00e9dica completa, incluso si los s\u00edntomas aparecen despu\u00e9s.</li>"
         "<li>Reporte policial y n\u00famero de reporte.</li>"
         "<li>Fotos de los veh\u00edculos, el lugar y las lesiones visibles.</li>"
         "<li>Datos de testigos.</li>"
         "<li>Notifique a su aseguranza, pero no d\u00e9 declaraci\u00f3n grabada a la otra aseguranza todav\u00eda.</li>"
         "</ul>"),
        ("Tratamiento m\u00e9dico despu\u00e9s del alta",
         "<p>Una visita al ER no es suficiente para un caso grave. Siga las recomendaciones de seguimiento, "
         "terapia, especialistas e im\u00e1genes. Las brechas largas sin tratamiento son el argumento favorito de la "
         "aseguranza para reducir la oferta.</p>"),
        ("Aseguranza del otro conductor",
         "<ul>"
         "<li>Llama r\u00e1pido para abrir el reclamo.</li>"
         "<li>Puede ofrecer pagar la renta de un auto o un \u201cgesto\u201d inicial: documente todo por escrito.</li>"
         "<li>Pide declaraci\u00f3n grabada \u2014 generalmente conviene declinar hasta tener orientaci\u00f3n.</li>"
         "</ul>"),
        ("Su propia aseguranza",
         "<ul>"
         "<li>Notifique el accidente para preservar coberturas como Med-Pay o UM/UIM.</li>"
         "<li>Pregunte por sus l\u00edmites de p\u00f3liza.</li>"
         "<li>Si el otro no tiene suficiente seguro, su UM/UIM puede ser cr\u00edtico.</li>"
         "</ul>"),
        ("Cobertura disponible",
         "<ul>"
         "<li>Aseguranza del conductor culpable.</li>"
         "<li>P\u00f3liza comercial si manejaba por trabajo.</li>"
         "<li>P\u00f3liza paraguas.</li>"
         "<li>UM/UIM en su p\u00f3liza.</li>"
         "<li>Med-Pay.</li>"
         "</ul>"),
        ("P\u00e9rdida de ingresos",
         "<p>Documente todo: pay stubs, cartas del empleador, horarios, oportunidades perdidas. Si su capacidad "
         "para trabajar puede verse afectada de forma permanente, eso es un componente grande del valor del caso.</p>"),
        ("Cu\u00e1ndo conviene una revisi\u00f3n urgente",
         "<ul>"
         "<li>Hospitalizaci\u00f3n o cirug\u00eda.</li>"
         "<li>La aseguranza pide declaraci\u00f3n grabada.</li>"
         "<li>Le ofrecen una liquidaci\u00f3n r\u00e1pida.</li>"
         "<li>La aseguranza disputa la culpa.</li>"
         "<li>El otro conductor estaba manejando por trabajo.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfDebo hablar con la aseguranza del otro conductor?",
         "Puede confirmar lo b\u00e1sico, pero las declaraciones grabadas formales pueden esperar."),
        ("\u00bfCu\u00e1nto tiempo tengo para reclamar?",
         "Generalmente 2 a\u00f1os en California; 6 meses contra entidades p\u00fablicas."),
        ("\u00bfQu\u00e9 pasa si no tengo seguro de auto propio?",
         "Todav\u00eda puede reclamar contra la aseguranza del responsable. La falta de seguro propio puede afectar la recuperaci\u00f3n por dolor y sufrimiento bajo Prop 213, pero no los gastos m\u00e9dicos ni la p\u00e9rdida de ingresos."),
        ("\u00bfCu\u00e1ndo conviene pedir abogado?",
         "Cuando hay hospitalizaci\u00f3n, cirug\u00eda, lesiones permanentes, m\u00faltiples p\u00f3lizas o disputa de culpa."),
        ("\u00bfQu\u00e9 hago si no puedo pagar el tratamiento?",
         "Existen opciones de tratamiento bajo lien que se pagan al final del reclamo. La revisi\u00f3n gratuita explica c\u00f3mo funciona."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidentes de auto en California", "/es/abogado-accidentes-auto-california/"),
        ("Conductor sin seguro", "/es/abogado-accidente-conductor-sin-seguro-los-angeles/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Accidente de Auto Grave",
))


# 12. /es/abogado-accidentes-auto-los-angeles/
_add(Page(
    en_path="/los-angeles-car-accident-lawyer",
    es_path="/es/abogado-accidentes-auto-los-angeles/",
    title="Abogado de accidentes de auto en Los \u00c1ngeles | Revisi\u00f3n gratuita",
    description=(
        "Ayuda en espa\u00f1ol para reclamos por accidentes de auto en Los \u00c1ngeles. Revise su caso, evite ofertas bajas "
        "y entienda sus opciones antes de aceptar."
    ),
    h1="Ayuda para reclamos por accidentes de auto en Los \u00c1ngeles",
    lead=(
        "Despu\u00e9s de un choque en Los \u00c1ngeles, la compa\u00f1\u00eda de seguros puede intentar minimizar sus lesiones, "
        "disputar la culpa o presionarlo para dar una declaraci\u00f3n. Nuestro equipo en espa\u00f1ol revisa su caso y "
        "le explica qu\u00e9 hacer antes de aceptar una oferta."
    ),
    sections=[
        ("Tipos comunes de choque en LA",
         "<ul>"
         "<li><a href=\"/es/abogado-choque-por-alcance-los-angeles/\">Choque por alcance (rear-end)</a></li>"
         "<li><a href=\"/es/abogado-choque-lateral-los-angeles/\">Choque lateral (T-Bone)</a></li>"
         "<li><a href=\"/es/abogado-accidente-fuga-los-angeles/\">Accidente con fuga (hit and run)</a></li>"
         "<li><a href=\"/es/abogado-accidente-uber-lyft-los-angeles/\">Uber o Lyft</a></li>"
         "<li><a href=\"/es/abogado-accidente-conductor-sin-seguro-los-angeles/\">Conductor sin seguro</a></li>"
         "<li><a href=\"/es/abogado-accidente-peaton-los-angeles/\">Atropello a peat\u00f3n</a></li>"
         "<li><a href=\"/es/abogado-accidente-estacionamiento-los-angeles/\">Accidente en estacionamiento</a></li>"
         "<li><a href=\"/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/\">Scooter o bicicleta el\u00e9ctrica</a></li>"
         "</ul>"),
        ("Qu\u00e9 hace la aseguranza en Los \u00c1ngeles",
         "<ul>"
         "<li>Llama r\u00e1pido y pide declaraci\u00f3n grabada.</li>"
         "<li>Ofrece pagar la renta de un auto a cambio de informaci\u00f3n.</li>"
         "<li>Etiqueta el choque como \u201cimpacto bajo\u201d basado en fotos.</li>"
         "<li>Pone presi\u00f3n para aceptar una oferta r\u00e1pida.</li>"
         "</ul>"),
        ("Qu\u00e9 documentar",
         "<ul>"
         "<li>Fotos del lugar, los veh\u00edculos y las lesiones.</li>"
         "<li>Reporte policial (LAPD o CHP).</li>"
         "<li>Datos del otro conductor y su seguro.</li>"
         "<li>Testigos.</li>"
         "<li>Toda comunicaci\u00f3n por escrito con la aseguranza.</li>"
         "</ul>"),
        ("Cobertura habitual en California",
         "<ul>"
         "<li>L\u00edmite m\u00ednimo de responsabilidad del otro conductor (a menudo bajo).</li>"
         "<li>UM/UIM propia para cuando el otro no tiene suficiente.</li>"
         "<li>Med-Pay para pagos m\u00e9dicos iniciales.</li>"
         "<li>P\u00f3lizas comerciales si el otro conductor manejaba por trabajo.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir una revisi\u00f3n",
         "<ul>"
         "<li>Si est\u00e1 yendo a terapia o citas m\u00e9dicas.</li>"
         "<li>Si la aseguranza ya hizo una oferta.</li>"
         "<li>Si pidieron declaraci\u00f3n grabada.</li>"
         "<li>Si la culpa est\u00e1 en disputa.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfTengo que tener seguro para reclamar?",
         "No es obligatorio para reclamar contra el responsable, aunque Prop 213 puede limitar algunos da\u00f1os si usted manejaba sin seguro y tuvo culpa."),
        ("\u00bfQu\u00e9 pasa si fui pasajero?",
         "Como pasajero generalmente no tiene culpa y puede reclamar contra la aseguranza del conductor responsable."),
        ("\u00bfCu\u00e1nto puede valer mi caso?",
         "Depende de las lesiones, tratamiento, culpa y cobertura disponible. La revisi\u00f3n gratuita ayuda a darle una idea realista."),
        ("\u00bfTengo que ir a corte?",
         "La mayor\u00eda de los casos en LA se resuelven sin ir a corte."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed. Toda la revisi\u00f3n y comunicaci\u00f3n puede hacerse en espa\u00f1ol."),
    ],
    related=[
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Accidentes de auto en California", "/es/abogado-accidentes-auto-california/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.9,
    sitemap_changefreq="monthly",
    breadcrumb_label="Accidentes de Auto Los \u00c1ngeles",
))


# 13. /es/abogado-accidentes-auto-california/
_add(Page(
    en_path="/california-car-accident-lawyer",
    es_path="/es/abogado-accidentes-auto-california/",
    title="Reclamos por accidentes de auto en California | Ayuda en espa\u00f1ol",
    description=(
        "C\u00f3mo funcionan los reclamos por accidentes de auto en California: cobertura, culpa comparativa, plazos, "
        "ofertas y cu\u00e1ndo pedir una revisi\u00f3n."
    ),
    h1="Ayuda con reclamos por accidentes de auto en California",
    lead=(
        "California tiene reglas espec\u00edficas para reclamos de auto: culpa comparativa pura, plazos cortos en "
        "casos contra entidades p\u00fablicas y l\u00edmites m\u00ednimos de p\u00f3liza relativamente bajos. Esta p\u00e1gina explica "
        "los puntos clave antes de aceptar cualquier oferta."
    ),
    sections=[
        ("Culpa comparativa pura",
         "<p>California permite recuperar incluso si usted tiene parte de culpa. Su recuperaci\u00f3n se reduce por su "
         "porcentaje, pero no se elimina. La aseguranza casi siempre intenta asignar m\u00e1s culpa de la que la evidencia apoya.</p>"),
        ("L\u00edmites m\u00ednimos en California",
         "<p>Los l\u00edmites m\u00ednimos de responsabilidad pueden ser muy bajos. Si las lesiones superan ese l\u00edmite, su UM/UIM puede ser clave.</p>"),
        ("Plazos",
         "<ul>"
         "<li>2 a\u00f1os desde el accidente para la mayor\u00eda de reclamos.</li>"
         "<li>6 meses contra entidades p\u00fablicas.</li>"
         "<li>Reglas distintas para menores y descubrimiento tard\u00edo.</li>"
         "</ul>"),
        ("Documentaci\u00f3n cr\u00edtica",
         "<ul>"
         "<li>Reporte policial.</li>"
         "<li>Im\u00e1genes m\u00e9dicas y notas de m\u00e9dico.</li>"
         "<li>Pay stubs y cartas del empleador.</li>"
         "<li>Comunicaciones con la aseguranza.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir una revisi\u00f3n",
         "<p>Si la aseguranza ya hizo una oferta, si la culpa est\u00e1 en disputa, si hay m\u00e1s de una p\u00f3liza posible "
         "o si las lesiones requieren tratamiento serio, conviene una revisi\u00f3n antes de firmar.</p>"),
    ],
    faqs=[
        ("\u00bfPuedo reclamar si tuve parte de culpa?",
         "S\u00ed. California permite recuperaci\u00f3n proporcional bajo culpa comparativa pura."),
        ("\u00bfQu\u00e9 si la oferta es menor que mis facturas m\u00e9dicas?",
         "Una oferta as\u00ed casi siempre se puede negociar al alza con buena documentaci\u00f3n."),
        ("\u00bfDebo usar mi propia aseguranza?",
         "Si la del otro no es suficiente, su UM/UIM puede ser la cobertura principal."),
        ("\u00bfCu\u00e1l es el plazo legal?",
         "Generalmente 2 a\u00f1os; menos en casos contra entidades p\u00fablicas."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Accidentes de Auto California",
))


# 14. /es/lesiones-personales/accidentes-auto/
_add(Page(
    en_path="/personal-injury/auto-accidents",
    es_path="/es/lesiones-personales/accidentes-auto/",
    title="Reclamos por accidentes de auto en California | Insider Lawyers",
    description=(
        "Gu\u00eda en espa\u00f1ol sobre reclamos por accidentes de auto en California: pasos, cobertura, ofertas y revisi\u00f3n del caso."
    ),
    h1="Reclamos por accidentes de auto en California",
    lead=(
        "Un accidente de auto puede dejar facturas m\u00e9dicas, da\u00f1o al veh\u00edculo, p\u00e9rdida de ingresos y mucha "
        "frustraci\u00f3n con la aseguranza. Esta p\u00e1gina explica las partes principales de un reclamo en California."
    ),
    sections=[
        ("Tipos de choque",
         "<ul>"
         "<li><a href=\"/es/abogado-choque-por-alcance-los-angeles/\">Choque por alcance</a></li>"
         "<li><a href=\"/es/abogado-choque-lateral-los-angeles/\">Choque lateral (T-Bone)</a></li>"
         "<li><a href=\"/es/abogado-accidente-fuga-los-angeles/\">Hit and run</a></li>"
         "<li><a href=\"/es/abogado-accidente-conductor-sin-seguro-los-angeles/\">Conductor sin seguro</a></li>"
         "<li><a href=\"/es/abogado-accidente-uber-lyft-los-angeles/\">Uber/Lyft</a></li>"
         "</ul>"),
        ("Pasos inmediatos",
         "<ul>"
         "<li>Atenci\u00f3n m\u00e9dica.</li>"
         "<li>Reporte policial.</li>"
         "<li>Fotos y testigos.</li>"
         "<li>Notifique a su aseguranza.</li>"
         "</ul>"),
        ("Cobertura",
         "<ul>"
         "<li>Responsabilidad del otro conductor.</li>"
         "<li>UM/UIM propia.</li>"
         "<li>Med-Pay.</li>"
         "<li>P\u00f3lizas comerciales o paraguas.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<p>Cuando la aseguranza ofrece poco, demora la respuesta o pide declaraci\u00f3n grabada.</p>"),
    ],
    faqs=[
        ("\u00bfCu\u00e1nto tarda un caso de auto?",
         "Depende del tratamiento y la negociaci\u00f3n. Casos simples pueden durar meses; casos serios pueden tomar m\u00e1s tiempo."),
        ("\u00bfQu\u00e9 pasa si el otro huy\u00f3?",
         "Su UM/UIM puede aplicar. Vea la <a href=\"/es/abogado-accidente-fuga-los-angeles/\">p\u00e1gina de hit and run</a>."),
        ("\u00bfNecesito ir a corte?",
         "La mayor\u00eda de los casos se resuelve sin corte."),
        ("\u00bfQu\u00e9 documentos guardar?",
         "Reporte policial, fotos, facturas, recibos y toda comunicaci\u00f3n por escrito."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed."),
    ],
    related=[
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidentes de auto en California", "/es/abogado-accidentes-auto-california/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Accidentes de Auto",
))


# 15. /es/lesiones-personales/resbalon-caida/
_add(Page(
    en_path="/personal-injury/slip-and-fall",
    es_path="/es/lesiones-personales/resbalon-caida/",
    title="Reclamos por resbal\u00f3n y ca\u00edda en California | Lo que debe saber",
    description=(
        "Cu\u00e1ndo el due\u00f1o responde por una ca\u00edda: condiciones peligrosas, evidencia, plazos y revisi\u00f3n de "
        "ofertas de la aseguranza en California."
    ),
    h1="Reclamos por resbal\u00f3n y ca\u00edda en California",
    lead=(
        "Un resbal\u00f3n y ca\u00edda puede causar lesiones serias \u2014 fracturas, lesiones de cabeza, columna o cadera. "
        "Si la condici\u00f3n peligrosa pudo evitarse con cuidado razonable del due\u00f1o, puede haber un reclamo."
    ),
    sections=[
        ("Condiciones que suelen generar reclamo",
         "<ul>"
         "<li>Piso mojado sin se\u00f1al.</li>"
         "<li>Alfombras o tapetes rotos o levantados.</li>"
         "<li>Escaleras sin pasamanos o con escalones desnivelados.</li>"
         "<li>Pisos rotos en supermercados, restaurantes o tiendas.</li>"
         "<li>Iluminaci\u00f3n insuficiente.</li>"
         "</ul>"),
        ("Qu\u00e9 hay que demostrar",
         "<ul>"
         "<li>La condici\u00f3n exist\u00eda.</li>"
         "<li>El negocio sab\u00eda o deber\u00eda haber sabido.</li>"
         "<li>No tom\u00f3 medidas razonables para corregirlo o advertir.</li>"
         "<li>La condici\u00f3n caus\u00f3 la ca\u00edda y la lesi\u00f3n.</li>"
         "</ul>"),
        ("Qu\u00e9 hacer despu\u00e9s",
         "<ul>"
         "<li>Atenci\u00f3n m\u00e9dica r\u00e1pida.</li>"
         "<li>Reporte al gerente o due\u00f1o (pida una copia).</li>"
         "<li>Fotos de la condici\u00f3n exacta.</li>"
         "<li>Pida preservar video de c\u00e1mara de seguridad.</li>"
         "<li>Datos de testigos.</li>"
         "</ul>"),
        ("T\u00e1cticas comunes",
         "<ul>"
         "<li>\u201cFue culpa suya por no ver.\u201d</li>"
         "<li>\u201cEl piso estaba se\u00f1alizado.\u201d (cuando no lo estaba)</li>"
         "<li>Borrar video despu\u00e9s de cierto tiempo.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfTengo culpa por no ver el l\u00edquido?",
         "California usa culpa comparativa: su recuperaci\u00f3n puede reducirse, no eliminarse."),
        ("\u00bfQu\u00e9 hago si el gerente no quiso hacer un reporte?",
         "Documente la negativa por escrito y pida una revisi\u00f3n del caso."),
        ("\u00bfCu\u00e1nto tiempo tengo para reclamar?",
         "Generalmente 2 a\u00f1os; 6 meses si la propiedad es de una entidad p\u00fablica."),
        ("\u00bfQu\u00e9 lesiones son comunes?",
         "Fracturas de mu\u00f1eca, cadera, lesi\u00f3n de espalda, conmoci\u00f3n y lesiones de rodilla."),
        ("\u00bfNecesito ver al m\u00e9dico aunque me sienta bien?",
         "S\u00ed. Muchas lesiones aparecen horas o d\u00edas despu\u00e9s."),
    ],
    related=[
        ("Responsabilidad de propiedad", "/es/responsabilidad-de-propiedad/"),
        ("Accidente en estacionamiento", "/es/guia-reclamo-accidente-estacionamiento-california/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Resbal\u00f3n y Ca\u00edda",
))


# 16. /es/guia-reclamo-accidente-estacionamiento-california/
_add(Page(
    en_path="/california-parking-lot-accident-claim-guide",
    es_path="/es/guia-reclamo-accidente-estacionamiento-california/",
    title="Reclamos por accidente en estacionamiento en California | Gu\u00eda",
    description=(
        "C\u00f3mo funcionan los reclamos por accidentes en estacionamientos en California: culpa, evidencia, da\u00f1o al "
        "veh\u00edculo, lesiones a peatones y revisi\u00f3n del caso."
    ),
    h1="Reclamos por accidente en estacionamiento en California",
    lead=(
        "Los accidentes en estacionamientos parecen \u201cmenores\u201d pero pueden causar lesiones serias y disputas "
        "complicadas de culpa. La regla com\u00fan de \u201cel que sale en reversa tiene culpa\u201d no siempre aplica."
    ),
    sections=[
        ("Tipos comunes",
         "<ul>"
         "<li>Choque por reversa en pasillo.</li>"
         "<li>Dos veh\u00edculos saliendo al mismo tiempo.</li>"
         "<li>Atropello a peat\u00f3n en estacionamiento.</li>"
         "<li>Resbal\u00f3n por aceite o agua en el piso.</li>"
         "<li>Choque por mala se\u00f1alizaci\u00f3n del estacionamiento.</li>"
         "</ul>"),
        ("Qui\u00e9n tiene la culpa",
         "<p>Depende de qui\u00e9n estaba en movimiento, qui\u00e9n ten\u00eda el derecho de paso y la se\u00f1alizaci\u00f3n. El video de "
         "c\u00e1mara de seguridad muchas veces decide el caso.</p>"),
        ("Evidencia que ayuda",
         "<ul>"
         "<li>Fotos del lugar y posici\u00f3n final de los veh\u00edculos.</li>"
         "<li>Reporte al gerente del estacionamiento o negocio.</li>"
         "<li>Testigos.</li>"
         "<li>Video de c\u00e1mara (p\u00eddalo antes de que se borre).</li>"
         "<li>Reporte policial si hay lesiones.</li>"
         "</ul>"),
        ("Responsabilidad del due\u00f1o",
         "<p>El operador del estacionamiento puede ser responsable si las condiciones eran peligrosas: pintura "
         "borrada, iluminaci\u00f3n insuficiente, pavimento roto o falta de se\u00f1alizaci\u00f3n.</p>"),
        ("Cu\u00e1ndo pedir una revisi\u00f3n",
         "<ul>"
         "<li>Si hay lesiones m\u00e1s all\u00e1 de da\u00f1o al veh\u00edculo.</li>"
         "<li>Si la culpa est\u00e1 en disputa.</li>"
         "<li>Si la aseguranza minimiza el impacto.</li>"
         "<li>Si fue atropellado como peat\u00f3n.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfSiempre tiene culpa el que sale en reversa?",
         "No. Si el otro conductor estaba a exceso de velocidad o no se detuvo, la culpa puede repartirse."),
        ("\u00bfPuedo reclamar contra el operador del estacionamiento?",
         "S\u00ed, cuando las condiciones del lugar contribuyeron al accidente."),
        ("\u00bfQu\u00e9 pasa si fui peat\u00f3n?",
         "Los peatones en estacionamientos generalmente tienen prioridad. Su reclamo puede ser contra el conductor y, a veces, contra el operador."),
        ("\u00bfMi seguro paga el da\u00f1o aunque sea menor?",
         "Depende de su cobertura. La revisi\u00f3n gratuita ayuda a aclararlo."),
        ("\u00bfHay c\u00e1mara en todos los estacionamientos?",
         "No, pero muchos negocios s\u00ed tienen. Conviene pedir el video r\u00e1pido."),
    ],
    related=[
        ("Abogado de accidente en estacionamiento (LA)", "/es/abogado-accidente-estacionamiento-los-angeles/"),
        ("Resbal\u00f3n y ca\u00edda", "/es/lesiones-personales/resbalon-caida/"),
        ("Responsabilidad de propiedad", "/es/responsabilidad-de-propiedad/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="weekly",
    breadcrumb_label="Accidente en Estacionamiento",
))


# 17. /es/abogado-accidente-estacionamiento-los-angeles/
_add(Page(
    en_path="/parking-lot-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-estacionamiento-los-angeles/",
    title="Accidente en estacionamiento en Los \u00c1ngeles | Revisi\u00f3n del reclamo",
    description=(
        "Reclamos por accidente en estacionamiento en Los \u00c1ngeles: culpa, c\u00e1mara, lesiones a peatones y revisi\u00f3n gratuita."
    ),
    h1="Accidentes en estacionamiento en Los \u00c1ngeles",
    lead=(
        "Los estacionamientos de tiendas, supermercados y centros comerciales en LA generan muchos accidentes \u2014 "
        "tanto entre veh\u00edculos como atropellos a peatones. La culpa rara vez es tan simple como parece."
    ),
    sections=[
        ("Situaciones comunes",
         "<ul>"
         "<li>Choque por reversa en pasillo del centro comercial.</li>"
         "<li>Atropello a peat\u00f3n en frente del negocio.</li>"
         "<li>Ca\u00edda por mantenimiento deficiente.</li>"
         "<li>Choque por iluminaci\u00f3n insuficiente.</li>"
         "</ul>"),
        ("Evidencia clave en LA",
         "<ul>"
         "<li>Video de c\u00e1mara del negocio (p\u00eddalo r\u00e1pido).</li>"
         "<li>Reporte al gerente.</li>"
         "<li>Reporte LAPD si hay lesiones.</li>"
         "<li>Fotos del lugar y de la se\u00f1alizaci\u00f3n.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<ul>"
         "<li>Si hay lesiones.</li>"
         "<li>Si la culpa est\u00e1 en disputa.</li>"
         "<li>Si fue atropellado como peat\u00f3n.</li>"
         "<li>Si el negocio se niega a entregar el video.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfQu\u00e9 hago si el negocio no quiere darme el video?",
         "Documente por escrito su solicitud lo antes posible. Un abogado puede pedir su preservaci\u00f3n formalmente."),
        ("\u00bfQui\u00e9n paga si el peat\u00f3n fue atropellado?",
         "Generalmente la aseguranza del conductor; el operador del lugar puede responder si la condici\u00f3n del lugar contribuy\u00f3."),
        ("\u00bfPuedo reclamar por da\u00f1o solo al auto?",
         "S\u00ed, aunque a menudo el da\u00f1o m\u00e1s grande es la lesi\u00f3n."),
        ("\u00bfQu\u00e9 si la aseguranza minimiza el impacto?",
         "Conviene revisar con im\u00e1genes m\u00e9dicas y documentaci\u00f3n del tratamiento."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed."),
    ],
    related=[
        ("Gu\u00eda de accidente en estacionamiento", "/es/guia-reclamo-accidente-estacionamiento-california/"),
        ("Resbal\u00f3n y ca\u00edda", "/es/lesiones-personales/resbalon-caida/"),
        ("Responsabilidad de propiedad", "/es/responsabilidad-de-propiedad/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Estacionamiento LA",
))


# 18. /es/valor-reclamo-choque-lateral-california/
_add(Page(
    en_path="/t-bone-accident-claim-value-california",
    es_path="/es/valor-reclamo-choque-lateral-california/",
    title="Valor del reclamo por choque lateral (T-Bone) en California | Gu\u00eda",
    description=(
        "C\u00f3mo se valoran los reclamos por choque lateral en California: lesiones t\u00edpicas, disputas de culpa, "
        "p\u00f3lizas de seguro y revisi\u00f3n del caso."
    ),
    h1="C\u00f3mo se valoran los reclamos por choque lateral en California",
    lead=(
        "Los choques laterales (T-Bone) suelen causar lesiones m\u00e1s severas que un choque por alcance porque "
        "el lado del veh\u00edculo absorbe menos energ\u00eda. El valor del caso depende de las lesiones, la disputa de "
        "culpa y la cobertura disponible."
    ),
    sections=[
        ("Por qu\u00e9 las lesiones suelen ser m\u00e1s graves",
         "<ul>"
         "<li>Menor zona de absorci\u00f3n de impacto.</li>"
         "<li>Cabeza y cuello reciben fuerza lateral.</li>"
         "<li>Riesgo alto de lesi\u00f3n de columna, hombro y costillas.</li>"
         "</ul>"),
        ("Disputas comunes de culpa",
         "<ul>"
         "<li>Sem\u00e1foro en rojo o amarillo.</li>"
         "<li>Vuelta a la izquierda contra tr\u00e1fico.</li>"
         "<li>Stop sign no respetada.</li>"
         "<li>Intersecciones sin se\u00f1alizaci\u00f3n clara.</li>"
         "</ul>"),
        ("Evidencia importante",
         "<ul>"
         "<li>Reporte policial con diagrama del choque.</li>"
         "<li>Fotos de la posici\u00f3n y da\u00f1os.</li>"
         "<li>Video de c\u00e1mara de tr\u00e1fico o de negocio cercano.</li>"
         "<li>Datos de testigos.</li>"
         "<li>Im\u00e1genes m\u00e9dicas tempranas.</li>"
         "</ul>"),
        ("Cobertura disponible",
         "<ul>"
         "<li>Responsabilidad del conductor culpable.</li>"
         "<li>UM/UIM propia si la cobertura del otro no alcanza.</li>"
         "<li>Med-Pay.</li>"
         "<li>P\u00f3lizas comerciales si manejaba por trabajo.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<p>Cuando hay hospitalizaci\u00f3n, im\u00e1genes positivas (MRI, CT), tratamiento prolongado, disputa de culpa "
         "o cuando la aseguranza ofrece poco a pesar del impacto.</p>"),
    ],
    faqs=[
        ("\u00bfQui\u00e9n tiene la culpa en un T-Bone?",
         "Generalmente el conductor que no respet\u00f3 sem\u00e1foro o stop sign, pero hay casos con culpa compartida."),
        ("\u00bfPor qu\u00e9 las lesiones son tan serias?",
         "Porque la fuerza llega lateral, donde el veh\u00edculo tiene menos zona de absorci\u00f3n."),
        ("\u00bfQu\u00e9 si el otro huy\u00f3?",
         "Su UM/UIM puede aplicar."),
        ("\u00bfCu\u00e1nto puede valer el caso?",
         "Depende de la severidad, tratamiento y cobertura. La revisi\u00f3n gratuita da una idea realista."),
        ("\u00bfTengo que ir a corte?",
         "La mayor\u00eda de los casos se resuelven sin corte, aunque a veces se presenta demanda para presionar la negociaci\u00f3n."),
    ],
    related=[
        ("Abogado de choque lateral en LA", "/es/abogado-choque-lateral-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Choque Lateral",
))


# 19. /es/abogado-choque-lateral-los-angeles/
_add(Page(
    en_path="/t-bone-accident-lawyer-los-angeles",
    es_path="/es/abogado-choque-lateral-los-angeles/",
    title="Choque lateral (T-Bone) en Los \u00c1ngeles | Revisi\u00f3n del caso",
    description=(
        "Ayuda para reclamos por choque lateral en LA: culpa, evidencia, cobertura, lesiones y revisi\u00f3n gratuita en espa\u00f1ol."
    ),
    h1="Choques laterales (T-Bone) en Los \u00c1ngeles",
    lead=(
        "Los choques laterales ocurren con frecuencia en intersecciones de LA. Las lesiones suelen ser m\u00e1s "
        "severas y la disputa de culpa puede ser intensa cuando dos conductores reclaman tener la luz verde."
    ),
    sections=[
        ("Intersecciones de mayor riesgo en LA",
         "<p>Las intersecciones grandes con varios carriles y sem\u00e1foros con varias fases son donde m\u00e1s se ven "
         "choques laterales: Wilshire, Vermont, Western, Sunset, La Brea, Sepulveda y otras avenidas principales.</p>"),
        ("C\u00f3mo se decide la culpa",
         "<ul>"
         "<li>Reporte policial con diagrama.</li>"
         "<li>Testigos.</li>"
         "<li>Video del negocio o c\u00e1maras de tr\u00e1fico.</li>"
         "<li>Posici\u00f3n final de los veh\u00edculos.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<ul>"
         "<li>Si hubo hospitalizaci\u00f3n.</li>"
         "<li>Si la culpa est\u00e1 en disputa.</li>"
         "<li>Si la aseguranza minimiza la oferta.</li>"
         "<li>Si la otra parte estaba manejando por trabajo.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfPuedo reclamar si la culpa est\u00e1 en duda?",
         "S\u00ed. California permite reclamar con culpa compartida; la recuperaci\u00f3n se reduce proporcionalmente."),
        ("\u00bfQu\u00e9 lesiones son comunes?",
         "Lesi\u00f3n de cuello, hombro, costillas, columna y conmoci\u00f3n cerebral."),
        ("\u00bfCu\u00e1nto tarda el caso?",
         "Depende del tratamiento; casos serios pueden tomar varios meses."),
        ("\u00bfQu\u00e9 si soy pasajero?",
         "Como pasajero generalmente puede reclamar contra cualquiera de los conductores responsables."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed."),
    ],
    related=[
        ("Valor del reclamo por T-Bone", "/es/valor-reclamo-choque-lateral-california/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="T-Bone LA",
))


# 20. /es/abogado-choque-por-alcance-los-angeles/
_add(Page(
    en_path="/rear-end-accident-lawyer-los-angeles",
    es_path="/es/abogado-choque-por-alcance-los-angeles/",
    title="Choque por alcance (rear-end) en Los \u00c1ngeles | Revisi\u00f3n del caso",
    description=(
        "Reclamos por choque por alcance en LA: lesiones de cuello y espalda, ofertas bajas y revisi\u00f3n del caso en espa\u00f1ol."
    ),
    h1="Choques por alcance (rear-end) en Los \u00c1ngeles",
    lead=(
        "El choque por alcance es uno de los m\u00e1s comunes en LA. Aunque parece \u201cmenor\u201d, las lesiones de cuello "
        "y espalda pueden durar meses y requerir terapia o im\u00e1genes m\u00e9dicas."
    ),
    sections=[
        ("Lesiones t\u00edpicas",
         "<ul>"
         "<li>Whiplash (latigazo cervical).</li>"
         "<li>Hernias o protrusiones de disco.</li>"
         "<li>Dolor de espalda baja.</li>"
         "<li>Conmoci\u00f3n cerebral.</li>"
         "</ul>"),
        ("Por qu\u00e9 la aseguranza ofrece poco",
         "<ul>"
         "<li>Etiqueta el choque como \u201cimpacto bajo\u201d basado en fotos.</li>"
         "<li>Argumenta que el da\u00f1o al auto fue m\u00ednimo.</li>"
         "<li>Pide declaraci\u00f3n grabada antes de saber el alcance.</li>"
         "</ul>"),
        ("Qu\u00e9 fortalece el caso",
         "<ul>"
         "<li>Tratamiento m\u00e9dico temprano y consistente.</li>"
         "<li>Im\u00e1genes m\u00e9dicas (MRI/CT) que documenten la lesi\u00f3n.</li>"
         "<li>Notas del m\u00e9dico que relacionen los s\u00edntomas con el accidente.</li>"
         "<li>Continuidad del tratamiento sin gaps largos.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfTengo culpa si yo iba adelante?",
         "Casi nunca. El que viene atr\u00e1s tiene la responsabilidad de mantener distancia segura."),
        ("\u00bfPor qu\u00e9 me duele el cuello d\u00edas despu\u00e9s?",
         "Es com\u00fan que los s\u00edntomas de whiplash aparezcan horas o d\u00edas despu\u00e9s del choque."),
        ("\u00bfPuedo reclamar si el auto qued\u00f3 \u201csin da\u00f1o\u201d?",
         "S\u00ed. El da\u00f1o al auto no determina la lesi\u00f3n."),
        ("\u00bfTengo que dar declaraci\u00f3n grabada?",
         "Generalmente no es obligatorio antes de revisar el caso."),
        ("\u00bfHablan espa\u00f1ol?",
         "S\u00ed."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Choque por Alcance LA",
))


# 21. /es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/
_add(Page(
    en_path="/electric-scooter-ebike-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/",
    title="Accidente de scooter o bicicleta el\u00e9ctrica en LA | Revisi\u00f3n del caso",
    description=(
        "Reclamos por accidentes en scooter, e-bike y bicicleta el\u00e9ctrica en Los \u00c1ngeles: lesiones, cobertura "
        "y revisi\u00f3n del caso."
    ),
    h1="Accidentes de scooter y bicicleta el\u00e9ctrica en Los \u00c1ngeles",
    lead=(
        "Los scooters el\u00e9ctricos y bicicletas el\u00e9ctricas son cada vez m\u00e1s comunes en LA. Cuando un conductor "
        "atropella o cierra el paso a un scooter o e-bike, las lesiones suelen ser graves porque no hay carrocer\u00eda "
        "que proteja al usuario."
    ),
    sections=[
        ("Situaciones comunes",
         "<ul>"
         "<li>Conductor abre la puerta y golpea al ciclista (dooring).</li>"
         "<li>Conductor da vuelta sin ceder el paso.</li>"
         "<li>Choque en cruce.</li>"
         "<li>Conductor en fuga.</li>"
         "</ul>"),
        ("Cobertura disponible",
         "<ul>"
         "<li>Aseguranza del conductor responsable.</li>"
         "<li>UM/UIM si el conductor huy\u00f3 o no tiene seguro.</li>"
         "<li>Med-Pay de su propio seguro de auto, incluso si iba en scooter.</li>"
         "<li>Aseguranza del hogar (en algunos casos limitados).</li>"
         "</ul>"),
        ("Lesiones comunes",
         "<ul>"
         "<li>Fracturas de mu\u00f1eca, brazo, clav\u00edcula.</li>"
         "<li>Lesi\u00f3n cerebral aunque haya usado casco.</li>"
         "<li>Lesi\u00f3n de columna.</li>"
         "<li>Da\u00f1o a tendones y ligamentos.</li>"
         "</ul>"),
        ("Recuperaci\u00f3n del scooter/e-bike",
         "<p>Vea la p\u00e1gina espec\u00edfica sobre "
         "<a href=\"/es/recuperar-scooter-bicicleta-electrica-danada/\">c\u00f3mo recuperar el valor de un scooter o e-bike da\u00f1ado</a>.</p>"),
    ],
    faqs=[
        ("\u00bfMi seguro de auto cubre cuando voy en e-bike?",
         "Med-Pay y UM/UIM pueden aplicar dependiendo del lenguaje de la p\u00f3liza."),
        ("\u00bfQu\u00e9 pasa si el conductor huy\u00f3?",
         "Su UM/UIM puede pagar. Reporte r\u00e1pido a la polic\u00eda."),
        ("\u00bfTengo culpa si no traje casco?",
         "California permite culpa comparativa; no usar casco puede reducir algunos da\u00f1os pero no elimina el reclamo."),
        ("\u00bfQu\u00e9 pasa con el scooter alquilado?",
         "El reclamo principal es contra el conductor culpable; la empresa de scooters generalmente tiene t\u00e9rminos limitantes."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Recuperar scooter/e-bike da\u00f1ado", "/es/recuperar-scooter-bicicleta-electrica-danada/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Accidente con fuga (hit and run)", "/es/abogado-accidente-fuga-los-angeles/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Scooter / E-Bike LA",
))


# 22. /es/recuperar-scooter-bicicleta-electrica-danada/
_add(Page(
    en_path="/recover-destroyed-scooter-ebike",
    es_path="/es/recuperar-scooter-bicicleta-electrica-danada/",
    title="Recuperar valor de scooter o bicicleta el\u00e9ctrica da\u00f1ada en California",
    description=(
        "C\u00f3mo recuperar el valor de un scooter o e-bike destruido en un accidente en California. Reclamo por "
        "da\u00f1o a la propiedad versus reclamo por lesi\u00f3n."
    ),
    h1="Recuperar el valor de un scooter o bicicleta el\u00e9ctrica da\u00f1ada",
    lead=(
        "Si su scooter o e-bike qued\u00f3 destruido en un accidente, tiene dos reclamos posibles: uno por el da\u00f1o "
        "a la propiedad (el veh\u00edculo) y otro por la lesi\u00f3n. Son procesos separados aunque se manejen al mismo tiempo."
    ),
    sections=[
        ("Da\u00f1o a la propiedad vs. lesi\u00f3n",
         "<ul>"
         "<li>El reclamo de propiedad cubre el costo del scooter/e-bike, casco, ropa, electr\u00f3nica.</li>"
         "<li>El reclamo de lesi\u00f3n cubre tratamiento m\u00e9dico, dolor, p\u00e9rdida de ingresos.</li>"
         "<li>Son separables: puede aceptar el pago de propiedad sin firmar nada que afecte la lesi\u00f3n.</li>"
         "</ul>"),
        ("Conductor conocido y con seguro",
         "<p>La aseguranza del conductor paga el valor de mercado del veh\u00edculo. Pida documentaci\u00f3n: factura "
         "original, recibos de modificaciones, fotos del veh\u00edculo antes del accidente.</p>"),
        ("Conductor en fuga o sin seguro",
         "<p>Su propio seguro puede pagar el da\u00f1o bajo cobertura de auto o de hogar, dependiendo de la p\u00f3liza. "
         "Reporte r\u00e1pido a la polic\u00eda.</p>"),
        ("C\u00f3mo se calcula el valor",
         "<ul>"
         "<li>Valor de mercado actual (no precio de reemplazo nuevo).</li>"
         "<li>Edad, condici\u00f3n y kilometraje (en e-bike).</li>"
         "<li>Modificaciones documentadas.</li>"
         "<li>Equipo destruido (casco, luces, candado).</li>"
         "</ul>"),
        ("T\u00e1cticas comunes",
         "<ul>"
         "<li>Oferta inicial baja basada en \u201cdepreciaci\u00f3n\u201d.</li>"
         "<li>No incluir accesorios destruidos.</li>"
         "<li>Mezclar el reclamo de propiedad con la lesi\u00f3n para forzar firma temprana.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfPuedo aceptar el pago del scooter sin afectar la lesi\u00f3n?",
         "S\u00ed, si el release est\u00e1 limitado a la propiedad. Lea el documento antes de firmar."),
        ("\u00bfQu\u00e9 si el conductor huy\u00f3?",
         "Su propio seguro puede aplicar. Reporte r\u00e1pido."),
        ("\u00bfQu\u00e9 hago con las piezas destruidas?",
         "Gu\u00e1rdelas hasta que la aseguranza confirme p\u00e9rdida total. Tome fotos."),
        ("\u00bfCu\u00e1nto vale mi e-bike?",
         "Valor de mercado, no precio nuevo. Documentaci\u00f3n s\u00f3lida ayuda a subir la oferta."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidente de scooter/e-bike en LA", "/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Lista para revisar el acuerdo", "/es/lista-revision-liquidacion-lesiones-california/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Recuperar Scooter / E-Bike",
))


# 23. /es/abogado-accidente-fuga-los-angeles/
_add(Page(
    en_path="/hit-and-run-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-fuga-los-angeles/",
    title="Accidente con fuga (hit and run) en Los \u00c1ngeles | Qu\u00e9 hacer",
    description=(
        "Reclamos por accidente con fuga en LA: pasos inmediatos, cobertura UM/UIM, evidencia y revisi\u00f3n del caso."
    ),
    h1="Accidente con fuga (hit and run) en Los \u00c1ngeles",
    lead=(
        "Cuando el otro conductor huye, todav\u00eda tiene opciones. Su propia cobertura de motorista sin seguro "
        "(UM/UIM) puede pagar sus gastos m\u00e9dicos y otros da\u00f1os."
    ),
    sections=[
        ("Pasos inmediatos",
         "<ul>"
         "<li>Llame al 911 si hay lesiones.</li>"
         "<li>Reporte el hit and run a la polic\u00eda (LAPD / CHP) lo antes posible.</li>"
         "<li>Anote placa, color y marca aunque sea parcial.</li>"
         "<li>Busque testigos.</li>"
         "<li>Pida videos de negocios cercanos antes de que se borren.</li>"
         "</ul>"),
        ("Cobertura UM/UIM",
         "<p>La cobertura de motorista sin seguro (UM) y la cobertura para motorista con seguro insuficiente "
         "(UIM) pueden pagar cuando el responsable huy\u00f3. Su aseguranza puede investigar y pagar igual.</p>"),
        ("Evidencia que ayuda",
         "<ul>"
         "<li>N\u00famero de reporte policial.</li>"
         "<li>Fotos del lugar y del veh\u00edculo da\u00f1ado.</li>"
         "<li>Video de c\u00e1mara cercana.</li>"
         "<li>Testigos.</li>"
         "</ul>"),
        ("Qu\u00e9 puede pagar el seguro",
         "<ul>"
         "<li>Gastos m\u00e9dicos.</li>"
         "<li>P\u00e9rdida de ingresos.</li>"
         "<li>Dolor y sufrimiento.</li>"
         "<li>Da\u00f1o a la propiedad (depende de la p\u00f3liza).</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfMe sube la prima si uso mi UM/UIM?",
         "Generalmente no, porque usted no tiene culpa por que el otro huyera. Conviene confirmar con su agente."),
        ("\u00bfQu\u00e9 pasa si no anot\u00e9 la placa?",
         "Todav\u00eda puede reclamar bajo UM/UIM siempre que reporte el accidente a la polic\u00eda."),
        ("\u00bfCu\u00e1nto tiempo tengo para reportar?",
         "Conviene reportar el mismo d\u00eda o lo antes posible para preservar la cobertura UM."),
        ("\u00bfHay l\u00edmite a lo que paga UM/UIM?",
         "S\u00ed. La cobertura tiene l\u00edmites. Por eso conviene revisar su p\u00f3liza pronto."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Conductor sin seguro", "/es/abogado-accidente-conductor-sin-seguro-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Hit and Run LA",
))


# 24. /es/abogado-accidente-peaton-los-angeles/
_add(Page(
    en_path="/pedestrian-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-peaton-los-angeles/",
    title="Atropello a peat\u00f3n en Los \u00c1ngeles | Revisi\u00f3n del caso",
    description=(
        "Reclamos por atropello a peat\u00f3n en LA: culpa, evidencia, cobertura y revisi\u00f3n del caso en espa\u00f1ol."
    ),
    h1="Atropello a peat\u00f3n en Los \u00c1ngeles",
    lead=(
        "Los peatones en LA suelen tener prioridad en cruces marcados y no marcados. Cuando un peat\u00f3n es "
        "atropellado, las lesiones tienden a ser severas y el reclamo puede involucrar m\u00e1s de una p\u00f3liza."
    ),
    sections=[
        ("Reglas b\u00e1sicas del peat\u00f3n en California",
         "<ul>"
         "<li>Los peatones tienen prioridad en cruces marcados y no marcados en intersecciones.</li>"
         "<li>Los conductores deben ceder el paso al peat\u00f3n.</li>"
         "<li>El peat\u00f3n tambi\u00e9n debe cruzar con cuidado razonable.</li>"
         "</ul>"),
        ("Disputas comunes de culpa",
         "<ul>"
         "<li>Cruce fuera de zona marcada (jaywalking).</li>"
         "<li>Sem\u00e1foro peatonal en rojo.</li>"
         "<li>Distractores: tel\u00e9fono, audifonos.</li>"
         "</ul>"
         "<p>Aun cuando la culpa se reparte, California permite recuperar bajo culpa comparativa.</p>"),
        ("Cobertura disponible",
         "<ul>"
         "<li>Responsabilidad del conductor.</li>"
         "<li>UM/UIM propia si el conductor huy\u00f3 o no tiene seguro.</li>"
         "<li>Med-Pay propio (aplica aunque iba caminando).</li>"
         "<li>P\u00f3liza comercial si manejaba por trabajo.</li>"
         "</ul>"),
        ("Lesiones comunes",
         "<ul>"
         "<li>Fracturas m\u00faltiples.</li>"
         "<li>Lesi\u00f3n cerebral.</li>"
         "<li>Lesi\u00f3n de columna.</li>"
         "<li>Lesiones internas.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfPuedo reclamar si estaba cruzando fuera de la l\u00ednea?",
         "S\u00ed. California permite reclamar bajo culpa comparativa aunque haya culpa compartida."),
        ("\u00bfQu\u00e9 si el conductor huy\u00f3?",
         "Su UM/UIM puede aplicar."),
        ("\u00bfMed-Pay me cubre como peat\u00f3n?",
         "En muchas p\u00f3lizas, s\u00ed."),
        ("\u00bfCu\u00e1nto tiempo tengo?",
         "Generalmente 2 a\u00f1os; menos contra entidades p\u00fablicas."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidente con fuga", "/es/abogado-accidente-fuga-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Peat\u00f3n LA",
))


# 25. /es/abogado-accidente-uber-lyft-los-angeles/
_add(Page(
    en_path="/uber-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-uber-lyft-los-angeles/",
    title="Accidente Uber o Lyft en Los \u00c1ngeles | Reclamos y cobertura",
    description=(
        "Reclamos por accidente en Uber, Lyft u otro rideshare en LA: cobertura de $1M, qui\u00e9n paga y revisi\u00f3n del caso."
    ),
    h1="Accidente Uber o Lyft en Los \u00c1ngeles",
    lead=(
        "Uber y Lyft mantienen p\u00f3lizas de hasta $1 mill\u00f3n cuando el conductor est\u00e1 en \u201cmodo activo\u201d con un pasajero. "
        "Saber qu\u00e9 cobertura aplica depende de en qu\u00e9 fase de la app estaba el conductor."
    ),
    sections=[
        ("Las tres fases de la app",
         "<ul>"
         "<li><strong>App apagada:</strong> aplica solo la p\u00f3liza personal del conductor.</li>"
         "<li><strong>App encendida sin pasajero:</strong> p\u00f3liza limitada de Uber/Lyft m\u00e1s la personal.</li>"
         "<li><strong>Con pasajero o camino al pasajero:</strong> p\u00f3liza de $1M de Uber/Lyft.</li>"
         "</ul>"),
        ("Qui\u00e9n puede reclamar",
         "<ul>"
         "<li>Pasajero del rideshare.</li>"
         "<li>Conductor del rideshare lesionado por culpa de otro.</li>"
         "<li>Conductor o pasajero del otro veh\u00edculo.</li>"
         "<li>Peat\u00f3n o ciclista atropellado por un conductor de Uber/Lyft.</li>"
         "</ul>"),
        ("Evidencia clave",
         "<ul>"
         "<li>Captura del recibo del viaje y de la app.</li>"
         "<li>Reporte policial.</li>"
         "<li>Datos del conductor de Uber/Lyft.</li>"
         "<li>Comunicaci\u00f3n con soporte de Uber/Lyft.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<p>Cuando hay lesiones m\u00e1s all\u00e1 de \u201cmoreton sin importancia\u201d, cuando Uber/Lyft niega cobertura "
         "o cuando la aseguranza personal del conductor culpable no quiere abrir reclamo.</p>"),
    ],
    faqs=[
        ("\u00bfUber o Lyft pagan todos los casos?",
         "No. La cobertura depende de la fase de la app al momento del accidente."),
        ("\u00bfPuedo reclamar como pasajero?",
         "S\u00ed. Como pasajero generalmente puede reclamar contra cualquiera de los conductores responsables."),
        ("\u00bfQu\u00e9 si soy conductor de Uber/Lyft?",
         "Tambi\u00e9n puede reclamar contra el otro conductor. La cobertura UM/UIM de Uber/Lyft puede aplicar."),
        ("\u00bfQu\u00e9 hago primero?",
         "Atenci\u00f3n m\u00e9dica, reporte policial, guardar el recibo del viaje y reportar dentro de la app."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Conductor sin seguro", "/es/abogado-accidente-conductor-sin-seguro-los-angeles/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Uber / Lyft LA",
))


# 26. /es/lesiones-personales/accidentes-camion/
_add(Page(
    en_path="/personal-injury/truck-accidents",
    es_path="/es/lesiones-personales/accidentes-camion/",
    title="Accidentes de cami\u00f3n en California | Reclamos y revisi\u00f3n del caso",
    description=(
        "Reclamos por accidente con cami\u00f3n comercial en California: cobertura, evidencia, lesiones y revisi\u00f3n del caso."
    ),
    h1="Accidentes de cami\u00f3n en California",
    lead=(
        "Los accidentes con camiones comerciales suelen causar lesiones graves. La cobertura disponible es "
        "much\u00edsimo mayor que en un choque normal, pero las aseguranzas y las empresas de transporte se mueven "
        "r\u00e1pido para limitar la responsabilidad."
    ),
    sections=[
        ("Por qu\u00e9 los casos de cami\u00f3n son distintos",
         "<ul>"
         "<li>Cobertura m\u00ednima federal mucho m\u00e1s alta que un auto.</li>"
         "<li>Regulaciones federales (FMCSA) sobre horas de manejo, mantenimiento y entrenamiento.</li>"
         "<li>M\u00e1s de un demandado posible: conductor, empresa de transporte, due\u00f1o del cami\u00f3n, broker, cargador.</li>"
         "<li>Caja negra (ECM) con datos de velocidad y frenado.</li>"
         "</ul>"),
        ("Evidencia que se preserva r\u00e1pido",
         "<ul>"
         "<li>Registro de horas del conductor (logs).</li>"
         "<li>Datos de la caja negra.</li>"
         "<li>Mantenimiento del veh\u00edculo.</li>"
         "<li>Video del veh\u00edculo o del lugar.</li>"
         "<li>Reporte de tr\u00e1fico y comunicaciones internas.</li>"
         "</ul>"),
        ("Lesiones t\u00edpicas",
         "<ul>"
         "<li>Lesi\u00f3n cerebral.</li>"
         "<li>Lesi\u00f3n de columna.</li>"
         "<li>Fracturas m\u00faltiples.</li>"
         "<li>Quemaduras o lesiones por carga descontrolada.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n urgente",
         "<ul>"
         "<li>Hospitalizaci\u00f3n o cirug\u00eda.</li>"
         "<li>Cami\u00f3n con marca comercial.</li>"
         "<li>La empresa de transporte ya envi\u00f3 a un \u201cinvestigador\u201d.</li>"
         "<li>La aseguranza pide declaraci\u00f3n grabada.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfA qui\u00e9n se reclama en un accidente de cami\u00f3n?",
         "Puede haber varios demandados: el conductor, la empresa de transporte y otras partes. Una revisi\u00f3n identifica todas las p\u00f3lizas posibles."),
        ("\u00bfPor qu\u00e9 importa la caja negra?",
         "Porque registra velocidad, frenado y otros datos cr\u00edticos. Hay que pedir su preservaci\u00f3n r\u00e1pido."),
        ("\u00bfCu\u00e1nto tiempo tengo para reclamar?",
         "Generalmente 2 a\u00f1os, pero la evidencia se pierde r\u00e1pido. Conviene actuar pronto."),
        ("\u00bfQu\u00e9 si manejaba para una empresa?",
         "Su Workers\u2019 Compensation propia puede aplicar adem\u00e1s del reclamo civil contra el responsable."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Accidentes de veh\u00edculos", "/es/accidentes-vehiculos/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Accidentes de Cami\u00f3n",
))


# 27. /es/abogado-accidente-conductor-sin-seguro-los-angeles/
_add(Page(
    en_path="/uninsured-driver-accident-lawyer-los-angeles",
    es_path="/es/abogado-accidente-conductor-sin-seguro-los-angeles/",
    title="Accidente con conductor sin seguro en Los \u00c1ngeles | UM/UIM",
    description=(
        "Qu\u00e9 hacer cuando el otro conductor no tiene seguro en LA. C\u00f3mo funciona su UM/UIM, evidencia y revisi\u00f3n."
    ),
    h1="Accidente con conductor sin seguro en Los \u00c1ngeles",
    lead=(
        "Cuando el otro conductor no tiene seguro o tiene cobertura muy baja, su propia cobertura de motorista sin "
        "seguro (UM) o motorista con seguro insuficiente (UIM) puede pagar sus da\u00f1os."
    ),
    sections=[
        ("UM vs. UIM",
         "<ul>"
         "<li><strong>UM</strong> aplica cuando el otro no tiene seguro o huy\u00f3.</li>"
         "<li><strong>UIM</strong> aplica cuando el otro s\u00ed tiene seguro, pero no es suficiente para sus da\u00f1os.</li>"
         "</ul>"),
        ("Qu\u00e9 paga su UM/UIM",
         "<ul>"
         "<li>Gastos m\u00e9dicos.</li>"
         "<li>P\u00e9rdida de ingresos.</li>"
         "<li>Dolor y sufrimiento.</li>"
         "<li>Da\u00f1o a la propiedad (depende de la p\u00f3liza).</li>"
         "</ul>"),
        ("Pasos despu\u00e9s del accidente",
         "<ul>"
         "<li>Reporte policial.</li>"
         "<li>Notifique a su aseguranza pronto.</li>"
         "<li>Tratamiento m\u00e9dico.</li>"
         "<li>Solicite por escrito la apertura del reclamo UM/UIM.</li>"
         "</ul>"),
        ("Aseguranza propia que se opone",
         "<p>A pesar de ser <em>su</em> aseguranza, en un reclamo UM/UIM act\u00faa como contraparte. Puede ofrecer "
         "poco, pedir declaraciones grabadas y exigir documentaci\u00f3n detallada. Una revisi\u00f3n ayuda a entender qu\u00e9 esperar.</p>"),
    ],
    faqs=[
        ("\u00bfMe sube la prima si uso mi UM?",
         "Generalmente no si usted no tuvo culpa. Conviene confirmar con su agente."),
        ("\u00bfQu\u00e9 si no tengo UM/UIM?",
         "Existen otros caminos posibles (p\u00f3lizas familiares, Med-Pay, propiedad comercial). Revise su p\u00f3liza."),
        ("\u00bfCu\u00e1nto tiempo tengo?",
         "Su p\u00f3liza puede exigir aviso r\u00e1pido. Reporte lo antes posible."),
        ("\u00bfQu\u00e9 documentaci\u00f3n necesita la aseguranza?",
         "Reporte policial, registros m\u00e9dicos, prueba de p\u00e9rdida de ingresos."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Accidente con fuga (hit and run)", "/es/abogado-accidente-fuga-los-angeles/"),
        ("Accidentes de auto en LA", "/es/abogado-accidentes-auto-los-angeles/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Conductor Sin Seguro LA",
))


# 28. /es/abogado-negligencia-asilo-ancianos-los-angeles/
_add(Page(
    en_path="/los-angeles-nursing-home-neglect-lawyer",
    es_path="/es/abogado-negligencia-asilo-ancianos-los-angeles/",
    title="Negligencia en asilos de ancianos en Los \u00c1ngeles | Revisi\u00f3n confidencial",
    description=(
        "Se\u00f1ales de negligencia o abuso en asilos de ancianos en LA. Revisi\u00f3n confidencial del caso y pasos para proteger a su familiar."
    ),
    h1="Revisi\u00f3n de casos de negligencia en asilos de ancianos en Los \u00c1ngeles",
    lead=(
        "Las \u00falceras por presi\u00f3n, ca\u00eddas, deshidrataci\u00f3n, p\u00e9rdida de peso, infecciones o cambios repentinos "
        "pueden ser se\u00f1ales de negligencia. Si sospecha que un familiar fue descuidado en un asilo, puede solicitar "
        "una revisi\u00f3n confidencial."
    ),
    sections=[
        ("Se\u00f1ales comunes de negligencia",
         "<ul>"
         "<li>\u00dalceras por presi\u00f3n (escaras / bedsores), especialmente etapa 3 o 4.</li>"
         "<li>Ca\u00eddas repetidas.</li>"
         "<li>P\u00e9rdida de peso, deshidrataci\u00f3n.</li>"
         "<li>Infecciones recurrentes del tracto urinario o sepsis.</li>"
         "<li>Higiene deficiente.</li>"
         "<li>Cambios emocionales repentinos o miedo del personal.</li>"
         "<li>Lesiones inexplicables.</li>"
         "</ul>"),
        ("Qu\u00e9 documentar",
         "<ul>"
         "<li>Fotos con fecha de las lesiones o condiciones.</li>"
         "<li>Notas sobre lo que el personal le dijo.</li>"
         "<li>Registros m\u00e9dicos del hospital si fue trasladado.</li>"
         "<li>Comunicaciones con el director del asilo.</li>"
         "</ul>"),
        ("Pasos pr\u00e1cticos",
         "<ul>"
         "<li>Pida los registros m\u00e9dicos del asilo por escrito.</li>"
         "<li>Reporte a Long-Term Care Ombudsman y al CDPH (California Department of Public Health).</li>"
         "<li>Si hay riesgo inmediato, considere mover a su familiar.</li>"
         "<li>Pida una revisi\u00f3n confidencial del caso.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n urgente",
         "<ul>"
         "<li>\u00dalceras etapa 3 o 4 con hospitalizaci\u00f3n.</li>"
         "<li>Fractura por ca\u00edda no atendida.</li>"
         "<li>Sepsis o muerte inesperada.</li>"
         "<li>Asilo se niega a entregar registros.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfQu\u00e9 cuenta como negligencia legal?",
         "Cuando el asilo incumple los est\u00e1ndares razonables de cuidado y eso causa da\u00f1o real al residente."),
        ("\u00bfPuedo reclamar despu\u00e9s del fallecimiento?",
         "S\u00ed. La familia puede tener un reclamo por elder abuse o por muerte injusta."),
        ("\u00bfQu\u00e9 documentos son cr\u00edticos?",
         "Registros m\u00e9dicos, fotos con fecha, notas de visita y comunicaciones por escrito."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
        ("\u00bfCu\u00e1l es el plazo legal?",
         "Generalmente 2 a\u00f1os, aunque hay reglas espec\u00edficas para casos de elder abuse y muerte injusta."),
    ],
    related=[
        ("\u00dalceras por presi\u00f3n y negligencia", "/es/ulceras-presion-negligencia-asilo-ancianos/"),
        ("Muerte injusta", "/es/lesiones-personales/muerte-injusta/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.8,
    sitemap_changefreq="monthly",
    breadcrumb_label="Asilos de Ancianos LA",
))


# 29. /es/ulceras-presion-negligencia-asilo-ancianos/
_add(Page(
    en_path="/pressure-ulcers-nursing-home-neglect",
    es_path="/es/ulceras-presion-negligencia-asilo-ancianos/",
    title="\u00dalceras por presi\u00f3n (bedsores) y negligencia en asilos | Lo que debe saber",
    description=(
        "Las \u00falceras por presi\u00f3n etapa 3 y 4 suelen ser una se\u00f1al de negligencia en asilos. Qu\u00e9 son, c\u00f3mo se "
        "previenen y c\u00f3mo proteger a su familiar."
    ),
    h1="\u00dalceras por presi\u00f3n (bedsores): cu\u00e1ndo son negligencia",
    lead=(
        "Las \u00falceras por presi\u00f3n son lesiones de la piel y tejido por presi\u00f3n prolongada. En la mayor\u00eda de los "
        "casos son <em>prevenibles</em> si el personal del asilo cumple con los est\u00e1ndares de reposicionamiento y cuidado."
    ),
    sections=[
        ("Etapas de la \u00falcera",
         "<ul>"
         "<li><strong>Etapa 1:</strong> piel enrojecida que no blanquea al presionar.</li>"
         "<li><strong>Etapa 2:</strong> p\u00e9rdida parcial de la piel, ampolla o herida abierta.</li>"
         "<li><strong>Etapa 3:</strong> p\u00e9rdida total de piel, tejido visible.</li>"
         "<li><strong>Etapa 4:</strong> exposici\u00f3n de m\u00fasculo, hueso o tend\u00f3n.</li>"
         "</ul>"),
        ("Por qu\u00e9 se consideran negligencia",
         "<ul>"
         "<li>Falta de reposicionamiento cada 2 horas.</li>"
         "<li>No mover al residente con movilidad limitada.</li>"
         "<li>Ropa o pa\u00f1ales mojados sin cambiar.</li>"
         "<li>Falta de hidrataci\u00f3n y nutrici\u00f3n.</li>"
         "<li>Ignorar lesiones tempranas hasta que avanzan.</li>"
         "</ul>"),
        ("Qu\u00e9 hacer si su familiar tiene una \u00falcera",
         "<ul>"
         "<li>Tome fotos con fecha y regla para escala.</li>"
         "<li>Pida los registros m\u00e9dicos completos.</li>"
         "<li>Pida cambio de plan de cuidado por escrito.</li>"
         "<li>Reporte a CDPH y al Ombudsman.</li>"
         "<li>Solicite una revisi\u00f3n confidencial del caso.</li>"
         "</ul>"),
    ],
    faqs=[
        ("\u00bfTodas las \u00falceras son negligencia?",
         "No. Algunas son inevitables en pacientes muy enfermos, pero las etapas 3 y 4 suelen indicar fallas de cuidado."),
        ("\u00bfQu\u00e9 estandar deben cumplir los asilos?",
         "Las regulaciones federales y estatales exigen evaluaci\u00f3n de riesgo, reposicionamiento y planes individualizados."),
        ("\u00bfPuedo cambiar a mi familiar de asilo?",
         "S\u00ed. Documente la condici\u00f3n antes y despu\u00e9s del cambio."),
        ("\u00bfCu\u00e1l es el plazo legal?",
         "Reglas espec\u00edficas para elder abuse y muerte injusta. Conviene revisar pronto."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Negligencia en asilos LA", "/es/abogado-negligencia-asilo-ancianos-los-angeles/"),
        ("Muerte injusta", "/es/lesiones-personales/muerte-injusta/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="\u00dalceras por Presi\u00f3n",
))


# 30. /es/lesiones-personales/muerte-injusta/
_add(Page(
    en_path="/personal-injury/wrongful-death",
    es_path="/es/lesiones-personales/muerte-injusta/",
    title="Reclamos por muerte injusta en California | Apoyo para la familia",
    description=(
        "Reclamos por muerte injusta (wrongful death) en California: qui\u00e9n puede reclamar, qu\u00e9 da\u00f1os, plazos "
        "y revisi\u00f3n del caso."
    ),
    h1="Reclamos por muerte injusta en California",
    lead=(
        "Cuando una persona muere por negligencia de otra, la familia sobreviviente puede presentar un reclamo de "
        "muerte injusta. Es separado del proceso penal y busca compensaci\u00f3n por la p\u00e9rdida que sufre la familia."
    ),
    sections=[
        ("Qui\u00e9n puede reclamar",
         "<ul>"
         "<li>C\u00f3nyuge sobreviviente.</li>"
         "<li>Pareja dom\u00e9stica registrada.</li>"
         "<li>Hijos.</li>"
         "<li>Otros dependientes financieros en algunos casos.</li>"
         "</ul>"),
        ("Da\u00f1os que pueden reclamarse",
         "<ul>"
         "<li>Gastos funerarios y de entierro.</li>"
         "<li>P\u00e9rdida de apoyo financiero futuro.</li>"
         "<li>P\u00e9rdida de servicios del hogar.</li>"
         "<li>P\u00e9rdida de compa\u00f1\u00eda, afecto y orientaci\u00f3n.</li>"
         "<li>Gastos m\u00e9dicos hasta el fallecimiento.</li>"
         "</ul>"),
        ("Causas comunes",
         "<ul>"
         "<li>Accidente de auto, cami\u00f3n o motocicleta.</li>"
         "<li>Atropello de peat\u00f3n.</li>"
         "<li>Negligencia en asilo de ancianos.</li>"
         "<li>Negligencia m\u00e9dica.</li>"
         "<li>Accidente laboral por falta de seguridad.</li>"
         "</ul>"),
        ("Plazos",
         "<p>Generalmente 2 a\u00f1os desde el fallecimiento. Casos contra entidades p\u00fablicas tienen plazo m\u00e1s corto (6 meses).</p>"),
    ],
    faqs=[
        ("\u00bfTengo que esperar a que termine el caso penal?",
         "No. El reclamo civil es independiente."),
        ("\u00bfPuedo reclamar si no estaba casado legalmente?",
         "Depende. Hijos y dependientes financieros tambi\u00e9n tienen opciones."),
        ("\u00bfQu\u00e9 evidencia se preserva?",
         "Reporte policial, autopsia, registros m\u00e9dicos, fotos y testigos."),
        ("\u00bfCu\u00e1nto tarda el caso?",
         "Depende del responsable y la cobertura. Algunos resuelven en menos de un a\u00f1o, otros toman m\u00e1s."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
    ],
    related=[
        ("Negligencia en asilos LA", "/es/abogado-negligencia-asilo-ancianos-los-angeles/"),
        ("Gu\u00eda de reclamos por lesiones", "/es/lesiones-personales/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Muerte Injusta",
))


# 31. /es/lesiones-personales/lesion-cerebral/
_add(Page(
    en_path="/personal-injury/brain-injuries",
    es_path="/es/lesiones-personales/lesion-cerebral/",
    title="Reclamos por lesi\u00f3n cerebral en California | Conmoci\u00f3n y TBI",
    description=(
        "Lesi\u00f3n cerebral traum\u00e1tica (TBI) y conmoci\u00f3n cerebral en California: s\u00edntomas, tratamiento y revisi\u00f3n del caso."
    ),
    h1="Reclamos por lesi\u00f3n cerebral (TBI) en California",
    lead=(
        "Las lesiones cerebrales traum\u00e1ticas (TBI) y las conmociones cerebrales pueden tener efectos largos: "
        "memoria, sue\u00f1o, concentraci\u00f3n, emociones. A veces se subestiman porque \u201cse ven bien\u201d por fuera."
    ),
    sections=[
        ("S\u00edntomas comunes",
         "<ul>"
         "<li>Dolores de cabeza persistentes.</li>"
         "<li>Mareo, n\u00e1usea, sensibilidad a la luz.</li>"
         "<li>Confusi\u00f3n, problemas de memoria.</li>"
         "<li>Cambios de humor.</li>"
         "<li>Dificultad para dormir.</li>"
         "</ul>"),
        ("Por qu\u00e9 importan en el reclamo",
         "<p>Las TBI pueden afectar la capacidad para trabajar, estudiar y vivir como antes. La documentaci\u00f3n "
         "con neur\u00f3logo, neuropsic\u00f3logo o terapia cognitiva es clave para el valor del caso.</p>"),
        ("Evidencia que ayuda",
         "<ul>"
         "<li>Im\u00e1genes m\u00e9dicas (MRI/CT).</li>"
         "<li>Notas del m\u00e9dico de cabecera, neur\u00f3logo y terapia.</li>"
         "<li>Diario de s\u00edntomas.</li>"
         "<li>Testimonios de familiares sobre cambios.</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n",
         "<p>Cuando hay s\u00edntomas persistentes despu\u00e9s de 2-4 semanas, cuando hubo p\u00e9rdida de conciencia, o "
         "cuando la aseguranza minimiza el caso porque \u201clas im\u00e1genes son normales\u201d.</p>"),
    ],
    faqs=[
        ("\u00bfLas conmociones son siempre graves?",
         "No, pero pueden serlo. Conmociones repetidas o sin seguimiento adecuado pueden tener efectos prolongados."),
        ("\u00bfMi MRI fue normal, eso afecta el caso?",
         "No necesariamente. Algunas lesiones no se ven en im\u00e1genes pero s\u00ed afectan funci\u00f3n. La evaluaci\u00f3n neuropsicol\u00f3gica ayuda."),
        ("\u00bfQu\u00e9 tipo de m\u00e9dico debo ver?",
         "Empiece con su m\u00e9dico de cabecera; \u00e9l puede referir a neur\u00f3logo o neuropsicolog\u00eda."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
        ("\u00bfCu\u00e1l es el plazo legal?",
         "Generalmente 2 a\u00f1os; 6 meses contra entidades p\u00fablicas."),
    ],
    related=[
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
        ("Lesiones catastr\u00f3ficas", "/es/lesiones-personales/lesiones-catastroficas/"),
        ("Lesiones de columna", "/es/lesiones-personales/lesiones-columna/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Lesi\u00f3n Cerebral",
))


# 32. /es/lesiones-personales/lesiones-columna/
_add(Page(
    en_path="/personal-injury/spine-injuries",
    es_path="/es/lesiones-personales/lesiones-columna/",
    title="Reclamos por lesi\u00f3n de columna en California | Herniaci\u00f3n y fusi\u00f3n",
    description=(
        "Reclamos por lesi\u00f3n de columna en California: herniaci\u00f3n de disco, fusi\u00f3n, dolor cr\u00f3nico y revisi\u00f3n del caso."
    ),
    h1="Reclamos por lesiones de columna en California",
    lead=(
        "Las lesiones de columna pueden ir desde dolor cr\u00f3nico de espalda hasta hernias de disco que requieren "
        "cirug\u00eda. El valor del caso depende del diagn\u00f3stico, las im\u00e1genes m\u00e9dicas y el impacto en la vida diaria."
    ),
    sections=[
        ("Tipos comunes de lesi\u00f3n",
         "<ul>"
         "<li>Hernia o protrusi\u00f3n de disco.</li>"
         "<li>Lumbalgia cr\u00f3nica.</li>"
         "<li>Lesi\u00f3n cervical (cuello).</li>"
         "<li>Fractura vertebral.</li>"
         "<li>Lesi\u00f3n medular (en casos catastr\u00f3ficos).</li>"
         "</ul>"),
        ("Tratamiento t\u00edpico",
         "<ul>"
         "<li>Terapia f\u00edsica.</li>"
         "<li>Inyecciones epidurales.</li>"
         "<li>Manejo del dolor.</li>"
         "<li>Cirug\u00eda (microdiscectom\u00eda, fusi\u00f3n) en casos serios.</li>"
         "</ul>"),
        ("Evidencia que fortalece el caso",
         "<ul>"
         "<li>MRI con hallazgos positivos.</li>"
         "<li>Notas que conecten la lesi\u00f3n con el accidente.</li>"
         "<li>Tratamiento consistente sin grandes gaps.</li>"
         "<li>Recomendaciones quir\u00fargicas.</li>"
         "</ul>"),
        ("Por qu\u00e9 la aseguranza minimiza",
         "<ul>"
         "<li>Argumenta que era condici\u00f3n preexistente.</li>"
         "<li>Etiqueta el caso como \u201cdolor de espalda gen\u00e9rico\u201d.</li>"
         "<li>Cuestiona los gaps de tratamiento.</li>"
         "</ul>"
         "<p>California permite recuperar por agravaci\u00f3n de condiciones preexistentes \u2014 la documentaci\u00f3n marca la diferencia.</p>"),
    ],
    faqs=[
        ("\u00bfPuedo reclamar si ya ten\u00eda dolor de espalda?",
         "S\u00ed. California permite recuperar por agravaci\u00f3n de condiciones preexistentes."),
        ("\u00bfTengo que tener cirug\u00eda para tener caso?",
         "No. Casos con tratamiento conservador tambi\u00e9n pueden tener valor."),
        ("\u00bfCu\u00e1nto vale un caso de hernia?",
         "Depende de los s\u00edntomas, im\u00e1genes y tratamiento. La revisi\u00f3n gratuita da una idea realista."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
        ("\u00bfCu\u00e1l es el plazo legal?", "Generalmente 2 a\u00f1os; 6 meses contra entidades p\u00fablicas."),
    ],
    related=[
        ("Lesi\u00f3n cerebral", "/es/lesiones-personales/lesion-cerebral/"),
        ("Lesiones catastr\u00f3ficas", "/es/lesiones-personales/lesiones-catastroficas/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Lesiones de Columna",
))


# 33. /es/lesiones-personales/lesiones-catastroficas/
_add(Page(
    en_path="/personal-injury/catastrophic-injuries",
    es_path="/es/lesiones-personales/lesiones-catastroficas/",
    title="Lesiones catastr\u00f3ficas en California | Casos serios",
    description=(
        "Lesiones catastr\u00f3ficas en California: lesi\u00f3n cerebral severa, par\u00e1lisis, quemaduras, amputaciones y revisi\u00f3n urgente."
    ),
    h1="Lesiones catastr\u00f3ficas en California",
    lead=(
        "Las lesiones catastr\u00f3ficas cambian la vida del lesionado y de su familia. Requieren tratamiento prolongado, "
        "cuidados especializados y una valoraci\u00f3n cuidadosa de la cobertura disponible."
    ),
    sections=[
        ("Lesiones t\u00edpicas",
         "<ul>"
         "<li>Lesi\u00f3n cerebral severa (TBI).</li>"
         "<li>Lesi\u00f3n medular y par\u00e1lisis.</li>"
         "<li>Quemaduras graves.</li>"
         "<li>Amputaciones.</li>"
         "<li>Fracturas m\u00faltiples.</li>"
         "<li>Lesiones internas serias.</li>"
         "</ul>"),
        ("Por qu\u00e9 son distintos",
         "<ul>"
         "<li>Tratamiento m\u00e9dico de por vida en algunos casos.</li>"
         "<li>P\u00e9rdida permanente de capacidad para trabajar.</li>"
         "<li>Adaptaciones del hogar y del veh\u00edculo.</li>"
         "<li>Cuidados de enfermer\u00eda.</li>"
         "<li>Apoyo psicol\u00f3gico.</li>"
         "</ul>"),
        ("Cobertura y damages",
         "<ul>"
         "<li>Cobertura del responsable.</li>"
         "<li>P\u00f3lizas paraguas y comerciales.</li>"
         "<li>UM/UIM propia.</li>"
         "<li>Posibles demandados adicionales (empresas, fabricantes).</li>"
         "</ul>"),
        ("Cu\u00e1ndo pedir revisi\u00f3n urgente",
         "<p>Lo antes posible. La evidencia se pierde r\u00e1pido y las aseguranzas se mueven con investigadores propios. "
         "La revisi\u00f3n gratuita ayuda a entender qu\u00e9 preservar y c\u00f3mo proteger a la familia.</p>"),
    ],
    faqs=[
        ("\u00bfQu\u00e9 cuenta como catastr\u00f3fica?",
         "Lesiones permanentes, con impacto serio en la capacidad para trabajar y vivir como antes."),
        ("\u00bfCu\u00e1nto tarda este tipo de caso?",
         "Puede tomar m\u00e1s tiempo porque requiere proyectar tratamiento futuro y cobertura total."),
        ("\u00bfHay m\u00e1s de un demandado?",
         "Muchas veces s\u00ed: conductor, empresa, fabricante, propietario, etc."),
        ("\u00bfHablan espa\u00f1ol?", "S\u00ed."),
        ("\u00bfCu\u00e1ndo conviene actuar?",
         "Lo antes posible. La evidencia es cr\u00edtica en casos serios."),
    ],
    related=[
        ("Lesi\u00f3n cerebral", "/es/lesiones-personales/lesion-cerebral/"),
        ("Lesiones de columna", "/es/lesiones-personales/lesiones-columna/"),
        ("Accidente de auto grave", "/es/accidente-auto-grave/"),
    ],
    sitemap_priority=0.7,
    sitemap_changefreq="monthly",
    breadcrumb_label="Lesiones Catastr\u00f3ficas",
))


# ---------------------------------------------------------------------------
# Legal / privacy pages (link to English source for legal substance)
# ---------------------------------------------------------------------------

LEGAL_PAGES = [
    ("/privacy-policy", "/es/politica-privacidad/", "Pol\u00edtica de Privacidad",
     "Resumen en espa\u00f1ol de nuestra Pol\u00edtica de Privacidad. La versi\u00f3n oficial y completa en ingl\u00e9s es la que controla legalmente."),
    ("/legal-terms", "/es/terminos-legales/", "T\u00e9rminos Legales",
     "Resumen en espa\u00f1ol de los T\u00e9rminos y Condiciones. La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
    ("/disclaimer", "/es/aviso-legal/", "Aviso Legal",
     "Resumen en espa\u00f1ol del aviso legal del sitio. La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
    ("/cookie-policy", "/es/politica-cookies/", "Pol\u00edtica de Cookies",
     "Resumen en espa\u00f1ol de la Pol\u00edtica de Cookies. La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
    ("/california-privacy-rights", "/es/derechos-privacidad-california/", "Derechos de Privacidad de California",
     "Resumen en espa\u00f1ol de los derechos de privacidad de California (CCPA/CPRA). La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
    ("/do-not-sell-or-share-my-personal-information", "/es/no-vender-compartir-informacion-personal/", "No Vender ni Compartir Mi Informaci\u00f3n Personal",
     "C\u00f3mo solicitar que no se venda ni comparta su informaci\u00f3n personal. La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
    ("/accessibility", "/es/accesibilidad/", "Accesibilidad",
     "Declaraci\u00f3n de accesibilidad del sitio en espa\u00f1ol. La versi\u00f3n oficial en ingl\u00e9s es la que controla legalmente."),
]

for en_p, es_p, label, summary in LEGAL_PAGES:
    _add(Page(
        en_path=en_p,
        es_path=es_p,
        title=f"{label} | Insider Lawyers en Espa\u00f1ol",
        description=summary,
        h1=label,
        lead=summary,
        sections=[
            ("Versi\u00f3n oficial en ingl\u00e9s",
             f"<p>El texto oficial y completo de esta p\u00e1gina est\u00e1 en ingl\u00e9s. Por favor consulte la "
             f"<a href=\"{en_p}\" lang=\"en\" hreflang=\"en\">versi\u00f3n en ingl\u00e9s</a> para los t\u00e9rminos legales vigentes. "
             f"Esta p\u00e1gina ofrece un resumen general en espa\u00f1ol \u00fanicamente como cortes\u00eda. En caso de conflicto, "
             f"prevalece el texto en ingl\u00e9s.</p>"),
            ("Resumen",
             f"<p>{summary}</p>"
             "<p>Si tiene alguna pregunta sobre privacidad, datos personales, cookies, accesibilidad o sus "
             "derechos como residente de California, puede contactarnos al "
             "<a href=\"tel:844-467-4335\" class=\"phone-link\" data-callrail-phone=\"844-467-4335\">844-467-4335</a> "
             "o por la <a href=\"/es/contacto/\">p\u00e1gina de contacto</a>.</p>"),
            ("Sus derechos clave",
             "<ul>"
             "<li>Solicitar acceso a la informaci\u00f3n personal que tenemos sobre usted.</li>"
             "<li>Solicitar la correcci\u00f3n de informaci\u00f3n incorrecta.</li>"
             "<li>Solicitar la eliminaci\u00f3n de su informaci\u00f3n personal.</li>"
             "<li>Solicitar que no se venda ni comparta su informaci\u00f3n personal.</li>"
             "<li>No ser discriminado por ejercer sus derechos.</li>"
             "</ul>"),
        ],
        faqs=[
            ("\u00bfD\u00f3nde est\u00e1 la versi\u00f3n oficial?",
             f"La versi\u00f3n oficial est\u00e1 en ingl\u00e9s en <a href=\"{en_p}\" lang=\"en\" hreflang=\"en\">{en_p}</a>. Si hay diferencia, prevalece el ingl\u00e9s."),
            ("\u00bfPuedo hacer mi solicitud de privacidad en espa\u00f1ol?",
             "S\u00ed. Puede llamar o usar la <a href=\"/es/contacto/\">p\u00e1gina de contacto</a>."),
            ("\u00bfQu\u00e9 pasa si no estoy de acuerdo con el tratamiento de mis datos?",
             "Puede ejercer sus derechos de privacidad por escrito o por tel\u00e9fono. La respuesta puede tomar hasta 45 d\u00edas."),
        ],
        related=[
            ("Pol\u00edtica de Privacidad", "/es/politica-privacidad/"),
            ("T\u00e9rminos Legales", "/es/terminos-legales/"),
            ("Aviso Legal", "/es/aviso-legal/"),
            ("Pol\u00edtica de Cookies", "/es/politica-cookies/"),
            ("Derechos de Privacidad de California", "/es/derechos-privacidad-california/"),
            ("No Vender ni Compartir", "/es/no-vender-compartir-informacion-personal/"),
            ("Accesibilidad", "/es/accesibilidad/"),
            ("Contacto", "/es/contacto/"),
        ],
        sitemap_priority=0.3,
        sitemap_changefreq="yearly",
        breadcrumb_label=label,
        page_kind="legal",
        legal_source=en_p,
    ))


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def render_breadcrumb(p: Page) -> str:
    parts = [('<a href="/es/">Inicio</a>',)]
    crumb = p.breadcrumb_label
    return (
        '<nav class="breadcrumb breadcrumb--plain" aria-label="Breadcrumb">'
        '<div class="container">'
        '<a href="/es/">Inicio</a> '
        '<span class="breadcrumb__sep">&gt;</span> '
        f'<span class="breadcrumb__current">{escape(crumb)}</span>'
        '</div></nav>'
    )


def render_faq_schema(p: Page) -> str:
    if not p.faqs:
        return ""
    main = []
    for q, a in p.faqs:
        clean = re.sub(r"<[^>]+>", "", a)
        clean = clean.replace("\n", " ").strip()
        main.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": clean}})
    data = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "es", "mainEntity": main}
    return f"<script type=\"application/ld+json\">{json.dumps(data, ensure_ascii=False)}</script>"


def render_article_schema(p: Page) -> str:
    if p.schema_type == "WebSite":
        data = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Insider Lawyers en Espa\u00f1ol",
            "alternateName": "Recurso de reclamos por lesiones en California",
            "url": p.es_url,
            "inLanguage": "es",
            "description": p.description,
            "publisher": {"@type": "Organization", "name": "Insider Lawyers", "url": SITE + "/", "telephone": "+1-844-467-4335"},
        }
    else:
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": p.h1,
            "url": p.es_url,
            "inLanguage": "es",
            "description": p.description,
            "isPartOf": {"@type": "WebSite", "name": "Insider Lawyers", "url": SITE + "/"},
        }
    return f"<script type=\"application/ld+json\">{json.dumps(data, ensure_ascii=False)}</script>"


def render_hreflang(p: Page) -> str:
    return "\n".join([
        f'<link rel="alternate" hreflang="en" href="{p.en_url}">',
        f'<link rel="alternate" hreflang="es" href="{p.es_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{p.en_url}">',
    ])


def render_sections(p: Page) -> str:
    pieces = []
    for h2, body in p.sections:
        pieces.append(f"<h2>{h2}</h2>\n{body}")
    return "\n\n".join(pieces)


def render_faqs(p: Page) -> str:
    if not p.faqs:
        return ""
    items = []
    for q, a in p.faqs:
        items.append(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>')
    return '<h2 id="faqs">Preguntas frecuentes</h2>\n' + "\n".join(items)


def render_related(p: Page) -> str:
    if not p.related:
        return ""
    items = "\n".join(f'<li><a href="{href}">{escape(label)}</a></li>' for label, href in p.related)
    return f'<h2>P\u00e1ginas relacionadas</h2>\n<ul class="related-list">\n{items}\n</ul>'


def render_hero_image(p: Page) -> str:
    """Render the page's top editorial hero image (eagerly loaded, sized).

    Returns empty string if the page has no image (legal/contact pages, etc.).
    """
    if not p.hero_image:
        return ""
    src = SITE + p.hero_image if p.hero_image.startswith("/") else p.hero_image
    alt = escape(p.hero_image_alt or "")
    return (
        '<figure class="es-hero-img" aria-hidden="false">'
        f'<img src="{src}" alt="{alt}" '
        f'width="{p.hero_image_width}" height="{p.hero_image_height}" '
        'loading="eager" fetchpriority="high" decoding="async">'
        '</figure>'
    )


def render_section_image(p: Page, copy_heading: str, copy_body: str, flip: bool = False) -> str:
    """Render a 50/50 image+text strip lower on the page (lazy loaded).

    Returns empty string if the page has no secondary image.
    """
    if not p.section_image:
        return ""
    src = SITE + p.section_image if p.section_image.startswith("/") else p.section_image
    alt = escape(p.section_image_alt or "")
    cls = "es-inline-image es-inline-image--flip" if flip else "es-inline-image"
    return (
        f'<aside class="{cls}">'
        '<figure class="es-inline-image__media">'
        f'<img src="{src}" alt="{alt}" width="800" height="600" loading="lazy" decoding="async">'
        '</figure>'
        '<div class="es-inline-image__copy">'
        f'<h3>{copy_heading}</h3>'
        f'<p>{copy_body}</p>'
        '</div>'
        '</aside>'
    )


def render_content_page(p: Page) -> str:
    """Standard content page (most Tier 1 pages)."""

    hero_img_html = render_hero_image(p)
    section_img_html = render_section_image(
        p,
        copy_heading="\u00bfQuiere una revisi\u00f3n personal de su caso?",
        copy_body=(
            "Cu\u00e9ntenos brevemente lo que pas\u00f3 y un miembro del equipo le devuelve la "
            "llamada en espa\u00f1ol para revisar los hechos, la oferta y las opciones."
        ),
    )

    # Preload hero image on pages that have one (improves LCP).
    preload_hero = ""
    if p.hero_image:
        src = SITE + p.hero_image if p.hero_image.startswith("/") else p.hero_image
        preload_hero = f'<link rel="preload" as="image" href="{src}" fetchpriority="high">'

    og_image = (SITE + p.hero_image) if p.hero_image else f"{SITE}/images/hero/ktown-bg.jpg"

    head = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<link rel=\"stylesheet\" href=\"/styles/main.css?v=2\">
<title>{escape(p.title)}</title>
<meta name=\"description\" content=\"{escape(p.description)}\">
<link rel=\"canonical\" href=\"{p.es_url}\">
{render_hreflang(p)}
<meta name=\"robots\" content=\"index,follow,max-image-preview:large\">
<meta property=\"og:type\" content=\"article\">
<meta property=\"og:title\" content=\"{escape(p.title)}\">
<meta property=\"og:description\" content=\"{escape(p.description)}\">
<meta property=\"og:url\" content=\"{p.es_url}\">
<meta property=\"og:locale\" content=\"es_US\">
<meta property=\"og:site_name\" content=\"Insider Lawyers\">
<meta property=\"og:image\" content=\"{og_image}\">
<meta name=\"twitter:card\" content=\"summary_large_image\">
<meta name=\"twitter:title\" content=\"{escape(p.title)}\">
<meta name=\"twitter:description\" content=\"{escape(p.description)}\">
<meta name=\"twitter:image\" content=\"{og_image}\">
{render_article_schema(p)}
{render_faq_schema(p)}
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\">
{preload_hero}
<style>{INLINE_CSS}</style>
{GTM_HEAD}
</head>
<body>
{GTM_NOSCRIPT}
{UTM_CAPTURE}
<header class=\"header header--unified\" id=\"header\"></header>
<main>
{render_breadcrumb(p)}
<section class=\"section-content\">
<div class=\"container\">
<div class=\"content-body\">
<h1>{escape(p.h1)}</h1>
<p class=\"lead-text\">{p.lead}</p>
{hero_img_html}
{cta_block("Solicite una revisi\u00f3n gratuita", "Cu\u00e9ntenos brevemente qu\u00e9 pas\u00f3 y d\u00f3nde est\u00e1 hoy el caso. Le explicamos sus opciones \u2014 incluida una segunda opini\u00f3n, revisi\u00f3n del acuerdo o consulta con un abogado si es necesario. Sin presi\u00f3n y sin compromiso. Enviar este formulario no crea una relaci\u00f3n abogado-cliente.")}
{render_sections(p)}
{section_img_html}
{cta_block("\u00bfTiene una oferta sobre la mesa? Rev\u00edsela primero.", "Antes de firmar un release o aceptar una liquidaci\u00f3n en California, repase la <a href=\"/es/lista-revision-liquidacion-lesiones-california/\">lista de revisi\u00f3n del acuerdo</a> y solicite una revisi\u00f3n gratuita. Una vez firmado, el reclamo generalmente se cierra.")}
{render_faqs(p)}
{render_related(p)}
<div class=\"disclaimer-block\">{DISCLAIMER_ES}</div>
<p style=\"margin-top:24px\"><a href=\"/es/#case-evaluation\" class=\"btn-primary\">Solicitar Revisi\u00f3n Gratuita</a> <a href=\"tel:844-467-4335\" class=\"btn-secondary\" data-callrail-phone=\"844-467-4335\">Llame al 844-467-4335</a></p>
</div>
</div>
</section>
</main>
<footer class=\"site-footer\" id=\"footer-contact\"></footer>
{BODY_END_SCRIPTS}
</body>
</html>
"""
    return head


def render_home(p: Page) -> str:
    """Spanish homepage - hero with lead form, same structure as English home."""
    head = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<meta name=\"description\" content=\"{escape(p.description)}\">
<link rel=\"canonical\" href=\"{p.es_url}\">
{render_hreflang(p)}
<title>{escape(p.title)}</title>
<link rel=\"stylesheet\" href=\"/styles/main.css?v=2\">
<link rel=\"stylesheet\" href=\"/styles/settlements.css?v=2\">
<link rel=\"preload\" as=\"image\" href=\"{SITE}/images/hero/ktown-bg.jpg\">
<link rel=\"preconnect\" href=\"{SITE}\">
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&display=swap\" media=\"print\" onload=\"this.media='all'\">
<noscript><link href=\"https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&display=swap\" rel=\"stylesheet\"></noscript>
{render_article_schema(p)}
{render_faq_schema_home()}
<meta property=\"og:type\" content=\"website\">
<meta property=\"og:title\" content=\"{escape(p.title)}\">
<meta property=\"og:description\" content=\"{escape(p.description)}\">
<meta property=\"og:url\" content=\"{p.es_url}\">
<meta property=\"og:locale\" content=\"es_US\">
<meta property=\"og:site_name\" content=\"Insider Lawyers\">
<meta property=\"og:image\" content=\"{SITE}/images/hero/ktown-bg.jpg\">
<style>
:root{{--brand-navy:#01366c;--brand-blue:#01468a;--brand-accent-yellow:#fbba00;--brand-gray-700:#374151;}}
html{{scroll-behavior:smooth;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#212121;min-height:100vh;-webkit-font-smoothing:antialiased;}}
.container{{width:100%;max-width:1400px;margin:0 auto;padding:0 24px;}}
.hero.hero-section{{position:relative;min-height:100vh;display:flex;align-items:center;padding:2rem 0 5rem;background-color:#0c2334;background-image:linear-gradient(135deg,rgba(12,35,52,0.92) 0%,rgba(1,54,108,0.88) 50%,rgba(1,42,82,0.9) 100%),url('{SITE}/images/hero/ktown-bg.jpg');background-size:cover;background-position:center;background-repeat:no-repeat;color:#fff;filter:contrast(1.12);}}
.hero.hero-section .hero-text h1{{font-family:Roboto,Arial,sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-1px;line-height:1.2;margin-bottom:0.5em;font-size:2.1em;color:#fff;}}
@media(max-width:600px){{.hero.hero-section .hero-text h1{{font-size:1.4em;}}}}
@media(max-width:767px){{.hero.hero-section{{filter:none;}}.defer-mobile{{content-visibility:auto;contain-intrinsic-size:1px 900px;}}}}
.hero.hero-section .hero-subhead{{color:rgba(255,255,255,0.95);font-size:1.1rem;margin-bottom:0.5rem;}}
.hero.hero-section .hero-highlight{{color:var(--brand-accent-yellow);font-weight:700;}}
.btn-primary-cta{{display:inline-block;background:linear-gradient(180deg,#ffd54f 0%,#ffbf00 50%,#f5a623 100%);color:#01366c;font-weight:800;padding:1.1rem 1.5rem;border-radius:10px;text-decoration:none;border:none;cursor:pointer;font-size:1.2rem;box-shadow:0 4px 0 #c99400,0 6px 20px rgba(255,191,0,0.35);transition:transform 0.2s ease,box-shadow 0.2s ease;}}
.btn-primary-cta:hover{{transform:translateY(-3px);box-shadow:0 6px 0 #c99400,0 10px 28px rgba(255,191,0,0.45);}}
body:not(.loaded) *{{animation-play-state:paused;}}
.content-section h2{{color:#01366c;}}
.section-pad{{padding:2rem 0;}}
.fact-card{{background:#fff;border:1px solid #dce6f2;border-radius:12px;padding:1.25rem 1.4rem;margin-bottom:1rem;box-shadow:0 4px 14px rgba(1,54,108,0.05);display:flex;flex-direction:column;}}
.fact-card .fact-card__icon{{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:10px;background:linear-gradient(180deg,#eaf2fb,#dce8f6);color:#01366c;margin-bottom:0.55rem;flex:0 0 auto;}}
.fact-card .fact-card__icon svg{{width:22px;height:22px;}}
.fact-card h3{{color:#01366c;margin:0 0 0.4rem;font-size:1.1rem;}}
.fact-card p{{margin:0;color:#374151;line-height:1.6;font-size:0.96rem;}}
.fact-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;}}
.es-faq{{background:#fff;border:1px solid #dce6f2;border-radius:10px;padding:1.25rem;margin-bottom:1rem;}}
.es-faq h3{{color:#01366c;margin:0 0 0.5rem;font-size:1.1rem;}}
.es-faq p{{margin:0;color:#374151;line-height:1.6;}}
/* Spanish homepage: supporting claim-review image + trust strip */
.es-home-support{{display:grid;grid-template-columns:5fr 6fr;gap:32px;align-items:center;margin:0 auto 0.5rem;max-width:1100px;}}
.es-home-support__media{{margin:0;border-radius:14px;overflow:hidden;box-shadow:0 12px 30px rgba(1,54,108,0.12);background:#eef2f7;}}
.es-home-support__media img{{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;}}
.es-home-support__copy h3{{color:#01366c;margin:0 0 0.5rem;font-size:1.35rem;}}
.es-home-support__copy p{{margin:0 0 0.6rem;color:#374151;font-size:1rem;line-height:1.65;}}
.es-home-support__copy ul{{margin:0.4rem 0 0 1.1rem;padding:0;color:#374151;}}
.es-home-support__copy ul li{{margin:0.25rem 0;}}
.es-trust-bar{{background:linear-gradient(180deg,#01468a 0%,#01366c 100%);color:#fff;text-align:center;padding:1rem 1.25rem;border-radius:12px;margin:1.25rem auto 0;max-width:1100px;font-size:0.95rem;line-height:1.55;}}
.es-trust-bar strong{{color:#fbba00;}}
@media(max-width:760px){{.es-home-support{{grid-template-columns:1fr;gap:18px;}}}}
</style>
{FORM_TRACKING_INLINE}
{GTM_HEAD}
</head>
<body class=\"ppc-page landing-page\">
{GTM_NOSCRIPT}
{UTM_CAPTURE}
<header class=\"header header--unified\" id=\"header\"></header>
<section class=\"hero hero-section\" id=\"case-evaluation\">
  <div class=\"container\">
    <div class=\"hero-content\">
      <div class=\"hero-text\">
        <h1>{escape(p.h1)}</h1>
        <p class=\"hero-subhead\" style=\"margin-bottom:0.5rem; font-size:1.05rem; color:rgba(255,255,255,0.95);\">{p.lead}</p>
        <ul class=\"hero__benefits hero__benefits--large list-style\" style=\"list-style:none; padding:0; margin:0.5rem 0 1rem 0;\">
          <li><span class=\"hero-highlight\">Revisi\u00f3n gratuita del reclamo</span></li>
          <li><span class=\"hero-highlight\">Segunda opini\u00f3n sobre su caso</span></li>
          <li><span class=\"hero-highlight\">Revisi\u00f3n de la oferta antes de firmar</span></li>
        </ul>
        <p style=\"margin-top:1rem;\"><a href=\"#case-evaluation\" class=\"btn-primary-cta\">Revise su reclamo gratis</a> <a href=\"tel:844-467-4335\" class=\"phone-link\" data-callrail-phone=\"844-467-4335\" style=\"display:inline-block;margin-left:0.5rem;color:#fbba00;font-weight:700;text-decoration:underline;font-size:1.1rem;\">o llame al 844-467-4335</a></p>
      </div>
      <div class=\"hero-form-column\" style=\"width:100%;\">
        <style>
        #ial-hero-form-card{{background:linear-gradient(180deg,#2878b5 0%,#1e6a9e 50%,#165c8a 100%)!important;border:2px solid rgba(255,255,255,0.3)!important;border-radius:12px!important;padding:2rem!important;box-shadow:0 12px 40px rgba(1,54,108,0.25)!important;text-align:center!important;}}
        #ial-hero-form-card *{{box-sizing:border-box;}}
        #ial-hero-form-card .ial-badge{{display:inline-block!important;background:rgba(251,186,0,0.35)!important;color:#fff!important;font-size:0.85rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.06em!important;padding:0.5rem 1.25rem!important;border-radius:999px!important;border:1px solid rgba(251,186,0,0.5)!important;margin-bottom:12px!important;}}
        #ial-hero-form-card .ial-heading{{font-size:1.5rem!important;font-weight:700!important;color:#fff!important;margin:0 0 0.5rem!important;line-height:1.25!important;text-align:center!important;}}
        #ial-hero-form-card .ial-intro{{font-size:1.05rem!important;color:rgba(255,255,255,0.95)!important;text-align:center!important;margin:0 0 1.5rem!important;line-height:1.5!important;}}
        #ial-hero-form-card .ial-label{{display:block!important;font-size:0.9rem!important;font-weight:700!important;color:#fff!important;margin-bottom:0.4rem!important;text-transform:uppercase!important;letter-spacing:0.05em!important;text-align:center!important;}}
        #ial-hero-form-card .ial-input{{display:block!important;width:100%!important;padding:0.85rem 1rem!important;border:2px solid rgba(255,255,255,0.35)!important;border-radius:8px!important;font-size:1rem!important;background:#fff!important;color:#1f2937!important;margin-bottom:1rem!important;-webkit-appearance:none!important;appearance:none!important;}}
        #ial-hero-form-card .ial-input:focus{{outline:none!important;border-color:#fbba00!important;box-shadow:0 0 0 3px rgba(251,186,0,0.25)!important;}}
        #ial-hero-form-card .ial-input::placeholder{{color:#64748b!important;opacity:0.95!important;}}
        #ial-hero-form-card .ial-textarea{{min-height:90px!important;resize:vertical!important;}}
        #ial-hero-form-card .ial-checkbox-wrap{{display:flex!important;align-items:flex-start!important;gap:0.5rem!important;text-align:left!important;margin-bottom:0.75rem!important;}}
        #ial-hero-form-card .ial-checkbox-wrap input[type=checkbox]{{margin-top:0.25rem!important;flex-shrink:0!important;accent-color:#fbba00!important;}}
        #ial-hero-form-card .ial-checkbox-label{{font-size:0.85rem!important;color:rgba(255,255,255,0.92)!important;line-height:1.4!important;font-weight:500!important;}}
        #ial-hero-form-card .ial-submit{{display:block!important;width:100%!important;padding:1.1rem 1.5rem!important;font-size:1.15rem!important;font-weight:800!important;color:#fff!important;background:linear-gradient(180deg,#fbba00 0%,#e5a800 100%)!important;border:none!important;border-radius:10px!important;cursor:pointer!important;text-transform:uppercase!important;letter-spacing:0.04em!important;margin-top:0.5rem!important;box-shadow:0 4px 14px rgba(251,186,0,0.4)!important;transition:transform 0.15s ease,box-shadow 0.15s ease!important;}}
        #ial-hero-form-card .ial-submit:hover{{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(251,186,0,0.5)!important;}}
        @media(max-width:991px){{#ial-hero-form-card{{padding:1.5rem 1.25rem!important;}}}}
        @media(max-width:600px){{#ial-hero-form-card{{padding:1.25rem 1rem!important;}}#ial-hero-form-card .ial-heading{{font-size:1.25rem!important;}}#ial-hero-form-card .ial-intro{{font-size:0.95rem!important;}}}}
        </style>
        <div id=\"ial-hero-form-card\">
          <div class=\"ial-badge\">Gratis y Confidencial</div>
          <h2 class=\"ial-heading\">Solicite una revisi\u00f3n gratuita</h2>
          <p class=\"ial-intro\">Cu\u00e9ntenos qu\u00e9 pas\u00f3. Nuestro equipo revisa el caso en espa\u00f1ol y le explica sus opciones \u2014 incluida una segunda opini\u00f3n, revisi\u00f3n del acuerdo o consulta con un abogado si tiene sentido. Enviar este formulario no crea una relaci\u00f3n abogado-cliente.</p>
          {FORM_HTML}
        </div>
      </div>
    </div>
  </div>
</section>
<section class=\"content-section defer-mobile section-pad\" style=\"background:#fff;padding-top:3rem;\">
  <div class=\"container\" style=\"max-width:1100px;\">
    <aside class=\"es-home-support\">
      <figure class=\"es-home-support__media\">
        <img src=\"{SITE}/images/insurance-adjuster-claim-valuation.jpg\" alt=\"Persona revisando documentos de un reclamo por lesiones en California junto a una calculadora\" width=\"800\" height=\"600\" loading=\"lazy\" decoding=\"async\">
      </figure>
      <div class=\"es-home-support__copy\">
        <h3>Una mirada neutral antes de firmar nada</h3>
        <p>La aseguranza tiene su propio equipo. Usted merece una mirada independiente y en espa\u00f1ol sobre lo que realmente vale su caso, qu\u00e9 cubre el seguro disponible y qu\u00e9 pasa si firma el <em>release</em>.</p>
        <ul>
          <li>Revisi\u00f3n gratuita y sin compromiso, en espa\u00f1ol.</li>
          <li>Le ayudamos a entender una oferta antes de aceptarla.</li>
          <li>No tiene que despedir a su abogado actual para pedir una segunda opini\u00f3n.</li>
        </ul>
      </div>
    </aside>
    <h2 style=\"text-align:center;color:#01366c;margin:2rem 0 0.5rem;\">Un recurso neutral para reclamos por lesiones en California</h2>
    <p style=\"text-align:center;color:#374151;max-width:760px;margin:0 auto 1.5rem;\">Insider Lawyers en espa\u00f1ol es un recurso para personas lesionadas en California que est\u00e1n revisando una oferta de la aseguranza, decidiendo si aceptar un acuerdo o evaluando si pedir una segunda opini\u00f3n sobre su caso actual.</p>
    <div class=\"fact-grid\">
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M3 5h12l2 2v12H3z\"/><path d=\"M7 9h6M7 13h6M7 17h4\"/></svg></span><h3>Revisi\u00f3n del reclamo</h3><p>Una mirada neutral a su caso \u2014 hechos, lesiones, cobertura y oferta. Le ayudamos a entender d\u00f3nde est\u00e1 hoy y qu\u00e9 sigue. <a href=\"/es/lesiones-personales/\">Vea la gu\u00eda de reclamos</a>.</p></div>
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><circle cx=\"11\" cy=\"11\" r=\"7\"/><path d=\"M21 21l-4.3-4.3\"/></svg></span><h3>Segunda opini\u00f3n</h3><p>Si su caso est\u00e1 estancado o no le est\u00e1n explicando el valor, puede pedir una <a href=\"/es/segunda-opinion-reclamo-lesiones-california/\">segunda opini\u00f3n</a> sin despedir a su abogado actual.</p></div>
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\"/><path d=\"M8 12l3 3 5-6\"/></svg></span><h3>Revisi\u00f3n del acuerdo</h3><p>Antes de firmar un release, repase la <a href=\"/es/lista-revision-liquidacion-lesiones-california/\">lista de revisi\u00f3n</a>. Una vez firmado, el reclamo generalmente se cierra.</p></div>
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M4 6h16M4 12h12M4 18h8\"/><path d=\"M18 18l3-3M18 18l3 3\"/></svg></span><h3>Carta de demanda</h3><p>Entienda qu\u00e9 es y qu\u00e9 debe incluir una <a href=\"/es/carta-demanda-lesiones-personales-california/\">carta de demanda</a> y c\u00f3mo afecta la negociaci\u00f3n.</p></div>
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M3 13l2-5h10l2 5\"/><path d=\"M3 13v5h16v-5\"/><circle cx=\"7\" cy=\"18\" r=\"1.5\"/><circle cx=\"15\" cy=\"18\" r=\"1.5\"/></svg></span><h3>Accidentes de auto</h3><p>Choque, conductor sin seguro, hit and run, peat\u00f3n, Uber/Lyft y otros tipos. <a href=\"/es/accidentes-vehiculos/\">Vea los tipos de accidente</a>.</p></div>
      <div class=\"fact-card\"><span class=\"fact-card__icon\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M4 21h16\"/><path d=\"M5 21v-7l7-5 7 5v7\"/><path d=\"M10 14h4v7h-4z\"/></svg></span><h3>Resbal\u00f3n y propiedad</h3><p>Cuando el due\u00f1o de un negocio o propiedad fue negligente. <a href=\"/es/responsabilidad-de-propiedad/\">Vea responsabilidad de propiedad</a>.</p></div>
    </div>
    <p class=\"es-trust-bar\">L\u00e9anos en espa\u00f1ol &middot; <strong>Revisi\u00f3n gratuita 24/7</strong> &middot; Enviar este formulario no crea una relaci\u00f3n abogado-cliente.</p>
  </div>
</section>
<section class=\"content-section defer-mobile section-pad\" style=\"background:#f8fbfe;border-top:1px solid #e5eef7;\">
  <div class=\"container\" style=\"max-width:1100px;\">
    <h2 style=\"text-align:center;color:#01366c;margin-bottom:1rem;\">Cu\u00e1ndo conviene pedir una revisi\u00f3n</h2>
    <div class=\"fact-grid\">
      <div class=\"fact-card\"><h3>La aseguranza ya hizo una oferta</h3><p>Antes de firmar, conviene revisar si la oferta incluye gastos m\u00e9dicos, tratamiento futuro, p\u00e9rdida de ingresos y dolor.</p></div>
      <div class=\"fact-card\"><h3>Su caso est\u00e1 estancado</h3><p>Si lleva meses sin movimiento o sin respuestas claras de su abogado, una segunda opini\u00f3n ayuda a aclarar.</p></div>
      <div class=\"fact-card\"><h3>Le presionan para firmar</h3><p>No firme un release sin entenderlo. Pida tiempo razonable y rev\u00edselo con alguien.</p></div>
      <div class=\"fact-card\"><h3>Lesiones serias o tratamiento prolongado</h3><p>Hospitalizaci\u00f3n, cirug\u00eda o terapia que sigue activa son se\u00f1ales de que el caso necesita una revisi\u00f3n cuidadosa.</p></div>
      <div class=\"fact-card\"><h3>Disputa de culpa</h3><p>California permite recuperar con culpa compartida. No deje que la aseguranza le asigne m\u00e1s culpa de la que la evidencia apoya.</p></div>
      <div class=\"fact-card\"><h3>Hablamos espa\u00f1ol</h3><p>Toda la revisi\u00f3n y comunicaci\u00f3n puede hacerse completamente en espa\u00f1ol.</p></div>
    </div>
    <p style=\"text-align:center;margin-top:1.5rem;\"><a href=\"#case-evaluation\" class=\"btn-primary-cta\" style=\"padding:0.95rem 1.4rem;font-size:1.05rem;\">Solicitar revisi\u00f3n gratuita</a> <a href=\"tel:844-467-4335\" class=\"phone-link\" data-callrail-phone=\"844-467-4335\" style=\"display:inline-block;margin-left:0.5rem;padding:0.95rem 1.4rem;background:#01468a;color:#fff;font-weight:700;border-radius:8px;text-decoration:none;font-size:1.05rem;\">Llamar 844-467-4335</a></p>
  </div>
</section>
<section class=\"content-section defer-mobile section-pad\" style=\"background:#fff;\">
  <div class=\"container\" style=\"max-width:820px;\">
    <h2 style=\"text-align:center;color:#01366c;margin-bottom:1.25rem;\">Preguntas frecuentes</h2>
    <div class=\"es-faq\"><h3>\u00bfLa revisi\u00f3n del reclamo es gratis?</h3><p>S\u00ed. La revisi\u00f3n inicial es gratuita y no crea una relaci\u00f3n abogado-cliente.</p></div>
    <div class=\"es-faq\"><h3>\u00bfPuedo pedir una segunda opini\u00f3n si ya tengo abogado?</h3><p>S\u00ed. Muchas personas piden una segunda opini\u00f3n cuando sienten que su caso est\u00e1 estancado o no reciben respuestas claras. No tiene que despedir a su abogado actual.</p></div>
    <div class=\"es-faq\"><h3>\u00bfQu\u00e9 pasa si la aseguranza ya me hizo una oferta?</h3><p>Antes de firmar, conviene revisar si la oferta considera sus gastos m\u00e9dicos, p\u00e9rdida de ingresos, dolor, tratamiento futuro y otros da\u00f1os posibles. <a href=\"/es/lista-revision-liquidacion-lesiones-california/\">Vea la lista de revisi\u00f3n</a>.</p></div>
    <div class=\"es-faq\"><h3>\u00bfCu\u00e1nto tiempo tengo para presentar un reclamo en California?</h3><p>Generalmente 2 a\u00f1os; 6 meses si es contra una entidad p\u00fablica. Casos de menores y descubrimiento tard\u00edo pueden tener reglas distintas.</p></div>
    <div class=\"es-faq\"><h3>\u00bfInsider Lawyers es un sitio informativo o un despacho de abogados?</h3><p>Es un recurso informativo y de revisi\u00f3n. Si su caso parece necesitar representaci\u00f3n legal, es posible que un abogado calificado o un equipo legal se comunique con usted. Enviar informaci\u00f3n a trav\u00e9s del sitio no crea una relaci\u00f3n abogado-cliente.</p></div>
    <p style=\"text-align:center;margin-top:1.5rem;\"><a href=\"#case-evaluation\" class=\"btn-primary-cta\" style=\"padding:0.85rem 1.4rem;font-size:1.05rem;\">Solicitar revisi\u00f3n gratuita</a></p>
  </div>
</section>
<footer class=\"site-footer\" id=\"footer-contact\"></footer>
<script>window.addEventListener('load', function() {{ document.body.classList.add('loaded'); }});</script>
{BODY_END_SCRIPTS}
</body>
</html>
"""
    return head


def render_faq_schema_home() -> str:
    main = [
        ("\u00bfLa revisi\u00f3n del reclamo es gratis?", "S\u00ed. La revisi\u00f3n inicial es gratuita y no crea una relaci\u00f3n abogado-cliente."),
        ("\u00bfPuedo pedir una segunda opini\u00f3n si ya tengo abogado?", "S\u00ed. No tiene que despedir a su abogado actual para pedir una segunda opini\u00f3n."),
        ("\u00bfQu\u00e9 pasa si la aseguranza ya me hizo una oferta?", "Antes de firmar, conviene revisar si la oferta considera sus gastos m\u00e9dicos, p\u00e9rdida de ingresos, dolor, tratamiento futuro y otros da\u00f1os posibles."),
        ("\u00bfCu\u00e1nto tiempo tengo para presentar un reclamo en California?", "Generalmente 2 a\u00f1os; 6 meses si es contra una entidad p\u00fablica."),
        ("\u00bfInsider Lawyers es un sitio informativo o un despacho de abogados?", "Es un recurso informativo y de revisi\u00f3n. Si su caso parece necesitar representaci\u00f3n legal, es posible que un abogado calificado o un equipo legal se comunique con usted."),
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "es",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in main],
    }
    return f"<script type=\"application/ld+json\">{json.dumps(data, ensure_ascii=False)}</script>"


def render_page(p: Page) -> str:
    if p.page_kind == "home":
        return render_home(p)
    return render_content_page(p)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_pages() -> tuple[int, list[str]]:
    written = []
    for p in PAGES:
        html = render_page(p)
        p.fs_dir.mkdir(parents=True, exist_ok=True)
        p.fs_index.write_text(html, encoding="utf-8")
        written.append(p.es_path)
    return len(written), written


# Inject hreflang into matching English pages' <head>.
HREFLANG_BLOCK_RE = re.compile(
    r"<!-- ES_HREFLANG_START -->[\s\S]*?<!-- ES_HREFLANG_END -->\s*",
    flags=re.I,
)


def hreflang_block_for(p: Page) -> str:
    return (
        "<!-- ES_HREFLANG_START -->\n"
        f"<link rel=\"alternate\" hreflang=\"en\" href=\"{p.en_url}\">\n"
        f"<link rel=\"alternate\" hreflang=\"es\" href=\"{p.es_url}\">\n"
        f"<link rel=\"alternate\" hreflang=\"x-default\" href=\"{p.en_url}\">\n"
        "<!-- ES_HREFLANG_END -->\n"
    )


def english_index_for(en_path: str) -> Path | None:
    rel = en_path.strip("/")
    if rel == "":
        return ROOT / "index.html"
    candidate = ROOT / Path(rel) / "index.html"
    if candidate.is_file():
        return candidate
    candidate = ROOT / (rel + ".html")
    if candidate.is_file():
        return candidate
    return None


def inject_hreflang_into_english() -> tuple[int, list[str]]:
    updated: list[str] = []
    for p in PAGES:
        en_file = english_index_for(p.en_path)
        if not en_file:
            continue
        raw = en_file.read_text(encoding="utf-8", errors="replace")
        cleaned = HREFLANG_BLOCK_RE.sub("", raw)
        m = re.search(r"<link\s+rel=\"canonical\"[^>]*>", cleaned, flags=re.I)
        block = hreflang_block_for(p)
        if m:
            insert_at = m.end()
            new = cleaned[:insert_at] + "\n" + block + cleaned[insert_at:]
        else:
            m2 = re.search(r"<head[^>]*>", cleaned, flags=re.I)
            if not m2:
                continue
            insert_at = m2.end()
            new = cleaned[:insert_at] + "\n" + block + cleaned[insert_at:]
        if new != raw:
            en_file.write_text(new, encoding="utf-8")
            updated.append(p.en_path)
    return len(updated), updated


# ---------------------------------------------------------------------------
# Sitemap update
# ---------------------------------------------------------------------------
#
# As of June 2026 the sitemap system is owned by scripts/build_sitemaps.py,
# which emits a sitemap index plus categorised child sitemaps. This script
# no longer writes /sitemap.xml directly. It just delegates the sitemap
# refresh to the orchestrator so any future regeneration of Spanish pages
# automatically re-emits the categorised sitemap structure with the right
# Spanish entries.

def update_sitemap() -> tuple[int, list[str]]:
    try:
        import subprocess
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_sitemaps.py")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT),
        )
        # Surface the orchestrator's output for the operator.
        if out.stdout:
            print(out.stdout)
        if out.returncode != 0:
            sys.stderr.write(out.stderr or "")
    except Exception as exc:  # pragma: no cover
        print(f"warning: could not run build_sitemaps.py: {exc}")
    return len(PAGES), [p.es_path for p in PAGES]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    apply_image_map()
    n_pages, pages_paths = write_pages()
    n_en, en_paths = inject_hreflang_into_english()
    print(f"Spanish pages written: {n_pages}")
    for x in pages_paths:
        print("  ES", x)
    print(f"English pages updated with hreflang: {n_en}")
    for x in en_paths:
        print("  EN", x)
    # Delegate sitemap rebuild to the orchestrator (single source of truth).
    n_sm, _ = update_sitemap()
    print(f"Spanish entries delegated to build_sitemaps.py: {n_sm}")
    # Image coverage report.
    with_img = [p.es_path for p in PAGES if p.hero_image]
    without_img = [p.es_path for p in PAGES if not p.hero_image]
    print(f"Pages with hero image: {len(with_img)}")
    print(f"Pages intentionally without hero image: {len(without_img)}")
    for x in without_img:
        print("  no-img", x)


if __name__ == "__main__":
    main()
    sys.exit(0)
