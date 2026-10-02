[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$TtsArgs
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Виртуальное окружение не найдено. Сначала выполните .\setup.ps1"
}

& $Python .\tts_generate.py @TtsArgs
exit $LASTEXITCODE
