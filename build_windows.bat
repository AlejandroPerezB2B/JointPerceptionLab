@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: Run setup_windows.bat first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name JointPerceptionLab --collect-all psychopy --collect-all PySide6 --collect-all cv2 joint_perception_lab\__main__.py
if errorlevel 1 goto fail
echo Candidate executable: dist\JointPerceptionLab\JointPerceptionLab.exe
echo WARNING: This executable requires testing on the target Windows computer.
pause
exit /b 0
:fail
echo Windows build failed. Check errors above.
pause
exit /b 1
