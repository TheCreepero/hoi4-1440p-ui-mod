BeforeDiscovery {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $repoRoot 'tools') 'GuiParsing.ps1')

    $python = Get-Command python -ErrorAction SilentlyContinue
    $hasPillow = $false
    if ($python) {
        try { & $python.Source -I -c 'import PIL' 2>$null; $hasPillow = ($LASTEXITCODE -eq 0) } catch { $hasPillow = $false }
    }
    $gameDir = Resolve-HoiGameDir
    $canRender = $hasPillow -and $gameDir

    # Every overridden window renders; every scene composes.
    $windowCases = @()
    $sceneCases = @()
    if ($canRender) {
        foreach ($file in @(Get-ChildItem -Path (Join-Path $repoRoot 'interface') -Recurse -File -Filter '*.gui')) {
            $root = ConvertFrom-GuiText -Text (Read-GuiText -Path $file.FullName)
            foreach ($window in @(Get-GuiTopLevelWindows -Root $root)) {
                $windowCases += @{ Window = $window.Name; File = $file.Name }
            }
        }
        foreach ($scene in @(Get-ChildItem -Path (Join-Path (Join-Path $repoRoot 'tools') 'scenes') -Filter '*.json' -ErrorAction SilentlyContinue)) {
            $sceneCases += @{ Scene = $scene.BaseName }
        }
    }
}

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path (Join-Path $script:RepoRoot 'tools') 'GuiParsing.ps1')
    $script:Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    $script:RenderPy = Join-Path (Join-Path $script:RepoRoot 'tools') 'render_gui.py'
    $script:OutDir = Join-Path (Join-Path $script:RepoRoot 'scratch') 'test-renders'
    if (-not (Test-Path $script:OutDir)) { New-Item -ItemType Directory -Path $script:OutDir -Force | Out-Null }
}

Describe 'Renderer prerequisites' {
    It 'has Python with Pillow and a game install, or the render tests are skipped' {
        if (-not $script:Python) { Set-ItResult -Skipped -Because 'python is not installed'; return }
        & $script:Python -I -c 'import PIL' 2>$null
        if ($LASTEXITCODE -ne 0) { Set-ItResult -Skipped -Because 'Pillow is not installed'; return }
        if (-not (Resolve-HoiGameDir)) { Set-ItResult -Skipped -Because 'no Hearts of Iron IV install (textures and fonts come from it)'; return }
        $true | Should -BeTrue
    }
}

if ($windowCases.Count -gt 0) {
    Describe 'Render window <Window> (<File>)' -ForEach $windowCases {
        It 'draws without an error and names no undeclared sprite' {
            $out = Join-Path $script:OutDir "$Window.png"
            $output = @(& $script:Python -I $script:RenderPy $Window --scale 1 --out $out 2>&1)
            $LASTEXITCODE | Should -Be 0 -Because ($output -join "`n")
            Test-Path $out | Should -BeTrue
            # vanilla windows carry placeholder sprite names the code replaces (GFX_idea_HOL_wilhelmina ...), so only mod sprites count
            @($output | Where-Object { $_ -match 'GFX_1440p_\w+ is not declared in any \.gfx file' }) | Should -BeNullOrEmpty -Because 'a sprite name the game cannot find draws nothing'
            @($output | Where-Object { $_ -match '(1440p_ui|GFX_1440p_).*not found' }) | Should -BeNullOrEmpty -Because 'a missing mod texture draws nothing in game either'
            @($output | Where-Object { $_ -match 'font .* not found' }) | Should -BeNullOrEmpty -Because 'a font name that vanilla does not declare shows no text'
        }
    }
}

if ($sceneCases.Count -gt 0) {
    Describe 'Render scene <Scene>' -ForEach $sceneCases {
        It 'composes every window of the scene' {
            $out = Join-Path $script:OutDir "$Scene`_scene.png"
            $output = @(& $script:Python -I $script:RenderPy --scene $Scene --out $out 2>&1)
            $LASTEXITCODE | Should -Be 0 -Because ($output -join "`n")
            @($output | Where-Object { $_ -match 'NOT FOUND' }) | Should -BeNullOrEmpty -Because 'every window named in a scene must exist'
            @($output | Where-Object { $_ -match '^\s*cut off\s' }) | Should -BeNullOrEmpty -Because 'a sample text that is cut off needs a wider box or a shorter sample'
        }
    }
}
