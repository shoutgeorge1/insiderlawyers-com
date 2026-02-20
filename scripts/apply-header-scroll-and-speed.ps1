# Add header scroll-hide (scroll down = hide, scroll up = show) and PageSpeed tweaks to all LP index.html
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$headerScrollScript = @'
    <script>
      document.addEventListener('DOMContentLoaded',function(){var h=document.querySelector('.sticky-header');var ly=0;var nw=document.getElementById('header-nav-wrap');var mt=document.getElementById('mobile-menu-toggle');if(h){window.addEventListener('scroll',function(){if(window.innerWidth>767){h.classList.remove('header--hidden');return;}var y=window.scrollY;if(y>80){if(y>ly){h.classList.add('header--hidden');if(nw)nw.classList.remove('is-open');if(mt)mt.setAttribute('aria-expanded','false');}else h.classList.remove('header--hidden');}else h.classList.remove('header--hidden');ly=y;},{passive:true});}});
    </script>
'@

$cssHeaderHidden = "@media(max-width:767px){.sticky-header.header--hidden{transform:translateY(-100%)}}"
$transitionInSticky = ";transition:transform .25s ease"

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $_.FullName -notlike "*_old-site-extract*" -and $_.FullName -notlike "*\scripts\*"
}

$countScroll = 0
$countCss = 0
$countFont = 0
$countImg = 0

foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $changed = $false

    # 1. Add header scroll-hide script if missing (has sticky-header but no header--hidden logic)
    if ($html -match "sticky-header" -and $html -notmatch "header\.classList\.add\('header--hidden'\)" -and $html -notmatch "h\.classList\.add\('header--hidden'\)") {
        # Insert script before <header class="sticky-header">
        if ($html -match '</script>\s*<header class="sticky-header">' -and $html -notmatch 'header--hidden.*passive:true') {
            $html = $html -replace '(</script>)\s*(<header class="sticky-header">)', "`$1$headerScrollScript`$2"
            $changed = $true
            $countScroll++
        }
    }

    # 2. Add CSS for header--hidden and transition on .sticky-header if missing
    if ($html -match "sticky-header") {
        # Add transition to .sticky-header block if not present
        if ($html -match '\.sticky-header\{[^}]+\}' -and $html -notmatch '\.sticky-header\{[^}]*transition[^}]*\}') {
            $html = $html -replace '(\.sticky-header\{[^}]+)(box-shadow:[^}]+\})', "`$1`$2$transitionInSticky"
            $changed = $true
        }
        # Add media rule if not present (check for the actual CSS rule, not the class name in script)
        if ($html -match '@media\(max-width:900px\)' -and $html -notmatch '\.sticky-header\.header--hidden\{transform') {
            $html = $html -replace '(\s)(@media\(max-width:900px\))', "`$1$cssHeaderHidden`n`$1`$2"
            $changed = $true
            $countCss++
        }
    }

    # 3. Ensure Google Fonts has display=swap (avoid render-blocking)
    if ($html -match 'fonts\.googleapis\.com/css2\?' -and $html -notmatch 'display=swap') {
        $html = $html -replace '(&family=[^"&]+)(&display=[^"&]+)?(")', "`$1&display=swap`$3"
        $changed = $true
        $countFont++
    }

    # 4. Add width/height to content-hero-img to reduce CLS (use style or dimensions)
    if ($html -match 'content-hero-img' -and $html -match '<img\s+src="[^"]*custom/[^"]*"' -and $html -notmatch 'content-hero-img[^>]*>[\s\S]*?<img[^>]+width=') {
        # Add decoding="async" and fetchpriority="high" for LCP image; keep existing style
        $html = $html -replace '(<figure class="content-hero-img"[^>]*>)\s*<img(\s+src="[^"]*")', '${1}<img decoding="async"${2}'
        $changed = $true
        $countImg++
    }

    if ($changed) {
        [System.IO.File]::WriteAllText($f.FullName, $html, [System.Text.UTF8Encoding]::new($false))
    }
}

Write-Host "Header scroll script added: $countScroll | CSS header--hidden: $countCss | Font swap: $countFont | Img decoding: $countImg"
