@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Python environment missing. Run setup_windows.bat first.
  pause
  exit /b 1
)
set "VIDEO=%~1"
if "%VIDEO%"=="" set "VIDEO=stimuli\biological_motion\S24L0.mp4"
if not exist "%VIDEO%" (
  echo ERROR: Video not found: "%VIDEO%"
  echo Copy S24L0.mp4 into stimuli\biological_motion, or drag a video onto this batch file.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" diagnose_video_v2.py "%VIDEO%"
if errorlevel 1 echo ERROR: Video diagnostic failed. Please copy the error above.
pause
