from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"
AUDIO_DIR = BASE_DIR / "audio"
TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def load_settings():
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    voice = os.getenv("YANDEX_VOICE", "ermil").strip()
    emotion = os.getenv("YANDEX_EMOTION", "good").strip()
    speed = os.getenv("YANDEX_SPEED", "1.0").strip()
    audio_format = os.getenv("YANDEX_FORMAT", "mp3").strip()
    lang = os.getenv("YANDEX_LANG", "ru-RU").strip()

    if not api_key:
        raise RuntimeError(
            "YANDEX_API_KEY не заполнен. Скопируйте .env.example в .env "
            "и вставьте API-ключ."
        )

    return {
        "api_key": api_key,
        "folder_id": folder_id,
        "voice": voice,
        "emotion": emotion,
        "speed": speed,
        "format": audio_format,
        "lang": lang,
    }


def get_slide_files(slide: int | None):
    if slide is not None:
        path = TEXT_DIR / f"slide{slide:02d}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Не найден файл: {path}")
        return [path]

    files = sorted(TEXT_DIR.glob("slide*.txt"))
    if not files:
        raise FileNotFoundError(f"В папке {TEXT_DIR} нет файлов slideXX.txt")
    return files


def synthesize(text: str, out_path: Path, settings: dict, timeout: int = 90):
    headers = {
        "Authorization": f"Api-Key {settings['api_key']}",
    }

    data = {
        "text": text,
        "lang": settings["lang"],
        "voice": settings["voice"],
        "speed": settings["speed"],
        "format": settings["format"],
    }

    if settings["emotion"]:
        data["emotion"] = settings["emotion"]

    if settings["folder_id"]:
        data["folderId"] = settings["folder_id"]

    response = requests.post(
        TTS_URL,
        headers=headers,
        data=data,
        timeout=timeout,
    )

    if response.status_code != 200:
        body = response.text[:1200]
        raise RuntimeError(
            f"Yandex SpeechKit вернул HTTP {response.status_code}\n{body}"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(response.content)


def main():
    parser = argparse.ArgumentParser(
        description="Озвучка урока 6 TWG через Yandex SpeechKit"
    )
    parser.add_argument(
        "--slide",
        type=int,
        help="Озвучить только один слайд, например: --slide 1",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписывать существующие mp3",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет озвучено",
    )
    args = parser.parse_args()

    AUDIO_DIR.mkdir(exist_ok=True)
    files = get_slide_files(args.slide)

    if args.dry_run:
        print("Проверка файлов:")
        for f in files:
            text = f.read_text(encoding="utf-8-sig").strip()
            print(f"  {f.name}: {len(text)} символов")
        return

    settings = load_settings()

    print("Настройки:")
    print(f"  voice   = {settings['voice']}")
    print(f"  emotion = {settings['emotion'] or '(не задано)'}")
    print(f"  speed   = {settings['speed']}")
    print(f"  format  = {settings['format']}")
    print()

    for f in files:
        text = f.read_text(encoding="utf-8-sig").strip()
        if not text:
            print(f"[SKIP] {f.name}: пустой текст")
            continue

        out_path = AUDIO_DIR / f"{f.stem}.{settings['format']}"

        if out_path.exists() and not args.overwrite:
            print(f"[SKIP] {out_path.name}: уже существует")
            continue

        print(f"[TTS]  {f.name} -> {out_path.name} ({len(text)} символов)")
        try:
            synthesize(text, out_path, settings)
        except Exception as exc:
            print(f"[ERROR] {f.name}: {exc}", file=sys.stderr)
            sys.exit(1)

        print(f"[OK]   {out_path}")

    print()
    print("Готово.")
    print(f"Аудио: {AUDIO_DIR}")


if __name__ == "__main__":
    main()
