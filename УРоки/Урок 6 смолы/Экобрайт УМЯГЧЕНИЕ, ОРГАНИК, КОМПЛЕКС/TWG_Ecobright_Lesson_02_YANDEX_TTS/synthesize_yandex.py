from __future__ import annotations

import argparse
import html
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEXTS_DIR = ROOT / "texts"
OUTPUT_DIR = ROOT / "output"
API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def parse_slide_selection(value: str | None) -> list[int]:
    if not value:
        return list(range(1, 21))
    selected: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start > end:
                start, end = end, start
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    invalid = sorted(number for number in selected if not 1 <= number <= 20)
    if invalid:
        raise ValueError(f"Номера слайдов вне диапазона 1–20: {invalid}")
    return sorted(selected)


def normalize_for_tts(text: str) -> str:
    replacements = {
        "TWG": "ТВГ",
        "Twg": "ТВГ",
        "twg": "ТВГ",
        "ДВБ": "Дэ-вэ-бэ",
        "дВБ": "Дэ-вэ-бэ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def to_ssml(text: str, pause_ms: int) -> str:
    escaped = html.escape(normalize_for_tts(text), quote=False)
    escaped = escaped.replace("\n\n", f'<break time="{max(400, pause_ms)}ms"/>')
    escaped = escaped.replace("\n", " ")
    if pause_ms > 0:
        escaped = escaped.replace(",", f',<break time="{pause_ms}ms"/>')
    return f"<speak>{escaped}</speak>"


def synthesize(
    text: str,
    destination: Path,
    api_key: str,
    folder_id: str,
    voice: str,
    emotion: str,
    speed: float,
    pause_ms: int,
) -> None:
    payload = urllib.parse.urlencode(
        {
            "ssml": to_ssml(text, pause_ms),
            "lang": "ru-RU",
            "voice": voice,
            "emotion": emotion,
            "speed": str(speed),
            "format": "mp3",
            "folderId": folder_id,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            destination.write_bytes(response.read())
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"SpeechKit вернул HTTP {error.code}: {details}") from error


def build_audio_archive() -> Path | None:
    audio_files = [OUTPUT_DIR / f"slide{number:02d}.mp3" for number in range(1, 21)]
    if not all(path.exists() for path in audio_files):
        return None
    archive_path = OUTPUT_DIR / "TWG_Ecobright_Lesson_02_AUDIO_20.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in audio_files:
            archive.write(path, arcname=path.name)
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Озвучка урока 2 через Yandex SpeechKit")
    parser.add_argument("--only", help="Номера слайдов: 1 или 1,3,5 или 11-20")
    parser.add_argument("--overwrite", action="store_true", help="Перезаписать существующие MP3")
    parser.add_argument("--dry-run", action="store_true", help="Проверить тексты без обращения к API")
    args = parser.parse_args()

    load_env(ROOT / ".env")
    try:
        slide_numbers = parse_slide_selection(args.only)
    except ValueError as error:
        parser.error(str(error))

    voice = os.getenv("YA_VOICE", "ermil")
    emotion = os.getenv("YA_EMOTION", "good")
    speed = float(os.getenv("YA_SPEED", "1.0"))
    pause_ms = int(os.getenv("YA_PAUSE_MS", "300"))

    missing_texts = [
        TEXTS_DIR / f"slide{number:02d}.txt"
        for number in slide_numbers
        if not (TEXTS_DIR / f"slide{number:02d}.txt").exists()
    ]
    if missing_texts:
        print("Не найдены тексты:", file=sys.stderr)
        for path in missing_texts:
            print(f"  {path}", file=sys.stderr)
        return 2

    if args.dry_run:
        for number in slide_numbers:
            path = TEXTS_DIR / f"slide{number:02d}.txt"
            text = path.read_text(encoding="utf-8-sig")
            print(
                f"slide{number:02d}: {len(text)} символов, "
                f"SSML {len(to_ssml(text, pause_ms))} символов"
            )
        print(f"Настройки: voice={voice}, emotion={emotion}, speed={speed}, pause={pause_ms} ms")
        return 0

    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    if not api_key or not folder_id:
        print("Заполните YANDEX_API_KEY и YANDEX_FOLDER_ID в файле .env", file=sys.stderr)
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0
    for number in slide_numbers:
        source = TEXTS_DIR / f"slide{number:02d}.txt"
        destination = OUTPUT_DIR / f"slide{number:02d}.mp3"
        if destination.exists() and not args.overwrite:
            print(f"Пропуск {destination.name}: файл уже существует")
            continue
        text = source.read_text(encoding="utf-8-sig")
        print(f"Озвучка slide{number:02d}...", flush=True)
        synthesize(
            text=text,
            destination=destination,
            api_key=api_key,
            folder_id=folder_id,
            voice=voice,
            emotion=emotion,
            speed=speed,
            pause_ms=pause_ms,
        )
        generated += 1
        print(f"Готово: {destination}")

    archive_path = build_audio_archive()
    if archive_path:
        print(f"Архив аудио: {archive_path}")
    else:
        print("Общий архив MP3 будет создан автоматически, когда в output появятся все 20 файлов.")
    print(f"Создано файлов: {generated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
