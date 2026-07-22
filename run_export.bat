@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM CIM REDCap Export - Scheduled Task Wrapper
REM ============================================================

set PROJECT_DIR=D:\Services\cim_dashboard
set VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
set LOG_DIR=%PROJECT_DIR%\logs

REM Build a date stamp independent of regional Windows date format
REM (avoids relying on %DATE% formatting, which varies by locale).
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set TODAY=%%i
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format HHmmss"') do set NOW_TIME=%%i

set BAT_LOG=%LOG_DIR%\scheduler_run_%TODAY%.log

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================== >> "%BAT_LOG%"
echo %TODAY% %NOW_TIME% - Task started >> "%BAT_LOG%"
echo Running as: %USERDOMAIN%\%USERNAME% >> "%BAT_LOG%"
echo PROJECT_DIR: %PROJECT_DIR% >> "%BAT_LOG%"
echo VENV_PYTHON: %VENV_PYTHON% >> "%BAT_LOG%"

if not exist "%VENV_PYTHON%" (
    echo %TODAY% %NOW_TIME% - ERROR: python.exe not found at %VENV_PYTHON% >> "%BAT_LOG%"
    exit /b 9009
)

cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo %TODAY% %NOW_TIME% - ERROR: could not cd to %PROJECT_DIR% >> "%BAT_LOG%"
    exit /b 1
)

"%VENV_PYTHON%" main.py >> "%BAT_LOG%" 2>&1

set PYTHON_EXIT_CODE=%ERRORLEVEL%

echo %TODAY% %NOW_TIME% - main.py finished with exit code %PYTHON_EXIT_CODE% >> "%BAT_LOG%"
echo ============================================== >> "%BAT_LOG%"

REM ------------------------------------------------------------
REM Cleanup: delete scheduler_run_*.log files older than 30 days.
REM Runs every execution - cheap, and keeps the logs folder from
REM growing forever since this file type has no built-in rotation.
REM ------------------------------------------------------------
forfiles /P "%LOG_DIR%" /M "scheduler_run_*.log" /D -30 /C "cmd /c del @path" 2>nul

exit /b %PYTHON_EXIT_CODE%