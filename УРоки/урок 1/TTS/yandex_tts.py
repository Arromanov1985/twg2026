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

URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def synthesize(text: str, output_file: Path):

    if not API_KEY:
        raise RuntimeError("В .env не указан YANDEX_API_KEY")

    headers = {
        "Authorization": f"Api-Key {API_KEY}"
    }

    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": VOICE,
        "emotion": EMOTION,
        "speed": SPEED,
        "format": "mp3",
    }

    if FOLDER_ID:
        data["folderId"] = FOLDER_ID

    response = requests.post(
        URL,
        headers=headers,
        data=data,
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ошибка Yandex TTS: {response.status_code}\n"
            f"{response.text}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file.write_bytes(response.content)

    print(f"Готово: {output_file}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--slide",
        type=int
    )

    parser.add_argument(
        "--overwrite",
        action="store_true"
    )

    args = parser.parse_args()

    if args.slide:
        slides = [args.slide]
    else:
        slides = [1, 2, 3]

    for num in slides:

        text_file = TEXT_DIR / f"slide{num:02d}.txt"
        audio_file = AUDIO_DIR / f"slide{num:02d}.mp3"

        if not text_file.exists():
            print(f"Нет файла текста: {text_file}")
            continue

        if audio_file.exists() and not args.overwrite:
            print(
                f"Пропуск: {audio_file.name} уже существует"
            )
            continue

        text = text_file.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            print(f"Пустой файл: {text_file}")
            continue

        print(f"Озвучиваем слайд {num}...")

        synthesize(
            text,
            audio_file
        )


if __name__ == "__main__":
    main()