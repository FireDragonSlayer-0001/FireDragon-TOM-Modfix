@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [Setup] FireDragon TOM Modfix setup helper

goto :step_folders

:ask_to_continue
echo.
choice /M "Continue to next step"
if errorlevel 2 (
    echo [STOP] Setup cancelled by user.
    goto :eof
)
exit /b 0

:step_folders
echo Next step: create required folders (Source, Output, programs, Additional).
call :ask_to_continue || goto :eof
for %%D in (Source Output programs Additional) do (
    if not exist "%%D" (
        mkdir "%%D"
        echo [OK] Created folder: %%D
    ) else (
        echo [SKIP] Folder already exists: %%D
    )
)

goto :step_helpers

:step_helpers
echo Next step: download latest helper programs into programs\ from GitHub.
call :ask_to_continue || goto :eof
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
    $ErrorActionPreference = 'Stop';
    $base = 'https://raw.githubusercontent.com/FireDragonSlayer/FireDragon-TOM-Modfix/main/programs';
    $files = @('check_source_and_extract_to_output.py','rename_duplicate_mod_folders.py','validate_output_structure.py');
    foreach ($file in $files) {
        Invoke-WebRequest -Uri ($base + '/' + $file) -OutFile (Join-Path 'programs' $file)
        Write-Host ('[OK] Downloaded: ' + $file)
    }
}"
if errorlevel 1 (
    echo [WARN] Could not download helper scripts with PowerShell.
) else (
    echo [OK] Helper scripts refreshed.
)

goto :step_readme

:step_readme
echo Next step: download README.md and save it locally as README.txt.
call :ask_to_continue || goto :eof
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
    $ErrorActionPreference = 'Stop';
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/FireDragonSlayer/FireDragon-TOM-Modfix/main/README.md' -OutFile 'README.txt'
}"
if errorlevel 1 (
    echo [WARN] Could not download README.txt.
) else (
    echo [OK] README.txt downloaded.
)

goto :done

:done
echo.
echo [DONE] Setup complete.
pause
