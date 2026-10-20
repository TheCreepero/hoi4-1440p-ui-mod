BeforeDiscovery {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $repoRoot 'tools') 'GuiParsing.ps1')
    $python = Get-Command python -ErrorAction SilentlyContinue
    $hasPillow = $false
    if ($python) {
        try { & $python.Source -I -c 'import PIL' 2>$null; $hasPillow = ($LASTEXITCODE -eq 0) } catch { $hasPillow = $false }
    }
    $canRender = $hasPillow -and (Resolve-HoiGameDir)
}

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $script:RepoRoot 'tools') 'GuiParsing.ps1')
    $script:Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    $script:Tools = Join-Path $script:RepoRoot 'tools'
    $script:Example = Join-Path (Join-Path $script:Tools 'examples') 'a10-layout.json'
    $script:Work = Join-Path (Join-Path $script:RepoRoot 'scratch') 'test-layout'
    if (-not (Test-Path $script:Work)) { New-Item -ItemType Directory -Path $script:Work -Force | Out-Null }

    function Invoke-Tool {
        param([string[]]$Arguments)
        $output = & $script:Python -I @Arguments 2>&1
        return @{ Exit = $LASTEXITCODE; Output = ($output | Out-String) }
    }
}

Describe 'The layout file (tools/layout.py, tools/apply_layout.py)' {
    It 'the worked example loads and expands its repeats' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        $code = "import sys; sys.path.insert(0, r'$($script:Tools)'); import layout; lay = layout.load(r'$($script:Example)'); n = sum(len(layout.items(w)) for w in lay['windows']); print(n); print(len(layout.plate_declarations(lay)))"
        $result = Invoke-Tool @('-c', $code)
        $result.Exit | Should -Be 0 -Because $result.Output
        $lines = @($result.Output -split '\r?\n' | Where-Object { $_ })
        [int]$lines[0] | Should -BeGreaterThan 150 -Because 'A10 moves about 150 widgets and adds about 40 plates and captions'
        [int]$lines[1] | Should -Be 11 -Because 'A10 declares eleven plate sprites of the card style'
    }

    It 'applied to the vanilla baseline it gives the committed A10 file, and a second run changes nothing' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        $gui = Join-Path $script:Work 'a10-test.gui'
        $gfx = Join-Path $script:Work 'a10-test.gfx'
        Copy-Item -LiteralPath (Join-Path (Join-Path (Join-Path $script:RepoRoot 'baseline') 'strategicairview') 'strategicairview.gui') -Destination $gui -Force
        Copy-Item -LiteralPath (Join-Path (Join-Path $script:RepoRoot 'interface') '1440p_ui.gfx') -Destination $gfx -Force
        $first = Invoke-Tool @((Join-Path $script:Tools 'apply_layout.py'), $script:Example, '--gui', $gui, '--gfx', $gfx, '--no-scene')
        $first.Exit | Should -Be 0 -Because $first.Output
        $once = [System.IO.File]::ReadAllBytes($gui)
        $onceGfx = [System.IO.File]::ReadAllBytes($gfx)
        $second = Invoke-Tool @((Join-Path $script:Tools 'apply_layout.py'), $script:Example, '--gui', $gui, '--gfx', $gfx, '--no-scene')
        $second.Exit | Should -Be 0 -Because $second.Output
        [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes($gui)) | Should -Be ([System.Convert]::ToBase64String($once)) -Because 'the values are absolute'
        [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes($gfx)) | Should -Be ([System.Convert]::ToBase64String($onceGfx))
        # the committed file matches the layout in every place, size and font the layout names
        $compare = Invoke-Tool @((Join-Path $script:Tools 'apply_layout.py'), $script:Example, '--compare', (Join-Path (Join-Path $script:RepoRoot 'interface') 'zz_1440p_air_region.gui'))
        $compare.Exit | Should -Be 0 -Because $compare.Output
        # and the generated file differs from the committed one only in its header comments and comment lines
        $made = @([System.IO.File]::ReadAllLines($gui) | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith('#') })
        $committed = @([System.IO.File]::ReadAllLines((Join-Path (Join-Path $script:RepoRoot 'interface') 'zz_1440p_air_region.gui')) | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith('#') })
        ($made -join "`n") | Should -Be ($committed -join "`n")
    }

    It 'the generated sprite block parses and declares a tile per plate' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        $gfx = Join-Path $script:Work 'a10-test.gfx'
        if (-not (Test-Path $gfx)) { Set-ItResult -Skipped -Because 'the apply test did not run'; return }
        $text = [System.IO.File]::ReadAllText($gfx, [System.Text.Encoding]::UTF8)
        $text | Should -Match '# --- A10 layout ---'
        $text | Should -Match '# --- end A10 layout ---'
        ([regex]::Matches($text, 'name = "GFX_1440p_AR_card_a"')).Count | Should -Be 2 -Because 'the committed block and the generated one both declare it; the test file is a copy'
        @(Test-GuiFileSyntax -Path $gfx).Count | Should -Be 0 -Because 'balanced braces and quotes, no BOM'
    }
}

