from __future__ import annotations

import argparse
import os
import re
import sys
import time
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv


API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
ROOT = Path(__file__).resolve().parent
TEXT_DIR = ROOT / "texts"
OUTPUT_DIR = ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Создаёт MP3 для слайдов 01–20 через Yandex SpeechKit."
    )
    parser.add_argument(
        "--only",
        help="Номера отдельных слайдов: 1,3-5. По умолчанию — все 20.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписать уже созданные MP3.",
    )
    parser.add_argument(
        "--voice",
        help="Голос SpeechKit. По умолчанию берётся YA_VOICE или ermil.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        help="Скорость речи. По умолчанию берётся YA_SPEED или 1.0.",
    )
    return parser.parse_args()


def parse_slide_selection(raw: str | None) -> set[int]:
    if not raw:
        return set(range(1, 21))

    selected: set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_raw, end_raw = token.split("-", 1)
            start, end = int(start_raw), int(end_raw)
            if start > end:
                start, end = end, start
            selected.update(range(start, end + 1))
        else:
            selected.add(int(token))

    invalid = sorted(number for number in selected if number < 1 or number > 20)
    if invalid:
        raise ValueError(f"Допустимы номера слайдов от 1 до 20: {invalid}")
    return selected


def normalize_for_tts(text: str) -> str:
    """Минимальная нормализация без изменения смысла исходного текста."""
    text = re.sub(r"\bTWG\b", "ТВГ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bAERO\b", "АЭРО", text, flags=re.IGNORECASE)
    return re.sub(r"[ \t]+", " ", text).strip()


def synthesize(
    *,
    text: str,
    target: Path,
    api_key: str,
    folder_id: str,
    voice: str,
    speed: float,
) -> None:
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Api-Key {api_key}"},
     data={
    "text": normalize_for_tts(text),
    "lang": "ru-RU",
    "voice": voice,
    "emotion": "good",
    "speed": str(speed),
    "format": "mp3",
    "folderId": folder_id,
},
        timeout=180,
    )

    if not response.ok:
        details = response.text[:1000]
        raise RuntimeError(
            f"SpeechKit вернул HTTP {response.status_code}: {details}"
        )

    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type.lower():
        raise RuntimeError(f"Вместо MP3 получен JSON: {response.text[:1000]}")

    target.write_bytes(response.content)
    if target.stat().st_size < 1000:
        raise RuntimeError(f"Получен слишком маленький файл: {target.name}")


def make_audio_zip() -> Path | None:
    mp3_files = sorted(OUTPUT_DIR.glob("slide[0-9][0-9].mp3"))
    if not mp3_files:
        return None

    zip_path = OUTPUT_DIR / "TWG_AERO_4-6_AUDIO_20.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for mp3_file in mp3_files:
            archive.write(mp3_file, arcname=mp3_file.name)
    return zip_path


def main() -> int:
    load_dotenv(ROOT / ".env")
    args = parse_args()

    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    voice = args.voice or os.getenv("YA_VOICE", "ermil").strip() or "ermil"
    speed = args.speed if args.speed is not None else float(os.getenv("YA_SPEED", "1.0"))

    if not api_key or not folder_id:
        print(
            "Ошибка: заполните YANDEX_API_KEY и YANDEX_FOLDER_ID в файле .env.",
            file=sys.stderr,
        )
        return 2
    if not 0.1 <= speed <= 3.0:
        print("Ошибка: YA_SPEED должна быть от 0.1 до 3.0.", file=sys.stderr)
        return 2

    try:
        selected = parse_slide_selection(args.only)
    except ValueError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    completed = 0
    skipped = 0

    for number in sorted(selected):
        source = TEXT_DIR / f"slide{number:02d}.txt"
        target = OUTPUT_DIR / f"slide{number:02d}.mp3"

        if not source.exists():
            print(f"[ПРОПУСК] Нет файла {source.name}")
            skipped += 1
            continue
        if target.exists() and not args.overwrite:
            print(f"[ГОТОВО] {target.name} уже существует")
            skipped += 1
            continue

        print(f"[СИНТЕЗ] Слайд {number:02d} → {target.name}")
        try:
            synthesize(
                text=source.read_text(encoding="utf-8"),
                target=target,
                api_key=api_key,
                folder_id=folder_id,
                voice=voice,
                speed=speed,
            )
        except Exception as error:
            if target.exists():
                target.unlink()
            print(f"[ОШИБКА] Слайд {number:02d}: {error}", file=sys.stderr)
            return 1

        completed += 1
        time.sleep(0.25)

    zip_path = make_audio_zip()
    print(f"\nСоздано: {completed}. Пропущено: {skipped}.")
    if zip_path:
        print(f"Архив аудио: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
