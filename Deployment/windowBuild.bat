@echo off
setlocal enabledelayedexpansion

set PROJECT_PATH=C:\Users\User\Projects\Transaction_Forwarder
set VENV_PATH=%PROJECT_PATH%\venv
set PROJECT_NAME=Transaction Forwarder
set BUILD_DIR=Build\Window
set SOURCE=main.py
set OUTPUT_EXE=transactionForwarder.exe

echo [INFO] %PROJECT_NAME% - Build Script
echo ======================================

echo [INFO] Changing to project directory...
cd /d "%PROJECT_PATH%"
if not "%CD%"=="%PROJECT_PATH%" (
    echo [ERROR] Failed to change to project directory: %PROJECT_PATH%
    pause
    exit /b 1
)

echo [INFO] Current directory: %CD%

echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [INFO] Cleaning previous builds...
if exist "%BUILD_DIR%" (
    echo   Removing existing build directory...
    rmdir /s /q "%BUILD_DIR%"
    if exist "%BUILD_DIR%" (
        echo [ERROR] Failed to remove build directory!
        exit /b 1
    )
)

echo [INFO] Checking requirements...
if not exist "%SOURCE%" (
    echo [ERROR] Source file '%SOURCE%' not found!
    echo [INFO] Available files:
    dir /b *.py 2>nul || echo   No Python files found
    pause
    exit /b 1
)

echo [INFO] Assets check...
if exist "Assets" (
    echo   Assets folder found: Assets\
) else (
    echo   [WARNING] Assets folder not found
)

echo [INFO] Building with Nuitka...
echo   Source: %SOURCE%
echo   Output: %BUILD_DIR%\%OUTPUT_EXE%
echo   Jobs: 8 (parallel compilation)

set START_TIME=%TIME%
python -m nuitka --onefile ^
  --windows-console-mode=force ^
  --include-data-dir=Assets=Assets ^
  --output-dir=%BUILD_DIR% ^
  --output-filename=%OUTPUT_EXE% ^
  --remove-output ^
  --lto=yes ^
  --jobs=8 ^
  --assume-yes-for-downloads ^
  --follow-stdlib ^
  --follow-imports ^
  --show-progress ^
  %SOURCE%

set BUILD_ERRORLEVEL=%ERRORLEVEL%
set END_TIME=%TIME%

if %BUILD_ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo [SUCCESS] Build completed successfully!
    echo ======================================
    
    echo [INFO] Build details:
    echo   Output: %BUILD_DIR%\%OUTPUT_EXE%
    
    if exist "%BUILD_DIR%\%OUTPUT_EXE%" (
        for %%F in ("%BUILD_DIR%\%OUTPUT_EXE%") do (
            set FILE_SIZE=%%~zF
            set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
            set /a FILE_SIZE_KB=!FILE_SIZE!/1024
            echo   Size: !FILE_SIZE! bytes (!FILE_SIZE_KB! KB / !FILE_SIZE_MB! MB)
        )
    )
    
    echo [INFO] Build time: %START_TIME% - %END_TIME%
    
    echo.
    echo [INFO] Build location: %CD%\%BUILD_DIR%\
    
) else (
    echo.
    echo ======================================
    echo [ERROR] Build failed with exit code: %BUILD_ERRORLEVEL%
    echo ======================================
    echo [INFO] Common issues:
    echo   1. Check if Python and Nuitka are installed
    echo   2. Run: python -m pip install nuitka
    echo   3. Check dependencies in %SOURCE%
)

echo.
pause
endlocal