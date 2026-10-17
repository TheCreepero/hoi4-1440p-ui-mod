BeforeDiscovery {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $repoRoot 'tools') 'GuiParsing.ps1')

    # Grids and their entry rows, list boxes and their row windows: links the engine makes in code, kept
    # in tools/gui-links.json (shared with the renderer and the game harness). Add a row there per reworked list.
    $links = Get-GuiLinks -Path (Join-Path (Join-Path $repoRoot 'tools') 'gui-links.json')
    $entryPairCases = @($links.EntryPairs | ForEach-Object { @{ Grid = $_.grid; Entry = $_.entry; GridWindow = [string]$_.window } })
    $listRowCases = @($links.ListRows | ForEach-Object { @{ ListWindow = $_.listWindow; List = $_.list; Row = $_.row } })

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

    # The top-level window with this name from whichever mod .gui file defines it, or $null.
    function Find-ModWindow {
        param([string]$Name)
        foreach ($file in @(Get-ModGuiFiles -Filter '*.gui')) {
            $window = Get-ModWindow -Path $file.FullName -Name $Name
            if ($window) { return $window }
        }
        return $null
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

    It 'finds a vanilla widget inside a container the mod added' {
        $changed = $script:Sample -replace 'instantTextBoxType = \{ name = "title" font = "hoi_18mbs" \}', 'containerWindowType = { name = "mod1440_card" instantTextBoxType = { name = "title" font = "hoi_18mbs" } }'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node) | Should -Be @('sample_window/title|instanttextboxtype')
        @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node -WrapperPrefix 'mod1440_') | Should -BeNullOrEmpty
    }

    It 'reports a wrapped widget whose type the game still looks up among direct children only' {
        $sample = $script:Sample -replace 'instantTextBoxType = \{ name = "title" font = "hoi_18mbs" \}', 'listboxType = { name = "rows" }'
        $baseline = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $sample))[0]
        $changed = $sample -replace 'listboxType = \{ name = "rows" \}', 'containerWindowType = { name = "mod1440_card" listboxType = { name = "rows" } }'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Compare-GuiWidgetPaths -Baseline $baseline.Node -Actual $actual.Node -WrapperPrefix 'mod1440_') | Should -Be @('sample_window/rows|listboxtype (wrapped)')
    }

    It 'accepts an unchanged window and one with extra widgets' {
        $changed = $script:Sample -replace 'instantTextBoxType = \{ name = "title"', 'iconType = { name = "extra" } instantTextBoxType = { name = "title"'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        @(Compare-GuiWidgetPaths -Baseline $script:SampleWindow.Node -Actual $actual.Node) | Should -BeNullOrEmpty
    }

    It 'reports each changed, added and removed property by widget' {
        $changed = $script:Sample -replace 'width = 300 height = 30', 'width = 320 height = 30' -replace 'font = "hoi_18mbs"', 'maxWidth = 200' -replace 'height=300', 'height=300 moveable = yes'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        $changes = @(Compare-GuiWindows -Baseline $script:SampleWindow.Node -Actual $actual.Node | ForEach-Object { '{0}|{1}|{2}|{3}|{4}' -f $_.Kind, $_.Widget, $_.Property, $_.Old, $_.New })
        $changes | Should -Contain 'Changed|sample_window/list/grid|slotsize.width|300|320'
        $changes | Should -Contain 'Added|sample_window/title|maxWidth||200'
        $changes | Should -Contain 'Removed|sample_window/title|font|hoi_18mbs|'
        $changes | Should -Contain 'Added|sample_window|size.moveable||yes'
        $changes.Count | Should -Be 4
    }

    It 'reports a new or missing widget once, and nothing for reordered or reformatted text' {
        $changed = $script:Sample -replace '(?m)^\s*instantTextBoxType.*$', 'iconType = { name = "extra" spriteType = "GFX_x" }'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $changed))[0]
        $changes = @(Compare-GuiWindows -Baseline $script:SampleWindow.Node -Actual $actual.Node | ForEach-Object { '{0}|{1}' -f $_.Kind, $_.Widget })
        $changes | Should -Be @('NewWidget|sample_window/extra', 'MissingWidget|sample_window/title')

        $reformatted = $script:Sample -replace 'width = 400 height=300', "height = 300`n`t`t`twidth=400 # reordered" -replace '"sample_window"', 'sample_window'
        $actual = @(Get-GuiTopLevelWindows -Root (ConvertFrom-GuiText -Text $reformatted))[0]
        @(Compare-GuiWindows -Baseline $script:SampleWindow.Node -Actual $actual.Node) | Should -BeNullOrEmpty
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

