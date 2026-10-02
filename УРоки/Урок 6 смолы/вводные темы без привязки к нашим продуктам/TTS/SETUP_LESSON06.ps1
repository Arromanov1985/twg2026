$lesson = "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\УРоки\Урок 6 смолы"

Set-Location $lesson

$kit = Join-Path $lesson "TWG_Lesson_06_Ion_Exchange_Resins_VS_TTS_KIT"

if (-not (Test-Path $kit)) {
    Write-Host "Папка TTS KIT не найдена:" -ForegroundColor Yellow
    Write-Host $kit
    Write-Host ""
    Write-Host "Сначала распакуйте TWG_Lesson_06_Ion_Exchange_Resins_VS_TTS_KIT.zip в папку урока."
    exit 1
}

Set-Location $kit

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env создан из .env.example" -ForegroundColor Green
}

python -m pip install -r ".\requirements.txt"

Write-Host ""
Write-Host "Папка готова:" -ForegroundColor Green
Get-Location
Write-Host ""
Write-Host "1) Откройте .env и вставьте YANDEX_API_KEY"
Write-Host "2) Тест: python .\yandex_tts_lesson06.py --slide 1 --overwrite"
Write-Host "3) Все слайды: python .\yandex_tts_lesson06.py --overwrite"
