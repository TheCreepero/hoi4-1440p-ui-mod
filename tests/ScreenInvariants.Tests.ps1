# Checks that need the scene files (tools/scenes/*.json), the baselines and the game's fonts. They sit apart
# from GuiInvariants.Tests.ps1 so that the generic parser tests stay independent of the screen descriptions.

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $script:RepoRoot 'tools') 'GuiParsing.ps1')

    $script:InterfaceDir = Join-Path $script:RepoRoot 'interface'
    $script:BaselineDir = Join-Path $script:RepoRoot 'baseline'
    $script:SceneDir = Join-Path (Join-Path $script:RepoRoot 'tools') 'scenes'
    $script:GameDir = Resolve-HoiGameDir

    function Get-ModGuiFiles {
        if (-not (Test-Path $script:InterfaceDir)) { return }
        Get-ChildItem -Path $script:InterfaceDir -Recurse -File -Filter '*.gui'
    }

    function Get-ModWindows {
        foreach ($file in @(Get-ModGuiFiles)) {
            $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
            foreach ($window in @(Get-GuiTopLevelWindows -Root $root)) {
                [pscustomobject]@{ Name = $window.Name; Node = $window.Node; File = $file.Name; Line = $window.Line }
            }
        }
    }

    function Get-Scenes {
        foreach ($sceneFile in @(Get-ChildItem -Path $script:SceneDir -Filter '*.json' -ErrorAction SilentlyContinue)) {
            Get-GuiScene -Name $sceneFile.FullName
        }
    }

    function Get-Shortcuts {
        param($Node, [string]$Window)
        foreach ($block in @(Get-GuiNodes -Node $Node)) {
            foreach ($child in $block.Children) {
                if ($null -eq $child.Children -and $child.Key -ieq 'shortcut' -and $child.Value) {
                    [pscustomobject]@{ Key = $child.Value.ToLowerInvariant(); Widget = "$Window/$(Get-GuiValue -Node $block -Key 'name')" }
                }
            }
        }
    }
}

Describe 'Variables' {
    It 'defines in the override file every @variable its windows use' {
        # a file-level @variable of a vanilla file does not travel with an overridden window (Engine Facts L6)
        $undefined = foreach ($file in @(Get-ModGuiFiles)) {
            $use = Get-GuiVariableUse -Path $file.FullName
            foreach ($name in $use.Undefined) { "$($file.Name): $name" }
        }
        $undefined | Should -BeNullOrEmpty
    }
}