Describe 'Executable name search' {
    BeforeAll {
        # Two groups of zero-terminated string literals 5000 bytes apart, the way hoi4.exe stores them.
        $nul = [string][char]0
        $script:ExeSample = 'junk' + $nul + 'close_button' + $nul + ('x' * 5000) + $nul + 'row_name' + $nul + 'ROW_TOOLTIP' + $nul + 'hidden_value' + $nul + $nul + 'row_icon' + $nul + 'tail'
    }

    It 'puts the cluster that holds most of the names first' {
        $clusters = @(Get-ExeNameClusters -Text $script:ExeSample -Names @('row_name', 'row_icon', 'close_button', 'not_stored'))
        $clusters.Count | Should -Be 2
        $clusters[0].Names | Should -Be @('row_name', 'row_icon')
        $script:ExeSample.Substring($clusters[0].Start, $clusters[0].End - $clusters[0].Start) | Should -BeLike 'row_name*row_icon'
    }

    It 'lists every literal stored inside a cluster, in stored order' {
        $cluster = @(Get-ExeNameClusters -Text $script:ExeSample -Names @('row_name', 'row_icon'))[0]
        @(Get-ExeStrings -Text $script:ExeSample -Start ($cluster.Start - 1) -End ($cluster.End + 1) | ForEach-Object { $_.Value }) | Should -Be @('row_name', 'ROW_TOOLTIP', 'hidden_value', 'row_icon')
    }

    It 'matches whole literals only' {
        @(Get-ExeNameClusters -Text $script:ExeSample -Names @('row', 'name')).Count | Should -Be 0
    }
}

