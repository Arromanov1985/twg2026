from pathlib import Path
import argparse
import os
import requests
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
TEXT_DIR = BASE / "text"
AUDIO_DIR = BASE / "audio"

load_dotenv(BASE / ".env")

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
VOICE = os.getenv("YANDEX_VOICE", "ermil")
EMOTION = os.getenv("YANDEX_EMOTION", "good")
SPEED = os.getenv("YANDEX_SPEED", "1.0")
FORMAT = os.getenv("YANDEX_FORMAT", "mp3")

URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

def synthesize(text: str, out_file: Path):
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

    r = requests.post(URL, headers=headers, data=data, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Yandex TTS error {r.status_code}:\n{r.text}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(r.content)
    print(f"ГОТОВО: {out_file.name} ({len(r.content)/1024:.1f} КБ)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slide", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    nums = [args.slide] if args.slide else list(range(1, 6))

    for n in nums:
        txt = TEXT_DIR / f"slide{n:02d}.txt"
        mp3 = AUDIO_DIR / f"slide{n:02d}.mp3"

        if not txt.exists():
            print(f"Нет текста: {txt.name}")
            continue

        body = txt.read_text(encoding="utf-8").strip()

        if args.dry_run:
            print(f"slide{n:02d}: {len(body)} символов -> {mp3.name}")
            continue

        if mp3.exists() and not args.overwrite:
            print(f"Пропуск: {mp3.name} уже существует")
            continue

        print(f"Озвучиваем slide{n:02d}...")
        synthesize(body, mp3)

if __name__ == "__main__":
    main()
