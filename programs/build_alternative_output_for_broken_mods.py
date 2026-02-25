"""Build Alternative Output with only fixed versions of broken source mods."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from check_source_and_extract_to_output import (
        NESTED_PAYLOAD_FOLDER,
        is_bugged_mod_folder,
        transfer_contents,
    )
    from run_logging import ProgramLogger
    from shared_config import config_bool, load_config, root_from_config
except ModuleNotFoundError:
    from programs.check_source_and_extract_to_output import (
        NESTED_PAYLOAD_FOLDER,
        is_bugged_mod_folder,
        transfer_contents,
    )
    from programs.run_logging import ProgramLogger
    from programs.shared_config import config_bool, load_config, root_from_config


def build(source_root: Path, alternative_output_root: Path, do_move: bool, overwrite_files: bool) -> int:
    logger = ProgramLogger("05_alt_build")

    if not source_root.exists() or not source_root.is_dir():
        logger.detail(f"[ERROR] source root does not exist or is not a folder: {source_root}")
        logger.main_summary("failed: source root missing/invalid")
        return 1

    alternative_output_root.mkdir(parents=True, exist_ok=True)

    broken_processed = 0
    normal_skipped = 0
    errors = 0

    broken_mods: list[str] = []
    normal_mods: list[str] = []
    error_mods: list[str] = []

    for mod_folder in source_root.iterdir():
        if not mod_folder.is_dir():
            continue

        if not is_bugged_mod_folder(mod_folder):
            logger.detail(f"[SKIP] {mod_folder.name}: normal mod (not broken)")
            normal_skipped += 1
            normal_mods.append(mod_folder.name)
            continue

        try:
            nested = mod_folder / NESTED_PAYLOAD_FOLDER
            if not nested.exists() or not nested.is_dir():
                logger.detail(f"[ERR ] {mod_folder.name}: broken markers found but '{NESTED_PAYLOAD_FOLDER}' is missing")
                errors += 1
                error_mods.append(mod_folder.name)
                continue

            out_mod_folder = alternative_output_root / mod_folder.name
            out_mod_folder.mkdir(parents=True, exist_ok=True)
            transfer_contents(nested, out_mod_folder, do_move=do_move, overwrite_files=overwrite_files)

            logger.detail(f"[FIX ] {mod_folder.name}: wrote fixed broken mod to Alternative Output")
            broken_processed += 1
            broken_mods.append(mod_folder.name)
        except Exception as exc:
            logger.detail(f"[ERR ] {mod_folder.name}: {exc}")
            errors += 1
            error_mods.append(mod_folder.name)

    logger.detail("\n=== DONE ===")
    logger.detail(f"Broken processed: {broken_processed}")
    logger.detail(f"Normal skipped: {normal_skipped}")
    logger.detail(f"Errors: {errors}")
    logger.main_summary(
        f"broken_processed={broken_processed}, normal_skipped={normal_skipped}, errors={errors}"
    )
    logger.detail_summary(
        "Alternative output build outcome",
        {
            "Broken processed": broken_mods,
            "Normal skipped": normal_mods,
            "Errors": error_mods,
        },
    )
    return 0 if errors == 0 else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Alternative Output with fixed broken mods only.")
    parser.add_argument("--config", type=Path, default=Path("config.json"), help="Path to shared config file.")
    parser.add_argument("source_root", type=Path, nargs="?", help="Source mod folder path override.")
    parser.add_argument(
        "alternative_output_root",
        type=Path,
        nargs="?",
        help="Alternative Output folder path override.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    root = root_from_config(args.config)

    if not config_bool(config.get("enable_alternative_output", False), default=False):
        logger = ProgramLogger("05_alt_build")
        logger.detail("[INFO] Alternative output build is disabled by config (enable_alternative_output=false).")
        logger.main_summary("skipped: enable_alternative_output=false")
        return 0

    source_root = args.source_root or (root / config.get("source_folder", "Source"))
    alternative_output_root = args.alternative_output_root or (
        root / config.get("alternative_output_dir", "Alternative Output")
    )
    do_move = config_bool(config.get("do_move", False), default=False)
    overwrite_files = config_bool(config.get("overwrite_files", True), default=True)

    return build(source_root, alternative_output_root, do_move=do_move, overwrite_files=overwrite_files)


if __name__ == "__main__":
    raise SystemExit(main())
