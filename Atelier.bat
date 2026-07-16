@echo off
setlocal
cd /d "%~dp0"

rem Detection de Python : d'abord l'installation utilisateur 3.12, sinon le lanceur py
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY="
if not defined PY (
    where py >nul 2>nul && set "PY=py"
)
if not defined PY (
    echo Python 3.12 introuvable. Installe-le puis relance ce fichier.
    pause
    exit /b 1
)

rem Compilateur portable embarque : ajoute au PATH s'il est present a cote de l'appli
if exist "%~dp0w64devkit\bin\gcc.exe" set "PATH=%~dp0w64devkit\bin;%PATH%"

rem Le parcours vient de reglages.json (defaut be_c au premier lancement)
"%PY%" "%~dp0atelier_snake.py"
if errorlevel 1 pause
