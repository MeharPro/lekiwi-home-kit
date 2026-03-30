param(
    [string]$EnvName = "lekiwi-homekit"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Get-CondaExe {
    $candidates = @(
        (Get-Command conda.bat -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        (Get-Command conda -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        "$env:USERPROFILE\miniforge3\condabin\conda.bat",
        "$env:USERPROFILE\Miniforge3\condabin\conda.bat",
        "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat",
        "$env:LOCALAPPDATA\Miniforge3\condabin\conda.bat"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

    if ($candidates) {
        return $candidates[0]
    }

    return $null
}

$CondaExe = Get-CondaExe
if (-not $CondaExe) {
    throw "Conda was not found. Run windows\Setup-Windows.bat first."
}

& $CondaExe run --no-capture-output -n $EnvName python "$RepoRoot\scripts\list_leader_ports.py"
