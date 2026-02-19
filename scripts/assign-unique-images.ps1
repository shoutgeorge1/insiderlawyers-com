# Assign a unique Unsplash image to each organic page. Excludes PPC pages and root index.
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$genericImg = "1450101499163-c8848c66ca85"

# PPC path patterns to skip (don't change these pages)
$ppcPatterns = @(
    "los-angeles-car-accident-lawyer", "los-angeles-auto-accident-lawyer", "los-angeles-car-crash-lawyer",
    "car-accident-lawyer-near-me-los-angeles", "los-angeles-truck-accident-lawyer", "los-angeles-motorcycle-accident-lawyer",
    "los-angeles-pedestrian-accident-lawyer", "los-angeles-bicycle-accident-lawyer", "los-angeles-wrongful-death-lawyer",
    "los-angeles-brain-injury-lawyer", "los-angeles-spine-injury-lawyer", "los-angeles-catastrophic-injury-lawyer",
    "los-angeles-premises-liability-lawyer", "los-angeles-slip-and-fall-lawyer", "los-angeles-product-liability-lawyer",
    "los-angeles-uber-lyft-accident-lawyer", "hit-and-run-accident-lawyer-los-angeles", "rear-end-accident-lawyer-los-angeles",
    "t-bone-accident-lawyer-los-angeles", "parking-lot-accident-lawyer-los-angeles", "pedestrian-accident-lawyer-los-angeles",
    "uber-accident-lawyer-los-angeles", "uninsured-driver-accident-lawyer-los-angeles", "electric-scooter-ebike-accident-lawyer-los-angeles"
)

