@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto not_installed
".venv\Scripts\python.exe" -m joint_perception_lab
if errorlevel 1 goto failed
exit /b 0
:not_installed
echo ERROR: Python virtual environment not found in this project folder.
echo Run setup_windows.bat first, from this same folder.
pause
exit /b 1
:failed
echo.
echo Application exited with an error. See the message above.
pause
exit /b 1
