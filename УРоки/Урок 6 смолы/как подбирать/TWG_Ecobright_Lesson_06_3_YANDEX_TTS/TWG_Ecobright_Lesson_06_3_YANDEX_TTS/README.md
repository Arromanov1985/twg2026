# Урок 6.3 «Подбор оборудования с загрузками Экобрайт» — Yandex TTS

Комплект создаёт `slide01.mp3`–`slide20.mp3` через Yandex SpeechKit.

Настройки по умолчанию:

- голос: `ermil`;
- эмоция: `good`;
- скорость: `1.0`;
- пауза после запятой: `300 мс`;
- формат: `mp3`;
- заголовки `СЛАЙД ...` в озвучку не попадают;
- латинское `TWG` перед синтезом автоматически заменяется на `ТВГ`.

## Быстрый запуск в PowerShell / VS Code

Распакуйте архив, откройте папку проекта в VS Code и выполните:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
notepad .env
```

В `.env` вставьте ваши `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`.

Проверка текстов без обращения к API:

```powershell
python .\synthesize_yandex.py --dry-run
```

Проверка первого слайда:

```powershell
python .\synthesize_yandex.py --only 1 --overwrite
```

Генерация всех 20 слайдов:

```powershell
python .\synthesize_yandex.py --overwrite
```

Или:

```powershell
.\generate_audio.ps1
```

Повторная генерация отдельных слайдов:

```powershell
python .\synthesize_yandex.py --only 13,14 --overwrite
```

После появления всех 20 MP3 в папке `output` автоматически создаётся:

`TWG_Ecobright_Lesson_06_3_AUDIO_20.zip`
