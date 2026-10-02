from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"
AUDIO_DIR = BASE_DIR / "audio"
TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def settings() -> dict[str, str]:
    load_dotenv(BASE_DIR / ".env")

    cfg = {
        "api_key": os.getenv("YANDEX_API_KEY", "").strip(),
        "folder_id": os.getenv("YANDEX_FOLDER_ID", "").strip(),
        "voice": os.getenv("YANDEX_VOICE", "ermil").strip(),
        "speed": os.getenv("YANDEX_SPEED", "1.0").strip(),
        "format": os.getenv("YANDEX_FORMAT", "mp3").strip(),
        "lang": os.getenv("YANDEX_LANG", "ru-RU").strip(),
        "emotion": os.getenv("YANDEX_EMOTION", "").strip(),
    }

    if not cfg["api_key"]:
        raise RuntimeError(
            "Не заполнен YANDEX_API_KEY. Создайте .env из .env.example "
            "или скопируйте .env из рабочего TTS-kit урока 6."
        )
    return cfg


def slide_number(path: Path) -> int:
    m = re.search(r"slide(\d+)", path.stem, re.I)
    return int(m.group(1)) if m else 9999


def get_files(slide: int | None) -> list[Path]:
    if slide is not None:
        p = TEXT_DIR / f"slide{slide:02d}.txt"
        if not p.exists():
            raise FileNotFoundError(f"Не найден файл {p}")
        return [p]

    files = sorted(TEXT_DIR.glob("slide*.txt"), key=slide_number)
    if not files:
        raise FileNotFoundError(f"В {TEXT_DIR} нет файлов slideXX.txt")
    return files


def synthesize(text: str, output: Path, cfg: dict[str, str]) -> None:
    headers = {"Authorization": f"Api-Key {cfg['api_key']}"}
    data = {
        "text": text,
        "lang": cfg["lang"],
        "voice": cfg["voice"],
        "speed": cfg["speed"],
        "format": cfg["format"],
    }

    if cfg["folder_id"]:
        data["folderId"] = cfg["folder_id"]

    if cfg["emotion"]:
        data["emotion"] = cfg["emotion"]

    r = requests.post(TTS_URL, headers=headers, data=data, timeout=120)

    if r.status_code != 200:
        detail = r.text[:2000]
        raise RuntimeError(
            f"SpeechKit: HTTP {r.status_code}\n{detail}\n\n"
            "Если ошибка связана с emotion, оставьте YANDEX_EMOTION= пустым."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(r.content)

    if output.stat().st_size < 1000:
        raise RuntimeError(
            f"Файл {output.name} получился подозрительно маленьким "
            f"({output.stat().st_size} байт)."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TWG Lesson 07: Yandex SpeechKit TTS"
    )
    parser.add_argument("--slide", type=int, help="Озвучить только один слайд")
    parser.add_argument("--overwrite", action="store_true", help="Перезаписать MP3")
    parser.add_argument("--dry-run", action="store_true", help="Только проверить тексты")
    args = parser.parse_args()

    files = get_files(args.slide)
    AUDIO_DIR.mkdir(exist_ok=True)

    if args.dry_run:
        print(f"Найдено текстов: {len(files)}")
        for p in files:
            text = p.read_text(encoding="utf-8-sig").strip()
            print(f"{p.name}: {len(text)} символов")
        return 0

    cfg = settings()

    print("TWG Lesson 07 / Yandex SpeechKit")
    print(f"Voice : {cfg['voice']}")
    print(f"Speed : {cfg['speed']}")
    print(f"Lang  : {cfg['lang']}")
    print(f"Format: {cfg['format']}")
    print()

    for p in files:
        text = p.read_text(encoding="utf-8-sig").strip()
        if not text:
            print(f"[SKIP] {p.name}: пустой файл")
            continue

        out = AUDIO_DIR / f"{p.stem}.{cfg['format']}"

        if out.exists() and not args.overwrite:
            print(f"[SKIP] {out.name}: уже существует")
            continue

        print(f"[TTS]  {p.name} -> {out.name}")
        try:
            synthesize(text, out, cfg)
        except Exception as exc:
            print(f"[ERROR] {p.name}\n{exc}", file=sys.stderr)
            return 1

        print(f"[OK]   {out.name} ({out.stat().st_size / 1024:.1f} KB)")

    print()
    print(f"Готово. Аудио: {AUDIO_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