Describe 'Texts' {
    BeforeAll {
        # Every text box or button caption of the mod whose text is known: a scene sample, a literal, or a
        # vanilla localisation key without variables. Measured with the real font against maxWidth (Engine Facts W11).
        $samples = @{}
        foreach ($scene in @(Get-Scenes)) {
            foreach ($windowName in @($scene.samples.PSObject.Properties.Name)) {
                foreach ($prop in @($scene.samples.$windowName.PSObject.Properties)) {
                    $samples["$windowName/$($prop.Name)"] = [string]$prop.Value
                }
            }
        }
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        $boxes = @()
        foreach ($window in @(Get-ModWindows)) {
            foreach ($node in @(Get-GuiNodes -Node $window.Node)) {
                $type = $node.Key.ToLowerInvariant()
                if ($type -notin @('instanttextboxtype', 'textboxtype', 'buttontype', 'guibuttontype')) { continue }
                $font = Get-GuiValue -Node $node -Key 'font'
                if (-not $font) { $font = Get-GuiValue -Node $node -Key 'buttonFont' }
                $maxWidth = ConvertTo-GuiNumber (Get-GuiValue -Node $node -Key 'maxWidth')
                if ($null -eq $maxWidth) { $maxWidth = Get-GuiWidth -Node $node }
                if (-not $font -or -not $maxWidth) { continue }
                $maxHeight = ConvertTo-GuiNumber (Get-GuiValue -Node $node -Key 'maxHeight')
                if ($null -eq $maxHeight) { $maxHeight = Get-GuiHeight -Node $node }
                $literal = Get-GuiValue -Node $node -Key 'text'
                if (-not $literal) { $literal = Get-GuiValue -Node $node -Key 'buttonText' }
                $boxes += [pscustomobject]@{ Window = $window.Name; Widget = (Get-GuiValue -Node $node -Key 'name'); Font = $font; MaxWidth = $maxWidth; MaxHeight = $maxHeight; Literal = $literal; File = $window.File; Line = $node.Line }
                if ($literal -and $literal -cmatch '^[A-Z][A-Z0-9_]+$') { [void]$keys.Add($literal) }
            }
        }
        # resolve the vanilla keys in one pass over the English localisation
        $loc = @{}
        if ($script:GameDir -and $keys.Count) {
            $pattern = '^\s*(' + (($keys | ForEach-Object { [regex]::Escape($_) }) -join '|') + '):\d*\s*"(.*)"'
            foreach ($hit in (Select-String -Path (Join-Path $script:GameDir 'localisation\english\*.yml') -Pattern $pattern)) {
                $loc[$hit.Matches[0].Groups[1].Value] = $hit.Matches[0].Groups[2].Value
            }
        }
        $colorCode = [string][char]0xA7 + '[A-Za-z0-9!]'
        $script:TextCases = @()
        foreach ($box in $boxes) {
            $text = $null
            $source = $null
            $sampleKey = "$($box.Window)/$($box.Widget)"
            if ($samples.ContainsKey($sampleKey)) { $text = $samples[$sampleKey]; $source = 'sample' }
            elseif ($box.Literal -and $loc.ContainsKey($box.Literal)) { $text = $loc[$box.Literal]; $source = 'localisation' }
            elseif ($box.Literal -and $box.Literal -cnotmatch '^[A-Z][A-Z0-9_]+$') { $text = $box.Literal; $source = 'literal' }
            if (-not $text) { continue }
            if ($text.Contains('$') -or $text.Contains('[')) { continue }   # dynamic text, length unknown
            $text = $text -replace $colorCode, ''
            $script:TextCases += [pscustomobject]@{ Where = "$($box.File):$($box.Line) $($box.Window)/$($box.Widget)"; Text = $text; Font = $box.Font; MaxWidth = $box.MaxWidth; MaxHeight = $box.MaxHeight; Source = $source }
        }
    }

    It 'fit their box in their font: one line in maxWidth, or wrapped into the lines maxHeight holds' {
        if (-not $script:GameDir) { Set-ItResult -Skipped -Because 'the fonts live in the game install'; return }
        $tooWide = foreach ($case in $script:TextCases) {
            $lineHeight = Get-GuiFontLineHeight -Font $case.Font
            if ($null -eq $lineHeight) { continue }
            $linesAllowed = 1
            if ($case.MaxHeight -and $lineHeight -gt 0) { $linesAllowed = [Math]::Max(1, [Math]::Floor($case.MaxHeight / $lineHeight)) }
            # greedy word wrap, the way the game fills a box that holds more than one line (Engine Facts W10)
            $lines = 0
            $overflow = $null
            foreach ($paragraph in ($case.Text -split '\\n|\n')) {
                $current = ''
                foreach ($word in ($paragraph -split ' ')) {
                    $trial = if ($current) { "$current $word" } else { $word }
                    if ((Measure-GuiText -Font $case.Font -Text $trial) -le $case.MaxWidth -or -not $current) {
                        $current = $trial
                    } else {
                        $lines++
                        $current = $word
                    }
                    if ((Measure-GuiText -Font $case.Font -Text $current) -gt $case.MaxWidth) { $overflow = $current }
                }
                $lines++
            }
            if ($overflow) { "$($case.Where): '$overflow' is $(Measure-GuiText -Font $case.Font -Text $overflow) px in $($case.Font), maxWidth $($case.MaxWidth) ($($case.Source))" }
            elseif ($lines -gt $linesAllowed) { "$($case.Where): '$($case.Text)' needs $lines lines of $lineHeight px in $($case.Font); maxHeight $($case.MaxHeight) holds $linesAllowed ($($case.Source))" }
        }
        $tooWide | Should -BeNullOrEmpty -Because 'the game cuts off text that does not fit its box (Engine Facts W10); widen the box or shorten the sample'
    }
}

