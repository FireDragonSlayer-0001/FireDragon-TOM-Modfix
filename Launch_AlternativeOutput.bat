@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Launch] Alternative Output builder

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

for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('alternative_builder_script','programs/build_alternative_output_for_broken_mods.py'))"`) do set "ALT_SCRIPT=%%I"
if "%ALT_SCRIPT%"=="" set "ALT_SCRIPT=programs/build_alternative_output_for_broken_mods.py"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TOM_RUN_ID=%%I"
set "TOM_LOGS_ROOT=%ROOT%Logs"

echo [RUN ] %PYTHON_CMD% "%ALT_SCRIPT%"
%PYTHON_CMD% "%ALT_SCRIPT%" --config "config.json"
if errorlevel 1 (
    echo [ERROR] Alternative output build failed.
    pause
    exit /b 1
)

echo [DONE] Alternative output workflow complete.
pause
exit /b 0
