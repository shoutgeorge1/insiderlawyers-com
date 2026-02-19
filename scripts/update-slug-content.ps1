# Updates head (title, description, canonical) and main content for each slug.
# Usage: .\scripts\update-slug-content.ps1

$base = "c:\Users\georgea\insiderlawyer-com-lps\pi-search-caraccident-lp"
$pages = @(
    @{ slug="delayed-pain-after-car-accident"; title="Delayed Pain After Car Accident | Insider"; desc="Why pain can appear days after a crash. California injury claims and when to see a doctor and a lawyer." },
    @{ slug="what-if-i-cant-afford-deductible"; title="What If I Can't Afford My Deductible? | Insider"; desc="Options when you can't pay your car insurance deductible after an accident in California." },
    @{ slug="what-is-uninsured-motorist-coverage"; title="What Is Uninsured Motorist (UM) Coverage? | Insider"; desc="How UM coverage works in California when the at-fault driver has no insurance or flees." },
    @{ slug="underinsured-motorist-claims-explained"; title="Underinsured Motorist (UIM) Claims Explained | Insider"; desc="When the at-fault driver's limits aren't enough. UIM claims in California explained." },
    @{ slug="who-is-liable-scooter-accident"; title="Who Is Liable in a Scooter Accident? | Insider"; desc="Liability for e-scooter and bike accidents in California: rider, rental company, or driver." },
    @{ slug="why-insurance-delays-claims"; title="Why Insurance Companies Delay Claims | Insider"; desc="Common reasons insurers delay injury claims and what you can do in California." },
    @{ slug="recorded-statement-should-you-give-one"; title="Recorded Statements: Should You Give One? | Insider"; desc="When to give a recorded statement to the insurance company after a California accident." },
    @{ slug="demand-letters-explained"; title="Demand Letters Explained | Insider"; desc="What a demand letter is, what it includes, and how it starts settlement in California injury claims." },
    @{ slug="how-insurance-calculates-settlement-offers"; title="How Insurance Calculates Settlement Offers | Insider"; desc="How adjusters value injury claims and make settlement offers in California." },
    @{ slug="comparative-negligence-california-explained"; title="Comparative Negligence in California Explained | Insider"; desc="Pure comparative fault in California: how your recovery is reduced if you're partly at fault." },
    @{ slug="what-if-liability-disputed"; title="What If Liability Is Disputed? | Insider"; desc="When the other side blames you. How California handles disputed fault in injury claims." }
)

foreach ($p in $pages) {
    $path = Join-Path $base "$($p.slug)\index.html"
    if (-not (Test-Path $path)) { continue }
    $c = [System.IO.File]::ReadAllText($path)
    $c = $c -replace "hit-and-run-accidents-los-angeles", $p.slug
    $c = $c -replace "Hit and Run Accidents in Los Angeles | Insider Accident Lawyers", $p.title
    $c = $c -replace "<title>Hit and Run Accidents in Los Angeles | Insider Accident Lawyers</title>", "<title>$($p.title)</title>"
    $c = $c -replace 'Hit and run accidents in LA: your rights, reporting, and recovery. California-specific guidance from a Los Angeles injury firm.', $p.desc
    $c = $c -replace 'Hit and run accidents in LA: your rights, reporting, and recovery. California-specific guidance.', $p.desc
    $c = $c -replace '"name":"Hit and Run Accidents in Los Angeles"', "`"name`":`"$($p.title -replace ' \| Insider','')`""
    [System.IO.File]::WriteAllText($path, $c)
    Write-Host "Updated head: $($p.slug)"
}
