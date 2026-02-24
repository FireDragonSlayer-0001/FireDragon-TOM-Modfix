from pathlib import Path
import shutil

INITIALIZATION_VERSION = "0.3"

BUNDLED_FILES = [
    "Setup.bat",
    "Launch.bat",
    "Readme.txt",
    "config.json",
    "README.md",
    "First.py",
]

BUNDLED_PROGRAMS = [
    "check_source_and_extract_to_output.py",
    "rename_duplicate_mod_folders.py",
    "validate_output_structure.py",
    "shared_config.py",
]


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Folder ready: {path}")


def copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        print(f"[SKIP] Already exists: {dst.name}")
        return
    shutil.copy2(src, dst)
    print(f"[OK] Added: {dst.name}")


def main() -> None:
    base_path = Path.cwd()
    repo_root = Path(__file__).resolve().parent

    for folder in ("Source", "Output", "programs"):
        ensure_directory(base_path / folder)

    for filename in BUNDLED_FILES:
        src = repo_root / filename
        if src.exists():
            copy_if_missing(src, base_path / filename)

    for filename in BUNDLED_PROGRAMS:
        src = repo_root / "programs" / filename
        if src.exists():
            copy_if_missing(src, base_path / "programs" / filename)

    print(f"\nPortable package scaffold complete (v{INITIALIZATION_VERSION}).")


if __name__ == "__main__":
    main()
