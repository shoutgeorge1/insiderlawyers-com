# Indexability analysis - insiderlawyers-com
$ErrorActionPreference = "Stop"
$base = (Get-Location).Path
$exclude = '_old-site-extract|\\components\\|_dev|social-assets'

function Normalize-FilePathToUrlPath {
    param([string]$relPath)
    $relPath = $relPath -replace '\\', '/'
    if ($relPath -eq 'index.html') { return '/' }
    if ($relPath -match '^(.+)/index\.html$') { return '/' + $Matches[1] + '/' }
    $noExt = $relPath -replace '\.html$', ''
    return '/' + $noExt + '/'
}

function Normalize-LinkTarget {
    param([string]$href)
    $h = $href.Trim()
    if ($h -eq '' -or $h -eq '/') { return '/' }
    if ($h -match '^([^#]+)#') { $h = $Matches[1] }
    $h = $h.TrimEnd('/')
    if ($h -eq '') { return '/' }
    return $h + '/'
}

$htmlFiles = @()
Get-ChildItem -Path $base -Recurse -Filter "*.html" -File | Where-Object { $_.FullName -notmatch $exclude } | ForEach-Object {
    $rel = $_.FullName.Substring($base.Length + 1).Replace('\', '/')
    $htmlFiles += @{ RelPath = $rel; FullPath = $_.FullName }
}

$csvRows = @()
$allLinkTargets = @{}
$urlPathByFile = @{}

foreach ($f in $htmlFiles) {
    $relPath = $f.RelPath
    $urlPath = Normalize-FilePathToUrlPath -relPath $relPath
    $urlPathByFile[$relPath] = $urlPath
    $content = Get-Content -Path $f.FullPath -Raw -Encoding UTF8
    if (-not $content) { $content = '' }
    $hasCanonical = $content -match '<link\s+rel="canonical"'
    $hasTitle = $content -match '<title>'
    $noindex = ($content -match 'noindex') -or ($content -match 'robots[^>]*content="[^"]*noindex')
    $stripped = $content -replace '(?s)<script[^>]*>.*?</script>', ' '
    $stripped = $stripped -replace '(?s)<style[^>]*>.*?</style>', ' '
    $stripped = $stripped -replace '<[^>]+>', ' '
    $stripped = $stripped -replace '\s+', ' '
    $wordArr = [regex]::Split($stripped.Trim(), '\s+') | Where-Object { $_.Length -gt 0 }
    $words = $wordArr.Count
    $csvRows += [PSCustomObject]@{ path = $relPath; has_canonical = if ($hasCanonical) { '1' } else { '0' }; has_title = if ($hasTitle) { '1' } else { '0' }; noindex = if ($noindex) { '1' } else { '0' }; word_count = $words; url_path = $urlPath }
    $links = [regex]::Matches($content, 'href="(/(?:[^"#]*))"') | ForEach-Object { $_.Groups[1].Value }
    foreach ($link in $links) {
        $norm = Normalize-LinkTarget -href $link
        $allLinkTargets[$norm] = 1
    }
}

$allUrlPaths = @{}
foreach ($f in $htmlFiles) {
    $p = $urlPathByFile[$f.RelPath]
    $allUrlPaths[$p] = 1
}
$allUrlPaths['/'] = 1

$orphans = @()
foreach ($path in $allUrlPaths.Keys) {
    $normPath = $path
    if ($normPath -ne '/' -and -not $normPath.EndsWith('/')) { $normPath = $normPath + '/' }
    if (-not $allLinkTargets.ContainsKey($normPath)) { $orphans += $normPath }
}
$orphans = $orphans | Sort-Object

$indexContent = Get-Content -Path (Join-Path $base "index.html") -Raw -Encoding UTF8
$navFooterHrefs = [regex]::Matches($indexContent, 'href="(/(?:[^"#]*)?)"') | ForEach-Object { Normalize-LinkTarget -href $_.Groups[1].Value }
$mainNavTargets = @{}
foreach ($h in $navFooterHrefs) { $mainNavTargets[$h] = 1 }

$inMainNav = @()
$notInMainNav = @()
foreach ($path in ($allUrlPaths.Keys | Sort-Object)) {
    $normPath = $path
    if ($normPath -ne '/' -and -not $normPath.EndsWith('/')) { $normPath = $normPath + '/' }
    if ($mainNavTargets.ContainsKey($normPath)) { $inMainNav += $normPath } else { $notInMainNav += $normPath }
}

$uniqueTargets = $allLinkTargets.Keys | Sort-Object
$outPath = Join-Path $base "INDEXABILITY-ANALYSIS.txt"
$lines = @(
    "=== INDEXABILITY ANALYSIS ===",
    "Base: insiderlawyers-com (excluded: _old-site-extract, components, _dev, social-assets)",
    "",
    "--- CSV: path, has_canonical, has_title, noindex, word_count ---",
    "path,has_canonical,has_title,noindex,word_count"
)
$lines += ($csvRows | ForEach-Object { "$($_.path),$($_.has_canonical),$($_.has_title),$($_.noindex),$($_.word_count)" })
$lines += "", "--- All internal link targets (normalized) ---"
$lines += $uniqueTargets
$lines += "", "--- Orphan paths (never linked to by any page) ---"
$lines += $orphans
$lines += "", "--- Paths IN main nav (from index.html header nav + footer) ---"
$lines += ($inMainNav | Sort-Object)
$lines += "", "--- Paths NOT in main nav ---"
$lines += ($notInMainNav | Sort-Object)
$lines | Set-Content -Path $outPath -Encoding UTF8
"Done. Output: $outPath"
