# Урок 2 «Линейка смол Экобрайт» — Yandex TTS

Комплект создаёт `slide01.mp3`–`slide20.mp3` через Yandex SpeechKit.

Настройки по умолчанию:

- голос: `ermil`;
- эмоция: `good`;
- скорость: `1.0`;
- пауза после каждой запятой: `300 мс`;
- формат: `mp3`;
- латинское `TWG` перед синтезом автоматически заменяется на `ТВГ`.

## Подготовка в PowerShell VS Code

Перейдите в распакованную папку комплекта и выполните:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

В `.env` укажите реальные значения `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`.
Скрипт использует только стандартную библиотеку Python; внешние пакеты не требуются.

## Проверка без расходования средств

```powershell
python .\synthesize_yandex.py --dry-run
```

## Проверка первого слайда

```powershell
python .\synthesize_yandex.py --only 1 --overwrite
```

## Озвучка всех 20 слайдов

```powershell
python .\synthesize_yandex.py --overwrite
```

Или короткой командой, которая сама перейдёт в нужную папку:

```powershell
.\generate_audio.ps1
```

## Повторная озвучка отдельных слайдов

```powershell
python .\synthesize_yandex.py --only 13,14 --overwrite
```

Короткая команда для выбранных слайдов:

```powershell
.\generate_audio.ps1 -Only "13,14"
```

Готовые файлы появятся в папке `output`. После создания всех двадцати MP3 скрипт автоматически сформирует архив `TWG_Ecobright_Lesson_02_AUDIO_20.zip`.
