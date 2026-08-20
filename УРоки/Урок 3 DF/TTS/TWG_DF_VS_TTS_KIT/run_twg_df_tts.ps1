param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$TtsArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"

$VenvDir = Join-Path $ScriptDir ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$EnvFile = Join-Path $ScriptDir ".env"
$EnvExample = Join-Path $ScriptDir ".env.example"

if (!(Test-Path $PythonExe)) {
    Write-Host "Создаю виртуальное окружение .venv..." -ForegroundColor Cyan
    py -m venv $VenvDir
}

if (!(Test-Path $PythonExe)) {
    throw "Не удалось создать .venv. Проверьте, что Python установлен и команда py доступна."
}

Write-Host "Проверяю зависимости..." -ForegroundColor Cyan
& $PythonExe -c "import requests, dotenv" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r (Join-Path $ScriptDir "requirements.txt")
}

if (!(Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "" 
    Write-Host "Создан файл .env." -ForegroundColor Yellow
    Write-Host "Откройте .env в VS Code, вставьте YANDEX_API_KEY и сохраните файл." -ForegroundColor Yellow
    Write-Host "После этого повторите запуск." -ForegroundColor Yellow
    exit 2
}

& $PythonExe (Join-Path $ScriptDir "yandex_tts_df.py") @TtsArgs
exit $LASTEXITCODE
