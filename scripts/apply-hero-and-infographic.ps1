# One topic-appropriate hero + one infographic per page. FROZEN: home + all PPC pages.
# Run from repo root: .\scripts\apply-hero-and-infographic.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

# --- FROZEN: never modify these ---
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

# --- Hero URLs by topic (Unsplash, one per theme) ---
$heroUrl = @{
  car      = 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&q=80'
  truck    = 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=1200&q=80'
  motorcycle = 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1200&q=80'
  bicycle  = 'https://images.unsplash.com/photo-1571333250630-f0230c320b6d?w=1200&q=80'
  pedestrian = 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200&q=80'
  animal  = 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=1200&q=80'
  medical = 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200&q=80'
  legal   = 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80'
  documents = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80'
  premises = 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&q=80'
  rideshare = 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=80'
  default = 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1200&q=80'
}

# Order matters: first match wins
$heroRules = @(
  @{ pattern = 'truck'; topic = 'truck' },
  @{ pattern = 'motorcycle'; topic = 'motorcycle' },
  @{ pattern = 'bicycle'; topic = 'bicycle' },
  @{ pattern = 'pedestrian'; topic = 'pedestrian' },
  @{ pattern = 'dog-bite|animal-attack'; topic = 'animal' },
  @{ pattern = 'brain|spine|catastrophic|herniated|spinal|soft-tissue|traumatic-brain|tbi'; topic = 'medical' },
  @{ pattern = 'slip-and-fall|premises'; topic = 'premises' },
  @{ pattern = 'uber|lyft|rideshare'; topic = 'rideshare' },
  @{ pattern = 'insurance|adjuster|claim-value|demand-letter|lowball|playbook|tactics'; topic = 'documents' },
  @{ pattern = 'attorney-referral|lit-referral|litigation'; topic = 'legal' },
  @{ pattern = 'wrongful-death'; topic = 'legal' },
  @{ pattern = 'car-accident|major-car|california-car|proving-claim'; topic = 'car' },
  @{ pattern = 'personal-injury-court|personal-injury$|personal-injury/'; topic = 'legal' }
)

# Infographic path overrides (path key: relative path with /)
$infographicOverrides = @{
  'personal-injury' = '/images/generated/personal-injury-index-infographic-v4.svg'
  'personal-injury/motorcycle-accidents' = '/images/generated/personal-injury-motorcycle-accidents-infographic.svg'
}

function Get-HeroUrl($relPath) {
  $key = $relPath -replace '/', '-'
  foreach ($r in $heroRules) {
    if ($key -match $r.pattern) { return $heroUrl[$r.topic] }
  }
  return $heroUrl.default
}

function Get-InfographicPath($relPath) {
  $trimmed = $relPath.Trim('/')
  if ([string]::IsNullOrWhiteSpace($trimmed)) { return $null }
  if ($infographicOverrides.ContainsKey($trimmed)) { return $infographicOverrides[$trimmed] }
  $segments = $trimmed -split '/'
  if ($segments.Count -eq 1) {
    return "/images/generated/$($segments[0])-infographic-v4.svg"
  }
  if ($segments.Count -eq 2) {
    $slug = $segments[0] + '-' + $segments[1]
    $suffix = if ($segments[0] -eq 'personal-injury') { '-index-infographic-v4.svg' } else { '-infographic-v4.svg' }
    return "/images/generated/$slug$suffix"
  }
  if ($segments.Count -ge 3) {
    $slug = $segments -join '-'
    return "/images/generated/$slug-infographic-v4.svg"
  }
  return $null
}

$placeholderUrl = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80'
$heroRegex = '(<div class="asset-preview-grid">\s*)<img([^>]*)src="https://images\.unsplash\.com/photo-[^"]+"'

$indexFiles = Get-ChildItem -Path $root -Recurse -Filter 'index.html' -File |
  Where-Object { $p = $_.FullName.Replace($root, '').Replace('\', '/'); $p -notmatch '/styles/|/scripts/|/images/' }

$updated = 0
foreach ($file in $indexFiles) {
  if ($file.FullName -eq $homePage) { continue }
  $parentName = Split-Path -Leaf (Split-Path -Parent $file.FullName)
  if ($ppcFolders -contains $parentName) { continue }

  $relPath = ($file.FullName.Replace($root, '').Replace('\', '/').Trim('/')) -replace '/index\.html$', ''
  if ([string]::IsNullOrWhiteSpace($relPath)) { $relPath = $parentName }

  $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
  if ($content -notmatch 'asset-preview-grid') { continue }

  $infographicPath = Get-InfographicPath $relPath
  $heroUrlValue = Get-HeroUrl $relPath

  $orig = $content
  if ($infographicPath -and $content.IndexOf($placeholderUrl) -ge 0) {
    $content = $content.Replace("src=`"$placeholderUrl`"", "src=`"$infographicPath`"")
    $content = $content.Replace("href=`"$placeholderUrl`"", "href=`"$infographicPath`"")
  }
  if ($content -match $heroRegex) {
    $content = [regex]::Replace($content, $heroRegex, "`$1<img`$2src=`"$heroUrlValue`"")
  }

  if ($content -ne $orig) {
    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]::new($false))
    $updated++
    Write-Host "Updated: $relPath"
  }
}
Write-Host "Done. Updated $updated files."