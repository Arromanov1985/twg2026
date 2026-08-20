TWG Lesson 05 — AERO-FS — VS Code / Yandex TTS

1. Распаковать архив.
2. Открыть папку в VS Code.
3. В терминале:

Copy-Item ".env.example" ".env" -Force
code ".env"

4. В .env вставить YANDEX_API_KEY и сохранить Ctrl+S.

5. Установить зависимости:
python -m pip install -r ".\requirements.txt"

6. Проверить:
python ".\yandex_tts_aero_fs.py" --dry-run

7. Озвучить только первый слайд:
python ".\yandex_tts_aero_fs.py" --slide 1 --overwrite

8. Прослушать:
Invoke-Item ".\audio\slide01.mp3"

9. Озвучить все 5 слайдов:
python ".\yandex_tts_aero_fs.py" --overwrite
