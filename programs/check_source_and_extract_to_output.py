"""Task 1:
Check source mod folders, then extract/copy the correct contents into output.

This script provides the main source-to-output extraction flow with command-line options
so it can be used from the `programs` folder directly.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from run_logging import ProgramLogger
from shared_config import load_config, root_from_config


BUGGED_MARKERS = {"ModProject", "debug"}
NESTED_PAYLOAD_FOLDER = "debug"


def transfer_item(src: Path, dst: Path, do_move: bool, overwrite_files: bool) -> None:
    if src.is_dir():
        if do_move:
            dst.mkdir(parents=True, exist_ok=True)
            for child in src.iterdir():
                transfer_item(child, dst / child.name, do_move=True, overwrite_files=overwrite_files)
            try:
                src.rmdir()
            except OSError:
                pass
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if overwrite_files:
            dst.unlink()
        else:
            print(f"  [SKIP] File exists: {dst}")
            return

    if do_move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(src, dst)


def transfer_contents(src_dir: Path, dst_dir: Path, do_move: bool, overwrite_files: bool) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        transfer_item(item, dst_dir / item.name, do_move, overwrite_files)


def is_bugged_mod_folder(mod_folder: Path) -> bool:
    names = {p.name for p in mod_folder.iterdir() if p.is_dir()}
    return BUGGED_MARKERS.issubset(names)


def run(source_root: Path, output_root: Path, do_move: bool, overwrite_files: bool) -> int:
    logger = ProgramLogger("01_extract")
    if not source_root.exists() or not source_root.is_dir():
        logger.detail(f"[ERROR] source root does not exist or is not a folder: {source_root}")
        logger.main_summary("failed: source root missing/invalid")
        return 1

    output_root.mkdir(parents=True, exist_ok=True)

    total = 0
    fixed = 0
    normal = 0
    skipped = 0

    fixed_mods: list[str] = []
    normal_mods: list[str] = []
    skipped_mods: list[str] = []

    for mod_folder in source_root.iterdir():
        if not mod_folder.is_dir():
            continue

        total += 1
        out_mod_folder = output_root / mod_folder.name
        out_mod_folder.mkdir(parents=True, exist_ok=True)

        try:
            if is_bugged_mod_folder(mod_folder):
                nested = mod_folder / NESTED_PAYLOAD_FOLDER
                if nested.exists() and nested.is_dir():
                    logger.detail(f"[FIX ] {mod_folder.name} -> extracting contents of '{NESTED_PAYLOAD_FOLDER}'")
                    transfer_contents(nested, out_mod_folder, do_move, overwrite_files)
                    fixed += 1
                    fixed_mods.append(mod_folder.name)
                else:
                    logger.detail(f"[WARN] {mod_folder.name} has bug markers but missing '{NESTED_PAYLOAD_FOLDER}'")
                    skipped += 1
                    skipped_mods.append(mod_folder.name)
            else:
                logger.detail(f"[COPY] {mod_folder.name} -> already normal (or not matching bug markers)")
                transfer_contents(mod_folder, out_mod_folder, do_move, overwrite_files)
                normal += 1
                normal_mods.append(mod_folder.name)
        except Exception as exc:
            logger.detail(f"[ERR ] {mod_folder.name}: {exc}")
            skipped += 1
            skipped_mods.append(mod_folder.name)

    mode = "MOVE" if do_move else "COPY"
    logger.detail("\n=== DONE ===")
    logger.detail(f"Mode: {mode}")
    logger.detail(f"Total mod folders: {total}")
    logger.detail(f"Fixed bugged folders: {fixed}")
    logger.detail(f"Normal copied folders: {normal}")
    logger.detail(f"Skipped/errors: {skipped}")
    logger.main_summary(f"mode={mode}, total={total}, fixed={fixed}, normal={normal}, skipped={skipped}")
    logger.detail_summary(
        "Per-mod extraction outcome",
        {
            "Fixed bugged folders": fixed_mods,
            "Normal copied folders": normal_mods,
            "Skipped/error folders": skipped_mods,
        },
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check source mod folders and extract/copy into output.")
    parser.add_argument("source_root", type=Path, nargs="?", help="Path to source mod folder.")
    parser.add_argument("output_root", type=Path, nargs="?", help="Path to output mod folder.")
    parser.add_argument("--config", type=Path, default=Path("config.json"), help="Path to shared config file.")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying (overrides config).")
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite files if they already exist in output (overrides config).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    root = root_from_config(args.config)

    source_root = args.source_root or (root / config.get("source_folder", "Source"))
    output_root = args.output_root or (
        root / config.get("shippable_output_dir", config.get("output_folder", "Output"))
    )

    do_move = args.move if args.move else bool(config.get("do_move", False))
    overwrite_files = (not args.no_overwrite) and bool(config.get("overwrite_files", True))

    return run(
        source_root=source_root,
        output_root=output_root,
        do_move=do_move,
        overwrite_files=overwrite_files,
    )


if __name__ == "__main__":
    raise SystemExit(main())