Describe 'Alternative positions' {
    It 'move positionType entries by the same offset as the widget they belong to' {
        # the engine applies <widget>_<state>_position in another state; a widget that moved without
        # its alternative position jumps when the state changes (Engine Facts S8)
        $problems = foreach ($window in @(Get-ModWindows)) {
            $baseline = Find-GuiBaseline -BaselineDir $script:BaselineDir -Name $window.Name
            if (-not $baseline) { continue }
            $old = Get-GuiPropertyMap -Node $baseline.Node
            $new = Get-GuiPropertyMap -Node $window.Node
            $types = @($new.Values | Where-Object { $_.Property -eq '(type)' })
            foreach ($entry in @($types | Where-Object { $_.Value -eq 'positiontype' })) {
                $path = $entry.Widget
                $cut = $path.LastIndexOf('/')
                if ($cut -lt 0) { continue }
                $parentPath = $path.Substring(0, $cut)
                $leaf = $path.Substring($cut + 1)
                # vanilla also stores plain parameters in positionType blocks (divisions_summary_max_item_count);
                # only a block named *_position is an alternative position
                if ($leaf -notlike '*_position') { continue }
                # the owner is the longest sibling widget whose name prefixes the position name
                $owner = $null
                foreach ($candidate in @($types | Where-Object { $_.Value -ne 'positiontype' -and $_.Widget.StartsWith("$parentPath/") })) {
                    $candidateLeaf = $candidate.Widget.Substring($parentPath.Length + 1)
                    if ($candidateLeaf.Contains('/')) { continue }
                    if ($leaf.StartsWith($candidateLeaf + '_') -and (-not $owner -or $candidateLeaf.Length -gt $owner.Length)) { $owner = $candidateLeaf }
                }
                if (-not $owner) { continue }
                foreach ($axis in 'x', 'y') {
                    $ownerKey = ("$parentPath/$owner`tposition.$axis").ToLowerInvariant()
                    $posKey = ("$path`tposition.$axis").ToLowerInvariant()
                    if (-not ($old.Contains($ownerKey) -and $new.Contains($ownerKey) -and $old.Contains($posKey) -and $new.Contains($posKey))) { continue }
                    $ownerDelta = [double]$new[$ownerKey].Value - [double]$old[$ownerKey].Value
                    $posDelta = [double]$new[$posKey].Value - [double]$old[$posKey].Value
                    if ($ownerDelta -ne $posDelta) { "$($window.File): $path position.$axis moved by $posDelta but $owner moved by $ownerDelta" }
                }
            }
        }
        $problems | Should -BeNullOrEmpty
    }
}

Describe 'Hotkeys' {
    It 'adds no shortcut that another button of the same screen or of the vanilla file already uses' {
        # keys added by the mod, compared with every other shortcut in the same scene and in the vanilla
        # file the window comes from (Engine Facts W5, W7)
        $sceneOf = @{}
        $links = Get-GuiLinks
        foreach ($scene in @(Get-Scenes)) {
            foreach ($w in @($scene.windows)) { $sceneOf[$w.name] = $scene.screen }
        }
        foreach ($pair in @($links.ListRows)) {
            if ($sceneOf.ContainsKey($pair.listWindow) -and -not $sceneOf.ContainsKey($pair.row)) { $sceneOf[$pair.row] = $sceneOf[$pair.listWindow] }
        }
        $all = @()
        $added = @()
        $vanillaFiles = @{}
        foreach ($window in @(Get-ModWindows)) {
            $scene = $sceneOf[$window.Name]
            $mine = @(Get-Shortcuts -Node $window.Node -Window $window.Name)
            foreach ($s in $mine) { $all += [pscustomobject]@{ Key = $s.Key; Widget = $s.Widget; Scene = $scene } }
            $baseline = Find-GuiBaseline -BaselineDir $script:BaselineDir -Name $window.Name
            if (-not $baseline) { continue }
            $vanilla = @(Get-Shortcuts -Node $baseline.Node -Window $window.Name)
            foreach ($s in $mine) {
                if (-not ($vanilla | Where-Object { $_.Key -eq $s.Key -and $_.Widget -eq $s.Widget })) {
                    $added += [pscustomobject]@{ Key = $s.Key; Widget = $s.Widget; Scene = $scene; Source = $baseline.Source }
                    if ($baseline.Source) { $vanillaFiles[$baseline.Source] = $true }
                }
            }
        }
        $vanillaKeys = @()
        if ($script:GameDir) {
            foreach ($rel in $vanillaFiles.Keys) {
                $path = Join-Path $script:GameDir ($rel -replace '/', '\')
                if (-not (Test-Path -LiteralPath $path)) { continue }
                $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $path)
                foreach ($window in @(Get-GuiTopLevelWindows -Root $root)) {
                    foreach ($s in @(Get-Shortcuts -Node $window.Node -Window $window.Name)) { $vanillaKeys += [pscustomobject]@{ Key = $s.Key; Widget = $s.Widget; Source = $rel } }
                }
            }
        }
        $collisions = foreach ($a in $added) {
            foreach ($other in $all) {
                if ($other.Widget -ne $a.Widget -and $other.Key -eq $a.Key -and $a.Scene -and $other.Scene -eq $a.Scene) { "$($a.Widget) added '$($a.Key)', also on $($other.Widget) in scene $($a.Scene)" }
            }
            foreach ($v in $vanillaKeys) {
                if ($v.Source -eq $a.Source -and $v.Key -eq $a.Key -and $v.Widget -ne $a.Widget) { "$($a.Widget) added '$($a.Key)', also on vanilla $($v.Widget) in $($v.Source)" }
            }
        }
        @($collisions | Sort-Object -Unique) | Should -BeNullOrEmpty
    }
}

