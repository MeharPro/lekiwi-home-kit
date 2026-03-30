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
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "Miniforge is not installed and winget is unavailable. Install Miniforge3, then run this script again."
    }

    Write-Host "Installing Miniforge3..."
    & winget install --id CondaForge.Miniforge3 -e --accept-package-agreements --accept-source-agreements
    $CondaExe = Get-CondaExe
}

if (-not $CondaExe) {
    throw "Could not find conda after installing Miniforge3."
}

& $CondaExe run --no-capture-output -n $EnvName python --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating conda environment '$EnvName'..."
    & $CondaExe create -y -n $EnvName python=3.12
}

Write-Host "Upgrading pip..."
& $CondaExe run --no-capture-output -n $EnvName python -m pip install --upgrade pip

Write-Host "Installing vendored LeRobot with LEKIWI dependencies..."
& $CondaExe run --no-capture-output -n $EnvName python -m pip install -e "$RepoRoot\vendor\lerobot[lekiwi]"

$CalibrationSrc = Join-Path $RepoRoot "assets\calibration"
$CalibrationDst = Join-Path $env:USERPROFILE ".cache\huggingface\lerobot\calibration"
if (Test-Path $CalibrationSrc) {
    New-Item -ItemType Directory -Force -Path $CalibrationDst | Out-Null
    Copy-Item -Path (Join-Path $CalibrationSrc "*") -Destination $CalibrationDst -Recurse -Force
    Write-Host "Installed bundled calibration files to $CalibrationDst"
}

Write-Host
Write-Host "Setup complete."
Write-Host "Start manual control with:"
Write-Host "  windows\Start-Manual-Control.bat"
Write-Host
Write-Host "Calibrate the leader with:"
Write-Host "  windows\Calibrate-Leader.bat"
