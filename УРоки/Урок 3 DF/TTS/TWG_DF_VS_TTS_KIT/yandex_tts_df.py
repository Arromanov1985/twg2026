from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"
AUDIO_DIR = BASE_DIR / "audio"
ENV_FILE = BASE_DIR / ".env"

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
MAX_TEXT_CHARS = 5000
MAX_BODY_BYTES = 15 * 1024
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
SLIDE_PATTERN = re.compile(r"^slide(\d{2})\.txt$", re.IGNORECASE)


def load_settings() -> dict[str, str]:
    load_dotenv(ENV_FILE)

    settings = {
        "api_key": os.getenv("YANDEX_API_KEY", "").strip(),
        "iam_token": os.getenv("YANDEX_IAM_TOKEN", "").strip(),
        "folder_id": os.getenv("YANDEX_FOLDER_ID", "").strip(),
        "voice": os.getenv("YANDEX_VOICE", "ermil").strip() or "ermil",
        "emotion": os.getenv("YANDEX_EMOTION", "good").strip(),
        "speed": os.getenv("YANDEX_SPEED", "1.0").strip() or "1.0",
        "format": os.getenv("YANDEX_FORMAT", "mp3").strip().lower() or "mp3",
    }

    if not settings["api_key"] and not settings["iam_token"]:
        raise RuntimeError(
            "В файле .env не указан YANDEX_API_KEY или YANDEX_IAM_TOKEN."
        )

    try:
        speed = float(settings["speed"])
    except ValueError as exc:
        raise RuntimeError("YANDEX_SPEED должен быть числом, например 1.0.") from exc

    if not 0.1 <= speed <= 3.0:
        raise RuntimeError("YANDEX_SPEED должен находиться в диапазоне от 0.1 до 3.0.")

    if settings["format"] not in {"mp3", "oggopus", "lpcm"}:
        raise RuntimeError("YANDEX_FORMAT должен быть mp3, oggopus или lpcm.")

    return settings


def authorization_headers(settings: dict[str, str]) -> dict[str, str]:
    if settings["api_key"]:
        return {"Authorization": f"Api-Key {settings['api_key']}"}
    return {"Authorization": f"Bearer {settings['iam_token']}"}


def discover_slides() -> list[int]:
    slides: list[int] = []
    for path in TEXT_DIR.glob("slide*.txt"):
        match = SLIDE_PATTERN.match(path.name)
        if match:
            slides.append(int(match.group(1)))
    return sorted(set(slides))


def select_slides(requested_slide: int | None) -> list[int]:
    available = discover_slides()
    if not available:
        raise RuntimeError(f"В папке {TEXT_DIR} нет файлов slideXX.txt.")

    if requested_slide is None:
        return available

    if requested_slide not in available:
        raise RuntimeError(
            f"Файл slide{requested_slide:02d}.txt не найден. "
            f"Доступные слайды: {', '.join(str(n) for n in available)}."
        )
    return [requested_slide]


def validate_text(text: str, data: dict[str, str], source: Path) -> None:
    if not text:
        raise RuntimeError(f"Файл текста пустой: {source}")

    if len(text) > MAX_TEXT_CHARS:
        raise RuntimeError(
            f"{source.name}: {len(text)} символов. "
            f"Лимит одного запроса — {MAX_TEXT_CHARS} символов."
        )

    body_size = len(urlencode(data).encode("utf-8"))
    if body_size > MAX_BODY_BYTES:
        raise RuntimeError(
            f"{source.name}: размер POST-запроса {body_size} байт превышает "
            f"лимит {MAX_BODY_BYTES} байт."
        )


