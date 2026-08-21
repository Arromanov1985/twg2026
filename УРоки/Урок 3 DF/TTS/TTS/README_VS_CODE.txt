TWG DF — ГЕНЕРАЦИЯ ОЗВУЧКИ В VS CODE

В архиве уже находятся:
- 7 готовых текстов: text\slide01.txt ... text\slide07.txt
- генератор yandex_tts_df.py
- автоматические скрипты запуска
- файл настроек .env.example

БЫСТРЫЙ СПОСОБ

1. Распакуйте архив в отдельную папку.
2. Откройте именно эту папку в VS Code: File -> Open Folder.
3. В терминале PowerShell выполните:

   Copy-Item .env.example .env

4. Откройте .env и вставьте ключ:

   YANDEX_API_KEY=ВАШ_API_КЛЮЧ

   Остальные настройки уже заполнены:
   YANDEX_VOICE=ermil
   YANDEX_EMOTION=good
   YANDEX_SPEED=1.0
   YANDEX_FORMAT=mp3

5. Проверка первого слайда:

   .\START_TEST_SLIDE01.cmd

6. Генерация всех семи слайдов:

   .\START_ALL_SLIDES.cmd

Скрипты сами создадут .venv и установят зависимости. Активировать виртуальное
окружение не требуется. Execution Policy менять вручную тоже не требуется.

ГОТОВЫЕ ФАЙЛЫ

audio\slide01.mp3
audio\slide02.mp3
audio\slide03.mp3
audio\slide04.mp3
audio\slide05.mp3
audio\slide06.mp3
audio\slide07.mp3

РУЧНЫЕ КОМАНДЫ В ТЕРМИНАЛЕ VS CODE

Создать окружение:

   py -m venv .venv

Установить зависимости без активации окружения:

   .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Создать .env:

   Copy-Item .env.example .env

Проверить тексты и настройки без генерации:

   .\.venv\Scripts\python.exe .\yandex_tts_df.py --dry-run

Сгенерировать только первый слайд:

   .\.venv\Scripts\python.exe .\yandex_tts_df.py --slide 1 --overwrite

Сгенерировать все слайды:

   .\.venv\Scripts\python.exe .\yandex_tts_df.py --overwrite

Показать доступные слайды:

   .\.venv\Scripts\python.exe .\yandex_tts_df.py --list

ВАЖНО
- Не публикуйте файл .env и не отправляйте API-ключ другим людям.
- Тексты сохранены в UTF-8 и уже адаптированы под дикторское произношение.
- Если MP3 уже существует, без --overwrite он будет пропущен.
- Для проверки сначала всегда генерируйте slide01.mp3.
