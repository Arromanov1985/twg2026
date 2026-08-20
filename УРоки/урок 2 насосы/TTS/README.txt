TWG Lesson 02 — Yandex TTS PRO kit

Структура:
text/slide01.txt ... slide06.txt
audio/
yandex_tts_lesson2.py
generate_all.ps1
requirements.txt
.env.example
pronunciation_dictionary_twg.txt

БЫСТРЫЙ ЗАПУСК

1. Распакуйте архив в отдельную папку, например:
   Уроки\урок 2\TTS

2. Откройте эту папку в VS Code.

3. В PowerShell:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\generate_all.ps1

4. При первом запуске будет создан файл .env.
   Откройте его и вставьте YANDEX_API_KEY.

5. Снова:
   .\generate_all.ps1

Готовые файлы:
audio\slide01.mp3
audio\slide02.mp3
audio\slide03.mp3
audio\slide04.mp3
audio\slide05.mp3
audio\slide06.mp3

Сгенерировать только один слайд:
python .\yandex_tts_lesson2.py --slide 3 --overwrite

Сгенерировать все слайды:
python .\yandex_tts_lesson2.py --overwrite

Важно:
- Внутри Python-скрипта используются только папки text и audio.
- Русских путей в коде нет.
- Тексты читаются как UTF-8-SIG/UTF-8, чтобы избежать проблем с кодировкой PowerShell.
