TWG DF — озвучка через VS + Yandex SpeechKit

1. Откройте папку TWG_DF_TTS_VS в Visual Studio Code / VS.
2. Создайте виртуальное окружение:
   python -m venv .venv
3. Активируйте его (PowerShell):
   .\.venv\Scripts\Activate.ps1
4. Установите зависимости:
   pip install -r requirements.txt
5. Скопируйте .env.example в .env и вставьте ключ Yandex Cloud.
6. Запустите:
   python tts_generate.py
   или двойным кликом run_tts.bat

Вход:  input\slide01.txt ... slide20.txt
Выход: output\slide01.mp3 ... slide20.mp3

Текущие настройки:
- голос: ermil
- амплуа: good
- скорость: 1.0
- язык: ru-RU
- формат: mp3
- без SSML

Правило произношения в текстах:
- TWG пишем как ТВГ
- DF пишем как ДФ
