param(
    [string]$Only = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Создан файл .env. Заполните YANDEX_API_KEY и YANDEX_FOLDER_ID, затем повторите команду." -ForegroundColor Yellow
    exit 1
}

if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonCommand = ".\.venv\Scripts\python.exe"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = "python"
} else {
    throw "Python не найден. Установите Python и повторите запуск."
}

$arguments = @(".\synthesize_yandex.py", "--overwrite")
if ($Only.Trim()) {
    $arguments += @("--only", $Only.Trim())
}

& $pythonCommand @arguments
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
