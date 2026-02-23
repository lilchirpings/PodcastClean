@echo off
cd /d "%~dp0"

:: Find Python 3.11 automatically
set PYTHON=
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%APPDATA%\Python\Python311\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%p (
        set PYTHON=%%p
        goto :found
    )
)

:: Fall back to py launcher
where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=py -3.11
    goto :found
)

echo ERROR: Python 3.11 not found. Please install it from https://python.org
pause
exit /b 1

:found
%PYTHON% podcast_clean_ui.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Something went wrong. Make sure all packages are installed:
    echo %PYTHON% -m pip install customtkinter openai-whisper pydub numpy pillow mutagen triton-windows
    echo %PYTHON% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pause
)
