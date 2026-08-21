TWG LESSON 06 — ИОНООБМЕННЫЕ СМОЛЫ
Yandex SpeechKit / VS Code

ПАПКА УРОКА:
C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\УРоки\Урок 6 смолы

1. Распакуйте архив TWG_Lesson_06_Ion_Exchange_Resins_VS_TTS_KIT.zip
   прямо в папку:
   C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\УРоки\Урок 6 смолы

2. В терминале VS Code:
   Set-Location "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\УРоки\Урок 6 смолы\TWG_Lesson_06_Ion_Exchange_Resins_VS_TTS_KIT"

3. Создайте .env:
   Copy-Item ".env.example" ".env" -Force
   code ".env"

4. В .env вставьте:
   YANDEX_API_KEY=ВАШ_КЛЮЧ

   Остальные параметры уже настроены:
   YANDEX_VOICE=ermil
   YANDEX_EMOTION=good
   YANDEX_SPEED=1.0
   YANDEX_FORMAT=mp3
   YANDEX_LANG=ru-RU

5. Установите зависимости:
   python -m pip install -r ".\requirements.txt"

6. Проверка текстов без отправки в SpeechKit:
   python ".\yandex_tts_lesson06.py" --dry-run

7. Тест первого слайда:
   python ".\yandex_tts_lesson06.py" --slide 1 --overwrite

8. Прослушать:
   Invoke-Item ".\audio\slide01.mp3"

9. Озвучить все 11 слайдов:
   python ".\yandex_tts_lesson06.py" --overwrite

ГОТОВЫЕ MP3:
.\audio\slide01.mp3
...
.\audio\slide11.mp3

Если Yandex вернет ошибку по emotion:
в .env можно временно оставить:
YANDEX_EMOTION=

Если API использует Folder ID, заполните:
YANDEX_FOLDER_ID=...
