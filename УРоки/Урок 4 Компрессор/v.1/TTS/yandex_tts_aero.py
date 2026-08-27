from pathlib import Path
import os
import argparse
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"
AUDIO_DIR = BASE_DIR / "audio"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
VOICE = os.getenv("YANDEX_VOICE", "ermil")
EMOTION = os.getenv("YANDEX_EMOTION", "good")
SPEED = os.getenv("YANDEX_SPEED", "1.0")
FORMAT = os.getenv("YANDEX_FORMAT", "mp3")

URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

def synthesize(text: str, output_file: Path):
    if not API_KEY:
        raise RuntimeError("В .env не указан YANDEX_API_KEY")

    headers = {"Authorization": f"Api-Key {API_KEY}"}
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": VOICE,
        "emotion": EMOTION,
        "speed": SPEED,
        "format": FORMAT,
    }

    if FOLDER_ID:
        data["folderId"] = FOLDER_ID

    response = requests.post(URL, headers=headers, data=data, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(
            f"Ошибка Yandex TTS: {response.status_code}\n{response.text}"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(response.content)
    print(f"ГОТОВО: {output_file.name}, {len(response.content)/1024:.1f} КБ")

def main():
    parser = argparse.ArgumentParser(description="TWG AERO 4-6 voice generator")
    parser.add_argument("--slide", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    slides = [args.slide] if args.slide else list(range(1, 7))

    for num in slides:
        text_file = TEXT_DIR / f"slide{num:02d}.txt"
        audio_file = AUDIO_DIR / f"slide{num:02d}.mp3"

        if not text_file.exists():
            print(f"Нет файла текста: {text_file}")
            continue

        text = text_file.read_text(encoding="utf-8").strip()

        if args.dry_run:
            print(f"Слайд {num:02d}: {len(text)} символов -> {audio_file.name}")
            continue

        if audio_file.exists() and not args.overwrite:
            print(f"Пропуск: {audio_file.name} уже существует")
            continue

        print(f"Озвучиваем слайд {num:02d}...")
        synthesize(text, audio_file)

    print("\nВСЕ ГОТОВО. Файлы находятся в папке audio.")

if __name__ == "__main__":
    main()
