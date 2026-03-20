# -*- coding: utf-8 -*-
"""Shared GTM head snippet (hostname allowlist). Use by concatenation — not in f-strings."""

GTM_HEAD_GUARD = """
<script>
(function() {

var allowedHosts = [
"insiderlawyers.com",
"www.insiderlawyers.com",
"insideraccidentlawyers.com",
"www.insideraccidentlawyers.com",
"call.insideraccidentlawyers.com"
];

if (allowedHosts.includes(window.location.hostname)) {

(function(w,d,s,l,i){
w[l]=w[l]||[];
w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});
var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
j.async=true;
j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;
f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WS8XT5FC');

}

})();
</script>
""".strip()
