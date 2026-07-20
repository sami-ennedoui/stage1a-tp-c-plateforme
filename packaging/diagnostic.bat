@echo off
setlocal enableextensions
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%PATH%"
REM clangd (diagnostics en direct) : w64devkit ne le fournit pas, il est a part
if exist "%~dp0clangd\bin" set "PATH=%~dp0clangd\bin;%PATH%"
if exist "%USERPROFILE%\.local\bin" set "PATH=%USERPROFILE%\.local\bin;%PATH%"
if exist "%APPDATA%\npm" set "PATH=%APPDATA%\npm;%PATH%"

echo === Compilateur gcc (indispensable) ===
gcc --version
echo.
echo === clangd (diagnostics en direct, optionnel) ===
clangd --version
echo.
echo === Application ===
if exist "%~dp0TP-C-perso.exe" (echo TP-C-perso.exe present) else (echo TP-C-perso.exe INTROUVABLE)
echo.
echo === Tuteur IA (optionnel : claude ou codex) ===
where claude
where codex
echo.
echo Diagnostic termine. Si gcc affiche une version, le coeur de l'atelier fonctionne.
echo Le tuteur IA est optionnel : il s'active si claude ou codex apparait ci-dessus.
pause
