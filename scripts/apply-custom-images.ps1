# Copy your custom images from Cursor assets into LP assets/images/custom, then assign by topic to each page.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$customDir = Join-Path $root "assets\images\custom"
$cursorAssets = "C:\Users\georgea\.cursor\projects\c-Users-georgea-insiderlawyer-com-lps\assets"
if (-not (Test-Path (Join-Path $root "assets\images"))) { New-Item -ItemType Directory -Path (Join-Path $root "assets\images") -Force | Out-Null }
if (-not (Test-Path $customDir)) { New-Item -ItemType Directory -Path $customDir -Force | Out-Null }

# Copy themed images: extract name from c__Users_..._images_<name>-<uuid>.png -> custom/<name>.png
$copied = @{}
Get-ChildItem -LiteralPath $cursorAssets -Recurse -Filter "*.png" -File | ForEach-Object {
    if ($_.Name -match "_images_(.+)-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.png$") {
        $shortName = $Matches[1] + ".png"
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $customDir $shortName) -Force
        $copied[$shortName] = $true
    }
}
Write-Host "Copied $($copied.Count) custom images to assets/images/custom/"

# All your custom images (filename = context)
$allImages = @(Get-ChildItem -LiteralPath $customDir -Filter "*.png" -File | Sort-Object Name | ForEach-Object { $_.Name })
if ($allImages.Count -eq 0) { throw "No custom images in $customDir" }

# Filename stem -> slug match keys (your labels). Typos in filenames normalized so slug "settlement" matches settlemt11 etc.
$stemToKeys = @{
    "reffereals" = @("referral"); "reffferals" = @("referral"); "referalls" = @("referral")
    "settlemt" = @("settlement"); "settlemet" = @("settlement")
    "libability" = @("liability"); "motorcylce" = @("motorcycle"); "unisured" = @("uninsured")
    "claimscoverage" = @("claim", "coverage"); "caraccident" = @("accident", "car"); "carinsurance" = @("insurance")
    "braininjury" = @("brain"); "softtissue" = @("soft", "tissue"); "sine" = @("spine", "back")
    "car-accident" = @("accident", "car")
}
# Derive keys from each image filename: stem (no .png, trailing digits stripped) -> keys for slug matching
$imageKeys = @{}
foreach ($img in $allImages) {
    $base = $img -replace "\.png$", ""
    $stem = $base -replace "\d+$", ""   # strip trailing digits: legal1->legal, settlement22->settlement
    $keys = @($stem)
    if ($stemToKeys.ContainsKey($stem)) { $keys = $stemToKeys[$stem] }
    elseif ($stem -eq "tbi") { $keys = @("tbi", "brain") }
    elseif ($stem -eq "death") { $keys = @("death", "wrongful", "catastrophic") }
    elseif ($stem -eq "legal") { $keys = @("legal", "court") }
    elseif ($stem -match "^(truck|motorcycle|bike|scooter|uber|pedestrian|evidence|demand|adjusters|guide|disc|spine|liability|negligence|fmcsa|settleoffer|image)$") { $keys = @($stem) }
    $imageKeys[$img] = $keys
}
# Fallback keys for stems that didn't get a rule (e.g. death1 -> death, legal1 -> legal)
foreach ($img in $allImages) {
    if (-not $imageKeys.ContainsKey($img)) {
        $base = $img -replace "\.png$", ""
        $stem = $base -replace "\d+$", ""
        $imageKeys[$img] = @($stem)
    }
}

function Get-KeysForImage {
    param([string]$imgName)
    if ($imageKeys.ContainsKey($imgName)) { return $imageKeys[$imgName] }
    $base = ($imgName -replace "\.png$", "") -replace "\d+$", ""
    return @($base)
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

# Assign one image per page: prefer filename-context match, use each image at most once
$files = @(Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
    if ($rel -eq "index.html") { return $false }
    $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $html -match '<figure class="content-hero-img"' -and $html -match '<img\s+src='
} | Sort-Object FullName)

# Sort pages by slug length descending so specific slugs (wrongful-death, truck-accident-liability) get first pick
$pageSlugs = @()
foreach ($f in $files) {
    $slug = (Get-SlugFromPath -fullPath $f.FullName).ToLowerInvariant()
    $pageSlugs += @{ Path = $f.FullName; Slug = $slug; Depth = (Get-DepthFromPath -fullPath $f.FullName) }
}
$pageSlugs = @($pageSlugs | Sort-Object { -$_.Slug.Length })

$used = @{}
$assignment = @{}
foreach ($p in $pageSlugs) {
    $slug = $p.Slug
    $path = $p.Path
    $depth = $p.Depth
    $chosen = $null
    # Find images whose key appears in slug (your filename context)
    $candidates = @($allImages | Where-Object {
        $keys = Get-KeysForImage -imgName $_
        $match = $false
        foreach ($k in $keys) {
            if ($slug -like "*$k*") { $match = $true; break }
        }
        $match
    })
    # Prefer unused; if all used, reuse first candidate
    foreach ($c in $candidates) {
        if (-not $used[$c]) { $chosen = $c; break }
    }
    if (-not $chosen -and $candidates.Count -gt 0) { $chosen = $candidates[0] }
    # No topic match: prefer generic images (guide, car-accident, insurance) over death/liability
    if (-not $chosen) {
        $preferOrder = @("guide", "car-accident", "caraccident", "insurance", "carinsurance", "claim", "adjusters", "demand", "evidence", "negligence", "liability", "death")
        foreach ($pref in $preferOrder) {
            foreach ($img in $allImages) {
                if (-not $used[$img]) {
                    $ik = Get-KeysForImage -imgName $img
                    if ($ik -contains $pref) { $chosen = $img; break }
                }
            }
            if ($chosen) { break }
        }
        if (-not $chosen) {
            foreach ($img in $allImages) {
                if (-not $used[$img]) { $chosen = $img; break }
            }
        }
    }
    if (-not $chosen) {
        $chosen = $allImages[[Math]::Abs($slug.GetHashCode()) % $allImages.Count]
    }
    $used[$chosen] = $true
    $assignment[$path] = @{ img = $chosen; depth = $depth }
}

$updated = 0
foreach ($path in $assignment.Keys) {
    $html = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    $info = $assignment[$path]
    $imgFile = $info.img
    $depth = $info.depth
    $prefix = ("../" * $depth) + "assets/images/custom/"
    $relImg = $prefix + $imgFile
    if ($html -match '<h1[^>]*>([^<]+)</h1>') {
        $h1Text = $Matches[1] -replace "&[^;]+;", " "
        $altRaw = "Illustration: " + ($h1Text.Substring(0, [Math]::Min(60, $h1Text.Length))) -replace '"', ""
    } else { $altRaw = "Illustration" }
    $pattern = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"\s+alt="[^"]*"([^>]*)>'
    $replacement = "`$1<img src=`"$relImg`" alt=`"$altRaw`"`$2>"
    $newHtml = $html -replace $pattern, $replacement
    if ($newHtml -eq $html) {
        $newHtml = $html -replace '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"', "`$1<img src=`"$relImg`""
    }
    if ($newHtml -ne $html) {
        [System.IO.File]::WriteAllText($path, $newHtml, [System.Text.UTF8Encoding]::new($false))
        $updated++
    }
}
$uniqueUsed = ($used.Keys | Measure-Object).Count
Write-Host "Done. Updated $updated pages. Unique images used: $uniqueUsed of $($allImages.Count)."
