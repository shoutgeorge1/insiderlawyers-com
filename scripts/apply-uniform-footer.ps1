# Apply the same footer as los-angeles-car-accident-lawyer to all pages that don't have it.
# Run from repo root: .\scripts\apply-uniform-footer.ps1
# FROZEN: Home page and all injury/accident PPC pages (los-angeles-*-lawyer, etc.) are skipped—already uniform.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $PSScriptRoot 'footer-template.txt'
$canonicalFooter = Get-Content -Path $templatePath -Raw
$footerCssLink = "`n<link rel=`"stylesheet`" href=`"/styles/footer.css`">"

$indexFiles = Get-ChildItem -Path $root -Recurse -Filter 'index.html' -File |
  Where-Object { $relPath = $_.FullName.Replace($root, '').Replace('\', '/'); $relPath -notmatch '/styles/|/scripts/|/images/|/node_modules/' }

$footerPattern = '(?s)<footer[^>]*>.*?</footer>'
$updated = 0
$skipped = 0

foreach ($file in $indexFiles) {
  $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
  if ($content -match 'footer__disclaimer' -and $content -match 'Injury &amp; Accident Types</h4>' -and $content -match 'California Guides</h4>') {
    $skipped++
    continue
  }
  if ($content -notmatch $footerPattern) {
    Write-Warning "No footer found: $($file.FullName)"
    continue
  }
  $content = [System.Text.RegularExpressions.Regex]::Replace($content, $footerPattern, $canonicalFooter, [System.Text.RegularExpressions.RegexOptions]::Singleline)
  if ($content -notmatch 'main\.css') {
    $content = $content -replace '</head>', "$footerCssLink`n</head>"
  }
  [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]::new($false))
  $updated++
  $rel = $file.FullName.Substring($root.Length).TrimStart('\', '/')
  Write-Host "Updated: $rel"
}

Write-Host ""
Write-Host "Done. Updated $updated files, skipped $skipped (already uniform)."
