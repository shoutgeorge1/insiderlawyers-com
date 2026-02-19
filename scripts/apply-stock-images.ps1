# Replace placeholder hero/infographic images with free Unsplash stock photos on every page.
# Run from repo root: .\scripts\apply-stock-images.ps1
#
# FROZEN: Home page and all PPC landing pages are never modified by this script.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

# FROZEN – do not touch home page or PPC pages (real hero/ktown-bg, no placeholders)
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

# Free stock images (Unsplash - free to use, hotlinking allowed)
$heroUrl = 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80'
$infographicUrl = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80'

$heroPattern = 'src="/images/generated/[^"]*-hero-v[45]\.[a-z]+"'
$infographicSrcPattern = 'src="/images/generated/[^"]*-infographic-v[45]\.[a-z]+"'
$infographicHrefPattern = 'href="/images/generated/[^"]*-infographic-v[45]\.[a-z]+"'

$indexFiles = Get-ChildItem -Path $root -Recurse -Filter 'index.html' -File |
  Where-Object { $relPath = $_.FullName.Replace($root, '').Replace('\', '/'); $relPath -notmatch '/styles/|/scripts/|/images/' }

$updated = 0
foreach ($file in $indexFiles) {
  # FROZEN: skip home page and PPC pages
  if ($file.FullName -eq $homePage) { continue }
  $parentName = Split-Path -Leaf (Split-Path -Parent $file.FullName)
  if ($ppcFolders -contains $parentName) { continue }

  $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
  $orig = $content
  $content = $content -replace $heroPattern, "src=`"$heroUrl`""
  $content = $content -replace $infographicSrcPattern, "src=`"$infographicUrl`""
  $content = $content -replace $infographicHrefPattern, "href=`"$infographicUrl`""
  if ($content -ne $orig) {
    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]::new($false))
    $updated++
    Write-Host "Updated: $($file.FullName.Replace($root + '\', ''))"
  }
}
Write-Host "Done. Updated $updated files with stock images."
