@echo off
setlocal enabledelayedexpansion

rem Project settings
set PROJECT_PATH=C:\Users\User\Projects\Transaction_Forwarder
set PROJECT_NAME=Transaction Forwarder
set BUILD_DIR=Build\Linux
set SOURCE=main.py

echo [INFO] %PROJECT_NAME% - Linux Build Script (GLIBC 2.35 compatible)
echo ================================================================

rem Change to project directory
echo [INFO] Changing to project directory...
cd /d "%PROJECT_PATH%"
if errorlevel 1 (
    echo [ERROR] Failed to change to project directory: %PROJECT_PATH%
    pause
    exit /b 1
)

echo [INFO] Current directory: %CD%

rem Check if Docker is installed
echo [INFO] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found!
    echo [INFO] Please make sure Docker Desktop is running
    pause
    exit /b 1
)

echo [SUCCESS] Docker found: 
docker --version

rem Clean previous Linux builds
echo [INFO] Cleaning previous Linux builds...
if exist "%BUILD_DIR%" (
    echo   Removing existing build directory...
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%" 2>nul

rem Check if the source file exists
echo [INFO] Checking source file...
if not exist "%SOURCE%" (
    echo [ERROR] Source file '%SOURCE%' not found!
    pause
    exit /b 1
)

echo [SUCCESS] Found: %SOURCE%

rem Build the Linux executable with GLIBC 2.35 compatibility
echo [INFO] Building Linux executable with GLIBC 2.35 compatibility...
echo   Source: %SOURCE%
echo   Output: %BUILD_DIR%
echo   Docker Image: ubuntu:22.04 (GLIBC 2.35)

set START_TIME=%TIME%

rem === DOCKER BUILD COMMAND FOR UBUNTU 22.04 (GLIBC 2.35) ===
rem Ubuntu 22.04 has GLIBC 2.35 which is compatible with most Linux systems
docker run --rm ^
  -v "%CD%:/app" ^
  -v "%CD%\%BUILD_DIR%:/output" ^
  -w /app ^
  ubuntu:22.04 ^
  sh -c "apt-get update && apt-get install -y patchelf gcc g++ python3.10 python3-pip python3.10-venv ca-certificates && python3.10 -m venv /venv && /venv/bin/pip install --upgrade pip && echo '=== Installing requirements ===' && /venv/bin/pip install -r requirements.txt && echo '=== Build Command ===' && /venv/bin/python -m nuitka --onefile --follow-imports --include-package=httpx --include-package=httpcore --include-package=anyio --include-package=certifi --include-package=h11 --include-package=aiofiles --include-package=uvicorn --include-data-files=/venv/lib/python3.10/site-packages/certifi/cacert.pem=certifi/cacert.pem --include-data-files=assets/*=Assets/ --assume-yes-for-downloads --output-filename=transactionForwarder.bin %SOURCE% && cp /app/transactionForwarder.bin /output/"

set BUILD_ERRORLEVEL=%ERRORLEVEL%
set END_TIME=%TIME%

rem Check build results
if %BUILD_ERRORLEVEL% EQU 0 (
    if exist "%BUILD_DIR%\transactionForwarder.bin" (
        echo.
        echo ======================================
        echo [SUCCESS] Linux build completed!
        echo ======================================

        echo [INFO] Build details:
        echo   Output: %BUILD_DIR%\transactionForwarder.bin
        echo   GLIBC version: 2.35 (Ubuntu 22.04 compatible)

        for %%F in ("%BUILD_DIR%\transactionForwarder.bin") do (
            set FILE_SIZE=%%~zF
            set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
            echo   Size: !FILE_SIZE! bytes (!FILE_SIZE_MB! MB)
        )

        echo [INFO] Build time: %START_TIME% - %END_TIME%
        echo [INFO] File type: Linux ELF binary (compatible with most systems)
    ) else (
        echo [ERROR] Build succeeded but no executable found at %BUILD_DIR%\transactionForwarder.bin
    )
) else (
    echo [ERROR] Build failed: %BUILD_ERRORLEVEL%
)

rem === CLEANUP: Remove unnecessary build artifacts ===
echo [INFO] Cleaning up build artifacts...
if exist "main.build" rmdir /s /q "main.build"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.onefile-build" rmdir /s /q "main.onefile-build"
if exist "transactionForwarder.bin" del /f /q "transactionForwarder.bin"

echo [INFO] Cleanup complete.

echo.
pause
endlocal
goto :eof