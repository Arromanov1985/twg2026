$root = "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG"
$lesson = Join-Path $root "Уроки\Урок 7 Сорбенты"
$kit = Join-Path $lesson "TWG_Lesson_07_Sorbents_VS_TTS_KIT"
$python = Join-Path $root ".venv\Scripts\python.exe"

Set-Location $kit

if (-not (Test-Path $python)) {
    Write-Host "Виртуальное окружение не найдено. Создаю .venv..." -ForegroundColor Yellow
    py -m venv (Join-Path $root ".venv")
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Создан .env. Заполните YANDEX_API_KEY." -ForegroundColor Yellow
}

& $python -m pip install -r ".\requirements.txt"

Write-Host ""
Write-Host "Проверка текстов:" -ForegroundColor Cyan
& $python ".\yandex_tts_lesson07.py" --dry-run

Write-Host ""
Write-Host "Для теста первого слайда:" -ForegroundColor Green
Write-Host '& $python ".\yandex_tts_lesson07.py" --slide 1 --overwrite'
Write-Host ""
Write-Host "Для всех 18 слайдов:" -ForegroundColor Green
Write-Host '& $python ".\yandex_tts_lesson07.py" --overwrite'
