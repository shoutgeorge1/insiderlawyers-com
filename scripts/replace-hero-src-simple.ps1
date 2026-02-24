$mapPath = Join-Path $PSScriptRoot "image_mapping.json"
$lpRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$raw = Get-Content $mapPath -Raw -Encoding UTF8
$map = $raw | ConvertFrom-Json
$updated = 0
foreach ($img in $map.images) {
    $url = $img.url
    if ($url -match 'los-angeles-car-accident-lawyer') { continue }
    $path = ''
    if ($url -and $url -ne 'https://www.insiderlawyers.com' -and $url -ne 'https://www.insiderlawyers.com/' -and $url -ne 'https://www.insiderlawyers.com/index.html') {
        $uri = [System.Uri]$url
        $path = $uri.AbsolutePath.Trim('/')
        if ($path -eq 'index.html') { $path = '' }
    }
    $indexPath = if ($path -eq '') { Join-Path $lpRoot "index.html" } else { Join-Path (Join-Path $lpRoot ($path -replace '/', [char]92)) "index.html" }
    if (-not (Test-Path -LiteralPath $indexPath)) { continue }
    $html = Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8
    if ($null -eq $html) { continue }
    if ($html -notmatch 'content-hero-img' -or $html -notmatch 'assets/images') { continue }
    $filename = $img.suggested_filename
    $srcMatch = [regex]::Match($html, 'src="([^"]*assets/images[^"]+)"')
    if (-not $srcMatch.Success) { continue }
    $oldSrc = $srcMatch.Groups[1].Value
    $newHtml = $html.Replace('src="' + $oldSrc + '"', 'src="/images/' + $filename + '"')
    if ($newHtml -eq $html) { continue }
    Set-Content -LiteralPath $indexPath -Value $newHtml -NoNewline -Encoding UTF8
    $updated++
}
Write-Output "Updated $updated pages."
