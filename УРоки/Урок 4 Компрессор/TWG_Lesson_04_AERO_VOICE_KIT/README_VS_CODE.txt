TWG Lesson 04 — AERO 4-6 Voice Kit

Содержимое:
- text/slide01.txt ... slide06.txt
- yandex_tts_aero.py
- .env.example
- requirements.txt
- START_TEST_SLIDE01.cmd
- START_ALL_SLIDES.cmd
- pronunciation_dictionary.md
- audio/ — сюда будут сохранены MP3

Быстрый запуск в VS Code / PowerShell:

1) Создать настройки:
   Copy-Item ".env.example" ".env" -Force

2) Открыть .env:
   code ".env"

3) Вставить API-ключ Yandex Cloud:
   YANDEX_API_KEY=ВАШ_КЛЮЧ

4) Установить зависимости:
   python -m pip install -r ".\requirements.txt"

5) Проверить конфигурацию:
   python ".\yandex_tts_aero.py" --dry-run

6) Сгенерировать первый слайд:
   python ".\yandex_tts_aero.py" --slide 1 --overwrite

7) Сгенерировать все 6 слайдов:
   python ".\yandex_tts_aero.py" --overwrite

8) Прослушать:
   Invoke-Item ".\audio\slide01.mp3"
