@echo off
REM install_ffmpeg.bat
REM Downloads ffmpeg for Windows and updates PATH for current session

REM Download ffmpeg zip from official source
set FF_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
set FF_ZIP=ffmpeg-release-essentials.zip
set FF_DIR=ffmpeg

REM Download ffmpeg zip
powershell -Command "Invoke-WebRequest -Uri %FF_URL% -OutFile %FF_ZIP%"

REM Unzip ffmpeg
powershell -Command "Expand-Archive -Path %FF_ZIP% -DestinationPath %FF_DIR%"

REM Find bin directory
for /d %%i in (%FF_DIR%\ffmpeg-*) do set FF_BIN=%%i\bin

REM Add ffmpeg bin to PATH for current session
set PATH=%PATH%;%CD%\%FF_BIN%

REM Confirm ffmpeg is available
ffmpeg -version
