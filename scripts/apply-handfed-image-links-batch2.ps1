# Batch 2: Map image URLs to slugs by content, download to assets, update pages.
# Fills gaps (at-fault, attorney-referrals, insurance-company-playbook) + rows 37+.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$customDir = Join-Path $root "assets\images\custom"
if (-not (Test-Path $customDir)) { New-Item -ItemType Directory -Path $customDir -Force | Out-Null }

# Slug -> URL mapping (by image content / URL context). Skip page URLs and low-quality thumbnails where possible.
$slugToUrl = @{
    "at-fault-driver-no-insurance" = "https://bayukpratt.com/wp-content/uploads/2025/03/worried-uninsured-driver.jpg"
    "attorney-referrals" = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtKq5XSAJjLRGUZYAufgHEkLW8x4xnp29BCw&s"
    "insurance-company-playbook" = "https://www.bic-agent.com/wp-content/uploads/sites/158/2025/04/insurance-adjuster-inspecting-damaged-vehicle.jpg"
    "major-car-accident" = "https://d3b3by4navws1f.cloudfront.net/shutterstock_338951957.jpg"
    "motorcycle-accident-case" = "https://www.dolmanlaw.com/wp-content/uploads/2018/06/7-Common-Motorcycle-Crashes-and-How-to-Avoid-Them-e1515682663599.jpg"
    "parking-lot-accident-lawyer-los-angeles" = "https://rochlinlaw.com/wp-content/uploads/2016/10/parking-lot-crash.jpg"
    "what-if-i-cant-afford-deductible" = "https://www.grxstatic.com/4f3rgqwzdznj/3pDoiHrVOeMbrs5bC6LKMm/c7a0f032d6b8636282ca6b56d413b816/family_managing_their_budget_2182944390.webp?w=640&q=85&fm=webp"
    "personal-injury/auto-accidents" = "https://www.iii.org/sites/default/files/p_auto_accident_475395935.jpg"
    "what-is-uninsured-motorist-coverage" = "https://www.orionindemnity.com/assets/images/blog-images/insurance-tips/uninsured-motorist-coverage-feature.jpg"
    "personal-injury/brain-injuries" = "https://www.spencelawyers.com/images/jcogs_img/cache/types_of_TBI_May_-_28de80_-_2e8442d965620ff52d53b9a1a9a0fe3d30f5c75f.webp"
    "traumatic-brain-injury-car-accident-settlement-california" = "https://www.gjel.com/wp-content/uploads/2022/08/tbi-settlement-500x263-1.png"
    "recover-destroyed-scooter-ebike" = "https://www.datocms-assets.com/183103/1766018685-electric-scooter-injuries.jpg?auto=format,compress"
    "personal-injury/wrongful-death" = "https://www.oconnorpersonalinjury.com/wp-content/uploads/2020/04/family-file-wrongful-death.jpg"
    "lit-referral-wrongful-death" = "https://nesslerlaw.com/wp-content/uploads/2022/09/wrongful-death-min.jpg"
    "uber-or-lyft-accident" = "https://www.frplegal.com/wp-content/uploads/2023/06/Uber-Accident.webp"
    "uber-accident-lawyer-los-angeles" = "https://jmllaw.com/wp-content/uploads/Los-Angeles-Uber-Accident-Attorney.webp"
    "truck-accident-legal-rights" = "https://mcarthurlawfirm.com/wp-content/uploads/2025/04/truck_accident.webp"
    "proving-truck-accident-case" = "https://www.thetrucker.com/wp-content/uploads/2025/08/UTURN-copy-768x492-1.jpg"
    "injuries-truck-accidents" = "https://www.gerlinglaw.com/wp-content/uploads/2024/05/Truck-Accident.jpg"
    "personal-injury/spine-injuries" = "https://www.advancedreconstruction.com/hs-fs/hubfs/IFAR/spinal-cord-injury.jpg?width=1920&height=1200&name=spinal-cord-injury.jpg"
    "personal-injury/slip-and-fall" = "https://www.spektorlaw.com/wp-content/uploads/2022/06/slip-fall-accidents-main.webp"
}
# Optional: passenger-in-uninsured-car with first tbn if we want (low quality). Omit to avoid.
# "passenger-in-uninsured-car" = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxBFzULNyFM87-q_4749OJDgS2qGVzArSKKw&s"

$ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
$extMap = @{}

foreach ($slug in $slugToUrl.Keys) {
    $url = $slugToUrl[$slug]
    $uri = [System.Uri]$url
    $pathPart = $uri.AbsolutePath
    if ($pathPart -match '\.(jpe?g|png|webp|gif)$') { $ext = $Matches[1] } else { $ext = "jpg" }
    if ($ext -eq "jpeg") { $ext = "jpg" }
    $safeSlug = $slug -replace '/', '-'
    $outName = "$safeSlug.$ext"
    $outPath = Join-Path $customDir $outName
    try {
        Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing -UserAgent $ua -MaximumRedirection 5
        $extMap[$slug] = @{ ext = $ext; file = $outName }
        Write-Host "OK $slug"
    } catch {
        Write-Host "FAIL $slug : $_"
    }
}

# Update HTML: content-hero-img src -> /assets/images/custom/<file>
$updated = 0
foreach ($slug in $extMap.Keys) {
    $info = $extMap[$slug]
    $imgFile = $info.file
    $src = "/assets/images/custom/$imgFile"
    $path = $root
    foreach ($part in $slug -split '/') { $path = Join-Path $path $part }
    $path = Join-Path $path "index.html"
    if (-not (Test-Path $path)) { Write-Host "Page not found: $path"; continue }
    $html = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    $h1Match = [regex]::Match($html, '<h1[^>]*>([^<]+)</h1>')
    $altText = if ($h1Match.Success) { "Illustration: " + ($h1Match.Groups[1].Value -replace "&[^;]+;"," ").Substring(0, [Math]::Min(80, ($h1Match.Groups[1].Value).Length)) -replace '"', "'" } else { "Illustration" }
    $pattern = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+[^>]*src="[^"]*"[^>]*>'
    $replacement = "`$1<img decoding=`"async`" src=`"$src`" alt=`"$altText`" width=`"1200`" height=`"630`" style=`"width:100%;height:auto;display:block;`">"
    $newHtml = $html -replace $pattern, $replacement
    if ($newHtml -ne $html) {
        [System.IO.File]::WriteAllText($path, $newHtml, [System.Text.UTF8Encoding]::new($false))
        $updated++
    }
}
Write-Host "Updated $updated pages."
