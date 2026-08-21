TWG Lesson 1 — TTS update v2

Исправление произношения:
BB20 PRO -> «би би двадцать серии пр+о»
Знак + ставит ударение на О для Yandex SpeechKit.

Также:
TWG DF -> «ти дабл ю джи, ди эф»
DF-034 -> номер 034 в озвучке Урока 1 не произносится.

Куда положить:
Файл update_twg_lesson1_PRO_v2.ps1 положить в папку TTS рядом с yandex_tts.py.

Запуск:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\update_twg_lesson1_PRO_v2.ps1

Скрипт обновит:
text\slide01.txt
text\slide03.txt

И перегенерирует:
audio\slide01.mp3
audio\slide03.mp3

slide02.mp3 не изменяется.