Describe 'The mock-up from a layout (tools/mockup.py)' -Skip:(-not $canRender) {
    It 'draws the worked example' {
        $out = Join-Path $script:Work 'a10-mockup-test.png'
        if (Test-Path $out) { Remove-Item -LiteralPath $out -Force }
        $result = Invoke-Tool @((Join-Path $script:Tools 'mockup.py'), $script:Example, '--out', $out, '--crop', '690,280,2240,1040')
        $result.Exit | Should -Be 0 -Because $result.Output
        Test-Path $out | Should -BeTrue
        (Get-Item $out).Length | Should -BeGreaterThan 100000
    }
}

Describe 'The design page (tools/make_design_page.py)' {
    It 'makes a page with one composite image per figure group from a sample handoff folder' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        & $script:Python -I -c 'import PIL' 2>$null
        if ($LASTEXITCODE -ne 0) { Set-ItResult -Skipped -Because 'Pillow is not installed'; return }
        $phase = Join-Path $script:Work 'phase-sample'
        if (Test-Path $phase) { Remove-Item -LiteralPath $phase -Recurse -Force }
        New-Item -ItemType Directory -Path (Join-Path $phase 'build') -Force | Out-Null
        $design = @{
            id = 'T1'; title = 'Sample screen'; kind = 'screen'; verdict = 'rework'; effort = 'S'
            summary = 'Two **bold** words and `code`.'; current = 'Cramped.'
            proposal = @(@{ heading = 'Head'; body = 'Body.' })
            table = @{ columns = @('Part', 'Vanilla', 'Current', 'Proposed'); rows = @(, @('Panel', '1x1', '', '2x2')) }
            figures = @(@{ file = 'vanilla-main.png'; kind = 'vanilla'; group = 'main'; caption = 'v' }, @{ file = 'proposed-main.png'; kind = 'proposed'; group = 'main'; caption = 'p' })
            decisions = @(@{ question = 'Which width?'; options = @('A', 'B'); recommendation = 'A' })
            openInGame = @('The tooltip.'); risks = @(); knowledge = @(); additions = @()
        }
        [System.IO.File]::WriteAllText((Join-Path $phase 'design.json'), ($design | ConvertTo-Json -Depth 6), [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::WriteAllText((Join-Path $phase 'decisions-final.json'), '[{"question": "Which width?", "chosen": "A", "by": "user"}]', [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::WriteAllText((Join-Path (Join-Path $phase 'build') 'build.json'), '{"id": "T1", "summary": "Built.", "figures": [{"file": "build-main.png", "group": "main", "caption": "b"}], "deviations": [{"what": "x", "why": "y"}]}', [System.Text.UTF8Encoding]::new($false))
        $mk = "from PIL import Image; import os; d = r'$phase'; [Image.new('RGB', (200, 100), c).save(os.path.join(d, p)) for p, c in (('vanilla-main.png', (90, 30, 30)), ('proposed-main.png', (30, 90, 30)), ('build/build-main.png', (30, 30, 90)))]"
        $made = Invoke-Tool @('-c', $mk)
        $made.Exit | Should -Be 0 -Because $made.Output
        $result = Invoke-Tool @((Join-Path $script:Tools 'make_design_page.py'), $phase)
        $result.Exit | Should -Be 0 -Because $result.Output
        $page = Join-Path $phase 'design.html'
        Test-Path $page | Should -BeTrue
        $text = [System.IO.File]::ReadAllText($page, [System.Text.Encoding]::UTF8)
        $text | Should -Match 'Which width\?'
        $text | Should -Match 'Chosen: A'
        $text | Should -Match '<b>bold</b>'
        $text | Should -Match 'Where the build differs'
        ([regex]::Matches($text, '<img ')).Count | Should -Be 1 -Because 'one composite per figure group'
        Test-Path (Join-Path (Join-Path $phase 'figures') 'main.webp') | Should -BeTrue
    }
}

Describe 'The phase notes (tools/phase_notes.py)' {
    It 'writes the generated sections between markers from the handoff files, and a second run changes nothing' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        $scratch = Join-Path $script:Work 'notes-scratch'
        $phase = Join-Path $scratch 'N1'
        if (Test-Path $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
        New-Item -ItemType Directory -Path (Join-Path $phase 'checks') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $phase 'build') -Force | Out-Null
        $utf8 = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText((Join-Path $phase 'design.json'), '{"id": "N1", "summary": "A card pass.", "verdict": "refine", "effort": "S", "proposal": [{"heading": "Head", "body": "Body."}], "table": {"columns": ["Part", "Vanilla", "Proposed"], "rows": [["Panel", "1", "2"]]}, "figures": [{"file": "a.png", "kind": "proposed", "group": "main"}]}', $utf8)
        [System.IO.File]::WriteAllText((Join-Path (Join-Path $phase 'build') 'build.json'), '{"id": "N1", "agent": "builder-screen", "summary": "Built.", "deviations": [{"what": "x", "why": "y"}], "gameCheck": "tools/Invoke-GameCheck.ps1 air_region", "checklist": ["one", "two"], "tests": "green"}', $utf8)
        [System.IO.File]::WriteAllText((Join-Path (Join-Path $phase 'checks') 'check-1.json'), '{"id": "N1", "round": 1, "date": "2026-10-20", "build": "abc+dirty", "playset": "this mod only", "launches": [{"command": "tools/Invoke-GameCheck.ps1 air_region", "captures": ["scratch/checks/air_region_crop.png"], "clock": "1 Jan 1936", "errorLog": []}], "checklist": [{"item": 1, "result": "pass"}, {"item": 2, "result": "fail", "note": "cut", "evidence": "e.png", "box": [0, 0, 1, 1]}], "defects": [{"what": "cut", "where": "w", "evidence": "e.png"}], "forTheUser": ["tooltip"], "autosave": "not touched"}', $utf8)
        [System.IO.File]::WriteAllText((Join-Path $phase 'fixes.json'), '[{"round": 1, "date": "2026-10-20", "issue": "cut", "cause": "c", "fix": "f", "retest": "r", "by": "builder-screen"}]', $utf8)
        $notes = Join-Path $scratch 'N1-sample.md'
        Copy-Item -LiteralPath (Join-Path (Join-Path $script:RepoRoot 'wiki') 'Phase-Template.md') -Destination $notes -Force
        $first = Invoke-Tool @((Join-Path $script:Tools 'phase_notes.py'), 'N1', '--notes', $notes, '--scratch', $scratch)
        $first.Exit | Should -Be 0 -Because $first.Output
        $text = [System.IO.File]::ReadAllText($notes, [System.Text.Encoding]::UTF8)
        foreach ($name in @('proposal', 'build', 'game checks', 'fix rounds')) {
            $text | Should -Match ('<!-- generated: ' + $name + ' \(')
            $text | Should -Match ('<!-- end generated: ' + $name + ' -->')
        }
        $text | Should -Match 'A card pass\. Verdict: refine; effort: S\.'
        $text | Should -Match '\| 1 \| 2026-10-20 \| abc\+dirty \| game-checker \|'
        $text | Should -Match '### Fix round 1 \(2026-10-20\)'
        $text | Should -Match '(?m)^## Scope' -Because 'the hand-written sections stay'
        $check = Invoke-Tool @((Join-Path $script:Tools 'phase_notes.py'), 'N1', '--notes', $notes, '--scratch', $scratch, '--check')
        $check.Exit | Should -Be 0 -Because $check.Output
        $second = Invoke-Tool @((Join-Path $script:Tools 'phase_notes.py'), 'N1', '--notes', $notes, '--scratch', $scratch)
        [System.IO.File]::ReadAllText($notes, [System.Text.Encoding]::UTF8) | Should -Be $text
    }

    It 'the crop tool cuts a box out of a capture' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        & $script:Python -I -c 'import PIL' 2>$null
        if ($LASTEXITCODE -ne 0) { Set-ItResult -Skipped -Because 'Pillow is not installed'; return }
        $src = Join-Path $script:Work 'crop-src.png'
        $mk = "from PIL import Image; Image.new('RGB', (300, 200), (10, 20, 30)).save(r'$src')"
        (Invoke-Tool @('-c', $mk)).Exit | Should -Be 0
        $out = Join-Path $script:Work 'crop-out.png'
        $result = Invoke-Tool @((Join-Path $script:Tools 'crop_capture.py'), $src, '10,10,110,60', '--out', $out, '--scale', '2')
        $result.Exit | Should -Be 0 -Because $result.Output
        $result.Output | Should -Match '200x100'
    }
}