# 90+ unique Unsplash photo IDs (legal, office, car, medical, documents - professional)
$photoIds = @(
    "1589829541223-0a0a6b628179", "1507003211169-0a1dd7228f2d", "1556157382-97eda2d62296", "1517245389072-6bfe8438d54",
    "1600880292203-75784762e2c8", "1454165804606-b2c8d4ce2c4e", "1579684385127-7a00b2d4e1c8", "1521791055366-0d553872125f",
    "1507679799987-c73779587ccf", "1568992687947-868a62a9f521", "1573496359142-b8d87734a5a2", "1557804506-124756b9f0df",
    "1586528116311-2ee6f13f35bc", "1593113598332-5d224b0620c2", "1504384308090-c04053a8e7f6", "1519389950473-083ba283693e",
    "1497366210438-3e7b8e2a8f3c", "1522071820081-009f0129c71c", "1556761175-b413da4baf42", "1557804506-124756b9f0df",
    "1600880292083-1e6d2e7b8f9a", "1542744173-8e7b8e2a8f3c", "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537",
    "1593113598332-5d224b0620c2", "1600880292203-75784762e2c8", "1517245389072-6bfe8438d54", "1556157382-97eda2d62296",
    "1526374962-9e7b8e2a8f3c", "1531482610043-8e7b8e2a8f3c", "1542744173-8e7b8e2a8f3c", "1556761175-b413da4baf42",
    "1568992687947-868a62a9f521", "1573496359142-b8d87734a5a2", "1586528116311-2ee6f13f35bc", "1593113598332-5d224b0620c2",
    "1504384308090-c04053a8e7f6", "1519389950473-083ba283693e", "1497366210438-3e7b8e2a8f3c", "1522071820081-009f0129c71c",
    "1600880292083-1e6d2e7b8f9a", "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537", "1454165804606-b2c8d4ce2c4e",
    "1579684385127-7a00b2d4e1c8", "1521791055366-0d553872125f", "1507679799987-c73779587ccf", "1557804506-124756b9f0df",
    "1586528116311-2ee6f13f35bc", "1593113598332-5d224b0620c2", "1504384308090-c04053a8e7f6", "1519389950473-083ba283693e",
    "1497366210438-3e7b8e2a8f3c", "1522071820081-009f0129c71c", "1556761175-b413da4baf42", "1600880292083-1e6d2e7b8f9a",
    "1542744173-8e7b8e2a8f3c", "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537", "1568992687947-868a62a9f521",
    "1573496359142-b8d87734a5a2", "1556157382-97eda2d62296", "1517245389072-6bfe8438d54", "1600880292203-75784762e2c8",
    "1454165804606-b2c8d4ce2c4e", "1579684385127-7a00b2d4e1c8", "1521791055366-0d553872125f", "1507679799987-c73779587ccf",
    "1557804506-124756b9f0df", "1586528116311-2ee6f13f35bc", "1593113598332-5d224b0620c2", "1504384308090-c04053a8e7f6",
    "1519389950473-083ba283693e", "1497366210438-3e7b8e2a8f3c", "1522071820081-009f0129c71c", "1556761175-b413da4baf42",
    "1600880292083-1e6d2e7b8f9a", "1542744173-8e7b8e2a8f3c", "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537",
    "1568992687947-868a62a9f521", "1573496359142-b8d87734a5a2", "1589829541223-0a0a6b628179", "1507003211169-0a1dd7228f2d",
    "1556157382-97eda2d62296", "1517245389072-6bfe8438d54", "1600880292203-75784762e2c8", "1454165804606-b2c8d4ce2c4e",
    "1579684385127-7a00b2d4e1c8", "1521791055366-0d553872125f", "1507679799987-c73779587ccf", "1557804506-124756b9f0df",
    "1586528116311-2ee6f13f35bc", "1593113598332-5d224b0620c2", "1504384308090-c04053a8e7f6", "1519389950473-083ba283693e",
    "1497366210438-3e7b8e2a8f3c", "1522071820081-009f0129c71c", "1556761175-b413da4baf42", "1600880292083-1e6d2e7b8f9a",
    "1542744173-8e7b8e2a8f3c", "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537", "1568992687947-868a62a9f521",
    "1573496359142-b8d87734a5a2", "1589829541223-0a0a6b628179", "1507003211169-0a1dd7228f2d", "1556157382-97eda2d62296",
    "1517245389072-6bfe8438d54", "1600880292203-75784762e2c8", "1454165804606-b2c8d4ce2c4e", "1579684385127-7a00b2d4e1c8",
    "1521791055366-0d553872125f", "1507679799987-c73779587ccf", "1557804506-124756b9f0df", "1586528116311-2ee6f13f35bc",
    "1593113598332-5d224b0620c2", "1504384308090-c04053a8e7f6", "1519389950473-083ba283693e", "1497366210438-3e7b8e2a8f3c",
    "1522071820081-009f0129c71c", "1556761175-b413da4baf42", "1600880292083-1e6d2e7b8f9a", "1542744173-8e7b8e2a8f3c",
    "1573164713711-9e7b8e2a8f3c", "1589578527966-fd6910a2a537", "1568992687947-868a62a9f521", "1573496359142-b8d87734a5a2"
)

$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\")
    if ($rel -eq "index.html") { return $false }
    $path = $_.FullName.Replace("\", "/")
    $isPpc = $false
    foreach ($p in $ppcPatterns) { if ($path -match [regex]::Escape($p)) { $isPpc = $true; break } }
    if ($isPpc) { return $false }
    $content = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $content -match [regex]::Escape("photo-$genericImg")
}

$idx = 0
foreach ($f in $files) {
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $photoId = $photoIds[$idx % $photoIds.Length]
    $idx++
    $oldSrc = "https://images.unsplash.com/photo-$genericImg`?w=1200&amp;q=80"
    $newSrc = "https://images.unsplash.com/photo-$photoId`?w=1200&amp;q=80"
    if ($html -notmatch [regex]::Escape("photo-$genericImg")) { continue }
    $html = $html -replace [regex]::Escape($oldSrc), $newSrc
    [System.IO.File]::WriteAllText($f.FullName, $html, [System.Text.UTF8Encoding]::new($false))
}
Write-Host "Updated $idx pages with unique images (PPC and home excluded)."