Describe 'Localisation' {
    It 'has UTF-8 with BOM .yml files only, and build.ps1 packages the folder' {
        $locDir = Join-Path $script:RepoRoot 'localisation'
        $buildText = [System.IO.File]::ReadAllText((Join-Path $script:RepoRoot 'build.ps1'))
        $buildText | Should -Not -Match "'localisation'" -Because 'Copy-ModContent must not exclude the folder'
        if (-not (Test-Path $locDir)) { return }
        $problems = foreach ($file in (Get-ChildItem -Path $locDir -Recurse -File)) {
            if ($file.Extension -ne '.yml') { "$($file.Name): not a .yml file"; continue }
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
            if (-not ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)) { "$($file.Name): no UTF-8 BOM (the game needs one here, unlike .gui files)" }
        }
        $problems | Should -BeNullOrEmpty
    }
}

Describe 'Screen heights' {
    It 'keeps every docked window of a scene above the bottom bar (y 1140)' {
        # Engine Facts S15: a panel docked top left may run down to about y 1130; A1's accepted maxima end at 1139
        $windows = @{}
        foreach ($w in @(Get-ModWindows)) { $windows[$w.Name] = $w }
        $tooLow = foreach ($scene in @(Get-Scenes)) {
            foreach ($w in @($scene.windows)) {
                if (-not $w.at -or -not $windows.ContainsKey($w.name)) { continue }
                $node = $windows[$w.name].Node
                $orientation = [string](Get-GuiValue -Node $node -Key 'orientation')
                if ($orientation -and $orientation -notmatch '(?i)upper_left') { continue }
                $height = if ($w.height) { [double]$w.height } else { Get-GuiHeight -Node $node }
                if ($height -and ([double]$w.at[1] + $height) -gt 1140) { "$($scene.screen)/$($w.name): bottom at $([double]$w.at[1] + $height)" }
            }
        }
        $tooLow | Should -BeNullOrEmpty
    }

    It 'keeps centred windows within 1240 px' {
        Set-ItResult -Skipped -Because 'Engine Facts S14 is provisional; enable when the first centred window is judged in game'
    }
}

