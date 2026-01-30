@echo off
REM setup_syncmultimodal.bat
REM Automates starting SyncMulti-Modal FastAPI service and running tests (Windows)

REM Set ffmpeg bin directory in PATH for this session
set "FFMPEG_BIN=C:\xampp\htdocs\kiki_agent\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"
set "PATH=%FFMPEG_BIN%;%PATH%"

REM Start FastAPI service in background using .venv Python
start "SyncMultiModalAPI" /B C:\xampp\htdocs\kiki_agent\.venv\Scripts\python.exe -m uvicorn services.syncmultimodal.app:app --host 127.0.0.1 --port 8009

REM Wait for service to start
ping 127.0.0.1 -n 6 > nul

REM Run test script using .venv Python
C:\xampp\htdocs\kiki_agent\.venv\Scripts\python.exe services/syncmultimodal/test_syncmultimodal.py

REM Kill FastAPI service
for /f "tokens=2" %%a in ('tasklist ^| findstr uvicorn') do taskkill /PID %%a /F
