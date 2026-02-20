# Generate sitemap.xml from all index.html in repo. One URL per page, no trailing slash.
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$baseUrl = "https://www.insiderlawyers.com"
$today = Get-Date -Format "yyyy-MM-dd"

$rootNorm = [System.IO.Path]::GetFullPath($root).TrimEnd("\", "/")
$sep = [System.IO.Path]::DirectorySeparatorChar
$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | ForEach-Object {
    $fullPath = [System.IO.Path]::GetFullPath($_.FullName)
    if (-not $fullPath.StartsWith($rootNorm, [StringComparison]::OrdinalIgnoreCase)) { return $null }
    $afterRoot = $fullPath.Substring($rootNorm.Length).TrimStart($sep).Replace($sep, "/")
    $urlPath = $afterRoot -replace "/index\.html$", ""
    if ($urlPath -eq "") { "/" } else { "/" + $urlPath }
} | Where-Object { $_ } | Sort-Object

$out = New-Object System.Text.StringBuilder
[void]$out.AppendLine('<?xml version="1.0" encoding="UTF-8"?>')
[void]$out.AppendLine('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">')
# Home page first
[void]$out.AppendLine("  <url>")
[void]$out.AppendLine("    <loc>${baseUrl}/</loc>")
[void]$out.AppendLine("    <lastmod>$today</lastmod>")
[void]$out.AppendLine("    <changefreq>monthly</changefreq>")
[void]$out.AppendLine("    <priority>1.00</priority>")
[void]$out.AppendLine("  </url>")

$files = $files | Where-Object { $_ -ne "/" }
foreach ($path in $files) {
    $loc = $baseUrl + $path
    $priority = if ($path -eq "/") { "1.00" } else { "0.80" }
    [void]$out.AppendLine("  <url>")
    [void]$out.AppendLine("    <loc>$loc</loc>")
    [void]$out.AppendLine("    <lastmod>$today</lastmod>")
    [void]$out.AppendLine("    <changefreq>monthly</changefreq>")
    [void]$out.AppendLine("    <priority>$priority</priority>")
    [void]$out.AppendLine("  </url>")
}
[void]$out.AppendLine("</urlset>")

$outPath = Join-Path $root "sitemap.xml"
[System.IO.File]::WriteAllText($outPath, $out.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote sitemap.xml with $($files.Count + 1) URLs (including home)."