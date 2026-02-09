@echo off
setlocal enabledelayedexpansion

set PROJECT_PATH=C:\Users\User\Projects\Transaction_Forwarder
set PROJECT_NAME=Transaction Forwarder
set BUILD_DIR=Build\Linux
set SOURCE=main.py

echo [INFO] %PROJECT_NAME% - Linux Build Script (GLIBC 2.35 compatible)
echo ================================================================

echo [INFO] Changing to project directory...
cd /d "%PROJECT_PATH%"
if errorlevel 1 (
    echo [ERROR] Failed to change to project directory: %PROJECT_PATH%
    pause
    exit /b 1
)

echo [INFO] Current directory: %CD%

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

echo [INFO] Cleaning previous Linux builds...
if exist "%BUILD_DIR%" (
    echo   Removing existing build directory...
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%" 2>nul

echo [INFO] Checking source file...
if not exist "%SOURCE%" (
    echo [ERROR] Source file '%SOURCE%' not found!
    pause
    exit /b 1
)

echo [SUCCESS] Found: %SOURCE%

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
  sh -c "apt-get update && apt-get install -y patchelf gcc g++ python3.10 python3-pip python3.10-venv && python3.10 -m venv /venv && /venv/bin/pip install --upgrade pip && /venv/bin/pip install nuitka && /venv/bin/pip install -r requirements.txt && /venv/bin/python -m nuitka --onefile --follow-imports --assume-yes-for-downloads --no-pyi main.py && cp main.bin /output/"

set BUILD_ERRORLEVEL=%ERRORLEVEL%
set END_TIME=%TIME%

if %BUILD_ERRORLEVEL% EQU 0 (
    if exist "%BUILD_DIR%\main.bin" (
        ren "%BUILD_DIR%\main.bin" "transaction_forwarder"
        echo.
        echo ======================================
        echo [SUCCESS] Linux build completed!
        echo ======================================

        echo [INFO] Build details:
        echo   Output: %BUILD_DIR%\transaction_forwarder
        echo   GLIBC version: 2.35 (Ubuntu 22.04 compatible)

        for %%F in ("%BUILD_DIR%\transaction_forwarder") do (
            set FILE_SIZE=%%~zF
            set /a FILE_SIZE_MB=!FILE_SIZE!/1048576
            echo   Size: !FILE_SIZE! bytes (!FILE_SIZE_MB! MB)
        )

        echo [INFO] Build time: %START_TIME% - %END_TIME%
        echo [INFO] File type: Linux ELF binary (compatible with most systems)
    ) else (
        echo [ERROR] Build succeeded but no executable found
        call :check_output
    )
) else (
    echo.
    echo ======================================
    echo [ERROR] Build failed: %BUILD_ERRORLEVEL%
    echo ======================================
    
    echo [INFO] Trying alternative with Debian Bullseye (GLIBC 2.31)...
    call :debian_build
)

echo.
pause
endlocal
goto :eof

:check_output
echo [INFO] Checking what was created...
docker run --rm -v "%CD%:/app" -w /app ubuntu:22.04 sh -c "ls -la *.bin 2>/dev/null || echo 'No .bin files found'"
exit /b

:debian_build
rem === ALTERNATIVE: DEBIAN BULLSEYE (GLIBC 2.31) ===
echo [INFO] Building with Debian Bullseye (even older GLIBC 2.31)...

docker run --rm ^
  -v "%CD%:/app" ^
  -v "%CD%\%BUILD_DIR%:/output" ^
  -w /app ^
  debian:bullseye-slim ^
  sh -c "apt-get update && apt-get install -y patchelf gcc g++ python3 python3-pip python3-venv && python3 -m venv /venv && /venv/bin/pip install --upgrade pip && /venv/bin/pip install nuitka && /venv/bin/pip install -r requirements.txt && /venv/bin/python -m nuitka --onefile --follow-imports --assume-yes-for-downloads --no-pyi main.py && cp main.bin /output/"

if errorlevel 1 (
    echo [ERROR] Debian build also failed
    exit /b
)

if exist "%BUILD_DIR%\main.bin" (
    ren "%BUILD_DIR%\main.bin" "transaction_forwarder"
    echo [SUCCESS] Debian Bullseye build completed!
    echo [INFO] GLIBC version: 2.31 (compatible with older systems)
    dir "%BUILD_DIR%\transaction_forwarder"
)
exit /b