param (
    [Parameter()]
    [String]
    $Version
)

$ret = @()
$isMatch = $false
foreach ($line in Get-Content -Encoding utf8 docs/changelog.md) {
    if ($line -match "## \[(?<version>.+)]") {
        if ($Matches.version -eq ($Version -replace "^v", "")) {
            $isMatch = $true
        }
        elseif ($isMatch) {
            break
        }
        continue
    }
     
    if ($isMatch) {
        $ret += $line
    }
}

if ($ret.Length -eq 0) {
    throw "Version not found: $Version"
}


return ($ret -join "`n").TrimStart()
