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

for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print(c.get('source_folder', m.get('sourcefolder','Source')) if isinstance(c,dict) else 'Source')"`) do set "SOURCE_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print((c.get('shippable_output_dir') if isinstance(c,dict) else None) or m.get('shippableoutputdir') or (c.get('output_folder') if isinstance(c,dict) else None) or m.get('outputfolder') or 'Output')"`) do set "OUTPUT_FOLDER=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print(c.get('main_script', m.get('mainscript','programs/check_source_and_extract_to_output.py')) if isinstance(c,dict) else 'programs/check_source_and_extract_to_output.py')"`) do set "MAIN_SCRIPT=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print(c.get('flatten_script', m.get('flattenscript','programs/flatten_single_nested_mod_folder.py')) if isinstance(c,dict) else 'programs/flatten_single_nested_mod_folder.py')"`) do set "FLATTEN_SCRIPT=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print(c.get('rename_script', m.get('renamescript','programs/rename_duplicate_mod_folders.py')) if isinstance(c,dict) else 'programs/rename_duplicate_mod_folders.py')"`) do set "RENAME_SCRIPT=%%I"
for /f "usebackq tokens=*" %%I in (`%PYTHON_CMD% -c "import json; c=json.load(open('config.json','r',encoding='utf-8')); n=lambda s:''.join(ch for ch in s.lower() if ch.isalnum()); m={n(k):v for k,v in c.items()} if isinstance(c,dict) else {}; print(c.get('validate_script', m.get('validatescript','programs/validate_output_structure.py')) if isinstance(c,dict) else 'programs/validate_output_structure.py')"`) do set "VALIDATE_SCRIPT=%%I"

if "%SOURCE_FOLDER%"=="" set "SOURCE_FOLDER=Source"
if "%OUTPUT_FOLDER%"=="" set "OUTPUT_FOLDER=Output"
if "%MAIN_SCRIPT%"=="" set "MAIN_SCRIPT=programs/check_source_and_extract_to_output.py"
if "%FLATTEN_SCRIPT%"=="" set "FLATTEN_SCRIPT=programs/flatten_single_nested_mod_folder.py"
if "%RENAME_SCRIPT%"=="" set "RENAME_SCRIPT=programs/rename_duplicate_mod_folders.py"
if "%VALIDATE_SCRIPT%"=="" set "VALIDATE_SCRIPT=programs/validate_output_structure.py"

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
if not exist "Logs" mkdir "Logs"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TOM_RUN_ID=%%I"
set "TOM_LOGS_ROOT=%ROOT%Logs"

echo [INFO] Run log folder: Logs\%TOM_RUN_ID%

echo [RUN ] %PYTHON_CMD% "%MAIN_SCRIPT%"
%PYTHON_CMD% "%MAIN_SCRIPT%" --config "config.json"
if errorlevel 1 (
    echo [ERROR] Mod-fix workflow failed.
    pause
    exit /b 1
)

if exist "%FLATTEN_SCRIPT%" (
    echo [RUN ] %PYTHON_CMD% "%FLATTEN_SCRIPT%"
    %PYTHON_CMD% "%FLATTEN_SCRIPT%" --config "config.json"
    if errorlevel 1 (
        echo [ERROR] Flatten workflow failed.
        pause
        exit /b 1
    )
) else (
    echo [WARN] Flatten script not found, skipping: %FLATTEN_SCRIPT%
)

if exist "%RENAME_SCRIPT%" (
    echo [RUN ] %PYTHON_CMD% "%RENAME_SCRIPT%"
    %PYTHON_CMD% "%RENAME_SCRIPT%" --config "config.json"
    if errorlevel 1 (
        echo [ERROR] Rename workflow failed.
        pause
        exit /b 1
    )
) else (
    echo [WARN] Rename script not found, skipping: %RENAME_SCRIPT%
)

if exist "%VALIDATE_SCRIPT%" (
    echo [RUN ] %PYTHON_CMD% "%VALIDATE_SCRIPT%"
    %PYTHON_CMD% "%VALIDATE_SCRIPT%" --config "config.json"
    if errorlevel 1 (
        echo [ERROR] Validate workflow found issues.
        pause
        exit /b 1
    )
) else (
    echo [WARN] Validate script not found, skipping: %VALIDATE_SCRIPT%
)

echo [DONE] Fixed mods are available in "%OUTPUT_FOLDER%".
echo [DONE] Run logs are available in "Logs\%TOM_RUN_ID%".
pause
exit /b 0
