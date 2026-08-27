from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def build_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()
    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}
    raise RuntimeError(
        "Не задана авторизация. Укажите YANDEX_API_KEY или YANDEX_IAM_TOKEN в .env"
    )


def synthesize(text: str, out_file: Path) -> None:
    headers = build_headers()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    voice = os.getenv("TTS_VOICE", "ermil").strip() or "ermil"
    emotion = os.getenv("TTS_EMOTION", "good").strip() or "good"
    speed = os.getenv("TTS_SPEED", "1.0").strip() or "1.0"
    audio_format = os.getenv("TTS_FORMAT", "mp3").strip().lower() or "mp3"

    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": speed,
        "format": audio_format,
    }
    if folder_id:
        data["folderId"] = folder_id

    r = requests.post(API_URL, headers=headers, data=data, timeout=120)
    if not r.ok:
        detail = r.text[:1500]
        raise RuntimeError(f"SpeechKit HTTP {r.status_code}: {detail}")

    out_file.write_bytes(r.content)


def main() -> int:
    load_dotenv()

    base = Path(__file__).resolve().parent
    input_dir = base / "input"
    output_dir = base / "output"
    output_dir.mkdir(exist_ok=True)

    audio_format = os.getenv("TTS_FORMAT", "mp3").strip().lower() or "mp3"
    files = sorted(input_dir.glob("slide*.txt"))
    if not files:
        print("В папке input нет файлов slide*.txt")
        return 1

    print(f"Найдено файлов: {len(files)}")
    print(
        "Параметры: "
        f"voice={os.getenv('TTS_VOICE', 'ermil')}, "
        f"emotion={os.getenv('TTS_EMOTION', 'good')}, "
        f"speed={os.getenv('TTS_SPEED', '1.0')}, "
        f"format={audio_format}"
    )

    for idx, txt_file in enumerate(files, start=1):
        text = txt_file.read_text(encoding="utf-8").strip()
        if not text:
            print(f"[{idx:02d}/{len(files):02d}] {txt_file.name}: пустой файл, пропуск")
            continue
        if len(text) > 5000:
            raise RuntimeError(f"{txt_file.name}: текст длиннее 5000 символов")

        out_file = output_dir / f"{txt_file.stem}.{audio_format}"
        print(f"[{idx:02d}/{len(files):02d}] {txt_file.name} -> {out_file.name}")
        synthesize(text, out_file)
        time.sleep(0.15)

    print(f"Готово. Аудио: {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Остановлено пользователем")
        raise SystemExit(130)
    except Exception as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        raise SystemExit(1)
