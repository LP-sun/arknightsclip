@echo off
setlocal
chcp 65001 >nul 2>nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
title Arknights Operbox Standalone Collector

:: Check python in PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -X utf8 "%~dp0collector.py" %*
    goto :end
)

:: Check py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 -X utf8 "%~dp0collector.py" %*
    goto :end
)

:: Fallback warning if Python is not installed
echo ==================================================================
echo [ERROR] Python environment was not found on your system!
echo ==================================================================
echo.
echo Please install Python 3 (3.8 or newer recommended):
echo 1. Download from official site: https://www.python.org/downloads/
echo 2. IMPORTANT: Check the box "Add python.exe to PATH" during setup.
echo 3. After installation, double-click this file again.
echo.
pause

:end
endlocal