Describe 'Game recipes' {
    BeforeAll {
        # Every step of every scene and move, flattened: what a game check would run (wiki/Game-Recipes.md).
        $script:MovesPath = Join-Path (Join-Path $script:RepoRoot 'tools') 'moves.json'
        $script:Moves = @{}
        foreach ($prop in ([System.IO.File]::ReadAllText($script:MovesPath, [System.Text.Encoding]::UTF8) | ConvertFrom-Json).moves.PSObject.Properties) { $script:Moves[$prop.Name] = $prop.Value }
        $script:StepKinds = @('key', 'clickWidget', 'move', 'click', 'rightClick', 'drag', 'console')

        function Get-RecipeSteps {
            param($Steps, [string]$Where, [string]$Scene, [int]$Depth = 0)
            foreach ($step in @($Steps)) {
                if ($null -eq $step) { continue }
                [pscustomobject]@{ Step = $step; Where = $Where; Scene = $Scene }
                if ($step.move -and $script:Moves.ContainsKey([string]$step.move) -and $Depth -lt 8) {
                    Get-RecipeSteps -Steps $script:Moves[[string]$step.move].steps -Where "$Where > $($step.move)" -Scene $Scene -Depth ($Depth + 1)
                }
            }
        }

        $script:AllSteps = @()
        foreach ($scene in @(Get-Scenes)) {
            $script:AllSteps += @(Get-RecipeSteps -Steps $scene.setup -Where "$($scene.screen) setup" -Scene $scene.screen)
            foreach ($capture in @($scene.captures)) {
                if ($capture) { $script:AllSteps += @(Get-RecipeSteps -Steps $capture.steps -Where "$($scene.screen) capture $($capture.name)" -Scene $scene.screen) }
            }
        }
        foreach ($name in $script:Moves.Keys) {
            $script:AllSteps += @(Get-RecipeSteps -Steps $script:Moves[$name].steps -Where "move $name" -Scene $null)
        }
    }

    It 'uses only known step kinds, with well-formed values' {
        $problems = foreach ($item in $script:AllSteps) {
            $names = @($item.Step.PSObject.Properties.Name | Where-Object { $_ -notin @('wait', '_note', 'scene', 'offset', 'button') })
            $kinds = @($names | Where-Object { $script:StepKinds -contains $_ })
            $unknown = @($names | Where-Object { $script:StepKinds -notcontains $_ })
            if ($unknown.Count) { "$($item.Where): unknown key '$($unknown -join ', ')'" }
            if ($kinds.Count -gt 1) { "$($item.Where): more than one action in a step ($($kinds -join ', '))" }
            if (-not $kinds.Count -and -not $item.Step.wait) { "$($item.Where): a step without an action" }
            foreach ($pair in @(@('click', 2), @('rightClick', 2), @('drag', 4))) {
                $value = $item.Step.($pair[0])
                if ($null -ne $value -and @($value).Count -ne $pair[1]) { "$($item.Where): $($pair[0]) needs $($pair[1]) numbers" }
            }
            foreach ($position in @($item.Step.click, $item.Step.rightClick)) {
                if ($position -and ([int]$position[0] -lt 0 -or [int]$position[0] -ge 2560 -or [int]$position[1] -lt 0 -or [int]$position[1] -ge 1440)) { "$($item.Where): position $($position -join ',') is off a 2560x1440 screen" }
            }
        }
        @($problems | Sort-Object -Unique) | Should -BeNullOrEmpty
    }

    It 'names only moves that tools/moves.json defines' {
        $missing = foreach ($item in $script:AllSteps) {
            if ($item.Step.move -and -not $script:Moves.ContainsKey([string]$item.Step.move)) { "$($item.Where): move '$($item.Step.move)'" }
        }
        @($missing | Sort-Object -Unique) | Should -BeNullOrEmpty
    }

    It 'gives every scene a recipe' {
        $empty = foreach ($scene in @(Get-Scenes)) { if (-not @($scene.setup).Count) { $scene.screen } }
        $empty | Should -BeNullOrEmpty -Because 'a scene without setup captures an empty map; write its recipe (wiki/Game-Recipes.md)'
    }

    It 'finds every widget a recipe clicks or expects, in the modded and in the vanilla layout' {
        $python = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $python -or -not $script:GameDir) { Set-ItResult -Skipped -Because 'the layout needs Python with Pillow and the game install'; return }
        & $python -I -c 'import PIL' 2>$null
        if ($LASTEXITCODE -ne 0) { Set-ItResult -Skipped -Because 'Pillow is not installed'; return }

        # scene -> the widget specs laid out with it
        $wanted = @{}
        foreach ($item in $script:AllSteps) {
            if (-not $item.Step.clickWidget) { continue }
            $sceneName = if ($item.Step.scene) { [string]$item.Step.scene } else { $item.Scene }
            if (-not $sceneName) { "$($item.Where): clickWidget in a shared move needs a 'scene'" | Should -BeNullOrEmpty; continue }
            if (-not $wanted.ContainsKey($sceneName)) { $wanted[$sceneName] = [System.Collections.Generic.HashSet[string]]::new() }
            [void]$wanted[$sceneName].Add([string]$item.Step.clickWidget)
        }
        foreach ($scene in @(Get-Scenes)) {
            foreach ($spec in @($scene.expect)) {
                if (-not $spec) { continue }
                if (-not $wanted.ContainsKey($scene.screen)) { $wanted[$scene.screen] = [System.Collections.Generic.HashSet[string]]::new() }
                [void]$wanted[$scene.screen].Add([string]$spec)
            }
        }
        $renderPy = Join-Path (Join-Path $script:RepoRoot 'tools') 'render_gui.py'
        $notFound = foreach ($sceneName in $wanted.Keys) {
            foreach ($mode in '', '--vanilla') {
                $arguments = @('-I', $renderPy, '--scene', $sceneName, '--locate') + @($wanted[$sceneName])
                if ($mode) { $arguments += $mode }
                foreach ($line in @(& $python @arguments 2>$null | Where-Object { $_ -like "LOCATE`t*NOTFOUND" })) {
                    $label = if ($mode) { 'vanilla' } else { 'mod' }
                    "$sceneName ($label): $(($line -split "`t")[1])"
                }
            }
        }
        @($notFound) | Should -BeNullOrEmpty -Because 'a click on a widget the layout does not contain cannot be aimed; check the window/widget names and the scene windows'
    }
}
