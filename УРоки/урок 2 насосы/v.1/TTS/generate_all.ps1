$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "TWG Lesson 02 - Yandex TTS PRO" -ForegroundColor Cyan
Write-Host ""

python -m pip install -r ".\requirements.txt"

if (!(Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host ""
    Write-Host ".env created. Add YANDEX_API_KEY and run this script again." -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

python ".\yandex_tts_lesson2.py" --overwrite

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Generation failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "DONE. Audio files are in .\audio" -ForegroundColor Green
Get-ChildItem ".\audio\slide*.mp3"
