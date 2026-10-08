BeforeDiscovery {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $repoRoot 'tools') 'GuiParsing.ps1')

    # Grids and the entry rows the engine fills them with. The link lives in game code, so it is
    # listed here: add one row per reworked list, e.g. @{ Grid = 'names_grid'; Entry = 'designer_div_name_group_entry' }.
    $entryPairCases = @(
    )

    $guiFileCases = @()
    $windowCases = @()
    $interfaceDir = Join-Path $repoRoot 'interface'
    if (Test-Path $interfaceDir) {
        foreach ($file in (Get-ChildItem -Path $interfaceDir -Recurse -File -Filter '*.gui')) {
            $relPath = $file.FullName.Substring($repoRoot.Length + 1)
            $guiFileCases += @{ RelPath = $relPath; FullPath = $file.FullName }
            $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
            foreach ($window in @(Get-GuiTopLevelWindows -Root $root)) {
                $windowCases += @{ Window = $window.Name; RelPath = $relPath; FullPath = $file.FullName }
            }
        }
    }
}

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $script:RepoRoot 'tools') 'GuiParsing.ps1')

    $script:InterfaceDir = Join-Path $script:RepoRoot 'interface'
    $script:BaselineDir = Join-Path $script:RepoRoot 'baseline'
    # Windows the mod adds itself (no vanilla counterpart) must carry this prefix.
    $script:ModWindowPrefix = 'mod1440_'

    function Get-ModGuiFiles {
        param([string]$Filter)
        if (-not (Test-Path $script:InterfaceDir)) { return }
        Get-ChildItem -Path $script:InterfaceDir -Recurse -File -Filter $Filter
    }

    function Get-ModWindow {
        param([string]$Path, [string]$Name)
        $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $Path)
        return @(Get-GuiTopLevelWindows -Root $root | Where-Object { $_.Name -eq $Name })[0]
    }

    function Get-BaselineWindow {
        param([string]$Name)
        if (-not (Test-Path $script:BaselineDir)) { return $null }
        $file = Get-ChildItem -Path $script:BaselineDir -Recurse -File -Filter "$Name.gui" | Select-Object -First 1
        if (-not $file) { return $null }
        $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
        return @(Get-GuiTopLevelWindows -Root $root)[0]
    }
}

Describe 'GUI parser' {
    BeforeAll {
        $script:Sample = @'
guiTypes = {
	containerWindowType = {
		name = "sample_window"
		size = { width = 400 height=300 }	# a comment with a { brace and a " quote
		background = { name = "Background" quadTextureSprite = "GFX_tiled_window" }
		containerWindowType = {
			name = "list"
			verticalScrollbar = "right_vertical_slider"
			scroll_wheel_factor = 60
			gridBoxType = {
				name = "grid"
				slotsize = { width = 300 height = 30 }
			}
		}
		instantTextBoxType = { name = "title" font = "hoi_18mbs" }
	}
}
'@
        $script:SampleWindow = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $script:Sample))[0]
    }

    It 'finds a top-level window with its line range' {
        $script:SampleWindow.Name | Should -Be 'sample_window'
        $script:SampleWindow.Line | Should -Be 2
        $script:SampleWindow.EndLine | Should -Be 16
    }

    It 'reads values next to a comment that contains braces and quotes' {
        $size = Get-GuiBlock -Node $script:SampleWindow.Node -Key 'size'
        Get-GuiValue -Node $size -Key 'height' | Should -Be '300'
    }

    It 'lists named widgets by nesting path and element type' {
        $paths = @(Get-GuiWidgetPaths -Node $script:SampleWindow.Node)
        $paths | Should -Contain 'sample_window|containerwindowtype'
        $paths | Should -Contain 'sample_window/list/grid|gridboxtype'
        $paths | Should -Contain 'sample_window/title|instanttextboxtype'
        $paths.Count | Should -Be 5
    }

    It 'reports a widget that was removed' {
        $changed = $script:Sample -replace '(?m)^\s*instantTextBoxType.*$', ''
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node) | Should -Be @('sample_window/title|instanttextboxtype')
    }

    It 'reports a widget that moved to another parent' {
        $changed = $script:Sample -replace 'name = "list"', 'name = "list_renamed"'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        $missing = @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node)
        $missing | Should -Contain 'sample_window/list|containerwindowtype'
        $missing | Should -Contain 'sample_window/list/grid|gridboxtype'
    }

    It 'accepts an unchanged window and one with extra widgets' {
        $changed = $script:Sample -replace 'instantTextBoxType = \{ name = "title"', 'iconType = { name = "extra" } instantTextBoxType = { name = "title"'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node) | Should -BeNullOrEmpty
    }

    It 'flags a scroll factor that is not a whole number of rows' {
        @(Get-GuiScrollViolations -Node $script:SampleWindow.Node) | Should -BeNullOrEmpty
        $changed = $script:Sample -replace 'scroll_wheel_factor = 60', 'scroll_wheel_factor = 45'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Get-GuiScrollViolations -Node $actual.Node).Count | Should -Be 1
    }

    It 'flags a size larger than 2560x1440' {
        @(Get-GuiOversizeViolations -Node $script:SampleWindow.Node) | Should -BeNullOrEmpty
        $changed = $script:Sample -replace 'height=300', 'height=1500'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Get-GuiOversizeViolations -Node $actual.Node).Count | Should -Be 1
    }
}

