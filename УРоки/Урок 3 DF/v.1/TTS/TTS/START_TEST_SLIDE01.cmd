@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_twg_df_tts.ps1" --slide 1 --overwrite
pause
