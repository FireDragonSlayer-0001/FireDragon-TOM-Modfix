@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Setup] FireDragon TOM Modfix verifier/updater

set "HAS_ERROR=0"

if not exist "config.json" (
    echo [ERROR] Missing required file: config.json
    set "HAS_ERROR=1"
    goto :finish
)

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python 3 is not installed or not in PATH.
        echo         Install Python 3.8+ from https://www.python.org/downloads/
        set "HAS_ERROR=1"
        goto :finish
    )
)

echo [OK] Python command: %PYTHON_CMD%

for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('source_folder','Source'))"`) do set "SOURCE_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('output_folder','Output'))"`) do set "OUTPUT_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('programs_folder','programs'))"`) do set "PROGRAMS_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('auto_update_tools', False))"`) do set "AUTO_UPDATE_TOOLS=%%I"

if "%SOURCE_FOLDER%"=="" set "SOURCE_FOLDER=Source"
if "%OUTPUT_FOLDER%"=="" set "OUTPUT_FOLDER=Output"
if "%PROGRAMS_FOLDER%"=="" set "PROGRAMS_FOLDER=programs"

echo [INFO] Source folder: %SOURCE_FOLDER%
echo [INFO] Output folder: %OUTPUT_FOLDER%
echo [INFO] Programs folder: %PROGRAMS_FOLDER%

for %%D in ("%SOURCE_FOLDER%" "%OUTPUT_FOLDER%" "%PROGRAMS_FOLDER%" "Logs") do (
    if not exist %%~D (
        mkdir %%~D
        echo [FIX ] Created missing folder: %%~D
    ) else (
        echo [OK  ] Folder exists: %%~D
    )
)

for %%F in ("Readme.txt" "Launch.bat" "Setup.bat" "config.json") do (
    if not exist %%~F (
        echo [ERROR] Missing required file: %%~F
        set "HAS_ERROR=1"
    ) else (
        echo [OK  ] File exists: %%~F
    )
)

for %%P in ("check_source_and_extract_to_output.py" "rename_duplicate_mod_folders.py" "validate_output_structure.py" "flatten_single_nested_mod_folder.py" "run_logging.py") do (
    if not exist "%PROGRAMS_FOLDER%\%%~P" (
        echo [ERROR] Missing required helper: %PROGRAMS_FOLDER%\%%~P
        set "HAS_ERROR=1"
    ) else (
        echo [OK  ] Helper exists: %PROGRAMS_FOLDER%\%%~P
    )
)

if /I "%AUTO_UPDATE_TOOLS%"=="True" goto :update_tools
if /I "%AUTO_UPDATE_TOOLS%"=="true" goto :update_tools
if /I "%AUTO_UPDATE_TOOLS%"=="1" goto :update_tools
goto :finish

:update_tools
echo [INFO] auto_update_tools enabled. Refreshing helper scripts from GitHub...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $ErrorActionPreference='Stop'; $base='https://raw.githubusercontent.com/FireDragonSlayer-0001/FireDragon-TOM-Modfix/main/programs'; $files=@('check_source_and_extract_to_output.py','rename_duplicate_mod_folders.py','validate_output_structure.py','flatten_single_nested_mod_folder.py','run_logging.py'); foreach ($file in $files) { Invoke-WebRequest -Uri ($base + '/' + $file) -OutFile (Join-Path '%PROGRAMS_FOLDER%' $file); Write-Host ('[OK] Downloaded: ' + $file) } }"
if errorlevel 1 (
    echo [WARN] Tool refresh failed (offline or blocked). Keeping bundled versions.
)

:finish
echo.
if "%HAS_ERROR%"=="1" (
    echo [DONE WITH ERRORS] Please review messages above.
    pause
    exit /b 1
)

echo [DONE] Setup verification completed successfully.
pause
exit /b 0
