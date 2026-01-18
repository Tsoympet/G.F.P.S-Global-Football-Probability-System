$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "Python is required but was not found in PATH."
  exit 1
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Error "npm is required but was not found in PATH."
  exit 1
}

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"

$requirementsFile = "backend/requirements.txt"
if (Test-Path "backend/requirements.lock") {
  $nonComment = Get-Content backend/requirements.lock | Where-Object { $_ -match "\S" -and $_ -notmatch "^\s*#" }
  if ($nonComment.Count -gt 0) {
    $requirementsFile = "backend/requirements.lock"
  }
}

& $venvPython -m pip install -r $requirementsFile

if (-not (Test-Path ".env")) {
  Copy-Item .env.example .env
}

$lines = Get-Content .env

function Set-EnvKey {
  param(
    [string]$Key,
    [string]$Value,
    [ScriptBlock]$ShouldReplace
  )

  $found = $false
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -like "$Key=*") {
      $current = $lines[$i].Substring($Key.Length + 1)
      if (& $ShouldReplace $current) {
        $lines[$i] = "$Key=$Value"
      }
      $found = $true
      break
    }
  }

  if (-not $found) {
    $lines += "$Key=$Value"
  }
}

$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$secret = -join ($bytes | ForEach-Object { $_.ToString("x2") })

Set-EnvKey -Key "SECRET_KEY" -Value $secret -ShouldReplace { param($current) [string]::IsNullOrWhiteSpace($current) }
Set-EnvKey -Key "FRONTEND_BASE_URL" -Value "http://localhost:1420" -ShouldReplace {
  param($current)
  [string]::IsNullOrWhiteSpace($current) -or $current.Trim() -eq "https://example.com"
}

Set-Content .env $lines

if ($env:INSTALL_PLAYWRIGHT -eq "1") {
  & $venvPython -m playwright install
}

Push-Location GFPS/desktop
npm install
Pop-Location

Write-Host "Local setup complete."
if ($env:INSTALL_PLAYWRIGHT -eq "1") {
  Write-Host "Playwright browsers installed."
} else {
  Write-Host "Optional: run 'INSTALL_PLAYWRIGHT=1 .\\scripts\\setup_local.ps1' if you need the web scraper."
}
