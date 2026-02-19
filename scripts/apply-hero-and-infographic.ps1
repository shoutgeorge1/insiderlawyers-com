# One topic-appropriate hero image + restore original infographic on every page.
# FROZEN: Home page and all injury/accident PPC pages - never modified.
# Run from repo root: .\scripts\apply-hero-and-infographic.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

# FROZEN
$homePage = Join-Path $root 'index.html'
$ppcFolders = @(
  'los-angeles-car-accident-lawyer', 'los-angeles-auto-accident-lawyer', 'los-angeles-car-crash-lawyer',
  'car-accident-lawyer-near-me-los-angeles', 'los-angeles-truck-accident-lawyer', 'los-angeles-motorcycle-accident-lawyer',
  'los-angeles-pedestrian-accident-lawyer', 'los-angeles-bicycle-accident-lawyer', 'los-angeles-wrongful-death-lawyer',
  'los-angeles-brain-injury-lawyer', 'los-angeles-spine-injury-lawyer', 'los-angeles-catastrophic-injury-lawyer',
  'los-angeles-premises-liability-lawyer', 'los-angeles-slip-and-fall-lawyer', 'los-angeles-product-liability-lawyer',
  'los-angeles-uber-lyft-accident-lawyer', 'hit-and-run-accident-lawyer-los-angeles', 'rear-end-accident-lawyer-los-angeles',
  't-bone-accident-lawyer-los-angeles', 'parking-lot-accident-lawyer-los-angeles', 'pedestrian-accident-lawyer-los-angeles',
  'uber-accident-lawyer-los-angeles', 'uninsured-driver-accident-lawyer-los-angeles'
)

# Topic-appropriate Unsplash heroes (one per page, varied by theme)
$heroByTopic = @{
  car = 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&q=80'
  truck = 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=1200&q=80'
  motorcycle = 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1200&q=80'
  bicycle = 'https://images.unsplash.com/photo-1571333250630-f0230c320b6d?w=1200&q=80'
  pedestrian = 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200&q=80'
  animal = 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=1200&q=80'
  medical = 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200&q=80'
  legal = 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80'
  documents = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80'
  premises = 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&q=80'
  rideshare = 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=80'
  default = 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1200&q=80'
}

function Get-HeroTopic($relPath) {
  $key = $relPath -replace '/', '-'
  if ($key -match 'truck') { return $heroByTopic.truck }
  if ($key -match 'motorcycle') { return $heroByTopic.motorcycle }
  if ($key -match 'bicycle') { return $heroByTopic.bicycle }
  if ($key -match 'pedestrian') { return $heroByTopic.pedestrian }
  if ($key -match 'dog-bite|animal-attack') { return $heroByTopic.animal }
  if ($key -match 'brain|spine|catastrophic|herniated|spinal|soft-tissue|traumatic-brain|tbi') { return $heroByTopic.medical }
  if ($key -match 'slip-and-fall|premises') { return $heroByTopic.premises }
  if ($key -match 'uber|lyft|rideshare') { return $heroByTopic.rideshare }
  if ($key -match 'insurance|adjuster|claim-value|demand-letter|lowball|playbook|tactics') { return $heroByTopic.documents }
  if ($key -match 'attorney-referral|lit-referral|litigation') { return $heroByTopic.legal }
  if ($key -match 'wrongful-death') { return $heroByTopic.legal }
  if ($key -match 'car-accident|major-car|california-car|proving-claim') { return $heroByTopic.car }
  if ($key -match 'personal-injury-court|personal-injury$|personal-injury/') { return $heroByTopic.legal }
  return $heroByTopic.default
}

function Get-InfographicPath($relPath) {
  $trimmed = $relPath.Trim('/')
  if ([string]::IsNullOrWhiteSpace($trimmed)) { return $null }
  $segments = $trimmed -split '/'
  if ($segments.Count -eq 1) {
    if ($segments[0] -eq 'personal-injury') { return '/images/generated/personal-injury-index-infographic-v4.svg' }
    return "/images/generated/$($segments[0])-infographic-v4.svg"
  }
  if ($segments.Count -eq 2) {
    $slug = $segments[0] + '-' + $segments[1]
    if ($segments[0] -eq 'personal-injury') { return "/images/generated/$slug-index-infographic-v4.svg" }
    return "/images/generated/$slug-infographic-v4.svg"
  }
  if ($segments.Count -ge 3) {
    $slug = $segments -join '-'
    return "/images/generated/$slug-infographic-v4.svg"
  }
  return $null
}

$unsplashInfographicPlaceholder = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80'
$heroUnsplashPattern = 'src="https://images\.unsplash\.com/photo-[^"]+"'

$indexFiles = Get-ChildItem -Path $root -Recurse -Filter 'index.html' -File |
  Where-Object { $relPath = $_.FullName.Replace($root, '').Replace('\', '/').Trim('/'); $relPath -notmatch '^styles/|/styles/|^scripts/|/scripts/|^images/|/images/' }

$updated = 0
foreach ($file in $indexFiles) {
  if ($file.FullName -eq $homePage) { continue }
  $parentName = Split-Path -Leaf (Split-Path -Parent $file.FullName)
  if ($ppcFolders -contains $parentName) { continue }

  $relPath = ($file.FullName.Replace($root, '').Replace('\', '/').Trim('/')) -replace '/index\.html$', ''
  if ([string]::IsNullOrWhiteSpace($relPath)) { $relPath = (Split-Path -Leaf (Split-Path -Parent $file.FullName)) }

  $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
  if ($content -notmatch 'asset-preview-grid') { continue }

  $infographicPath = Get-InfographicPath $relPath
  $heroUrl = Get-HeroTopic $relPath

  $orig = $content
  # 1) Restore infographic: second img and href if still Unsplash placeholder
  if ($infographicPath -and $content -match [regex]::Escape($unsplashInfographicPlaceholder)) {
    $content = $content.Replace("src=`"$unsplashInfographicPlaceholder`"", "src=`"$infographicPath`"")
    $content = $content.Replace("href=`"$unsplashInfographicPlaceholder`"", "href=`"$infographicPath`"")
  }
  # 2) Replace hero (first img in grid): if it's an Unsplash URL, use topic-appropriate hero
  $heroRegex = '(<div class="asset-preview-grid">\s*)<img([^>]*)src="https://images\.unsplash\.com/photo-[^"]+"'
  if ($content -match $heroRegex) {
    $content = [regex]::Replace($content, $heroRegex, "`$1<img`$2src=`"$heroUrl`"")
  }

  if ($content -ne $orig) {
    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]::new($false))
    $updated++
    Write-Host "Updated: $relPath"
  }
}
Write-Host "Done. Updated $updated files."