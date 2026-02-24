@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Launch] FireDragon TOM Modfix

if not exist "config.json" (
    echo [ERROR] Missing config.json next to Launch.bat.
    pause
    exit /b 1
)

for /f "usebackq tokens=*" %%I in (`python -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('source_folder','Source'))"`) do set "SOURCE_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`python -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('output_folder','Output'))"`) do set "OUTPUT_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`python -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); print(c.get('main_script','programs/check_source_and_extract_to_output.py'))"`) do set "MAIN_SCRIPT=%%I"

if "%SOURCE_FOLDER%"=="" set "SOURCE_FOLDER=Source"
if "%OUTPUT_FOLDER%"=="" set "OUTPUT_FOLDER=Output"
if "%MAIN_SCRIPT%"=="" set "MAIN_SCRIPT=programs/check_source_and_extract_to_output.py"

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

echo [RUN ] python "%MAIN_SCRIPT%"
python "%MAIN_SCRIPT%" "%SOURCE_FOLDER%" "%OUTPUT_FOLDER%"
if errorlevel 1 (
    echo [ERROR] Mod-fix workflow failed.
    pause
    exit /b 1
)

echo [DONE] Fixed mods are available in "%OUTPUT_FOLDER%".
pause
exit /b 0
