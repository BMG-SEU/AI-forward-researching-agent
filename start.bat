@echo off
chcp 65001 >/dev/null
title AI Frontier Explorer

echo.
echo  ========================================
echo    AI Frontier Explorer - One-Click Start
echo  ========================================
echo.

:: check venv
if not exist .venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found. Run first:
    echo   python -m venv .venv
    pause
    exit /b 1
)

:: activate venv
call .venv\Scripts\activate.bat

:: check deps
python -c "import deepagents" 2>/dev/null
if errorlevel 1 (
    echo [INIT] Installing dependencies...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
)

:: launch
echo.
echo [LAUNCH] Loading AI Frontier Explorer...
echo.
python ai_frontier.py

echo.
echo Agent exited.
pause
