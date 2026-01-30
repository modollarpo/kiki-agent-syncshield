@echo off
REM setup_syncmultimodal_checkffmpeg.bat
REM Checks for ffmpeg.exe in bin directory, sets FFMPEG_BINARY env var, updates PATH, and runs SyncMulti-Modal workflow

REM Set ffmpeg bin directory explicitly
set "FFMPEG_BIN=C:\xampp\htdocs\kiki_agent\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"
set "FFMPEG_EXE=%FFMPEG_BIN%\ffmpeg.exe"
if not exist "%FFMPEG_EXE%" (
    echo ffmpeg.exe not found in %FFMPEG_BIN%. Please run setup_ffmpeg.ps1 first.
    exit /b 1
) else (
    echo ffmpeg.exe found in %FFMPEG_BIN%
    set "PATH=%FFMPEG_BIN%;%PATH%"
    set "FFMPEG_BINARY=%FFMPEG_EXE%"
)

REM Start FastAPI service in foreground so env vars are inherited
start "SyncMultiModalAPI" /WAIT C:\xampp\htdocs\kiki_agent\.venv\Scripts\python.exe -m uvicorn services.syncmultimodal.app:app --host 127.0.0.1 --port 8009

REM Wait for service to start
ping 127.0.0.1 -n 6 > nul

REM Run test script using .venv Python
C:\xampp\htdocs\kiki_agent\.venv\Scripts\python.exe services/syncmultimodal/test_syncmultimodal.py

REM Kill FastAPI service
for /f "tokens=2" %%a in ('tasklist ^| findstr uvicorn') do taskkill /PID %%a /F
