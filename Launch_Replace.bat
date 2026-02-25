@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Launch] Safe Replace from Alternative Output

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python 3 is not installed or not in PATH.
        pause
        exit /b 1
    )
)

if not exist "config.json" (
    echo [ERROR] Missing config.json next to launcher.
    pause
    exit /b 1
)

for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "from pathlib import Path; from programs.shared_config import load_config; c=load_config(Path('config.json')); print(c.get('safe_replace_script','programs/safe_replace_from_alternative_output.py'))"`) do set "REPLACE_SCRIPT=%%I"
if "%REPLACE_SCRIPT%"=="" set "REPLACE_SCRIPT=programs/safe_replace_from_alternative_output.py"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TOM_RUN_ID=%%I"
set "TOM_LOGS_ROOT=%ROOT%Logs"

echo [RUN ] %PYTHON_CMD% "%REPLACE_SCRIPT%"
%PYTHON_CMD% "%REPLACE_SCRIPT%" --config "config.json"
if errorlevel 1 (
    echo [ERROR] Safe replace workflow failed.
    pause
    exit /b 1
)

echo [DONE] Safe replace workflow complete.
pause
exit /b 0
