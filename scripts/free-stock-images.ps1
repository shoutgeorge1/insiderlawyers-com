# Free stock images: H1 keyword -> Pexels API search -> first image -> download to assets/images -> update HTML.
# No subscription. Get a free API key at https://www.pexels.com/api (instant).
# Set env: $env:PEXELS_API_KEY = "your-key"   Or paste key when prompted.
# Optional: $maxPagesToUpdate = 5 to try 4-5 pages first.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$assetsDir = Join-Path $root "assets\images"
if (-not (Test-Path $assetsDir)) { New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null }

$maxPagesToUpdate = 5
$apiKey = $env:PEXELS_API_KEY
if (-not $apiKey) {
    $apiKey = Read-Host "Pexels API key (get free at https://www.pexels.com/api)"
    if (-not $apiKey) { Write-Error "PEXELS_API_KEY required."; exit 1 }
}

function Get-SlugFromPath {
    param([string]$fullPath)
    $rel = $fullPath.Substring($root.Length).TrimStart("\", "/")
    $rel = $rel -replace "\\index\.html$", "" -replace "/index\.html$", ""
    if ([string]::IsNullOrWhiteSpace($rel)) { return "page" }
    return $rel.Replace("\", "-").Replace("/", "-")
}

function Get-DepthFromPath {
    param([string]$fullPath)
    $rel = $fullPath.Substring($root.Length).TrimStart("\", "/")
    $rel = $rel -replace "\\index\.html$", "" -replace "/index\.html$", ""
    if ([string]::IsNullOrWhiteSpace($rel)) { return 0 }
    return ($rel -split "[\\/]").Count
}

function Get-KeywordFromH1 {
    param([string]$h1)
    $t = $h1 -replace "\s+", " " -replace "[?()\-]", " " -replace "\s+", " " -replace "^\s+|\s+$", ""
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
    $base = ($kept -join " ").Trim()
    # Pair with "free stock" for better stock-photo results
    if ([string]::IsNullOrWhiteSpace($base)) { return "legal" }
    return $base
}

function Get-PexelsFirstImageUrl {
    param([string]$query)
    if ([string]::IsNullOrWhiteSpace($query)) { return $null }
    $enc = [System.Uri]::EscapeDataString($query.Trim())
    $url = "https://api.pexels.com/v1/search?query=" + $enc + "&per_page=1"
    $headers = @{ "Authorization" = $apiKey }
    try {
        $r = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    } catch {
        Write-Warning "Pexels search failed for '$query': $_"
        return $null
    }
    $photo = $r.photos | Select-Object -First 1
    if (-not $photo -or -not $photo.src) { return $null }
    # Prefer large (940w) or landscape (1200w) for content hero
    if ($photo.src.landscape) { return $photo.src.landscape }
    if ($photo.src.large) { return $photo.src.large }
    return $photo.src.original
}

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
    if ($rel -eq "index.html") { return $false }
    $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $html -match '<figure class="content-hero-img"' -and $html -match '<img\s+src='
}

$updated = 0
$failed = 0
foreach ($f in $files) {
    if ($maxPagesToUpdate -gt 0 -and $updated -ge $maxPagesToUpdate) { break }
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    if ($html -notmatch '<h1[^>]*>([^<]+)</h1>') { continue }
    $h1Text = $Matches[1] -replace "&[^;]+;", " "
    $keyword = Get-KeywordFromH1 -h1 $h1Text
    $imgUrl = Get-PexelsFirstImageUrl -query $keyword
    if (-not $imgUrl) {
        $failed++
        Write-Host "No result: $($f.FullName.Replace($root,'')) (keyword: $keyword)"
        continue
    }
    $slug = Get-SlugFromPath -fullPath $f.FullName
    $ext = ".jpg"
    $localPath = Join-Path $assetsDir ($slug + $ext)
    try {
        Invoke-WebRequest -Uri $imgUrl -OutFile $localPath -UseBasicParsing
    } catch {
        Write-Warning "Download failed: $_"
        $failed++; continue
    }
    $depth = Get-DepthFromPath -fullPath $f.FullName
    $relImg = ("../" * $depth) + "assets/images/" + $slug + $ext
    $altRaw = "Illustration: " + ($h1Text.Substring(0, [Math]::Min(60, $h1Text.Length))) -replace '"', ""
    $pattern = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"\s+alt="[^"]*"([^>]*)>'
    $replacement = "`$1<img src=`"$relImg`" alt=`"$altRaw`"`$2>"
    $newHtml = $html -replace $pattern, $replacement
    if ($newHtml -eq $html) {
        $pattern2 = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"'
        $newHtml = $html -replace $pattern2, "`$1<img src=`"$relImg`""
    }
    if ($newHtml -ne $html) {
        [System.IO.File]::WriteAllText($f.FullName, $newHtml, [System.Text.UTF8Encoding]::new($false))
        $updated++
        Write-Host "OK: $relImg <- $keyword"
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "Done. Updated: $updated, No result/fail: $failed"
