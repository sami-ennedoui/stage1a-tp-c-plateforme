@echo off
setlocal enableextensions
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%~dp0python;%PATH%"

REM --- Tuteur IA (optionnel) : ajoute claude au PATH s'il est installe mais absent ---
where claude >nul 2>nul
if not errorlevel 1 goto claude_ok
if exist "%APPDATA%\Claude\claude-code" (
  for /f "delims=" %%d in ('dir /b /ad /o-n "%APPDATA%\Claude\claude-code" 2^>nul') do (
    if exist "%APPDATA%\Claude\claude-code\%%d\claude.exe" (
      set "PATH=%APPDATA%\Claude\claude-code\%%d;%PATH%"
      goto claude_ok
    )
  )
)
if exist "%APPDATA%\npm\claude.cmd" set "PATH=%APPDATA%\npm;%PATH%"
:claude_ok

"%~dp0python\python.exe" "%~dp0plateforme\atelier_snake.py" --parcours perso
if errorlevel 1 (
  echo.
  echo Erreur au lancement. Fenetre laissee ouverte pour lire le message.
  pause
)
