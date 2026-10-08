<#
.SYNOPSIS
    Starts or extends a screen's override file with untouched copies of vanilla windows.

.DESCRIPTION
    Creates interface/zz_1440p_<screen>.gui, or adds windows to it, using the vanilla text saved
    under baseline/. A window without a baseline is exported first, which needs the game install.
    The result is a working override that changes nothing yet: edit the values afterwards and review
    them with tools/Compare-Baseline.ps1.

    Existing content is never overwritten. A window that any mod .gui file already defines is skipped.

.EXAMPLE
    .\tools\New-OverrideFile.ps1 air_selection airselectionview.gui air_selection_view, airwing_selection_item
    Creates interface/zz_1440p_air_selection.gui with two windows.

.EXAMPLE
    .\tools\New-OverrideFile.ps1 ship_designer naviesview.gui ship_refit_equipment_view
    Adds a window from a second vanilla file to an existing screen file.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)][ValidatePattern('^[a-z0-9_]+$')][string]$Screen,
    [Parameter(Mandatory, Position = 1)][string]$File,
    [Parameter(Mandatory, Position = 2, ValueFromRemainingArguments)][string[]]$Window,
    [string]$GameDir
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'GuiParsing.ps1')

# Accept "a, b" (PowerShell), "a b" and "a,b" (other shells) alike.
$Window = @($Window | ForEach-Object { $_ -split '[,\s]+' } | Where-Object { $_ })

$repoRoot = Split-Path -Parent $PSScriptRoot
$interfaceDir = Join-Path $repoRoot 'interface'
$baselineDir = Join-Path $repoRoot 'baseline'
$targetPath = Join-Path $interfaceDir "zz_1440p_$Screen.gui"
$targetRel = $targetPath.Substring($repoRoot.Length + 1)
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

# Windows the mod already overrides, in any file: defining one twice would make the last file win silently.
$defined = @{}
foreach ($guiFile in @(Get-ChildItem -LiteralPath $interfaceDir -Recurse -File -Filter '*.gui')) {
    foreach ($existing in @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text (Read-GuiText -Path $guiFile.FullName)))) {
        $defined[$existing.Name] = $guiFile.FullName.Substring($repoRoot.Length + 1)
    }
}

$wanted = [System.Collections.Generic.List[string]]::new()
foreach ($name in $Window) {
    if ($defined.ContainsKey($name)) {
        Write-Host "  [SKIP] $name is already defined in $($defined[$name])" -ForegroundColor Yellow
    } elseif (-not $wanted.Contains($name)) {
        $wanted.Add($name)
    }
}
if ($wanted.Count -eq 0) {
    Write-Host 'Nothing to add.'
    return
}

$missing = @($wanted | Where-Object { -not (Find-GuiBaseline -BaselineDir $baselineDir -Name $_) })
if ($missing.Count) {
    $exportArgs = @{ File = $File; Window = $missing }
    if ($GameDir) { $exportArgs.GameDir = $GameDir }
    & (Join-Path $PSScriptRoot 'Export-VanillaBaseline.ps1') @exportArgs
}

$source = 'interface/' + ($File -replace '\\', '/')
$added = [System.Collections.Generic.List[string]]::new()
$added.Add("`t# Windows from vanilla $source")
foreach ($name in $wanted) {
    $baseline = Find-GuiBaseline -BaselineDir $baselineDir -Name $name
    if (-not $baseline) { throw "No baseline for '$name' after the export." }
    if ($baseline.Source -and $baseline.Source -ne $source) {
        throw "The baseline of '$name' comes from $($baseline.Source), not from $source."
    }
    $added.AddRange([string[]]$baseline.Lines)
    $added.Add('')
}
$added.RemoveAt($added.Count - 1)

if (Test-Path -LiteralPath $targetPath) {
    $text = Read-GuiText -Path $targetPath
    $newline = "`n"
    if ($text.Contains("`r`n")) { $newline = "`r`n" }
    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.AddRange([string[]](($text -replace "`r`n", "`n") -split "`n"))

    # the last line that is only "}" closes guiTypes
    $close = $lines.FindLastIndex([Predicate[string]] { param($line) $line.Trim() -eq '}' })
    if ($close -lt 0) { throw "$targetRel has no closing brace to insert before." }
    $lines.Insert($close, '')
    $lines.InsertRange($close + 1, $added)
    [System.IO.File]::WriteAllText($targetPath, ($lines -join $newline), $utf8NoBom)
    Write-Host "  [OK] added $($wanted.Count) window(s) to $targetRel" -ForegroundColor Green
} else {
    $content = [System.Collections.Generic.List[string]]::new()
    $content.Add("# Screen '$Screen', reworked for 2560x1440.")
    $content.Add('# Overrides single top-level windows of the vanilla interface files; the vanilla files stay in place and')
    $content.Add('# supply every other window. The untouched vanilla text of each window is in baseline/.')
    $content.Add('guiTypes = {')
    $content.AddRange($added)
    $content.Add('}')
    $content.Add('')
    [System.IO.File]::WriteAllText($targetPath, ($content -join "`n"), $utf8NoBom)
    Write-Host "  [OK] created $targetRel with $($wanted.Count) window(s)" -ForegroundColor Green
}

# A scene file for the renderer and the game harness. A new one gets the windows just added; an existing
# one (the roadmap screens already have a recipe and a vanilla reference) gets them appended.
$scenePath = Join-Path (Join-Path $PSScriptRoot 'scenes') "$Screen.json"
if (-not (Test-Path -LiteralPath $scenePath)) {
    $windowsJson = ($wanted | ForEach-Object { '    { "name": "' + $_ + '" }' }) -join ",`n"
    $sceneText = @(
        '{'
        '  "_comment": "Scene for the ' + $Screen + ' screen. Keys are explained in wiki/Game-Recipes.md and in tools/scenes/army_selection.json. To do: setup (the recipe that brings the screen up from the clean state), at for each window (measure with render_gui.py --verify on a capture), expect (widgets that prove the screen is up), rows, hide, samples, crop.",'
        '  "screen": "' + $Screen + '",'
        '  "file": "zz_1440p_' + $Screen + '.gui",'
        '  "screenshot": "reference/vanilla/' + $Screen + '.jpg",'
        '  "windows": ['
        $windowsJson
        '  ],'
        '  "samples": {},'
        '  "setup": [],'
        '  "captures": [],'
        '  "expect": [],'
        '  "crop": [0, 60, 780, 1200],'
        '  "manual": [],'
        '  "checklist": []'
        '}'
        ''
    ) -join "`n"
    [System.IO.File]::WriteAllText($scenePath, $sceneText, $utf8NoBom)
    Write-Host "  [OK] created tools\scenes\$Screen.json (write its setup recipe: wiki\Game-Recipes.md)" -ForegroundColor Green
} else {
    $sceneJson = [System.IO.File]::ReadAllText($scenePath, [System.Text.Encoding]::UTF8)
    $listed = @(($sceneJson | ConvertFrom-Json).windows | ForEach-Object { $_.name })
    $toAdd = @($wanted | Where-Object { $listed -notcontains $_ })
    if ($toAdd.Count) {
        Write-Host "  [INFO] tools\scenes\$Screen.json exists; add these windows to its 'windows' list: $($toAdd -join ', ')" -ForegroundColor Yellow
    }
}

Write-Host "  Next: edit the values, then review them with tools\Compare-Baseline.ps1 zz_1440p_$Screen.gui"
Write-Host "        and look at them with python -I tools\render_gui.py --scene $Screen"
