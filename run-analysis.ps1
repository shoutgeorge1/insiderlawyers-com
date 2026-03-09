$base = "c:\Users\georgea\insiderlawyer-com-lps\insiderlawyers-com"
$outPath = Join-Path $base "INDEXABILITY-ANALYSIS.txt"
$exclude = '_old-site-extract|\\components\\|_dev|social-assets'
$htmlFiles = Get-ChildItem -Path $base -Recurse -Filter "*.html" -File | Where-Object { $_.FullName -notmatch $exclude }

function Normalize-ToUrlPath {
  param([string]$relPath)
  $relPath = $relPath -replace '\\', '/'
  if ($relPath -eq "index.html") { return "/" }
  if ($relPath -match '^(.+)/index\.html$') { return "/" + $Matches[1] + "/" }
  return "/" + ($relPath -replace '\.html$', '') + "/"
}

function Get-WordCount {
  param([string]$html)
  $noScript = [regex]::Replace($html, '(?s)<script[^>]*>.*?</script>', ' ')
  $noStyle = [regex]::Replace($noScript, '(?s)<style[^>]*>.*?</style>', ' ')
  $noTags = [regex]::Replace($noStyle, '<[^>]+>', ' ')
  $words = ($noTags -split '\s+').Where({ $_.Length -gt 0 })
  return $words.Count
}

function Get-InternalLinks {
  param([string]$html)
  [regex]::Matches($html, 'href="(/(?:[^"#?]*))') | ForEach-Object {
    $p = $_.Groups[1].Value.TrimEnd('/')
    if ($p -and $p -notmatch '^/(styles|scripts|images|assets|fonts)/' -and $p -notmatch '\.(css|js|png|jpg|jpeg|gif|svg|ico|woff)') {
      if ($p -eq '') { '/' } else { '/' + $p + '/' }
    }
  } | Where-Object { $_ }
}

$allTargets = @{}
$csvRows = @()
$linkTargetsSet = @{}

foreach ($f in $htmlFiles) {
  $rel = $f.FullName.Substring($base.Length + 1)
  $urlPath = Normalize-ToUrlPath $rel
  $html = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
  if (-not $html) { continue }
  $hasCanonical = $html -match '<link\s+[^>]*rel="canonical"'
  $hasTitle = $html -match '<title[^>]*>'
  $noindex = ($html -match 'noindex') -or ($html -match 'robots[^>]*content="[^"]*noindex')
  $wordCount = Get-WordCount $html
  $csvRows += "`"$urlPath`",$hasCanonical,$hasTitle,$noindex,$wordCount"
  $links = Get-InternalLinks $html
  foreach ($t in $links) {
    $norm = if ($t -eq '/') { '/' } else { $t.TrimEnd('/') + '/' }
    if ($norm -notmatch '^/(styles|scripts|images|assets|fonts)/' -and $norm -notmatch '\.(css|js|png|jpg)') {
      $linkTargetsSet[$norm] = $true
    }
  }
}

$allPaths = $csvRows | ForEach-Object { ($_ -split ',')[0] -replace '"', '' }
$orphans = $allPaths | Where-Object {
  $key = if ($_ -eq '/') { '/' } else { $_.TrimEnd('/') + '/' }
  -not $linkTargetsSet[$key]
} | Sort-Object -Unique

$indexHtml = Get-Content (Join-Path $base "index.html") -Raw
$navBlock = [regex]::Match($indexHtml, '(?s)<nav[^>]*>.*?</nav>').Value
$footerBlock = [regex]::Match($indexHtml, '(?s)<footer[^>]*>.*?</footer>').Value
$navFooterHtml = $navBlock + " " + $footerBlock
$navLinks = [regex]::Matches($navFooterHtml, 'href="(/(?:[^"#]*))') | ForEach-Object {
  $p = $_.Groups[1].Value -replace '#.*', '' -replace '\?.*', ''
  $p = $p.TrimEnd('/')
  if ($p -and $p -notmatch '^/(styles|scripts|images|assets|fonts)/' -and $p -notmatch '\.(css|js|png|jpg)') {
    if ($p -eq '') { '/' } else { '/' + $p + '/' }
  }
} | Sort-Object -Unique

$inNav = @{}
foreach ($n in $navLinks) { $inNav[$n] = $true }
$inNavList = $navLinks
$notInNavList = $allPaths | Where-Object {
  $key = if ($_ -eq '/') { '/' } else { $_.TrimEnd('/') + '/' }
  -not $inNav[$key]
} | Sort-Object

$allLinkTargetsList = $linkTargetsSet.Keys | Sort-Object -Unique

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("=== path, has_canonical, has_title, noindex, word_count ===")
foreach ($r in $csvRows) { [void]$sb.AppendLine($r) }
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=== All internal link targets (normalized) ===")
foreach ($t in $allLinkTargetsList) { [void]$sb.AppendLine($t) }
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=== Orphan paths (never linked to) ===")
foreach ($o in $orphans) { [void]$sb.AppendLine($o) }
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=== Paths IN main nav (from index.html nav+footer) ===")
foreach ($n in $inNavList) { [void]$sb.AppendLine($n) }
[void]$sb.AppendLine("")
[void]$sb.AppendLine("=== Paths NOT in main nav ===")
foreach ($x in $notInNavList) { [void]$sb.AppendLine($x) }
$sb.ToString() | Set-Content $outPath -Encoding UTF8
Write-Host "Written to $outPath"
