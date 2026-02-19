# Apply nav and footer from insurance-company-playbook to all other index.html; remove infographics; add image; fix buttons.
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$templatePath = Join-Path $root "insurance-company-playbook\index.html"
$templateHtml = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8

$navStartMark = '<nav class="header-nav-row"'
$navStart = $templateHtml.IndexOf($navStartMark)
$navEnd = $templateHtml.IndexOf("</nav>", $navStart) + 7
$newNav = $templateHtml.Substring($navStart, $navEnd - $navStart)

$footerStartMark = '<footer class="site-footer"'
$footerStart = $templateHtml.IndexOf($footerStartMark)
$footerEnd = $templateHtml.IndexOf("</footer>", $footerStart) + 9
$newFooter = $templateHtml.Substring($footerStart, $footerEnd - $footerStart)

$contentImg = @"
                <figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&amp;q=80" alt="Legal and injury claim guidance" style="width:100%;height:auto;display:block;"></figure>

"@

$indexFiles = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\")
    $rel -ne "index.html" -and $_.FullName -ne $templatePath
}

$navReplaced = 0
$footerReplaced = 0
$infographicRemoved = 0
$imageAdded = 0
$buttonFixed = 0

foreach ($file in $indexFiles) {
    $html = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    $changed = $false

    $oldNavStart = $html.IndexOf($navStartMark)
    if ($oldNavStart -ge 0) {
        $oldNavEnd = $html.IndexOf("</nav>", $oldNavStart) + 7
        $oldNav = $html.Substring($oldNavStart, $oldNavEnd - $oldNavStart)
        if ($oldNav -ne $newNav) {
            $html = $html.Substring(0, $oldNavStart) + $newNav + $html.Substring($oldNavEnd)
            $navReplaced++
            $changed = $true
        }
    }

    $oldFooterStart = $html.IndexOf($footerStartMark)
    if ($oldFooterStart -ge 0) {
        $oldFooterEnd = $html.IndexOf("</footer>", $oldFooterStart) + 9
        $oldFooter = $html.Substring($oldFooterStart, $oldFooterEnd - $oldFooterStart)
        if ($oldFooter -ne $newFooter) {
            $html = $html.Substring(0, $oldFooterStart) + $newFooter + $html.Substring($oldFooterEnd)
            $footerReplaced++
            $changed = $true
        }
    }

    # Remove section asset-preview-block
    if ($html -match '<section class="asset-preview-block"[^>]*>[\s\S]*?</section>\s*') {
        $html = $html -replace '<section class="asset-preview-block"[^>]*>[\s\S]*?</section>\s*', ''
        $infographicRemoved++
        $changed = $true
    }
    # Remove div asset-preview-block
    if ($html -match '<div class="asset-preview-block"[^>]*>[\s\S]*?</div>\s*') {
        $html = $html -replace '<div class="asset-preview-block"[^>]*>[\s\S]*?</div>\s*', ''
        $infographicRemoved++
        $changed = $true
    }

    # Add content image if none (try after first </p> in main)
    if ($html -notmatch 'content-hero-img' -and $html -match '<main>') {
        $mainStart = $html.IndexOf('<main>')
        $firstPClose = $html.IndexOf('</p>', $mainStart)
        if ($firstPClose -ge 0) {
            $insertPoint = $firstPClose + 4
            $html = $html.Substring(0, $insertPoint) + "`n                " + $contentImg.Trim() + "`n                " + $html.Substring($insertPoint)
            $imageAdded++
            $changed = $true
        }
    }


    if ($html -match 'Get My Free Case Review') {
        $html = $html -replace 'Get My Free Case Review', 'Free Case Review'
        $buttonFixed++
        $changed = $true
    }

    if ($changed) {
        [System.IO.File]::WriteAllText($file.FullName, $html, [System.Text.UTF8Encoding]::new($false))
    }
}

Write-Host "Nav replaced: $navReplaced"
Write-Host "Footer replaced: $footerReplaced"
Write-Host "Infographic blocks removed: $infographicRemoved"
Write-Host "Content image added: $imageAdded"
Write-Host "Buttons fixed: $buttonFixed"
Write-Host "Total files processed: $($indexFiles.Count)"