Describe 'Checksum' {
    It 'is changed by the scripted GUIs of Milestone D and by nothing else' {
        # Mirrors checksum_manifest.txt in the game folder. Since phase D2 the mod has scripted GUIs, which
        # live under common/ and end Ironman and achievement compatibility (wiki/Roadmap.md, "Checksum").
        # They stay in these four folders; tests/ScriptedGuis.Tests.ps1 checks what the files may say.
        $scriptedGuiFolders = @('scripted_guis', 'scripted_effects', 'on_actions', 'synchronized_dynamic_tokens')
        $rules = @(
            @{ Dir = 'common'; Extensions = @('.txt', '.lua') }
            @{ Dir = 'events'; Extensions = @('.txt') }
            @{ Dir = 'history'; Extensions = @('.txt') }
            @{ Dir = 'map'; Extensions = @('.txt', '.map', '.bmp', '.csv') }
        )
        $hits = foreach ($rule in $rules) {
            $dir = Join-Path $script:RepoRoot $rule.Dir
            if (-not (Test-Path $dir)) { continue }
            foreach ($file in @(Get-ChildItem -Path $dir -Recurse -File | Where-Object { $rule.Extensions -contains $_.Extension.ToLowerInvariant() })) {
                $rel = $file.FullName.Substring($script:RepoRoot.Length + 1)
                $parts = $rel -split '[\\/]'
                if ($rule.Dir -eq 'common' -and $parts.Count -eq 3 -and $scriptedGuiFolders -contains $parts[1]) { continue }
                $rel
            }
        }
        $hits | Should -BeNullOrEmpty -Because 'gameplay files other than scripted GUIs are outside what this mod does'
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

    It 'gives every declared sprite the GFX_1440p_ prefix, but the listed vanilla names' {
        # A vanilla name is declared again only where the code puts the sprite on a widget itself, only in
        # interface/zz_1440p_vanilla_sprites.gfx (it must sort after the vanilla file, LOAD-012), and only when
        # the screen named here is the only one that shows it (Design Rules, "Sprites and backgrounds").
        $allowed = @{
            'GFX_production_item'                = 'C1 production lines'
            'GFX_naval_production_item_bg_strip' = 'C1 production lines'
            'GFX_prod_progress_bar2'             = 'C1 production lines'
            'GFX_prod_progress_bar2_red'         = 'C1 production lines'
            'GFX_prod_progress_bar2_yellow'      = 'C1 production lines'
            'GFX_deploy_reinforcements_entry'    = 'A5 priority rows of Recruit & Deploy'
            'GFX_deploy_upgrades_entry'          = 'A5 priority rows of Recruit & Deploy'
            'GFX_deploy_supply_entry'            = 'A5 priority rows of Recruit & Deploy'
            'GFX_deploy_operations_entry'        = 'A5 priority rows of Recruit & Deploy'
            'GFX_deploy_garrisons_entry'         = 'A5 priority rows of Recruit & Deploy'
            'GFX_deploy_lendlease_entry'         = 'A5 priority rows of Recruit & Deploy'
            # --- a8-theatre ---
            'GFX_theatre_dropdown_bottom'        = 'A8 last row under a theatre box'
            # --- a5-recruit ---
            'GFX_deployment_entry_progressbar'         = 'A5 bars of the training lines of Recruit & Deploy'
            'GFX_deployment_entry_stalled_progressbar' = 'A5 bars of the training lines of Recruit & Deploy'
            # --- c2-state-rows ---
            'GFX_leader_selection_active_entry_bg'             = 'C2 general rows (also captured generals, see the gfx)'
            'GFX_leader_selection_unavailable_entry_bg'        = 'C2 general rows'
            'GFX_leader_selection_unavailable_active_entry_bg' = 'C2 general rows'
            'GFX_marshal_selection_entry_bg'                   = 'C2 general rows'
            'GFX_marshal_selection_active_entry_bg'            = 'C2 general rows'
            'GFX_leader_selection_entry_bg_faction'            = 'C2 general rows (faction commander window)'
            'GFX_leader_selection_active_entry_bg_faction'     = 'C2 general rows (faction commander window)'
            # --- A10 ---
            'GFX_strategicair_linechart'                       = 'A10 chart of the air region window'
        }
        $redefinitionFile = 'zz_1440p_vanilla_sprites.gfx'
        $wrong = foreach ($file in @(Get-ModGuiFiles -Filter '*.gfx')) {
            $text = Read-GuiText -Path $file.FullName
            foreach ($sprite in @(Get-GuiSpriteDeclarations -Root (ConvertFrom-GuiText -Text $text))) {
                if ($sprite.Name -like 'GFX_1440p_*') { continue }
                if (-not $allowed.ContainsKey($sprite.Name)) { "$($file.Name): $($sprite.Name) is a vanilla name that is not listed"; continue }
                if ($file.Name -ne $redefinitionFile) { "$($file.Name): $($sprite.Name) belongs in $redefinitionFile" }
            }
        }
        $wrong | Should -BeNullOrEmpty -Because 'redefining a vanilla sprite name changes every screen that uses it'
    }

    It 'points every declared sprite at a texture that exists' {
        # Textures may come from the mod or from vanilla. Without a game install (CI) only the mod is checked.
        $gameDir = Resolve-HoiGameDir
        $missing = foreach ($sprite in $script:DeclaredSprites) {
            if ($sprite.Type -ieq 'LineChartType') { continue }   # A10: a chart has a size and a line width, no texture
            if (-not $sprite.Textures.Count) { "$($sprite.Name): no texturefile"; continue }
            foreach ($texture in $sprite.Textures) {
                if (Test-Path (Join-Path $script:RepoRoot $texture)) { continue }
                if (-not $gameDir) { continue }
                if (-not (Test-Path (Join-Path $gameDir $texture))) { "$($sprite.Name): $texture" }
            }
        }
        $missing | Should -BeNullOrEmpty
    }
}

Describe 'Mod windows' {
    It 'defines every overridden window in one file only' {
        # With two definitions the file that loads last wins silently.
        $seen = @{}
        $duplicates = foreach ($file in @(Get-ModGuiFiles -Filter '*.gui')) {
            $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
            foreach ($window in @(Get-GuiTopLevelWindows -Root $root)) {
                if ($seen.ContainsKey($window.Name)) { "$($window.Name): $($seen[$window.Name]) and $($file.Name)" }
                else { $seen[$window.Name] = $file.Name }
            }
        }
        $duplicates | Should -BeNullOrEmpty
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
            Find-GuiBaseline -BaselineDir $script:BaselineDir -Name $Window | Should -Not -BeNullOrEmpty -Because 'run tools/Export-VanillaBaseline.ps1 before reworking a vanilla window'
        }

        It 'keeps every named vanilla widget under its vanilla parents, inside mod1440_ containers at most' {
            $baseline = Find-GuiBaseline -BaselineDir $script:BaselineDir -Name $Window
            if (-not $baseline) {
                Set-ItResult -Skipped -Because 'there is no baseline to compare against'
                return
            }
            $actual = Get-ModWindow -Path $FullPath -Name $Window
            @(Compare-GuiWidgetPaths -Baseline $baseline.Node -Actual $actual.Node -WrapperPrefix $script:ModWindowPrefix) | Should -BeNullOrEmpty -Because 'the engine binds data to widgets by name inside their parent; with the patched executable it also searches the containers the mod adds, for every element type but scrollbars, list boxes, browsers and positions'
        }
    }
}

