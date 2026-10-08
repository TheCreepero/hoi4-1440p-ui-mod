# Shared Clausewitz GUI parsing helpers for the tools in this folder and the Pester suites.
# Dot-source this file; it only defines functions. Keep it ASCII and Windows PowerShell 5.1 compatible.

function Resolve-HoiGameDir {
    param([string]$GameDir)

    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($GameDir) { $candidates.Add($GameDir) }
    if ($env:HOI4_GAME_DIR) { $candidates.Add($env:HOI4_GAME_DIR) }

    $steamRoots = [System.Collections.Generic.List[string]]::new()
    try {
        $steamPath = (Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamPath
        if ($steamPath) { $steamRoots.Add(($steamPath -replace '/', '\')) }
    } catch { }
    $steamRoots.Add('C:\Program Files (x86)\Steam')

    foreach ($root in @($steamRoots)) {
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($m in [regex]::Matches([System.IO.File]::ReadAllText($vdf), '"path"\s+"([^"]+)"')) {
                $steamRoots.Add(($m.Groups[1].Value -replace '\\\\', '\'))
            }
        }
    }
    foreach ($root in $steamRoots) {
        $candidates.Add((Join-Path $root 'steamapps\common\Hearts of Iron IV'))
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath (Join-Path $candidate 'interface'))) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Read-GuiText {
    param([Parameter(Mandatory)][string]$Path)

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $offset = 0
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { $offset = 3 }
    try {
        return [System.Text.UTF8Encoding]::new($false, $true).GetString($bytes, $offset, $bytes.Length - $offset)
    } catch {
        # Some vanilla files carry Windows-1252 bytes in comments.
        return [System.Text.Encoding]::GetEncoding(28591).GetString($bytes, $offset, $bytes.Length - $offset)
    }
}

function Test-GuiFileSyntax {
    param([Parameter(Mandatory)][string]$Path)

    $problems = [System.Collections.Generic.List[string]]::new()
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $problems.Add('UTF-8 BOM detected')
    }

    $cleanText = [regex]::Replace((Read-GuiText -Path $Path), '#[^\r\n]*', '')
    $openCount = ([regex]::Matches($cleanText, '\{')).Count
    $closeCount = ([regex]::Matches($cleanText, '\}')).Count
    if ($openCount -ne $closeCount) { $problems.Add("Bracket mismatch (open $openCount, close $closeCount)") }

    $quoteCount = ([regex]::Matches($cleanText, '"')).Count
    if ($quoteCount % 2 -ne 0) { $problems.Add("Unbalanced double quotes ($quoteCount found)") }

    return $problems
}

# Parses Clausewitz script into a tree. A block node has Children (a list); a key = value leaf has
# Children = $null. Line and EndLine are 1-based line numbers of the key and of the closing brace.
function ConvertFrom-GuiText {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Text)

    $lineStarts = [System.Collections.Generic.List[int]]::new()
    $lineStarts.Add(0)
    foreach ($newline in [regex]::Matches($Text, "\n")) { $lineStarts.Add($newline.Index + 1) }

    $root = [pscustomobject]@{ Key = ''; Value = $null; Children = [System.Collections.Generic.List[object]]::new(); Line = 1; EndLine = $lineStarts.Count }
    $stack = [System.Collections.Generic.Stack[object]]::new()
    $stack.Push($root)
    $pendingKey = $null
    $pendingLine = 0
    $expectValue = $false

    foreach ($match in [regex]::Matches($Text, '#[^\r\n]*|"[^"]*"|[{}=]|[^\s{}=#"]+')) {
        $token = $match.Value
        if ($token.StartsWith('#')) { continue }

        $lineIndex = $lineStarts.BinarySearch($match.Index)
        if ($lineIndex -lt 0) { $lineIndex = (-bnot $lineIndex) - 1 }
        $line = $lineIndex + 1
        $current = $stack.Peek()

        if ($token -eq '{') {
            $key = ''
            $keyLine = $line
            if ($expectValue) {
                $key = $pendingKey
                $keyLine = $pendingLine
            } elseif ($null -ne $pendingKey) {
                $current.Children.Add([pscustomobject]@{ Key = $pendingKey; Value = $null; Children = $null; Line = $pendingLine; EndLine = $pendingLine })
            }
            $node = [pscustomobject]@{ Key = $key; Value = $null; Children = [System.Collections.Generic.List[object]]::new(); Line = $keyLine; EndLine = $keyLine }
            $current.Children.Add($node)
            $stack.Push($node)
            $pendingKey = $null
            $expectValue = $false
        } elseif ($token -eq '}') {
            if ($null -ne $pendingKey) {
                $current.Children.Add([pscustomobject]@{ Key = $pendingKey; Value = $null; Children = $null; Line = $pendingLine; EndLine = $pendingLine })
            }
            $pendingKey = $null
            $expectValue = $false
            if ($stack.Count -gt 1) {
                $closed = $stack.Pop()
                $closed.EndLine = $line
            }
        } elseif ($token -eq '=') {
            $expectValue = $true
        } else {
            $value = $token
            if ($value.Length -ge 2 -and $value.StartsWith('"')) { $value = $value.Substring(1, $value.Length - 2) }
            if ($expectValue) {
                $current.Children.Add([pscustomobject]@{ Key = $pendingKey; Value = $value; Children = $null; Line = $pendingLine; EndLine = $line })
                $pendingKey = $null
                $expectValue = $false
            } else {
                if ($null -ne $pendingKey) {
                    $current.Children.Add([pscustomobject]@{ Key = $pendingKey; Value = $null; Children = $null; Line = $pendingLine; EndLine = $pendingLine })
                }
                $pendingKey = $value
                $pendingLine = $line
            }
        }
    }

    return $root
}

function Get-GuiValue {
    param($Node, [string]$Key)

    if ($null -eq $Node -or $null -eq $Node.Children) { return $null }
    foreach ($child in $Node.Children) {
        if ($null -eq $child.Children -and $child.Key -ieq $Key) { return $child.Value }
    }
    return $null
}

function Get-GuiBlock {
    param($Node, [string]$Key)

    if ($null -eq $Node -or $null -eq $Node.Children) { return $null }
    foreach ($child in $Node.Children) {
        if ($null -ne $child.Children -and $child.Key -ieq $Key) { return $child }
    }
    return $null
}

function ConvertTo-GuiNumber {
    param([string]$Value)

    if ($Value -match '^-?\d+(\.\d+)?$') {
        return [double]::Parse($Value, [System.Globalization.CultureInfo]::InvariantCulture)
    }
    return $null
}

# Every block at or below $Node, parents before children.
function Get-GuiNodes {
    param([Parameter(Mandatory)]$Node)

    $stack = [System.Collections.Generic.Stack[object]]::new()
    $stack.Push($Node)
    while ($stack.Count -gt 0) {
        $current = $stack.Pop()
        $current
        for ($i = $current.Children.Count - 1; $i -ge 0; $i--) {
            if ($null -ne $current.Children[$i].Children) { $stack.Push($current.Children[$i]) }
        }
    }
}

function Get-GuiTopLevelWindows {
    param([Parameter(Mandatory)]$Root)

    foreach ($section in $Root.Children) {
        if ($null -eq $section.Children -or $section.Key -ine 'guiTypes') { continue }
        foreach ($child in $section.Children) {
            if ($null -eq $child.Children) { continue }
            $name = Get-GuiValue -Node $child -Key 'name'
            if ($name) {
                [pscustomobject]@{ Name = $name; Type = $child.Key; Node = $child; Line = $child.Line; EndLine = $child.EndLine }
            }
        }
    }
}

# One "parent/child/name|type" entry (lower case) per named block at or below $Node.
# The engine finds widgets by name inside their parent, so both the name and the nesting matter.
function Get-GuiWidgetPaths {
    param([Parameter(Mandatory)]$Node)

    $stack = [System.Collections.Generic.Stack[object]]::new()
    $stack.Push(@($Node, ''))
    while ($stack.Count -gt 0) {
        $item = $stack.Pop()
        $current = $item[0]
        $prefix = $item[1]
        $name = Get-GuiValue -Node $current -Key 'name'
        if ($name) {
            if ($prefix) { $prefix = "$prefix/$name" } else { $prefix = $name }
            ('{0}|{1}' -f $prefix, $current.Key).ToLowerInvariant()
        }
        foreach ($child in $current.Children) {
            if ($null -ne $child.Children) { $stack.Push(@($child, $prefix)) }
        }
    }
}

# Widget paths present in $Baseline but missing from $Actual.
function Compare-GuiWidgetPaths {
    param([Parameter(Mandatory)]$Baseline, [Parameter(Mandatory)]$Actual)

    $have = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($path in (Get-GuiWidgetPaths -Node $Actual)) { [void]$have.Add($path) }

    $reported = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($path in (Get-GuiWidgetPaths -Node $Baseline)) {
        if (-not $have.Contains($path) -and $reported.Add($path)) { $path }
    }
}

# Scroll containers whose scroll_wheel_factor is not a whole number of rows.
function Get-GuiScrollViolations {
    param([Parameter(Mandatory)]$Node)

    foreach ($block in (Get-GuiNodes -Node $Node)) {
        $factor = ConvertTo-GuiNumber (Get-GuiValue -Node $block -Key 'scroll_wheel_factor')
        if ($null -eq $factor) { continue }

        $heights = @(
            foreach ($child in $block.Children) {
                if ($null -eq $child.Children -or $child.Key -ine 'gridBoxType') { continue }
                $height = ConvertTo-GuiNumber (Get-GuiValue -Node (Get-GuiBlock -Node $child -Key 'slotsize') -Key 'height')
                if ($null -ne $height -and $height -gt 0) { $height }
            }
        ) | Sort-Object -Unique
        $heights = @($heights)
        if ($heights.Count -ne 1) { continue }

        if (($factor % $heights[0]) -ne 0) {
            $name = Get-GuiValue -Node $block -Key 'name'
            "line $($block.Line): '$name' has scroll_wheel_factor $factor, not a multiple of the row height $($heights[0])"
        }
    }
}

# size blocks larger than the design target.
function Get-GuiOversizeViolations {
    param([Parameter(Mandatory)]$Node, [int]$MaxWidth = 2560, [int]$MaxHeight = 1440)

    foreach ($block in (Get-GuiNodes -Node $Node)) {
        if ($block.Key -ine 'size') { continue }
        $width = ConvertTo-GuiNumber (Get-GuiValue -Node $block -Key 'width')
        $height = ConvertTo-GuiNumber (Get-GuiValue -Node $block -Key 'height')
        if (($null -ne $width -and $width -gt $MaxWidth) -or ($null -ne $height -and $height -gt $MaxHeight)) {
            "line $($block.Line): size ${width}x${height} exceeds ${MaxWidth}x${MaxHeight}"
        }
    }
}

# Sprites declared in a parsed .gfx file.
function Get-GuiSpriteDeclarations {
    param([Parameter(Mandatory)]$Root)

    foreach ($section in $Root.Children) {
        if ($null -eq $section.Children -or $section.Key -ine 'spriteTypes') { continue }
        foreach ($sprite in $section.Children) {
            if ($null -eq $sprite.Children) { continue }
            $name = Get-GuiValue -Node $sprite -Key 'name'
            if (-not $name) { continue }
            $texture = [string](Get-GuiValue -Node $sprite -Key 'texturefile') -replace '[\\/]+', '/'
            [pscustomobject]@{ Name = $name; Type = $sprite.Key; Texture = $texture; Line = $sprite.Line }
        }
    }
}
