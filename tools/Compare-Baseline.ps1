<#
.SYNOPSIS
    Lists every value the mod changed in its overridden windows, compared with the vanilla baseline.

.DESCRIPTION
    The review step before a game check. Compares each top-level window of the mod's .gui files with
    its copy under baseline/ and prints one line per changed, added or removed property, grouped by
    window and named by widget. Whitespace, comments and the order of widgets do not count as changes.

.EXAMPLE
    .\tools\Compare-Baseline.ps1
    Every overridden window of every mod .gui file.

.EXAMPLE
    .\tools\Compare-Baseline.ps1 zz_1440p_air_selection.gui
    One file.

.EXAMPLE
    .\tools\Compare-Baseline.ps1 zz_1440p_air_selection.gui airwing_selection_item
    One window of one file.

.EXAMPLE
    .\tools\Compare-Baseline.ps1 -PassThru | Where-Object Property -like 'font*'
    The changes as objects, here filtered to font changes.

.EXAMPLE
    .\tools\Compare-Baseline.ps1 zz_1440p_air_selection.gui -Group
    One line per changed widget with the properties touched: the raw material of a game-check checklist.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$File,
    [Parameter(Position = 1, ValueFromRemainingArguments)][string[]]$Window,
    [switch]$PassThru,
    [switch]$Group
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'GuiParsing.ps1')

# Accept "a, b" (PowerShell), "a b" and "a,b" (other shells) alike.
$Window = @($Window | ForEach-Object { $_ -split '[,\s]+' } | Where-Object { $_ })

$repoRoot = Split-Path -Parent $PSScriptRoot
$interfaceDir = Join-Path $repoRoot 'interface'
$baselineDir = Join-Path $repoRoot 'baseline'

if ($File) {
    if (Test-Path -LiteralPath $File -PathType Leaf) {
        $files = @(Get-Item -LiteralPath $File)
    } else {
        $candidate = Join-Path $interfaceDir $File
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "File not found: $File (also looked in $interfaceDir)" }
        $files = @(Get-Item -LiteralPath $candidate)
    }
} else {
    $files = @(Get-ChildItem -LiteralPath $interfaceDir -Recurse -File -Filter '*.gui' | Sort-Object FullName)
}

$totalChanges = 0
$windowCount = 0
foreach ($guiFile in $files) {
    $relPath = $guiFile.FullName.Substring($repoRoot.Length + 1) -replace '\\', '/'
    $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $guiFile.FullName)

    foreach ($modWindow in @(Get-GuiTopLevelWindows -Root $root)) {
        if ($Window.Count -and ($Window -notcontains $modWindow.Name)) { continue }
        $windowCount++

        $baseline = Find-GuiBaseline -BaselineDir $baselineDir -Name $modWindow.Name
        if (-not $baseline) {
            if (-not $PassThru) { "== $($modWindow.Name)  ($relPath`:$($modWindow.Line))  no baseline: a mod-only window, or run tools/Export-VanillaBaseline.ps1" }
            continue
        }

        $changes = @(Compare-GuiWindows -Baseline $baseline.Node -Actual $modWindow.Node)
        $totalChanges += $changes.Count

        # show widgets relative to the window: "(window)" for the window itself
        $prefix = $modWindow.Name + '/'
        foreach ($change in $changes) {
            $widget = $change.Widget
            if ($widget -ieq $modWindow.Name) { $widget = '(window)' }
            elseif ($widget.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) { $widget = $widget.Substring($prefix.Length) }
            $change | Add-Member -NotePropertyName Window -NotePropertyValue $modWindow.Name
            $change | Add-Member -NotePropertyName File -NotePropertyValue $relPath
            $change.Widget = $widget
        }

        if ($PassThru) {
            $changes
            continue
        }

        "== $($modWindow.Name)  ($relPath`:$($modWindow.Line))  vanilla $($baseline.GameVersion) $($baseline.Source)  $($changes.Count) change(s)"
        if (-not $changes.Count) { continue }

        if ($Group) {
            # one line per widget: what kind of change and which properties, for the game-check checklist
            foreach ($bucket in ($changes | Group-Object Widget)) {
                $kinds = @($bucket.Group | ForEach-Object { $_.Kind } | Sort-Object -Unique)
                $properties = @($bucket.Group | ForEach-Object { $_.Property } | Sort-Object -Unique)
                '  {0,-45} {1,2} {2,-14} {3}' -f $bucket.Name, $bucket.Count, ($kinds -join '/'), ($properties -join ', ')
            }
            continue
        }

        $widgetWidth = ($changes | ForEach-Object { $_.Widget.Length } | Measure-Object -Maximum).Maximum
        $propertyWidth = ($changes | ForEach-Object { $_.Property.Length } | Measure-Object -Maximum).Maximum
        foreach ($change in $changes) {
            $where = if ($change.Line) { 'L{0,-5}' -f $change.Line } else { '      ' }
            $what = switch ($change.Kind) {
                'Changed'       { '{0} -> {1}' -f $change.Old, $change.New }
                'Added'         { '(not in vanilla) -> {0}' -f $change.New }
                'Removed'       { '{0} -> (removed)' -f $change.Old }
                'NewWidget'     { 'NEW WIDGET ({0})' -f $change.New }
                'MissingWidget' { 'MISSING WIDGET ({0})' -f $change.Old }
            }
            '  {0} {1}  {2}  {3}' -f $where, $change.Widget.PadRight($widgetWidth), $change.Property.PadRight($propertyWidth), $what
        }
    }
}

if (-not $PassThru) {
    ''
    "$windowCount window(s), $totalChanges change(s)"
}
