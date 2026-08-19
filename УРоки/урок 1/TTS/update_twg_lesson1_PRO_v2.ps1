# TWG Lesson 1 - pronunciation update v2
# Fixes BB20 PRO pronunciation using Yandex stress markup: пр+о

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$textDir = Join-Path $ScriptDir "text"
$audioDir = Join-Path $ScriptDir "audio"
$ttsScript = Join-Path $ScriptDir "yandex_tts.py"

if (!(Test-Path $textDir)) {
    New-Item -ItemType Directory -Path $textDir -Force | Out-Null
}

if (!(Test-Path $audioDir)) {
    New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
}

if (!(Test-Path $ttsScript)) {
    Write-Host ""
    Write-Host "ERROR: yandex_tts.py not found in this TTS folder." -ForegroundColor Red
    Write-Host "Place update_twg_lesson1_PRO_v2.ps1 next to yandex_tts.py." -ForegroundColor Yellow
    exit 1
}

$slide01 = @'
Посмотрите на схему целиком. Вода проходит несколько последовательных этапов — от источника до потребителя. Сначала источник даёт воду системе. Затем насос создаёт необходимый поток и давление. После этого дисковый фильтр Ти дабл ю джи, ди эф, задерживает механические примеси и защищает оборудование. Основная водоподготовка решает задачи, связанные с составом воды. Би би двадцать серии пр+о выполняет финишную механическую доочистку. И только после этого подготовленная вода поступает к потребителю. Главное — воспринимать эту цепочку как одну систему, а не как набор отдельных устройств.
'@

$slide03 = @'
Подведём итог. Система водоснабжения начинается с источника, затем насос создаёт поток и давление, ди эф выполняет предварительную механическую очистку, основная водоподготовка удаляет основные загрязнения, а би би двадцать серии пр+о завершает механическую доочистку. Каждый узел выполняет свою функцию и одновременно влияет на всю систему. Пока мы не разбираем загрузки, аэрацию, управляющие клапаны и подбор колонн. Главная мысль урока простая: правильная водоподготовка начинается с понимания всего пути воды — от источника до потребителя.
'@

$slide01Path = Join-Path $textDir "slide01.txt"
$slide03Path = Join-Path $textDir "slide03.txt"

$slide01 | Set-Content -Path $slide01Path -Encoding utf8
$slide03 | Set-Content -Path $slide03Path -Encoding utf8

Write-Host ""
Write-Host "Texts updated." -ForegroundColor Green
Write-Host "Pronunciation rules:" -ForegroundColor Cyan
Write-Host "  BB20 PRO -> би би двадцать серии пр+о"
Write-Host "  TWG DF   -> ти дабл ю джи, ди эф"
Write-Host "  DF-034   -> model number is not spoken in Lesson 1"

Write-Host ""
Write-Host "Generating slide01.mp3..." -ForegroundColor Cyan
python $ttsScript --slide 1 --overwrite
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Generating slide03.mp3..." -ForegroundColor Cyan
python $ttsScript --slide 3 --overwrite
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "DONE." -ForegroundColor Green
Write-Host "Updated audio:"
Write-Host "  audio\slide01.mp3"
Write-Host "  audio\slide03.mp3"
Write-Host ""
Write-Host "slide02.mp3 was not changed."
