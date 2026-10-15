BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    . (Join-Path $script:RepoRoot 'tools\HoiModBuild.ps1')
    $script:BuildConfig = Get-ModBuildConfig -RepoDir $script:RepoRoot
}

Describe 'build.ps1 configuration' {
    It 'ships the common, gfx, interface and localisation folders with the descriptor and thumbnail' {
        $shippedTopLevel = @(Get-ModContentFiles -Config $script:BuildConfig | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique)
        $shippedTopLevel | Should -Be @('common', 'descriptor.mod', 'gfx', 'interface', 'localisation', 'thumbnail.png') -Because 'tools, baseline and reference are development folders, and reference alone is tens of megabytes'
    }

    It 'installs as hoi4-1440p-ui-mod and packages hoi4-1440p-ui-mod.zip' {
        $script:BuildConfig.ModFolderName | Should -Be 'hoi4-1440p-ui-mod'
        $script:BuildConfig.ZipArchiveName | Should -Be 'hoi4-1440p-ui-mod.zip'
        $script:BuildConfig.PackageLayout | Should -Be 'Flat'
    }
}