Describe 'Checksum neutrality' {
    It 'contains no file type the game includes in its checksum' {
        # Mirrors checksum_manifest.txt in the game folder.
        $rules = @(
            @{ Dir = 'common'; Extensions = @('.txt', '.lua') }
            @{ Dir = 'events'; Extensions = @('.txt') }
            @{ Dir = 'history'; Extensions = @('.txt') }
            @{ Dir = 'map'; Extensions = @('.txt', '.map', '.bmp', '.csv') }
        )
        $hits = foreach ($rule in $rules) {
            $dir = Join-Path $script:RepoRoot $rule.Dir
            if (-not (Test-Path $dir)) { continue }
            Get-ChildItem -Path $dir -Recurse -File | Where-Object { $rule.Extensions -contains $_.Extension.ToLowerInvariant() } | ForEach-Object { $_.FullName.Substring($script:RepoRoot.Length + 1) }
        }
        $hits | Should -BeNullOrEmpty -Because 'the mod must stay Ironman, achievement and multiplayer compatible'
    }
}

Describe 'Mod sprites' {
    BeforeAll {
        $script:DeclaredSprites = @(
            foreach ($file in @(Get-ModGuiFiles -Filter '*.gfx')) {
                Get-GuiSpriteDeclarations -Root (ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName))
            }
        )
    }

    It 'declares every GFX_1440p_ sprite that a .gui file uses' {
        $used = foreach ($file in @(Get-ModGuiFiles -Filter '*.gui')) {
            $text = [regex]::Replace((Read-GuiText -Path $file.FullName), '#[^\r\n]*', '')
            [regex]::Matches($text, 'GFX_1440p_[A-Za-z0-9_]+') | ForEach-Object { $_.Value }
        }
        $declared = @($script:DeclaredSprites | ForEach-Object { $_.Name })
        $missing = @($used | Sort-Object -Unique | Where-Object { $declared -notcontains $_ })
        $missing | Should -BeNullOrEmpty
    }

    It 'gives every declared sprite the GFX_1440p_ prefix' {
        $foreign = @($script:DeclaredSprites | Where-Object { $_.Name -notlike 'GFX_1440p_*' } | ForEach-Object { $_.Name })
        $foreign | Should -BeNullOrEmpty -Because 'redefining a vanilla sprite name changes every screen that uses it'
    }

    It 'points every declared sprite at a texture that exists' {
        # Textures may come from the mod or from vanilla. Without a game install (CI) only the mod is checked.
        $gameDir = Resolve-HoiGameDir
        $missing = foreach ($sprite in $script:DeclaredSprites) {
            if (-not $sprite.Texture) { "$($sprite.Name): no texturefile"; continue }
            if (Test-Path (Join-Path $script:RepoRoot $sprite.Texture)) { continue }
            if (-not $gameDir) { continue }
            if (-not (Test-Path (Join-Path $gameDir $sprite.Texture))) { "$($sprite.Name): $($sprite.Texture)" }
        }
        $missing | Should -BeNullOrEmpty
    }
}

if ($guiFileCases.Count -gt 0) {
    Describe 'GUI file <RelPath>' -ForEach $guiFileCases {
        BeforeAll {
            $script:FileRoot = ConvertFrom-GuiText -Text (Read-GuiText -Path $FullPath)
        }

        It 'has no BOM and balanced braces and quotes' {
            @(Test-GuiFileSyntax -Path $FullPath) | Should -BeNullOrEmpty
        }

        It 'scrolls every list by a whole number of rows' {
            @(Get-GuiScrollViolations -Node $script:FileRoot) | Should -BeNullOrEmpty
        }

        It 'keeps every size within 2560x1440' {
            @(Get-GuiOversizeViolations -Node $script:FileRoot) | Should -BeNullOrEmpty
        }
    }
}

if ($windowCases.Count -gt 0) {
    Describe 'Window <Window> in <RelPath>' -ForEach $windowCases {
        It 'has a vanilla baseline, or is a mod-only window with the mod prefix' {
            if ($Window -like "$($script:ModWindowPrefix)*") { return }
            Get-BaselineWindow -Name $Window | Should -Not -BeNullOrEmpty -Because 'run tools/Export-VanillaBaseline.ps1 before reworking a vanilla window'
        }

        It 'keeps every named vanilla widget under the same parent' {
            $baseline = Get-BaselineWindow -Name $Window
            if (-not $baseline) {
                Set-ItResult -Skipped -Because 'there is no baseline to compare against'
                return
            }
            $actual = Get-ModWindow -Path $FullPath -Name $Window
            @(Compare-GuiWidgetPaths -Baseline $baseline.Node -Actual $actual.Node) | Should -BeNullOrEmpty -Because 'the engine binds data to widgets by name inside their parent'
        }
    }
}

if ($entryPairCases.Count -gt 0) {
    Describe 'List <Grid> filled with <Entry>' -ForEach $entryPairCases {
        It 'uses a slot width equal to the entry row width' {
            $gridNode = $null
            $entryNode = $null
            foreach ($file in @(Get-ModGuiFiles -Filter '*.gui')) {
                $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
                foreach ($node in @(Get-GuiNodes -Node $root)) {
                    if ($node.Key -ieq 'gridBoxType' -and (Get-GuiValue -Node $node -Key 'name') -eq $Grid) { $gridNode = $node }
                }
                $window = @(Get-GuiTopLevelWindows -Root $root | Where-Object { $_.Name -eq $Entry })[0]
                if ($window) { $entryNode = $window.Node }
            }
            $gridNode | Should -Not -BeNullOrEmpty -Because "grid '$Grid' should exist in a mod .gui file"
            $entryNode | Should -Not -BeNullOrEmpty -Because "entry window '$Entry' should exist in a mod .gui file"

            $slotWidth = Get-GuiValue -Node (Get-GuiBlock -Node $gridNode -Key 'slotsize') -Key 'width'
            $entryWidth = Get-GuiValue -Node (Get-GuiBlock -Node $entryNode -Key 'size') -Key 'width'
            $slotWidth | Should -Be $entryWidth
        }
    }
}
