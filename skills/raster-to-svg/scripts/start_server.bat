@echo off
rem R2S launcher for Windows — starts the local server and opens the browser.
rem Requires Python 3 (https://www.python.org/downloads/, tick "Add to PATH").
setlocal
cd /d "%~dp0\.."

where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% scripts\raster_to_svg_server.py --port 8642
if errorlevel 1 (
  echo.
  echo Failed to start the server. Make sure Python 3 is installed and
  echo "Add python.exe to PATH" was ticked during installation.
  pause
)
endlocal