if ($listRowCases.Count -gt 0) {
    Describe 'Rows <Row> in list <List>' -ForEach $listRowCases {
        It 'fit inside the list, which is overridden together with them' {
            $rowWindow = Find-ModWindow -Name $Row
            $rowWindow | Should -Not -BeNullOrEmpty -Because "row window '$Row' is listed in `$listRowCases, so a mod .gui file should define it"

            $listWindow = Find-ModWindow -Name $ListWindow
            $listWindow | Should -Not -BeNullOrEmpty -Because "'$ListWindow' holds the list of these rows; left at vanilla size it cuts wider rows off"

            $listNode = @(Get-GuiNodes -Node $listWindow.Node | Where-Object { (Get-GuiValue -Node $_ -Key 'name') -eq $List })[0]
            $listNode | Should -Not -BeNullOrEmpty -Because "'$ListWindow' should contain a list named '$List'"

            $rowWidth = Get-GuiWidth -Node $rowWindow.Node
            $listWidth = Get-GuiWidth -Node $listNode
            $rowWidth | Should -Not -BeNullOrEmpty
            $listWidth | Should -Not -BeNullOrEmpty
            $rowWidth | Should -BeLessOrEqual $listWidth -Because 'a list box cuts off anything wider than itself'

            # a list height of 0 or "set in code" means the engine sizes it; a written height must hold one row
            $rowHeight = Get-GuiHeight -Node $rowWindow.Node
            $listHeight = Get-GuiHeight -Node $listNode
            if ($rowHeight -and $listHeight -and $listHeight -gt 0) {
                $rowHeight | Should -BeLessOrEqual $listHeight -Because 'a list shorter than one row shows nothing'
            }
        }
    }
}

if ($entryPairCases.Count -gt 0) {
    Describe 'List <Grid> <GridWindow> filled with <Entry>' -ForEach $entryPairCases {
        It 'uses a slot width equal to the entry row width' {
            $gridNode = $null
            $entryNode = $null
            # one window can hold several grids of one name (the three item_grid of the army overview):
            # a pair names the container around its grid as "container/grid", as the renderer does
            $gridName = $Grid
            $gridParent = $null
            if ($Grid -like '*/*') { $gridParent, $gridName = $Grid -split '/', 2 }
            foreach ($file in @(Get-ModGuiFiles -Filter '*.gui')) {
                $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
                # two vanilla windows can each have a grid of one name (templates_grid): a pair may name its window
                $scopes = @($root)
                if ($GridWindow) { $scopes = @(Get-GuiTopLevelWindows -Root $root | Where-Object { $_.Name -eq $GridWindow } | ForEach-Object { $_.Node }) }
                if ($gridParent) { $scopes = @($scopes | ForEach-Object { Get-GuiNodes -Node $_ } | Where-Object { $_.Key -ieq 'containerWindowType' -and (Get-GuiValue -Node $_ -Key 'name') -eq $gridParent }) }
                foreach ($scope in $scopes) {
                    foreach ($node in @(Get-GuiNodes -Node $scope)) {
                        if ($node.Key -ieq 'gridBoxType' -and (Get-GuiValue -Node $node -Key 'name') -eq $gridName) { $gridNode = $node }
                    }
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
