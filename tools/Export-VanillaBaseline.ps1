<#
.SYNOPSIS
    Saves the untouched vanilla text of named top-level windows under baseline/.

.DESCRIPTION
    Run this before reworking a window. The saved copy is what the name-parity test compares the
    mod's version against, and re-running it after a game update shows in git what vanilla changed.
    Output: baseline/<gui file name>/<window>.gui and a row per window in baseline/manifest.csv.

.EXAMPLE
    .\tools\Export-VanillaBaseline.ps1 airselectionview.gui air_selection_view, unassigned_airwings_view
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)][string]$File,
    [Parameter(Mandatory, Position = 1, ValueFromRemainingArguments)][string[]]$Window,
    [string]$GameDir
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'GuiParsing.ps1')

# Accept "a, b" (PowerShell), "a b" and "a,b" (other shells) alike.
$Window = @($Window | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

$repoRoot = Split-Path -Parent $PSScriptRoot
$baselineDir = Join-Path $repoRoot 'baseline'
$manifestPath = Join-Path $baselineDir 'manifest.csv'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$resolvedGameDir = Resolve-HoiGameDir -GameDir $GameDir
if (-not $resolvedGameDir) { throw 'Hearts of Iron IV install not found. Pass -GameDir or set HOI4_GAME_DIR.' }

$sourcePath = Join-Path (Join-Path $resolvedGameDir 'interface') $File
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "Vanilla file not found: $sourcePath" }
$source = 'interface/' + ($File -replace '\\', '/')

$gameVersion = 'unknown'
$launcherSettings = Join-Path $resolvedGameDir 'launcher-settings.json'
if (Test-Path -LiteralPath $launcherSettings) {
    $gameVersion = (Get-Content -LiteralPath $launcherSettings -Raw | ConvertFrom-Json).rawVersion
}

$text = (Read-GuiText -Path $sourcePath) -replace "`r`n", "`n"
$lines = $text -split "`n"
$windows = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $text))

$rows = [System.Collections.Generic.List[object]]::new()
if (Test-Path -LiteralPath $manifestPath) {
    foreach ($row in @(Import-Csv -LiteralPath $manifestPath)) { $rows.Add($row) }
}

$targetDir = Join-Path $baselineDir ($File -replace '\.gui$', '')
if (-not (Test-Path -LiteralPath $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }

$sha = [System.Security.Cryptography.SHA256]::Create()
foreach ($name in $Window) {
    $match = $windows | Where-Object { $_.Name -ieq $name } | Select-Object -First 1
    if (-not $match) { throw "Window '$name' not found in $sourcePath" }

    $block = ($lines[($match.Line - 1)..($match.EndLine - 1)]) -join "`n"
    $hash = ([System.BitConverter]::ToString($sha.ComputeHash($utf8NoBom.GetBytes($block))) -replace '-', '').ToLowerInvariant()
    $lineRange = '{0}-{1}' -f $match.Line, $match.EndLine

    $content = @(
        "# Vanilla $gameVersion, $source, lines $lineRange."
        '# Reference copy for the name-parity test. Do not edit; regenerate with tools/Export-VanillaBaseline.ps1.'
        'guiTypes = {'
        $block
        '}'
        ''
    ) -join "`n"
    $targetPath = Join-Path $targetDir "$($match.Name).gui"
    [System.IO.File]::WriteAllText($targetPath, $content, $utf8NoBom)

    $existing = $rows | Where-Object { $_.Window -eq $match.Name -and $_.Source -eq $source } | Select-Object -First 1
    if ($existing) {
        if ($existing.Sha256 -ne $hash) { Write-Host "  [CHANGED] $($match.Name): vanilla text differs from the previous baseline ($($existing.GameVersion))" -ForegroundColor Yellow }
        [void]$rows.Remove($existing)
    }
    $rows.Add([pscustomobject]@{ Window = $match.Name; Source = $source; GameVersion = $gameVersion; Lines = $lineRange; Sha256 = $hash })
    Write-Host "  [OK] $($match.Name) -> $($targetPath.Substring($repoRoot.Length + 1))" -ForegroundColor Green
}
$sha.Dispose()

$csv = @($rows | Sort-Object Source, Window | ConvertTo-Csv -NoTypeInformation)
[System.IO.File]::WriteAllText($manifestPath, (($csv -join "`n") + "`n"), $utf8NoBom)
