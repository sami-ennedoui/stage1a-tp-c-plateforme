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

echo === gcc ===
gcc --version
echo === python ===
"%~dp0python\python.exe" --version
echo === import PyQt6 ===
"%~dp0python\python.exe" -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
echo === claude (tuteur IA, optionnel) ===
where claude
echo.
echo Diagnostic termine.
pause
