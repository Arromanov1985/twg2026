"""Генерация MP3 по слайдам через Yandex SpeechKit API v1."""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input"
DEFAULT_OUTPUT_DIR = ROOT / "output"
TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def load_env(path: Path) -> None:
    """Загружает простой .env без внешних библиотек."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def parse_slide_spec(value: str | None, available: set[int]) -> list[int]:
    """Преобразует '1,3,7-10' в отсортированный список номеров."""
    if value is None:
        return sorted(available)

    selected: set[int] = set()
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            parts = token.split("-", maxsplit=1)
            try:
                start, end = (int(part.strip()) for part in parts)
            except ValueError as exc:
                raise argparse.ArgumentTypeError(
                    f"Неверный диапазон слайдов: {token!r}"
                ) from exc
            if start > end:
                raise argparse.ArgumentTypeError(
                    f"Начало диапазона больше конца: {token!r}"
                )
            selected.update(range(start, end + 1))
        else:
            try:
                selected.add(int(token))
            except ValueError as exc:
                raise argparse.ArgumentTypeError(
                    f"Неверный номер слайда: {token!r}"
                ) from exc

    if not selected:
        raise argparse.ArgumentTypeError("Не указан ни один слайд.")

    missing = sorted(selected - available)
    if missing:
        raise argparse.ArgumentTypeError(
            "Нет текстовых файлов для слайдов: " + ", ".join(map(str, missing))
        )
    return sorted(selected)


def available_slides(input_dir: Path) -> set[int]:
    slides: set[int] = set()
    for path in input_dir.glob("slide[0-9][0-9].txt"):
        match = re.fullmatch(r"slide(\d{2})\.txt", path.name)
        if match:
            slides.add(int(match.group(1)))
    return slides


def normalize_for_speech(text: str) -> str:
    """Исправляет служебные обозначения перед формированием SSML."""
    replacements = {
        r"\bTWG\b": "ТВГ",
        r"\bDF\b": "ДФ",
    }
    result = text.replace("\ufeff", "").replace("\u00a0", " ")
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r" *\n *", "\n", result)
    return result.strip()


def make_ssml(text: str, comma_pause_ms: int, paragraph_pause_ms: int) -> str:
    """Экранирует текст и добавляет управляемые паузы."""
    normalized = normalize_for_speech(text)
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", normalized) if part.strip()]
    ssml_parts: list[str] = []
    for paragraph in paragraphs:
        paragraph = re.sub(r"\s*\n\s*", " ", paragraph)
        safe = escape(paragraph)
        safe = re.sub(
            r",(?=\s|$)",
            f',<break time="{comma_pause_ms}ms"/>',
            safe,
        )
        ssml_parts.append(safe)
    separator = f'<break time="{paragraph_pause_ms}ms"/>'
    return "<speak>" + separator.join(ssml_parts) + "</speak>"


def auth_headers() -> dict[str, str]:
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    iam_token = os.getenv("YANDEX_IAM_TOKEN", "").strip()
    if api_key:
        return {"Authorization": f"Api-Key {api_key}"}
    if iam_token:
        return {"Authorization": f"Bearer {iam_token}"}
    raise RuntimeError(
        "В .env укажите YANDEX_API_KEY или YANDEX_IAM_TOKEN."
    )


def synthesize(
    *,
    ssml: str,
    output_path: Path,
    voice: str,
    emotion: str,
    speed: str,
    retries: int,
) -> None:
    payload = {
        "ssml": ssml,
        "lang": "ru-RU",
        "voice": voice,
        "emotion": emotion,
        "speed": speed,
        "format": "mp3",
    }
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    if folder_id:
        payload["folderId"] = folder_id

    headers = {
        **auth_headers(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        request = Request(
            TTS_URL,
            data=urlencode(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=120) as response:
                audio = response.read()
        except HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace").strip()[:700]
            last_error = RuntimeError(
                f"SpeechKit вернул HTTP {exc.code}: {message}"
            )
            if exc.code in RETRYABLE_STATUS_CODES and attempt < retries:
                time.sleep(min(2**attempt, 8))
                continue
            raise last_error from exc
        except URLError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 8))
                continue
            raise RuntimeError(f"Ошибка подключения к SpeechKit: {exc}") from exc

        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = output_path.with_suffix(output_path.suffix + ".part")
        temp_path.write_bytes(audio)
        temp_path.replace(output_path)
        return

    raise RuntimeError(str(last_error or "Неизвестная ошибка SpeechKit."))


def iter_jobs(slides: Iterable[int], output_dir: Path) -> Iterable[tuple[int, Path, Path]]:
    for slide in slides:
        yield (
            slide,
            INPUT_DIR / f"slide{slide:02d}.txt",
            output_dir / f"slide{slide:02d}.mp3",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Генерация MP3 для урока 6 «Смолы» через Yandex SpeechKit."
    )
    parser.add_argument(
        "--slides",
        help="Только выбранные слайды: 10 или 4,8,10-12. Без параметра — все.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Папка для MP3 (по умолчанию ./output).",
    )
    parser.add_argument("--voice", default=os.getenv("TTS_VOICE", "ermil"))
    parser.add_argument("--emotion", default=os.getenv("TTS_EMOTION", "good"))
    parser.add_argument("--speed", default=os.getenv("TTS_SPEED", "1.0"))
    parser.add_argument("--comma-pause-ms", type=int, default=300)
    parser.add_argument("--paragraph-pause-ms", type=int, default=700)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Не перезаписывать уже созданные MP3.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать план без обращения к API и без записи MP3.",
    )
    return parser


def main() -> int:
    load_env(ROOT / ".env")
    parser = build_parser()
    args = parser.parse_args()

    available = available_slides(INPUT_DIR)
    if not available:
        parser.error(f"В папке {INPUT_DIR} не найдены файлы slideNN.txt.")
    try:
        slides = parse_slide_spec(args.slides, available)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    jobs = list(iter_jobs(slides, output_dir))
    print("Выбраны слайды:", ", ".join(str(slide) for slide in slides))

    for slide, input_path, output_path in jobs:
        if args.skip_existing and output_path.exists():
            print(f"[{slide:02d}] пропуск: {output_path.name} уже существует")
            continue

        text = input_path.read_text(encoding="utf-8")
        ssml = make_ssml(text, args.comma_pause_ms, args.paragraph_pause_ms)
        if args.dry_run:
            print(f"[{slide:02d}] {input_path.name} -> {output_path.name}; SSML: {len(ssml)} знаков")
            continue

        print(f"[{slide:02d}] синтез...", end=" ", flush=True)
        synthesize(
            ssml=ssml,
            output_path=output_path,
            voice=args.voice,
            emotion=args.emotion,
            speed=str(args.speed),
            retries=args.retries,
        )
        print(f"готово: {output_path.name}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
