# Replace all Unsplash photo URLs with the one known-good ID so images actually load.
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$goodUrl = "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&amp;q=80"
# Match any photo-XXXX-XXXX?w=1200 (with &amp; or &) and q=80
$pattern = "https://images\.unsplash\.com/photo-[0-9a-zA-Z\-]+\?w=1200(&amp;|&)q=80"
$files = Get-ChildItem -Path $root -Recurse -Filter "*.html" -File | Where-Object { $_.FullName -notmatch "\\node_modules\\" }
$count = 0
foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    if ($html -match $pattern) {
        $newHtml = $html -replace $pattern, $goodUrl
        if ($newHtml -ne $html) {
            [System.IO.File]::WriteAllText($f.FullName, $newHtml, [System.Text.UTF8Encoding]::new($false))
            $count++
        }
    }
}
Write-Host "Fixed Unsplash URLs in $count files."