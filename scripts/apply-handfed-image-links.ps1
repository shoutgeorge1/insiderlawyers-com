# Apply hand-fed image URLs: download to assets/images/custom and update pages 1-36.
# Skip homepage and PPC. Use root-relative /assets/images/custom/ for Vercel.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$customDir = Join-Path $root "assets\images\custom"
if (-not (Test-Path $customDir)) { New-Item -ItemType Directory -Path $customDir -Force | Out-Null }

# Slugs 1-36 (order from IMAGE-LINKS-SPEC)
$slugs = @(
    "adjuster-claim-valuation", "at-fault-driver-no-insurance", "attorney-referrals", "brain-injury",
    "california-car-accident-lawyer", "california-comparative-negligence-personal-injury", "can-i-sue-uninsured-driver-personally",
    "comparative-negligence-california-explained", "delayed-pain-after-car-accident", "demand-letter-negotiation", "demand-letters-explained",
    "does-filing-um-claim-raise-rates", "do-i-need-police-report-accident", "electric-scooter-ebike-accident-lawyer-los-angeles",
    "evidence-preservation-car-accident-california", "herniated-disc-car-accident-settlement-california", "hit-and-run-accident-lawyer-los-angeles",
    "hit-and-run-accidents-los-angeles", "how-adjusters-value-claims", "how-insurance-calculates-settlement-offers",
    "how-long-does-a-car-accident-settlement-take-california", "how-much-is-my-car-accident-worth-california", "injuries-truck-accidents",
    "insurance-company-playbook", "insurance-company-tactics-personal-injury", "lit-referral-brain-injury", "lit-referral-catastrophic-cases",
    "lit-referral-core", "lit-referral-coverage-disputes", "lit-referral-criteria", "lit-referral-economics",
    "lit-referral-process", "lit-referral-trial-ready-cocounsel", "lit-referral-truck-litigation", "lit-referral-wrongful-death",
    "lowball-offer-response"
)

