@echo off
setlocal
cd /d "%~dp0"
set "PATH=%~dp0w64devkit\bin;%~dp0python;%~dp0clangd\bin;%PATH%"
echo === gcc ===
gcc --version
echo === clangd (diagnostics en direct) ===
clangd --version
echo === python ===
"%~dp0python\python.exe" --version
echo === import PyQt6 ===
"%~dp0python\python.exe" -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
echo === claude (tuteur IA, optionnel) ===
where claude
echo.
echo Diagnostic termine.
pause
