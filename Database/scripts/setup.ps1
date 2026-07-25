$ErrorActionPreference = "Stop"

function Resolve-Psql {
    $cmd = Get-Command psql.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $found = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\psql.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1
    if ($found) { return $found.FullName }
    throw "psql not found on PATH or under C:\Program Files\PostgreSQL"
}

$psql = Resolve-Psql

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $scriptDir "..\..\Backend\.env"

$dbUrl = (Get-Content $envFile | Where-Object { $_ -match "^DATABASE_URL=" }) -replace "^DATABASE_URL=", ""
if (-not $dbUrl) { throw "DATABASE_URL not found in $envFile" }

if ($dbUrl -notmatch "://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)") {
    throw "Could not parse DATABASE_URL: $dbUrl"
}
$pgUser = $Matches[1]
$pgPass = [System.Uri]::UnescapeDataString($Matches[2])
$pgHost = $Matches[3]
$pgPort = $Matches[4]

$env:PGPASSWORD = $pgPass

Write-Host "Resetting database 'dailoqa' on $pgHost`:$pgPort ..." -ForegroundColor Yellow
& $psql -h $pgHost -p $pgPort -U $pgUser -d postgres -v ON_ERROR_STOP=1 -f (Join-Path $scriptDir "reset.sql")
if ($LASTEXITCODE -ne 0) { throw "reset.sql failed" }

Write-Host "Provisioning schema into 'dailoqa' ..." -ForegroundColor Yellow
& $psql -h $pgHost -p $pgPort -U $pgUser -d dailoqa -v ON_ERROR_STOP=1 -f (Join-Path $scriptDir "provision.sql")
if ($LASTEXITCODE -ne 0) { throw "provision.sql failed" }

Write-Host "Verifying tables ..." -ForegroundColor Yellow
& $psql -h $pgHost -p $pgPort -U $pgUser -d dailoqa -c "\dt public.*" -c "\dt app.*"

Write-Host "Done." -ForegroundColor Green