def request_audio(
    session: requests.Session,
    text: str,
    settings: dict[str, str],
    retries: int = 3,
) -> bytes:
    data: dict[str, str] = {
        "text": text,
        "lang": "ru-RU",
        "voice": settings["voice"],
        "speed": settings["speed"],
        "format": settings["format"],
    }

    if settings["emotion"]:
        data["emotion"] = settings["emotion"]
    if settings["folder_id"]:
        data["folderId"] = settings["folder_id"]

    validate_text(text, data, Path("text"))
    headers = authorization_headers(settings)

    last_error: str | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.post(
                API_URL,
                headers=headers,
                data=data,
                timeout=(20, 180),
            )
        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
                continue
            raise RuntimeError(f"Сетевая ошибка Yandex SpeechKit: {exc}") from exc

        if response.status_code == 200:
            if not response.content:
                raise RuntimeError("SpeechKit вернул пустой аудиофайл.")
            return response.content

        message = response.text.strip()
        if len(message) > 1000:
            message = message[:1000] + "…"
        last_error = f"HTTP {response.status_code}: {message}"

        if response.status_code in TRANSIENT_HTTP_CODES and attempt < retries:
            time.sleep(2 ** (attempt - 1))
            continue

        raise RuntimeError(f"Ошибка Yandex SpeechKit: {last_error}")

    raise RuntimeError(f"Не удалось получить аудио: {last_error or 'неизвестная ошибка'}")


def output_extension(settings: dict[str, str]) -> str:
    return {
        "mp3": ".mp3",
        "oggopus": ".ogg",
        "lpcm": ".lpcm",
    }[settings["format"]]


def synthesize_slide(
    slide: int,
    settings: dict[str, str],
    session: requests.Session,
    overwrite: bool,
    dry_run: bool,
) -> None:
    text_file = TEXT_DIR / f"slide{slide:02d}.txt"
    audio_file = AUDIO_DIR / f"slide{slide:02d}{output_extension(settings)}"

    text = text_file.read_text(encoding="utf-8-sig").strip()

    data_for_validation: dict[str, str] = {
        "text": text,
        "lang": "ru-RU",
        "voice": settings["voice"],
        "speed": settings["speed"],
        "format": settings["format"],
    }
    if settings["emotion"]:
        data_for_validation["emotion"] = settings["emotion"]
    if settings["folder_id"]:
        data_for_validation["folderId"] = settings["folder_id"]
    validate_text(text, data_for_validation, text_file)

    if audio_file.exists() and not overwrite:
        print(f"ПРОПУСК: {audio_file.name} уже существует. Используйте --overwrite.")
        return

    print(
        f"Слайд {slide:02d}: {len(text)} символов -> {audio_file.name} "
        f"[voice={settings['voice']}, emotion={settings['emotion'] or '-'}, "
        f"speed={settings['speed']}]"
    )

    if dry_run:
        return

    audio = request_audio(session, text, settings)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = audio_file.with_suffix(audio_file.suffix + ".part")
    temp_file.write_bytes(audio)
    temp_file.replace(audio_file)

    size_kb = audio_file.stat().st_size / 1024
    if size_kb < 1:
        raise RuntimeError(f"Получен подозрительно маленький файл: {audio_file}")
    print(f"ГОТОВО: {audio_file.name}, {size_kb:.1f} КБ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генерация озвучки Урока TWG DF через Yandex SpeechKit API v1."
    )
    parser.add_argument(
        "--slide",
        type=int,
        help="Сгенерировать только один слайд, например --slide 1.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписать существующие аудиофайлы.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Проверить настройки и тексты без обращения к API.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать доступные слайды и завершить работу.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list:
        slides = discover_slides()
        print("Доступные слайды:", ", ".join(f"{n:02d}" for n in slides) or "нет")
        return 0

    settings = load_settings()
    slides = select_slides(args.slide)

    print("TWG DF — генератор озвучки")
    print(f"Тексты: {TEXT_DIR}")
    print(f"Аудио:  {AUDIO_DIR}")
    print(f"Слайды: {', '.join(f'{n:02d}' for n in slides)}")
    print()

    with requests.Session() as session:
        for slide in slides:
            synthesize_slide(
                slide=slide,
                settings=settings,
                session=session,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )

    print()
    if args.dry_run:
        print("ПРОВЕРКА ЗАВЕРШЕНА: запросы к API не отправлялись.")
    else:
        print("ВСЕ ГОТОВО. Файлы находятся в папке audio.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nОперация отменена пользователем.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"\nОШИБКА: {exc}", file=sys.stderr)
        raise SystemExit(1)
