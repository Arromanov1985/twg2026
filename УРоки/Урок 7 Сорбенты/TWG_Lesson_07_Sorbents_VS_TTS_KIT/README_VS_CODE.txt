TWG — Урок 7. Сорбенты
VS Code + Yandex SpeechKit

Папка урока:
C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\Уроки\Урок 7 Сорбенты

ВАЖНО:
Активация .venv не обязательна.
Команды используют напрямую:
C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\.venv\Scripts\python.exe

1. Распакуйте TWG_Lesson_07_Sorbents_VS_TTS_KIT.zip
   в папку урока.

2. Перейдите:
Set-Location "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\Уроки\Урок 7 Сорбенты\TWG_Lesson_07_Sorbents_VS_TTS_KIT"

3. Если урок 6 уже озвучивался, можно скопировать рабочий .env:
Copy-Item "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\Уроки\Урок 6 смолы\TWG_Lesson_06_Ion_Exchange_Resins_VS_TTS_KIT\.env" ".\.env" -Force

Или:
Copy-Item ".env.example" ".env" -Force
code ".env"

4. Установить зависимости:
$py = "C:\Users\user6\Desktop\ОБУЧЕНИЕ TWG\.venv\Scripts\python.exe"
& $py -m pip install -r ".\requirements.txt"

5. Проверка:
& $py ".\yandex_tts_lesson07.py" --dry-run

6. Первый слайд:
& $py ".\yandex_tts_lesson07.py" --slide 1 --overwrite

7. Прослушать:
Invoke-Item ".\audio\slide01.mp3"

8. Все слайды:
& $py ".\yandex_tts_lesson07.py" --overwrite

Результат:
audio\slide01.mp3 ... audio\slide18.mp3
