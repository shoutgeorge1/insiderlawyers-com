# Add hero images to pages per image_mapping.json. Skips los-angeles-car-accident-lawyer.
$ErrorActionPreference = 'Stop'
$mapPath = "C:\Users\georgea\.cursor\projects\c-Users-georgea-insiderlawyer-com-images\image_mapping.json"
$lpRoot = "c:\Users\georgea\insiderlawyer-com-lps\pi-search-caraccident-lp"
$skipPaths = @{ 'los-angeles-car-accident-lawyer' = $true }

$raw = Get-Content $mapPath -Raw
$map = $raw | ConvertFrom-Json

function Get-PathFromUrl($url) {
    if (-not $url -or $url -eq 'https://www.insiderlawyers.com' -or $url -eq 'https://www.insiderlawyers.com/') { return '' }
    if ($url -eq 'https://www.insiderlawyers.com/index.html') { return '' }
    $u = [System.Uri]$url
    $p = $u.AbsolutePath.Trim('/')
    if ($p -eq 'index.html') { return '' }
    return $p
}

$byPath = @{}
foreach ($img in $map.images) {
    $p = Get-PathFromUrl $img.url
    if ($skipPaths[$p]) { continue }
    $byPath[$p] = @{ filename = $img.suggested_filename; alt = $img.alt_text }
}

$updated = 0
$skipped = 0
foreach ($key in $byPath.Keys) {
    $info = $byPath[$key]
    $indexPath = if ($key -eq '') { Join-Path $lpRoot "index.html" } else { Join-Path $lpRoot ($key -replace '/', '\') "index.html" }
    if (-not (Test-Path $indexPath)) { $skipped++; continue }

    $html = Get-Content $indexPath -Raw
    $altEscaped = $info.alt -replace '"', '&quot;'
    $heroBlock = "`n<div class=`"page-hero-img`"><img src=`"/images/$($info.filename)`" alt=`"$altEscaped`" width=`"800`" height=`"450`" loading=`"lazy`"></div>`n"

    if ($html -match 'page-hero-img|silo-hero-img') {
        if ($html -match "/images/$($info.filename)") { continue }
        if ($key -match '^motor-vehicle|^premises-liability') { continue }
        $html = $html -replace '(?s)(<div class="(?:page-hero-img|silo-hero-img)"[^>]*>\s*<img[^>]+src=")[^"]+', "`${1}/images/$($info.filename)`" alt=`"$altEscaped`" width=`"800`" height=`"450`" loading=`"lazy`"
        Set-Content $indexPath -Value $html -NoNewline
        $updated++
        continue
    }

    if ($html -match '(?s)(</h1>\s*)(\r?\n)(\s*)(<p |<div class="cta-row"|<div class="silo-|<ul |<h2 |<p>)') {
        $html = $html -replace '(?s)(</h1>\s*)(\r?\n)(\s*)(<p |<div class="cta-row"|<div class="silo-|<ul |<h2 |<p>)', ('$1$2$3' + $heroBlock + '$2$3$4')
        Set-Content $indexPath -Value $html -NoNewline
        $updated++
    } else {
        $html = $html -replace '(</h1>\s*)(\r?\n)', "`$1`$2$heroBlock`$2"
        if ($html -notmatch 'page-hero-img') { $skipped++ } else { Set-Content $indexPath -Value $html -NoNewline; $updated++ }
    }
}
Write-Output "Updated $updated pages. Skipped $skipped"
