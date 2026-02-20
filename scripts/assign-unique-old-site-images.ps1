# One unique image per page. Copies enough images from old site into assets/images/old-site,
# then assigns each page (in stable order) to a different image. No manual feed needed.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$oldRoot = Join-Path $root "_old-site-extract"
$oldImagesDir = Join-Path $oldRoot "Resources\images"
$oldFilesDir = Join-Path $oldRoot "Resources\files"
$destDir = Join-Path $root "assets\images\old-site"

if (-not (Test-Path $oldImagesDir)) {
    Write-Error "Old site not found at $oldRoot. Extract insideraccidentlawyers.zip to $oldRoot first."
}
if (-not (Test-Path (Join-Path $root "assets\images"))) {
    New-Item -ItemType Directory -Path (Join-Path $root "assets\images") -Force | Out-Null
}
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

# All content images to use (prefer -2880w or -1920w). Order determines assignment: page 1 -> image 1, etc.
$sources = @(
    @{ dir = "images"; name = "Animal Attacks-2880w.jpg" },
    @{ dir = "images"; name = "navigation-car-drive-road-2880w.jpg" },
    @{ dir = "images"; name = "Catastrophic Injuries-1920w.jpeg" },
    @{ dir = "images"; name = "Pedestrian Accidents-1920w.jpeg" },
    @{ dir = "images"; name = "Premises Liability-1920w.jpg" },
    @{ dir = "images"; name = "Product Liability-2880w.jpeg" },
    @{ dir = "images"; name = "Spine Injuries-2880w.jpeg" },
    @{ dir = "images"; name = "Uber and Lyft Accidents-2880w.jpeg" },
    @{ dir = "images"; name = "wrongful death (2)-1920w.jpg" },
    @{ dir = "images"; name = "sign-slippery-wet-caution-2880w.jpg" },
    @{ dir = "images"; name = "Premises-Liability-2880w.jpg" },
    @{ dir = "images"; name = "sky-road-travel-trip-163789-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-2199293-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-220996-1920w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-2263683-1920w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-2453284-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-5669602-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-5722161-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-6077447-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-6129049-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-6138720-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-6520059-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-7243785-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-8057037-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-953626-2880w.jpeg" },
    @{ dir = "images"; name = "pexels-photo-981451-2880w.jpeg" },
    @{ dir = "images"; name = "photo-1423592707957-3b212afa6733-2880w.jpg" },
    @{ dir = "images"; name = "Capture-1920w.JPG" },
    @{ dir = "images"; name = "152468053_l-2880w.jpg" },
    @{ dir = "images"; name = "50803105_l-2880w.jpg" },
    @{ dir = "files"; name = "auto accidents-1920w.webp" },
    @{ dir = "files"; name = "Brain Injury-1920w.webp" },
    @{ dir = "files"; name = "Animial-Attack-2880w.webp" },
    @{ dir = "files"; name = "Animial-Attack-b3ce58ec-1920w.webp" },
    @{ dir = "files"; name = "174260141_m_normal_none-2880w.webp" },
    @{ dir = "files"; name = "63871655_m-2880w-2880w.webp" },
    @{ dir = "files"; name = "countrywide 2-25-14b22fb4-2880w.webp" },
    @{ dir = "files"; name = "Personal Injury-2880w.webp" },
    @{ dir = "files"; name = "motorcycle accidents-2880w.webp" },
    @{ dir = "files"; name = "truck accidents-2880w.webp" },
    @{ dir = "files"; name = "slip and fall-2880w.webp" },
    @{ dir = "files"; name = "insider-accident-banner-1920w.webp" },
    @{ dir = "files"; name = "insider_attorneys_hero3-1920w.webp" },
    @{ dir = "files"; name = "insider_hero_blue w ucla-653c699a-1920w.webp" },
    @{ dir = "files"; name = "iStock-157180797-2880w.webp" },
    @{ dir = "files"; name = "pexels-photo-2181230-72e0c6ac-2880w-2880w.webp" },
    @{ dir = "files"; name = "pexels-photo-2525903-2880w-2880w.webp" },
    @{ dir = "files"; name = "pexels-photo-358383-2880w-2880w.webp" },
    @{ dir = "files"; name = "reviews-2880w.webp" },
    @{ dir = "images"; name = "Pedestrian Accidents-2880w.jpeg" },
    @{ dir = "images"; name = "Catastrophic Injuries-2880w.jpeg" },
    @{ dir = "images"; name = "sectionImg5.jpg" },
    @{ dir = "images"; name = "sunset-hair.jpg" }
)

# Copy to dest as page-001.ext, page-002.ext, ... (cycle if we have more pages than images)
$copiedList = @()
$idx = 0
foreach ($s in $sources) {
    $srcDir = if ($s.dir -eq "files") { $oldFilesDir } else { $oldImagesDir }
    $srcPath = Join-Path $srcDir $s.name
    if (Test-Path $srcPath) {
        $idx++
        $ext = [System.IO.Path]::GetExtension($s.name)
        $destName = "page-{0:D3}{1}" -f $idx, $ext
        Copy-Item -LiteralPath $srcPath -Destination (Join-Path $destDir $destName) -Force
        $copiedList += $destName
    }
}
Write-Host "Copied $($copiedList.Count) images to old-site/"

# Get all pages with content-hero-img in stable order
$files = @(Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart("\", "/").Replace("\", "/")
    if ($rel -eq "index.html") { return $false }
    $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $html -match '<figure class="content-hero-img"' -and $html -match '<img\s+src='
} | Sort-Object FullName)

$imageCount = $copiedList.Count
if ($imageCount -eq 0) { Write-Error "No images copied." }

function Get-DepthFromPath {
    param([string]$fullPath)
    $rel = $fullPath.Substring($root.Length).TrimStart("\", "/")
    $rel = $rel -replace "\\index\.html$", "" -replace "/index\.html$", ""
    if ([string]::IsNullOrWhiteSpace($rel)) { return 0 }
    return ($rel -split "[\\/]").Count
}

$updated = 0
for ($i = 0; $i -lt $files.Count; $i++) {
    $f = $files[$i]
    $html = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $depth = Get-DepthFromPath -fullPath $f.FullName
    $imgFile = $copiedList[$i % $imageCount]
    $prefix = ("../" * $depth) + "assets/images/old-site/"
    $relImg = $prefix + $imgFile
    if ($html -match '<h1[^>]*>([^<]+)</h1>') {
        $h1Text = $Matches[1] -replace "&[^;]+;", " "
        $altRaw = "Illustration: " + ($h1Text.Substring(0, [Math]::Min(60, $h1Text.Length))) -replace '"', ""
    } else { $altRaw = "Illustration" }
    $pattern = '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"\s+alt="[^"]*"([^>]*)>'
    $replacement = "`$1<img src=`"$relImg`" alt=`"$altRaw`"`$2>"
    $newHtml = $html -replace $pattern, $replacement
    if ($newHtml -eq $html) {
        $newHtml = $html -replace '(<figure class="content-hero-img"[^>]*>)\s*<img\s+src="[^"]*"', "`$1<img src=`"$relImg`""
    }
    if ($newHtml -ne $html) {
        [System.IO.File]::WriteAllText($f.FullName, $newHtml, [System.Text.UTF8Encoding]::new($false))
        $updated++
    }
}
Write-Host "Assigned unique images to $updated pages (each page gets a different image from the pool of $imageCount)."
