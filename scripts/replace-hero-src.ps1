# Replace content-hero-img img src and alt with /images/ mapped file. Skip los-angeles-car-accident-lawyer.
$mapPath = "C:\Users\georgea\.cursor\projects\c-Users-georgea-insiderlawyer-com-images\image_mapping.json"
$lpRoot = "c:\Users\georgea\insiderlawyer-com-lps\pi-search-caraccident-lp"
$raw = Get-Content $mapPath -Raw
$map = $raw | ConvertFrom-Json
$updated = 0
foreach ($img in $map.images) {
    $url = $img.url
    if ($url -match 'los-angeles-car-accident-lawyer') { continue }
    $path = ''
    if ($url -and $url -ne 'https://www.insiderlawyers.com' -and $url -ne 'https://www.insiderlawyers.com/' -and $url -ne 'https://www.insiderlawyers.com/index.html') {
        $path = [System.Uri]$url | ForEach-Object { $_.AbsolutePath.Trim('/') }
        if ($path -eq 'index.html') { $path = '' }
    }
    $indexPath = if ($path -eq '') { Join-Path $lpRoot "index.html" } else { Join-Path $lpRoot ($path -replace '/', '\') "index.html" }
    if (-not (Test-Path $indexPath)) { continue }
    $html = Get-Content $indexPath -Raw
    if ($html -notmatch 'content-hero-img' -or $html -notmatch 'assets/images') { continue }
    $filename = $img.suggested_filename
    $alt = $img.alt_text -replace '"', '&quot;'
    $srcMatch = [regex]::Match($html, 'src="([^"]*assets/images[^"]+)"')
    if (-not $srcMatch.Success) { continue }
    $oldSrc = $srcMatch.Groups[1].Value
    $newHtml = $html.Replace('src="' + $oldSrc + '"', 'src="/images/' + $filename + '"')
    $imgAltPattern = '(?s)(<figure class="content-hero-img"[^>]*>\s*<img[^>]+alt=")[^"]*(")'
    $newHtml = $newHtml -replace $imgAltPattern, "`${1}$alt`${2}"
    if ($newHtml -ne $html) { Set-Content $indexPath -Value $newHtml -NoNewline; $updated++ }
}
Write-Output "Updated $updated pages (hero img src/alt to /images/)"
</think>
