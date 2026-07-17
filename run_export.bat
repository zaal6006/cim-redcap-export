@echo off
setlocal

REM ============================================================
REM CIM REDCap Export - Scheduled Task Wrapper
REM ============================================================

set PROJECT_DIR=D:\Services\cim_dashboard
set VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
set BAT_LOG=%PROJECT_DIR%\logs\scheduler_run.log

REM Make sure logs folder exists before we try to write to it
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

echo ============================================== >> "%BAT_LOG%"
echo %DATE% %TIME% - Task started >> "%BAT_LOG%"
echo Running as: %USERDOMAIN%\%USERNAME% >> "%BAT_LOG%"
echo PROJECT_DIR: %PROJECT_DIR% >> "%BAT_LOG%"
echo VENV_PYTHON: %VENV_PYTHON% >> "%BAT_LOG%"

REM Verify python.exe actually exists BEFORE trying to run it.
REM This is the #1 cause of "silent success" failures.
if not exist "%VENV_PYTHON%" (
    echo %DATE% %TIME% - ERROR: python.exe not found at %VENV_PYTHON% >> "%BAT_LOG%"
    exit /b 9009
)

cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo %DATE% %TIME% - ERROR: could not cd to %PROJECT_DIR% >> "%BAT_LOG%"
    exit /b 1
)

REM Redirect BOTH stdout and stderr to the log file, so any Python
REM traceback or print output is captured even when running headless.
"%VENV_PYTHON%" main.py >> "%BAT_LOG%" 2>&1

REM Capture Python's exit code IMMEDIATELY - nothing between this
REM line and the "if" below, or ERRORLEVEL gets overwritten.
set PYTHON_EXIT_CODE=%ERRORLEVEL%

echo %DATE% %TIME% - main.py finished with exit code %PYTHON_EXIT_CODE% >> "%BAT_LOG%"
echo ============================================== >> "%BAT_LOG%"

REM Propagate the real exit code to Task Scheduler.
REM This is the critical fix: without "exit /b", the batch file
REM always returns 0 regardless of what happened above.
exit /b %PYTHON_EXIT_CODE%