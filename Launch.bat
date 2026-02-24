@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Launch] FireDragon TOM Modfix

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
        pause
        exit /b 1
    )
)

echo [INFO] Python command: %PYTHON_CMD%

if not exist "config.json" (
    echo [ERROR] Missing config.json next to Launch.bat.
    pause
    exit /b 1
)

for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('source_folder','Source'))"`) do set "SOURCE_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('output_folder','Output'))"`) do set "OUTPUT_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('main_script','programs/check_source_and_extract_to_output.py'))"`) do set "MAIN_SCRIPT=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('flatten_script','programs/flatten_single_nested_mod_folder.py'))"`) do set "FLATTEN_SCRIPT=%%I"

if "%SOURCE_FOLDER%"=="" set "SOURCE_FOLDER=Source"
if "%OUTPUT_FOLDER%"=="" set "OUTPUT_FOLDER=Output"
if "%MAIN_SCRIPT%"=="" set "MAIN_SCRIPT=programs/check_source_and_extract_to_output.py"
if "%FLATTEN_SCRIPT%"=="" set "FLATTEN_SCRIPT=programs/flatten_single_nested_mod_folder.py"

if not exist "%MAIN_SCRIPT%" (
    echo [ERROR] Main script not found: %MAIN_SCRIPT%
    pause
    exit /b 1
)

if not exist "%SOURCE_FOLDER%" (
    echo [ERROR] Source folder not found: %SOURCE_FOLDER%
    echo         Place mods there first, then run Launch.bat again.
    pause
    exit /b 1
)

if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"

echo [RUN ] %PYTHON_CMD% "%MAIN_SCRIPT%"
%PYTHON_CMD% "%MAIN_SCRIPT%" "%SOURCE_FOLDER%" "%OUTPUT_FOLDER%"
if errorlevel 1 (
    echo [ERROR] Mod-fix workflow failed.
    pause
    exit /b 1
)

if exist "%FLATTEN_SCRIPT%" (
    echo [RUN ] %PYTHON_CMD% "%FLATTEN_SCRIPT%"
    %PYTHON_CMD% "%FLATTEN_SCRIPT%" "%OUTPUT_FOLDER%"
    if errorlevel 1 (
        echo [ERROR] Flatten workflow failed.
        pause
        exit /b 1
    )
) else (
    echo [WARN] Flatten script not found, skipping: %FLATTEN_SCRIPT%
)

echo [DONE] Fixed mods are available in "%OUTPUT_FOLDER%".
pause
exit /b 0
