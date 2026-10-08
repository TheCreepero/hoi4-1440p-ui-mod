<#
.SYNOPSIS
    Runs recipe steps in the running game and captures the result: the tool for finding a new recipe.

.DESCRIPTION
    Start the game once with tools\Invoke-GameCheck.ps1 <scene> -KeepRunning (or -Start here), then call this
    script as often as needed: each call runs a few steps and writes a capture to scratch\checks. Read the
    capture, decide the next step, repeat. When the screen is up, copy the steps into the scene's "setup"
    (or into tools\moves.json when other scenes need them too). The method is in wiki/Game-Recipes.md.

    Without -Region the capture is saved at full size plus scratch\checks\view.png at half size, for an
    overview (multiply positions read from it by 2). With -Region x,y,w,h that part is saved enlarged with
    a grid labelled in screen coordinates, to read a click position off exactly.

.EXAMPLE
    .\tools\Invoke-GameSteps.ps1 -Start
    Starts the game with only this mod and stops at the clean state of a new 1936 Germany game.

.EXAMPLE
    .\tools\Invoke-GameSteps.ps1 -Reset -Steps '[{"key":"y","wait":1.2}]' -Region 0,60,560,420
    From the clean state: open production, then a grid capture of its top part.

.EXAMPLE
    .\tools\Invoke-GameSteps.ps1 -Scene army_selection -Steps '[{"move":"select_army_1"},{"clickWidget":"army_division_view/unitinfo_button","wait":2}]'
    A shared move, then a click on a widget by name, laid out with the army_selection scene.

.EXAMPLE
    .\tools\Invoke-GameSteps.ps1 -Stop
    Closes the game and restores the playset.
#>
[CmdletBinding()]
param(
    [string]$Steps = '[]',
    [string]$Scene,
    [int[]]$Region,
    [string]$Name = 'steps',
    [int]$Scale = 2,
    [int]$GridStep = 50,
    [switch]$Reset,
    [switch]$Start,
    [switch]$Vanilla,
    [switch]$Stop,
    [switch]$NoCapture
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'GameHarness.ps1')

if ($Stop) { Stop-Hoi4; return }
if ($Start) {
    if (Get-Hoi4Process) { throw 'The game is already running. Use -Stop first, or leave out -Start.' }
    if ($Vanilla) { Set-HoiPlayset -Vanilla | Out-Null } else { Set-HoiPlayset -OnlyThisMod | Out-Null }
    Start-Hoi4 | Out-Null
    Start-HoiNewGame
}
if (-not (Get-Hoi4Process)) { throw 'The game is not running. Start it with -Start, or with tools\Invoke-GameCheck.ps1 <scene> -KeepRunning.' }

Set-HoiHarnessContext -Scene $Scene -Vanilla:$Vanilla
if ($Reset) { Reset-HoiState | Out-Null }
# a JSON array of steps; a single step object is accepted too
$parsed = @($Steps | ConvertFrom-Json | ForEach-Object { $_ })
Invoke-HoiSteps -Steps $parsed -Scene $Scene
if ($NoCapture) { return }

if ($Region) {
    if ($Region.Count -ne 4) { throw '-Region takes x,y,width,height.' }
    Save-HoiGridCapture -Name $Name -Region $Region -Scale $Scale -Step $GridStep
} else {
    Add-Type -AssemblyName System.Drawing
    $shot = Save-HoiScreenshot -Name $Name
    $source = [System.Drawing.Image]::FromFile($shot)
    $bitmap = New-Object System.Drawing.Bitmap ([int]($source.Width / 2)), ([int]($source.Height / 2))
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.DrawImage($source, 0, 0, $bitmap.Width, $bitmap.Height)
    $view = Join-Path (Split-Path -Parent $shot) 'view.png'
    $bitmap.Save($view, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose(); $bitmap.Dispose(); $source.Dispose()
    Write-Host "  [OK] overview: $view (half size: multiply positions by 2)" -ForegroundColor Green
    $shot
}
