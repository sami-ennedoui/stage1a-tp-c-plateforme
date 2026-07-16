@echo off
setlocal enableextensions
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%PATH%"

REM --- Tuteur IA (optionnel) : rend claude ou codex trouvable s'il est installe ---
if exist "%USERPROFILE%\.local\bin" set "PATH=%USERPROFILE%\.local\bin;%PATH%"
if exist "%APPDATA%\npm" set "PATH=%APPDATA%\npm;%PATH%"
if exist "%APPDATA%\Claude\claude-code" (
  for /f "delims=" %%d in ('dir /b /ad /o-n "%APPDATA%\Claude\claude-code" 2^>nul') do (
    if exist "%APPDATA%\Claude\claude-code\%%d\claude.exe" (
      set "PATH=%APPDATA%\Claude\claude-code\%%d;%PATH%"
      goto ia_ok
    )
  )
)
:ia_ok

start "" "%~dp0TP-C-perso.exe" --parcours be_c
