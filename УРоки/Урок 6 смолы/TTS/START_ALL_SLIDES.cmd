@echo off
chcp 65001 >nul
cd /d "%~dp0"
python yandex_tts_lesson06.py --overwrite
pause
