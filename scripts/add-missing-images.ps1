# Add content-hero-img to every index.html that doesn't have it (except root).
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$imgBlock = "`n                <figure class=`"content-hero-img`" style=`"margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);`"><img src=`"https://images.unsplash.com/photo-1589829541223-0a0a6b628179?w=1200&amp;q=80`" alt=`"Legal and injury claim guidance`" style=`"width:100%;height:auto;display:block;`"></figure>`n                "

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/")
    $rel -ne "index.html" -and (Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8) -notmatch "content-hero-img"
}

$count = 0
foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $inserted = $false

    # Pattern 1: after first </p> inside <div class="content-body">
    if ($html -match '<div class="content-body">') {
        $idx = $html.IndexOf('<div class="content-body">')
        $firstP = $html.IndexOf('</p>', $idx)
        if ($firstP -ge 0) {
            $insertAt = $firstP + 4
            $html = $html.Substring(0, $insertAt) + $imgBlock + $html.Substring($insertAt)
            $inserted = $true
        }
    }

    # Pattern 2: no content-body but has <main> - insert after first </p> in main
    if (-not $inserted -and $html -match '<main>') {
        $idx = $html.IndexOf('<main>')
        $firstP = $html.IndexOf('</p>', $idx)
        if ($firstP -ge 0) {
            $insertAt = $firstP + 4
            $html = $html.Substring(0, $insertAt) + $imgBlock + $html.Substring($insertAt)
            $inserted = $true
        }
    }

    # Pattern 3: legal-style (wrap/card) - after first </p> after <div class="card">
    if (-not $inserted -and $html -match '<div class="card">') {
        $idx = $html.IndexOf('<div class="card">')
        $firstP = $html.IndexOf('</p>', $idx)
        if ($firstP -ge 0) {
            $insertAt = $firstP + 4
            $html = $html.Substring(0, $insertAt) + $imgBlock + $html.Substring($insertAt)
            $inserted = $true
        }
    }

    # Pattern 4: PPC hero layout - insert before <section class="block highlights">
    if (-not $inserted -and $html -match '<section class="block highlights">') {
        $idx = $html.IndexOf('<section class="block highlights">')
        $imgForPpc = "`n  <section class=`"content-hero-section`" style=`"margin:0;padding:24px 0;`"><div class=`"container`"><figure style=`"margin:0;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);`"><img src=`"https://images.unsplash.com/photo-1589829541223-0a0a6b628179?w=1200&amp;q=80`" alt=`"Legal and injury claim guidance`" style=`"width:100%;height:auto;display:block;`"></figure></div></section>`n  "
        $html = $html.Substring(0, $idx) + $imgForPpc + $html.Substring($idx)
        $inserted = $true
    }

    if ($inserted) {
        [System.IO.File]::WriteAllText($f.FullName, $html, [System.Text.UTF8Encoding]::new($false))
        $count++
    }
}
Write-Host "Added content image to $count pages."