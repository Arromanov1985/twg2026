from pathlib import Path
import argparse
import os
import sys
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"
AUDIO_DIR = BASE_DIR / "audio"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("YANDEX_API_KEY", "").strip()
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "").strip()
VOICE = os.getenv("YANDEX_VOICE", "ermil").strip()
EMOTION = os.getenv("YANDEX_EMOTION", "good").strip()
SPEED = os.getenv("YANDEX_SPEED", "1.0").strip()

URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def synthesize(text: str, output_file: Path) -> None:
    if not API_KEY:
        raise RuntimeError(
            "YANDEX_API_KEY is missing. Copy .env.example to .env and add your API key."
        )

    headers = {"Authorization": f"Api-Key {API_KEY}"}
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

    response = requests.post(URL, headers=headers, data=data, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(
            f"Yandex TTS error {response.status_code}:\n{response.text}"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(response.content)
    print(f"READY: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TWG Lesson 02 Yandex TTS generator")
    parser.add_argument("--slide", type=int, choices=range(1, 7))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    slides = [args.slide] if args.slide else list(range(1, 7))

    for num in slides:
        text_file = TEXT_DIR / f"slide{num:02d}.txt"
        audio_file = AUDIO_DIR / f"slide{num:02d}.mp3"

        if not text_file.exists():
            print(f"TEXT NOT FOUND: {text_file}")
            continue

        if audio_file.exists() and not args.overwrite:
            print(f"SKIP: {audio_file.name} already exists")
            continue

        text = text_file.read_text(encoding="utf-8-sig").strip()
        if not text:
            print(f"EMPTY TEXT: {text_file}")
            continue

        print(f"Generating slide {num}...")
        synthesize(text, audio_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
