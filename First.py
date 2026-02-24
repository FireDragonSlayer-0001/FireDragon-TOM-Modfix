from pathlib import Path
import shutil

from programs.shared_config import load_config

# Config start
CONFIG = load_config(Path(__file__).resolve().parent / "config.json")
SOURCE_ROOT = Path(__file__).resolve().parent / CONFIG.get("source_folder", "Source")
OUTPUT_ROOT = Path(__file__).resolve().parent / CONFIG.get("output_folder", "Output")

# these are for marking what the script checks for, the stuff inside { } is what the script checks for, its a TYPE ALL
BUGGED_MARKERS = {"ModProject", "debug"}

# this is where the script extracts the proper file structure from
NESTED_PAYLOAD_FOLDER = "debug"

DO_MOVE = bool(CONFIG.get("do_move", False))
OVERWRITE_FILES = bool(CONFIG.get("overwrite_files", True))
# Config End


def transfer_item(src: Path, dst: Path, do_move: bool):
    if src.is_dir():
        if do_move:
            dst.mkdir(parents=True, exist_ok=True)
            for child in src.iterdir():
                transfer_item(child, dst / child.name, do_move=True)
            try:
                src.rmdir()
            except OSError:
                pass
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if OVERWRITE_FILES:
                dst.unlink()
            else:
                print(f"  [SKIP] File exists: {dst}")
                return
        if do_move:
            shutil.move(str(src), str(dst))
        else:
            shutil.copy2(src, dst)


def transfer_contents(src_dir: Path, dst_dir: Path, do_move: bool):
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        transfer_item(item, dst_dir / item.name, do_move)


def is_bugged_mod_folder(mod_folder: Path) -> bool:
    names = {p.name for p in mod_folder.iterdir() if p.is_dir()}
    return BUGGED_MARKERS.issubset(names)


def main():
    if not SOURCE_ROOT.exists() or not SOURCE_ROOT.is_dir():
        print(f"[ERROR] SOURCE_ROOT not found or not a folder: {SOURCE_ROOT}")
        return

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    total = 0
    fixed = 0
    normal = 0
    skipped = 0

    for mod_folder in SOURCE_ROOT.iterdir():
        if not mod_folder.is_dir():
            continue

        total += 1
        out_mod_folder = OUTPUT_ROOT / mod_folder.name
        out_mod_folder.mkdir(parents=True, exist_ok=True)

        try:
            if is_bugged_mod_folder(mod_folder):
                nested = mod_folder / NESTED_PAYLOAD_FOLDER
                if nested.exists() and nested.is_dir():
                    print(f"[FIX ] {mod_folder.name} -> extracting contents of '{NESTED_PAYLOAD_FOLDER}'")
                    transfer_contents(nested, out_mod_folder, DO_MOVE)
                    fixed += 1
                else:
                    print(f"[WARN] {mod_folder.name} has bug markers but missing '{NESTED_PAYLOAD_FOLDER}'")
                    skipped += 1
            else:
                print(f"[COPY] {mod_folder.name} -> already normal (or not matching bug markers)")
                transfer_contents(mod_folder, out_mod_folder, DO_MOVE)
                normal += 1

        except Exception as e:
            print(f"[ERR ] {mod_folder.name}: {e}")
            skipped += 1

    mode = "MOVE" if DO_MOVE else "COPY"
    print("\n=== DONE ===")
    print(f"Mode: {mode}")
    print(f"Total mod folders: {total}")
    print(f"Fixed bugged folders: {fixed}")
    print(f"Normal copied folders: {normal}")
    print(f"Skipped/errors: {skipped}")


if __name__ == "__main__":
    main()
