@echo off
setlocal

REM Adjust these two paths for your server
set PROJECT_DIR=D:\Services\cim_dashboard
set VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe

cd /d "%PROJECT_DIR%"
"%VENV_PYTHON%" main.py

REM Capture exit code so Task Scheduler can report failure
if %ERRORLEVEL% NEQ 0 (
    echo Export failed with exit code %ERRORLEVEL% >> "%PROJECT_DIR%\logs\scheduler_errors.log"
)

endlocal