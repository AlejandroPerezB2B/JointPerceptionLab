@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg not found. Install it with: winget install -e --id Gyan.FFmpeg
  pause
  exit /b 1
)
if not exist "stimuli\biological_motion" mkdir "stimuli\biological_motion"
for %%F in ("stimuli\biological_motion\*.avi") do (
  if not exist "stimuli\biological_motion\%%~nF.mp4" (
    ffmpeg -i "%%~fF" -c:v libx264 -crf 17 -pix_fmt yuv420p -an "stimuli\biological_motion\%%~nF.mp4"
  )
)
echo Conversion finished. Move original AVI files out of this folder before validating.
pause
