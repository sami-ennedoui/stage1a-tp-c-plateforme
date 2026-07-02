@echo off
REM Mode DEMO : tout est debloque et le bouton "Le tuteur ecrit le code" apparait
REM (le tuteur redige un programme complet pour tester le correcteur). A NE PAS
REM distribuer aux etudiants : le lanceur normal est lancer.bat.
setlocal enableextensions
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%PATH%"

REM --- Tuteur IA (necessaire en demo pour la generation) ---
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

start "" "%~dp0TP-C-perso.exe" --demo --parcours be_c
