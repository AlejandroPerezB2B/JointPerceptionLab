@echo off
setlocal
cd /d "%~dp0"
echo Joint Perception Lab - Windows setup
echo Project folder: %CD%
echo.
py -3.11 --version >nul 2>&1
if errorlevel 1 goto no_python
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python 3.11 virtual environment...
    py -3.11 -m venv .venv
    if errorlevel 1 goto failed
)
echo Checking environment...
".venv\Scripts\python.exe" --version
if errorlevel 1 goto failed
echo Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto failed
echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Installation completed successfully.
echo Run run_windows.bat to launch Joint Perception Lab.
pause
exit /b 0
:no_python
echo ERROR: Python 3.11 was not found by the Windows py launcher.
echo Run: py -0p
echo Install Python 3.11 64-bit and try again.
pause
exit /b 1
:failed
echo.
echo ERROR: Setup failed. Read the error above and share it if needed.
pause
exit /b 1