# URLs 1-36 in order (skip #6 - page URL not image)
$urls = @(
    "https://erinjuryattorneys.com/wp-content/uploads/2022/01/insurance-adjuster.jpg",
    "https://jdchapmaninc.com/wp-content/uploads/2021/05/insurance-claims-adjustor-min.jpg",
    "https://jdchapmaninc.com/wp-content/uploads/2021/05/insurance-claims-adjustor-min.jpg",
    "https://myaccidentlaw.com/wp-content/uploads/2025/01/Is-an-uninsured-driver-automatically-at-fault-_30322498_Altered_Lloyd.webp",
    "https://www.myinjuryattorney.com/wp-content/uploads/2021/04/Car-accident-2.jpg",
    "https://feherlawfirm.com/wp-content/uploads/damaged-in-heavy-car-accident-vehicles-after-colli-2023-11-27-05-22-40-utc_1920x1280.webp",
    "https://www.vazirilaw.com/wp-content/uploads/2025/08/california-comparative-negligence-law-jpg1741765752.jpeg",
    "https://dubolawfirm.com/wp-content/uploads/2021/10/Can-I-Sue-an-Uninsured-Driver-in-Maryland.jpg",
    "https://www.singhahluwalia.com/wp-content/uploads/2023/11/Can-an-Uninsured-Driver-Still-Sue-for-Personal-Injuries-After-an-Accident.webp",
    "https://www.mmcdlaw.com/wp-content/uploads/2025/08/What-To-Do-When-You-Experience-Delayed-Pain-After-an-Accident.jpg",
    "https://aica.com/wp-content/uploads/2024/09/What-To-Do-About-Delayed-Back-Pain-After-a-Car-Accident.jpg",
    "https://www.lhllaw.com/wp-content/uploads/2024/12/What-to-Do-When-You-Experience-Delayed-Pain-After-an-Accident.jpg",
    "https://www.abellawfirm.com/wp-content/uploads/2022/09/what-happens-after-my-lawyer-sends-a-demand-letter.jpg",
    "https://cdn-cdmba.nitrocdn.com/uheqsOdLzLIywRoatxoItdjbtlmHZVLN/assets/images/optimized/rev-3e9dbf5/1800lionlaw.com/wp-content/uploads/2025/02/Arizona-demand-letter.jpg",
    "https://i0.wp.com/becklawny.com/wp-content/uploads/2025/11/New-York-Uninsured-Motorist-Benefits-Car-Accident-Claim-Denied-UM-Coverage-Options.jpg?fit=503%2C302&ssl=1",
    "https://www.tranlawgrp.com/wp-content/uploads/2022/07/2bf8a8_e6e053115d304d3e9d9aa2ca95223036_mv2.webp",
    "https://www.colombolaw.com/wp-content/uploads/2021/11/reporting-car-accident-to-police.jpg",
    "https://www.colombolaw.com/wp-content/uploads/2021/11/reporting-car-accident-to-police.jpg",
    "https://nypost.com/wp-content/uploads/sites/2/2024/07/electric-scooter-accident-no-criminality-4736669.jpg?quality=75&strip=all&w=1024",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBF8j9i8WGY07cEaS0z8rQkmiOKq8yvR11kg&s",
    "https://www.razavilawgroup.com/wp-content/uploads/2023/10/road-accident-with-car-and-broken-bicycle-scaled.jpg",
    "https://cdn.lawlytics.com/law-media/uploads/291/62208/large/Bigstock_20Hit_20and_20Run.jpg?1544571162",
    "https://quinnanlaw.com/wp-content/uploads/2019/06/hit-and-run-accidents-crime.jpeg",
    "https://lawforpersonalinjury.com/wp-content/uploads/2024/01/Car-Crash-Evidence-A-1024x572.webp",
    "https://mhkylaw.com/wp-content/uploads/2023/10/woman-getting-evidence-after-car-crash-scaled-1.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEoBQwfRuFpQD_G1HLxuFAOrccqUnKwkev0g&s",
    "https://www.socalpersonalinjurylawyer.com/wp-content/uploads/2021/10/average-settlement-for-herniated-disk-car-accident.jpg",
    "https://helpingthehurt.com/hubfs/Blog%20Images/What%20is%20a%20Claims%20Adjuster%20and%20How%20do%20they%20Determine%20the%20Value%20of%20my%20Car/Insurance%20Adjuster%20Determining%20the%20Value%20of%20a%20Car%20after%20an%20accident.jpg",
    "https://www.oconnorpersonalinjury.com/wp-content/uploads/2019/08/insurance-settlements.jpg",
    "https://cooperatornews.com/_data/ny/articles/1908_image1.jpg?w=793",
    "https://www.klnivenlaw.com/wp-content/uploads/2023/12/Car-Accident-Settlement-Timeline-in-Pennsylvania.jpeg",
    "https://lawyer1.com/wp-content/uploads/2024/02/header-claim-worth.jpg",
    "https://www.bressmanlaw.com/wp-content/uploads/2022/08/how-are-truck-accidents-different-than-car-accidents.jpg",
    "https://fgpglaw.com/wp-content/uploads/2021/09/How-Many-Trucking-Accidents-Happen-a-Year.jpg",
    "https://www.yourcentralvalley.com/wp-content/uploads/sites/54/2024/08/SEMI-PIC.jpg?w=900",
    "https://parris.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F2hppufv0%2Fproduction%2Fe2b309ddfae7483df51b7cefa7608853f74ba16e-708x471.webp&w=3840&q=75",
    "https://www.vylawfirm.com/wp-content/uploads/2024/08/insurance-adjuster-secret-tactics-you-need-to-know.png",
    "https://citywideinjury.com/wp-content/uploads/2025/10/pi-lawyers-vs-insurance.webp",
    "https://mindsmatterllc.com/wp-content/uploads/2024/01/referral-e1705874702211.jpg",
    "https://www.ihsslaw.com/wp-content/uploads/2024/08/Traumatic-Brain-Injury-1024x658.jpg",
    "https://eco99e9y5oz.exactdn.com/wp-content/uploads/2023/08/traumatic-brain-injury.jpg?strip=all&webp=92",
    "https://gautreauxlawfirm.com/wp-content/uploads/2023/10/catastrophic.jpg",
    "https://gm8-ydlegal-cdn.b-cdn.net/wp-content/uploads/2022/01/Catastrophic-Injuries.jpg",
    "https://panewsmedia.org/wp-content/uploads/Stock_PNA_Photos/Feature_Images/Legal-LegalServices.jpg",
    "https://www.crantfordmeehan.com/wp-content/uploads/2026/01/Attorney-Referrals-Image.webp",
    "https://michellawyers.com/wp-content/uploads/2016/06/Decubitus-Ulcer-Lawyer1.jpg",
    "https://www.legal-insurance-blog.com/files/2014/12/95322156-attorney-clients-shacking-hands-deal-contract-negotiations.jpeg",
    "https://www.hugheylawfirm.com/wp-content/uploads/2020/11/hugh_attorney-referrals_photo-850x424.jpg",
    "https://www.datocms-assets.com/148522/1739981750-daycare-abuse-and-negligence-banner.jpg?auto=format,compress&w=1680",
    "https://cdn.prod.website-files.com/64e7a19b488adcdfce8602bb/6584891f4d92341e4edab646_AdobeStock_488406404.jpg"
)

# Use first 36 URLs only (one per slug)
$urls = $urls[0..35]
if ($slugs.Count -ne $urls.Count) { throw "Slug count $($slugs.Count) vs URL count $($urls.Count)" }

$ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
$extMap = @{}  # slug -> extension to use in HTML

for ($i = 0; $i -lt $urls.Count; $i++) {
    $slug = $slugs[$i]
    $url = $urls[$i]
    $uri = [System.Uri]$url
    $pathPart = $uri.AbsolutePath
    if ($pathPart -match '\.(jpe?g|png|webp|gif)$') { $ext = $Matches[1] } else { $ext = "jpg" }
    if ($ext -eq "jpeg") { $ext = "jpg" }
    $outName = "$slug.$ext"
    $outPath = Join-Path $customDir $outName
    try {
        Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing -UserAgent $ua -MaximumRedirection 5
        $extMap[$slug] = $ext
        Write-Host "OK $($i+1)/$($urls.Count) $slug"
    } catch {
        Write-Host "FAIL $($i+1) $slug : $_"
    }
}

# Update HTML: set content-hero-img src to /assets/images/custom/<slug>.<ext> (root-relative for Vercel)
$slugToExt = $extMap
$updated = 0
foreach ($slug in $slugs) {
    if (-not $slugToExt.ContainsKey($slug)) { continue }
    $ext = $slugToExt[$slug]
    $imgFile = "$slug.$ext"
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
Write-Host "Updated $updated pages with new image paths."
