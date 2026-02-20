# For each page with content-hero-img: get H1 -> search Wikipedia (API) -> first result's main image -> download to assets/images -> update HTML.
# Skips root index and PPC hero pages. Uses Wikipedia API only (no Google). Many articles have no main image ("No image").
# Wikimedia may return 429 if you run too often; use 1.5s delay and run in one batch. Set $maxPagesToUpdate = 5 to test.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$assetsDir = Join-Path $root "assets\images"
if (-not (Test-Path $assetsDir)) { New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null }

# Optional: set to a number to process only that many pages (for testing). 0 = no limit.
$maxPagesToUpdate = 0
$wikiBase = "https://en.wikipedia.org/w/api.php"

function Get-SlugFromPath {
    param([string]$fullPath)
    $rel = $fullPath.Substring($root.Length).TrimStart("\", "/")
    $rel = $rel -replace "\\index\.html$", "" -replace "/index\.html$", ""
    if ([string]::IsNullOrWhiteSpace($rel)) { return "page" }
    $slug = $rel.Replace("\", "-").Replace("/", "-")
    return $slug
}

function Get-DepthFromPath {
    param([string]$fullPath)
    $rel = $fullPath.Substring($root.Length).TrimStart("\", "/")
    $rel = $rel -replace "\\index\.html$", "" -replace "/index\.html$", ""
    if ([string]::IsNullOrWhiteSpace($rel)) { return 0 }
    $depth = ($rel -split "[\\/]").Count
    return $depth
}

function Get-KeywordFromH1 {
    param([string]$h1)
    $t = $h1 -replace "\s+", " " -replace "[?()\-]", " " -replace "\s+", " " -replace "^\s+|\s+$", ""
    # Drop leading question words and location/role words for better Wikipedia match
    $drop = @("what", "how", "when", "who", "why", "should", "can", "do", "four", "the", "los angeles", "california", "lawyer", "attorney", "near me", "in california", "step-by-step")
    $words = $t -split "\s+"
    $kept = @()
    foreach ($w in $words) {
        $l = $w.ToLowerInvariant()
        if ($l -in $drop -or $l.Length -lt 2) { continue }
        $kept += $w
        if ($kept.Count -ge 4) { break }
    }
    if ($kept.Count -eq 0) {
        $words = ($t -split "\s+") | Where-Object { $_.Length -ge 2 }
        $kept = $words[0..([Math]::Min(3, $words.Count - 1))]
    }
    return ($kept -join " ").Trim()
}

function Get-WikipediaImageUrl {
    param([string]$searchQuery)
    if ([string]::IsNullOrWhiteSpace($searchQuery)) { return $null }
    $searchQuery = $searchQuery.Trim()
    $searchEnc = [System.Uri]::EscapeDataString($searchQuery)
    $searchUrl = $wikiBase + '?action=query&list=search&srsearch=' + $searchEnc + '&format=json'
    try {
        $searchResp = Invoke-RestMethod -Uri $searchUrl -Method Get -UseBasicParsing
    } catch {
        Write-Warning "Wikipedia search failed for '$searchQuery': $_"
        return $null
    }
    $first = $searchResp.query.search | Select-Object -First 1
    if (-not $first) { return $null }
    $title = $first.title
    $titleEnc = [System.Uri]::EscapeDataString($title)
    $imgUrl = $wikiBase + '?action=query&format=json&formatversion=2&prop=pageimages&piprop=original&titles=' + $titleEnc
    try {
        $imgResp = Invoke-RestMethod -Uri $imgUrl -Method Get -UseBasicParsing
    } catch {
        Write-Warning "Wikipedia pageimages failed for '$title': $_"
        return $null
    }
    $page = $imgResp.query.pages | Select-Object -First 1
    if (-not $page -or -not $page.original) { return $null }
    return $page.original.source
}

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
    if ($rel -eq "index.html") { return $false }
    $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    # Only pages that have content-hero-img (standard content image), not PPC hero
    $html -match '<figure class="content-hero-img"' -and $html -match '<img\s+src='
}

$updated = 0
$skipped = 0
$failed = 0
foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    if ($html -notmatch '<h1[^>]*>([^<]+)</h1>') {
        $skipped++; continue
    }
    $h1Text = $Matches[1] -replace "&[^;]+;", " "  # decode entities roughly
    $keyword = Get-KeywordFromH1 -h1 $h1Text
    if ([string]::IsNullOrWhiteSpace($keyword)) {
        $skipped++; continue
    }
    $imgUrl = Get-WikipediaImageUrl -searchQuery $keyword
    if (-not $imgUrl) {
        $failed++
        Write-Host "No image: $($f.FullName.Replace($root,'')) (keyword: $keyword)"
        continue
    }
    $slug = Get-SlugFromPath -fullPath $f.FullName
    $ext = [System.IO.Path]::GetExtension($imgUrl).ToLowerInvariant()
    $imageExts = @(".jpg", ".jpeg", ".png", ".svg", ".webp", ".gif")
    if ($ext -notin $imageExts) { $ext = ".jpg" }
    $localName = $slug + $ext
    $localPath = Join-Path $assetsDir $localName
    $headers = @{ "User-Agent" = "InsiderLawyersLP/1.0 (Wikipedia images for legal content)" }
    $downloaded = $false
    foreach ($try in 1..2) {
        try {
            Invoke-WebRequest -Uri $imgUrl -OutFile $localPath -UseBasicParsing -Headers $headers
            $downloaded = $true
            break
        } catch {
            if ($try -eq 1 -and $_.Exception.Response.StatusCode.value__ -eq 429) {
                Start-Sleep -Seconds 5
            } else {
                Write-Warning "Download failed $imgUrl -> $localPath : $_"
                $failed++; continue
            }
        }
    }
    if (-not $downloaded) { $failed++; continue }
    $depth = Get-DepthFromPath -fullPath $f.FullName
    $prefix = if ($depth -gt 0) { ("../" * $depth) + "assets/images/" } else { "assets/images/" }
    $relImg = $prefix + $localName
    $altRaw = "Illustration: " + ($h1Text.Substring(0, [Math]::Min(60, $h1Text.Length))) -replace '"', ""
    # Replace existing img inside content-hero-img figure: src and alt
    $pattern = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"\s+alt="[^"]*"([^>]*)>'
    $replacement = "`$1<img src=`"$relImg`" alt=`"$altRaw`"`$2>"
    $newHtml = $html -replace $pattern, $replacement
    if ($newHtml -eq $html) {
        # Fallback: replace any img src in that figure
        $pattern2 = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"'
        $replacement2 = "`$1<img src=`"$relImg`""
        $newHtml = $html -replace $pattern2, $replacement2
    }
    if ($newHtml -ne $html) {
        [System.IO.File]::WriteAllText($f.FullName, $newHtml, [System.Text.UTF8Encoding]::new($false))
        $updated++
        Write-Host "OK: $relImg <- $keyword"
        if ($maxPagesToUpdate -gt 0 -and $updated -ge $maxPagesToUpdate) {
            Write-Host "Reached limit of $maxPagesToUpdate updates."
            break
        }
    }
    Start-Sleep -Milliseconds 1500
}

Write-Host "Done. Updated: $updated, Skipped: $skipped, No image/fail: $failed"
