# Use images from the old website (insideraccidentlawyers.zip). Extract zip to _old-site-extract first, or run from repo with zip path.
# Copies selected content images into assets/images/old-site, then updates each LP page content-hero img to use one by topic.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$oldRoot = Join-Path $root "_old-site-extract"
$oldImages = Join-Path $oldRoot "Resources\images"
$oldFiles = Join-Path $oldRoot "Resources\files"
$destDir = Join-Path $root "assets\images\old-site"

if (-not (Test-Path $oldImages)) {
    Write-Error "Old site not found at $oldRoot. Extract insideraccidentlawyers.zip to $oldRoot first."
}
if (-not (Test-Path (Join-Path $root "assets\images"))) {
    New-Item -ItemType Directory -Path (Join-Path $root "assets\images") -Force | Out-Null
}
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

# Content images to copy (prefer -1920w or -2880w). Key = simple name for mapping.
$contentImages = @(
    @{ src = "Animal Attacks-2880w.jpg"; dest = "animal-attacks.jpg" },
    @{ src = "auto accidents-1920w.webp"; dir = "files"; dest = "auto-accidents.webp" },
    @{ src = "Brain Injury-1920w.webp"; dir = "files"; dest = "brain-injury.webp" },
    @{ src = "Catastrophic Injuries-1920w.jpeg"; dest = "catastrophic-injuries.jpeg" },
    @{ src = "Pedestrian Accidents-1920w.jpeg"; dest = "pedestrian-accidents.jpeg" },
    @{ src = "Premises Liability-1920w.jpg"; dest = "premises-liability.jpg" },
    @{ src = "Product Liability-2880w.jpeg"; dest = "product-liability.jpeg" },
    @{ src = "Spine Injuries-2880w.jpeg"; dest = "spine-injuries.jpeg" },
    @{ src = "Uber and Lyft Accidents-2880w.jpeg"; dest = "uber-lyft-accidents.jpeg" },
    @{ src = "wrongful death (2)-1920w.jpg"; dest = "wrongful-death.jpg" },
    @{ src = "navigation-car-drive-road-2880w.jpg"; dest = "car-accident.jpg" },
    @{ src = "sign-slippery-wet-caution-2880w.jpg"; dest = "slip-and-fall.jpg" },
    @{ src = "Premises-Liability-2880w.jpg"; dest = "premises-liability-alt.jpg" },
    @{ src = "pexels-photo-2199293-2880w.jpeg"; dest = "legal-general.jpeg" },
    @{ src = "pexels-photo-2453284-2880w.jpeg"; dest = "legal-general-2.jpeg" },
    @{ src = "pexels-photo-6129049-2880w.jpeg"; dest = "legal-general-3.jpeg" },
    @{ src = "sky-road-travel-trip-163789-2880w.jpeg"; dest = "truck-road.jpeg" }
)

foreach ($entry in $contentImages) {
    $srcDir = if ($entry.dir -eq "files") { $oldFiles } else { $oldImages }
    $srcPath = Join-Path $srcDir $entry.src
    if (Test-Path $srcPath) {
        Copy-Item -LiteralPath $srcPath -Destination (Join-Path $destDir $entry.dest) -Force
        Write-Host "Copied: $($entry.dest)"
    } else {
        Write-Warning "Missing: $($entry.src)"
    }
}

# Slug/keyword -> image filename (under old-site/)
$slugToImage = @{
    "animal-attacks" = "animal-attacks.jpg"
    "auto-accidents" = "auto-accidents.webp"
    "brain" = "brain-injury.webp"
    "catastrophic" = "catastrophic-injuries.jpeg"
    "pedestrian" = "pedestrian-accidents.jpeg"
    "premises" = "premises-liability.jpg"
    "product-liability" = "product-liability.jpeg"
    "spine" = "spine-injuries.jpeg"
    "uber" = "uber-lyft-accidents.jpeg"
    "lyft" = "uber-lyft-accidents.jpeg"
    "wrongful-death" = "wrongful-death.jpg"
    "slip-and-fall" = "slip-and-fall.jpg"
    "truck" = "truck-road.jpeg"
    "motorcycle" = "legal-general.jpeg"
    "bicycle" = "legal-general-2.jpeg"
    "insurance" = "car-accident.jpg"
    "demand" = "legal-general.jpeg"
    "adjuster" = "car-accident.jpg"
    "claim" = "legal-general-2.jpeg"
    "accident" = "car-accident.jpg"
    "car-" = "car-accident.jpg"
    "legal" = "legal-general.jpeg"
    "disclaimer" = "legal-general.jpeg"
    "attorney-referrals" = "legal-general-2.jpeg"
}

$defaultImages = @("legal-general.jpeg", "legal-general-2.jpeg", "legal-general-3.jpeg", "car-accident.jpg", "truck-road.jpeg")
$defaultIndex = 0

function Get-ImageForSlug {
    param([string]$slug)
    $slugLower = $slug.ToLowerInvariant()
    foreach ($key in $slugToImage.Keys) {
        if ($slugLower -like "*$key*") { return $slugToImage[$key] }
    }
    $idx = [Math]::Abs($slug.GetHashCode()) % $defaultImages.Count
    return $defaultImages[$idx]
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

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
    if ($rel -eq "index.html") { return $false }
    $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $html -match '<figure class="content-hero-img"' -and $html -match '<img\s+src='
}

$updated = 0
foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $slug = Get-SlugFromPath -fullPath $f.FullName
    $depth = Get-DepthFromPath -fullPath $f.FullName
    $imgFile = Get-ImageForSlug -slug $slug
    $prefix = ("../" * $depth) + "assets/images/old-site/"
    $relImg = $prefix + $imgFile
    if ($html -match '<h1[^>]*>([^<]+)</h1>') {
        $h1Text = $Matches[1] -replace "&[^;]+;", " "
        $altRaw = "Illustration: " + ($h1Text.Substring(0, [Math]::Min(60, $h1Text.Length))) -replace '"', ""
    } else { $altRaw = "Illustration" }
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
        Write-Host "OK: $slug -> old-site/$imgFile"
    }
}
Write-Host "Done. Updated $updated pages with old-site images."
