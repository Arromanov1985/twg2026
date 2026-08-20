@echo off
python -m pip install -r requirements.txt
python yandex_tts_aero_fs.py --slide 1 --overwrite
pause
