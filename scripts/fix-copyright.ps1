$root = Split-Path -Parent $PSScriptRoot
$bad = [char]0xC2 + [char]0xA9
$good = [char]0x00A9
Get-ChildItem -Path $root -Recurse -Filter index.html -File |
  Where-Object { $_.FullName -notmatch '\\styles\\|\\scripts\\|\\images\\' } |
  ForEach-Object {
    $c = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    if ($c.Contains($bad)) {
      $c = $c.Replace($bad, $good)
      [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
      Write-Host $_.FullName.Replace("$root\", '')
    }
  }
