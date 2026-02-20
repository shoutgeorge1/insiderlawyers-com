# Minimal HTTP server for local preview (no Node/Python required). Run from repo root.
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$port = 3000
$prefix = "http://localhost:$port/"

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host "Serving at $prefix"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

function Get-MimeType($ext) {
  $map = @{
    ".html"="text/html"; ".css"="text/css"; ".js"="application/javascript"
    ".jpg"="image/jpeg"; ".jpeg"="image/jpeg"; ".png"="image/png"; ".webp"="image/webp"
    ".svg"="image/svg+xml"; ".ico"="image/x-icon"; ".json"="application/json"
  }
  if ($map.ContainsKey($ext)) { return $map[$ext] }
  "application/octet-stream"
}

try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    $path = $request.Url.LocalPath.TrimStart("/").Replace("/", [IO.Path]::DirectorySeparatorChar)
    if ([string]::IsNullOrEmpty($path)) { $path = "index.html" }
    $filePath = Join-Path $root $path
    if (Test-Path $filePath -PathType Leaf) {
      $bytes = [IO.File]::ReadAllBytes($filePath)
      $ext = [IO.Path]::GetExtension($filePath).ToLowerInvariant()
      $response.ContentType = Get-MimeType $ext
      $response.ContentLength64 = $bytes.Length
      $response.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host "200 $($request.Url.LocalPath)"
    } elseif (Test-Path (Join-Path $filePath "index.html") -PathType Leaf) {
      $filePath = Join-Path $filePath "index.html"
      $bytes = [IO.File]::ReadAllBytes($filePath)
      $response.ContentType = "text/html"
      $response.ContentLength64 = $bytes.Length
      $response.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host "200 $($request.Url.LocalPath)/"
    } else {
      $response.StatusCode = 404
      $msg = [Text.Encoding]::UTF8.GetBytes("Not Found")
      $response.OutputStream.Write($msg, 0, $msg.Length)
      Write-Host "404 $($request.Url.LocalPath)"
    }
    $response.Close()
  }
} finally {
  $listener.Stop()
}
