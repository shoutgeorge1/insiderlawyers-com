$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$insert = @'
<div id="smsPopup" class="sms-popup">
  <div class="sms-popup-content">
    <button class="sms-close" aria-label="Close popup">&times;</button>
    <img 
      src="/images/shawn-rokni-popup.webp" 
      alt="Shawn Rokni" 
      class="sms-image"
      width="90"
      height="90"
      loading="lazy"
    />
    <h3>Prefer to text instead?</h3>
    <p>Message our intake team directly. We're available 24/7.</p>
    <a href="sms:2136368571" class="sms-button">Text Our Team Now</a>
    <div class="sms-footer">No Fee Unless We Win</div>
  </div>
</div>

<script>
(function() {
  const popup = document.getElementById("smsPopup");

  if (!sessionStorage.getItem("smsPopupShown")) {
    setTimeout(function() {
      popup.classList.add("show");
      sessionStorage.setItem("smsPopupShown", "true");
    }, 20000);
  }

  document.addEventListener("click", function(e) {
    if (e.target.classList.contains("sms-close")) {
      popup.classList.remove("show");
    }
  });
})();
</script>

</body>
'@
$files = Get-ChildItem -Path $root -Recurse -Filter "index.html" -File | Where-Object { $_.FullName -notmatch "_old-site-extract" }
$count = 0
foreach ($f in $files) {
  $content = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
  if ($content -match '</body>' -and $content -notmatch 'id="smsPopup"') {
    $newContent = $content -replace '</body>', $insert
    [System.IO.File]::WriteAllText($f.FullName, $newContent, [System.Text.UTF8Encoding]::new($false))
    $count++
  }
}
Write-Host "Injected SMS popup into $count files."
