@echo off
setlocal enabledelayedexpansion
echo --- HopeOn Wheel GitHub Uploader (Smart Fix) ---
echo.

:: 1. Check if git is in PATH
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Git not in system PATH. Searching common install locations...
    
    :: Search common paths
    set "GIT_PATH="
    if exist "C:\Program Files\Git\bin\git.exe" set "GIT_PATH=C:\Program Files\Git\bin\git.exe"
    if not defined GIT_PATH if exist "C:\Program Files (x86)\Git\bin\git.exe" set "GIT_PATH=C:\Program Files (x86)\Git\bin\git.exe"
    if not defined GIT_PATH if exist "%LOCALAPPDATA%\Programs\Git\bin\git.exe" set "GIT_PATH=%LOCALAPPDATA%\Programs\Git\bin\git.exe"
    
    if defined GIT_PATH (
        echo [FIX] Found Git at: !GIT_PATH!
        set "PATH=!PATH!;!GIT_PATH%:\git.exe=!"
        doskey git="!GIT_PATH!" $*
    ) else (
        echo [ERROR] Git could not be found on this computer.
        echo Please download and install Git from: https://git-scm.com/download/win
        pause
        exit /b
    )
)

echo [OK] Git is ready. Starting upload...
echo.

:: Check identity
git config user.email >nul 2>&1
if %errorlevel% neq 0 (
    echo [FIX] Setting temporary Git identity...
    git config --global user.email "hchaurasia@example.com"
    git config --global user.name "H. Chaurasia"
)

echo [1/5] Initializing Git...
git init

echo [2/5] Adding all project files...
git add .

echo [3/5] Committing to local machine...
git commit -m "Full Migration: HopeOn Wheel Phase 1 Complete"

echo [4/5] Connecting to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/hchaurasia907/HopeOnWheel.git

echo [5/5] Pushing to GitHub (main branch)...
git branch -M main
git push -u origin main

echo.
echo --- SUCCESS! Project is now on GitHub ---
pause
