@echo off
setlocal
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%~dp0python;%PATH%"
"%~dp0python\python.exe" "%~dp0plateforme\atelier_snake.py" --parcours be_c
if errorlevel 1 (
  echo.
  echo Erreur au lancement. Fenetre laissee ouverte pour lire le message.
  pause
)
