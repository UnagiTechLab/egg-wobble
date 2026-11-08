@echo off
setlocal
cd /d "%~dp0"

set "DEST=%USERPROFILE%\Documents\maya\scripts"
if not exist "%DEST%" (
  echo [ERROR] Maya scripts folder not found:
  echo   %DEST%
  echo Create it or copy egg_wobble.py manually.
  pause
  exit /b 1
)

copy /Y "%~dp0egg_wobble.py" "%DEST%\egg_wobble.py" >nul
if errorlevel 1 (
  echo [ERROR] Copy failed.
  pause
  exit /b 1
)

if exist "%~dp0egg_wobble_launch.mel" (
  copy /Y "%~dp0egg_wobble_launch.mel" "%DEST%\egg_wobble_launch.mel" >nul
)

echo Installed:
echo   %DEST%\egg_wobble.py
if exist "%DEST%\egg_wobble_launch.mel" echo   %DEST%\egg_wobble_launch.mel
echo.
echo In Maya Script Editor (Python):
echo   import importlib
echo   import egg_wobble as ew
echo   importlib.reload(ew)
echo   ew.show()
echo.
echo Or run egg_wobble_launch.mel from the MEL tab / shelf.
echo.
pause
