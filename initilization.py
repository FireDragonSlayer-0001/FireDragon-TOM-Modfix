from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
import shutil

INITIALIZATION_VERSION = "0.2"
BASE_RAW_URL = "https://raw.githubusercontent.com/FireDragonSlayer/FireDragon-TOM-Modfix/main"
PROGRAM_DOWNLOADS = {
    "check_source_and_extract_to_output.py": f"{BASE_RAW_URL}/programs/check_source_and_extract_to_output.py",
    "rename_duplicate_mod_folders.py": f"{BASE_RAW_URL}/programs/rename_duplicate_mod_folders.py",
    "validate_output_structure.py": f"{BASE_RAW_URL}/programs/validate_output_structure.py",
}
README_DOWNLOAD_URL = f"{BASE_RAW_URL}/README.md"
SETUP_BAT_NAME = "Setup.bat"

SETUP_BAT_CONTENT = r"""@echo off
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
"""


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Folder ready: {path}")


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"[OK] File written: {path}")


def download_text(url: str, target_path: Path) -> bool:
    try:
        with urlopen(url, timeout=30) as response:
            content = response.read().decode("utf-8")
        write_file(target_path, content)
        return True
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"[WARN] Failed to download {target_path.name}: {error}")
        return False


def download_program(programs_path: Path, filename: str, url: str) -> None:
    target_path = programs_path / filename
    if download_text(url, target_path):
        print(f"[OK] Downloaded latest helper: {filename}")
        return

    local_source = Path(__file__).resolve().parent / "programs" / filename
    if local_source.exists():
        if local_source.resolve() == target_path.resolve():
            print(f"[SKIP] Local helper already present: {filename}")
        else:
            shutil.copy2(local_source, target_path)
            print(f"[OK] Download blocked, copied bundled file instead: {filename}")
    else:
        print(f"[WARN] No bundled fallback found for: {filename}")


def main() -> None:
    base_path = Path.cwd()

    for folder in ("Source", "Output", "programs", "Additional"):
        ensure_directory(base_path / folder)

    programs_path = base_path / "programs"
    for filename, url in PROGRAM_DOWNLOADS.items():
        download_program(programs_path, filename, url)

    if not download_text(README_DOWNLOAD_URL, base_path / "README.txt"):
        readme_local = Path(__file__).resolve().parent / "README.md"
        if readme_local.exists():
            readme_target = base_path / "README.txt"
            if readme_local.resolve() == readme_target.resolve():
                print("[SKIP] README.txt already available in current folder")
            else:
                shutil.copy2(readme_local, readme_target)
                print("[OK] Download blocked, copied local README.md into README.txt")

    write_file(base_path / SETUP_BAT_NAME, SETUP_BAT_CONTENT)

    legacy_bat = base_path / "Run Program.bat"
    if legacy_bat.exists():
        legacy_bat.unlink()
        print("[OK] Removed legacy Run Program.bat (replaced by Setup.bat)")

    print(f"\nSetup completed (v{INITIALIZATION_VERSION}).")


if __name__ == "__main__":
    main()
