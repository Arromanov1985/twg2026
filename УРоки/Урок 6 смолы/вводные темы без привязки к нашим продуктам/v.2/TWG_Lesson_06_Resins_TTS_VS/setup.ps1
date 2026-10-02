$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -m venv .venv
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python -m venv .venv
} else {
    throw "Python не найден. Установите Python 3.10 или новее."
}

& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt

if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
    Write-Host "Создан файл .env. Вставьте в него ключ Yandex SpeechKit."
} else {
    Write-Host "Файл .env уже существует и не был изменён."
}

Write-Host "Готово. Откройте .env, добавьте ключ и запустите .\run_tts.ps1"
